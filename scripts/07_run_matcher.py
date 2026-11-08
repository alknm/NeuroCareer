"""Run the hybrid matcher on the pilot dataset and analyze recommendations.

Outputs:
  data/processed/recommendations.csv      - top-10 recommendations per respondent
  reports/matcher_examples.md             - 5 illustrative full reports
  reports/matcher_summary.json            - global statistics
  reports/figures/07a_top_categories.png  - which categories get recommended
  reports/figures/07b_score_distribution.png  - distribution of top-1 scores
  reports/figures/07c_breakdown_by_cluster.png - score components per cluster
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ID_COL, MBTI_TYPE_COL, load_pilot
from core.matcher import build_default_matcher

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
PROCESSED = ROOT / "data" / "processed"
sns.set_theme(style="whitegrid", context="notebook")


def main() -> None:
    pilot = load_pilot()
    canonical = pd.read_csv(PROCESSED / "clusters_canonical.csv", encoding="utf-8")
    pilot = pilot.merge(canonical, on=ID_COL)
    print(f"pilot: {pilot.shape}")

    matcher = build_default_matcher()
    print(f"matcher loaded: {len(matcher.professions)} professions, "
          f"weights={matcher.weights.as_dict()}")

    # --- batch matching ---
    all_records = []
    full_results: dict[str, list] = {}
    for _, row in pilot.iterrows():
        user = pd.DataFrame([row])
        matches = matcher.match(user, top_k=10)
        full_results[row[ID_COL]] = matches
        for rank, m in enumerate(matches, start=1):
            all_records.append({
                "respondent_id": row[ID_COL],
                "respondent_mbti": row[MBTI_TYPE_COL],
                "respondent_cluster": row["cluster_label"],
                "rank": rank,
                "profession_id": m.profession_id,
                "profession_ru": m.name_ru,
                "category": m.category,
                "total_score": round(m.total_score, 2),
                "score_gardner": round(m.breakdown.gardner, 2),
                "score_mbti": round(m.breakdown.mbti, 2),
                "score_cluster": round(m.breakdown.cluster, 2),
                "score_roles": round(m.breakdown.roles, 2),
            })

    rec_df = pd.DataFrame(all_records)
    rec_df.to_csv(PROCESSED / "recommendations.csv", index=False, encoding="utf-8")
    print(f"saved per-respondent top-10 -> {PROCESSED/'recommendations.csv'}")

    # --- summary statistics ---
    top1 = rec_df[rec_df["rank"] == 1]
    cat_top1 = top1["category"].value_counts()
    cat_top10 = rec_df["category"].value_counts()
    prof_top1 = top1["profession_ru"].value_counts()
    prof_top10 = rec_df["profession_ru"].value_counts()
    score_top1_stats = top1["total_score"].describe().round(2).to_dict()
    score_top10_stats = rec_df["total_score"].describe().round(2).to_dict()

    n_unique_top1 = top1["profession_id"].nunique()
    n_unique_top10 = rec_df["profession_id"].nunique()

    summary = {
        "n_respondents": int(pilot.shape[0]),
        "n_professions_in_kb": len(matcher.professions),
        "weights": matcher.weights.as_dict(),
        "top1_score_stats": score_top1_stats,
        "top10_score_stats": score_top10_stats,
        "top1_category_distribution": cat_top1.to_dict(),
        "top10_category_distribution": cat_top10.to_dict(),
        "n_unique_professions_seen_at_top1": int(n_unique_top1),
        "n_unique_professions_seen_in_top10": int(n_unique_top10),
        "top10_most_recommended_top1": prof_top1.head(10).to_dict(),
        "top10_most_recommended_overall": prof_top10.head(10).to_dict(),
    }
    with open(REPORTS / "matcher_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"saved summary -> {REPORTS/'matcher_summary.json'}")

    # --- examples markdown ---
    examples_idx = []
    by_cluster = pilot.groupby("cluster_label")
    for label in ["balanced", "mobilized", "depleted"]:
        if label in by_cluster.groups:
            sub = pilot.loc[by_cluster.groups[label]]
            scores = top1[top1["respondent_id"].isin(sub[ID_COL])].set_index("respondent_id")
            if not scores.empty:
                best_id = scores["total_score"].idxmax()
                examples_idx.append(best_id)
    rng = np.random.default_rng(42)
    extras = list(set(pilot[ID_COL]) - set(examples_idx))
    if len(extras) >= 2:
        examples_idx += list(rng.choice(extras, size=2, replace=False))

    md = ["# Hybrid Matcher - Illustrative Recommendations\n"]
    md.append("Five sample respondents drawn from across the three cognitive "
              "clusters (balanced / mobilized / depleted). For each respondent "
              "the matcher returns the top-5 professions with a per-component "
              "breakdown; LLM-driven natural-language explanations will be "
              "added in Stage 5.\n")
    for rid in examples_idx:
        row = pilot[pilot[ID_COL] == rid].iloc[0]
        matches = full_results[rid][:5]
        md.append(f"## {rid}")
        md.append(f"* MBTI: **{row[MBTI_TYPE_COL]}**, cluster: **{row['cluster_label']}**")
        from core.data_loader import GARDNER_FEATURES as G
        top_intel = pd.Series({k: row[k] for k in G}).sort_values(ascending=False).head(3)
        md.append("* Top intelligences: " + ", ".join(
            f"{k} ({v:.0f})" for k, v in top_intel.items()))
        md.append("")
        rows = []
        for i, m in enumerate(matches, start=1):
            rows.append({
                "rank": i,
                "profession": m.name_ru,
                "category": m.category,
                "total": round(m.total_score, 1),
                "gardner": round(m.breakdown.gardner, 1),
                "mbti": round(m.breakdown.mbti, 1),
                "cluster": round(m.breakdown.cluster, 1),
                "roles": round(m.breakdown.roles, 1),
            })
        md.append(pd.DataFrame(rows).to_markdown(index=False))
        md.append("")
    (REPORTS / "matcher_examples.md").write_text("\n".join(md), encoding="utf-8")
    print(f"saved examples -> {REPORTS/'matcher_examples.md'}")

    # --- figures ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    cat_top1.sort_values().plot(kind="barh", ax=axes[0], color="#3a7ca5")
    axes[0].set_title(f"Top-1 recommendation: category distribution (n={len(top1)})")
    axes[0].set_xlabel("# respondents")
    cat_top10.sort_values().plot(kind="barh", ax=axes[1], color="#d6a85a")
    axes[1].set_title(f"Top-10 recommendations: category distribution (total {len(rec_df)})")
    axes[1].set_xlabel("# slots")
    fig.tight_layout()
    fig.savefig(FIGURES / "07a_top_categories.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.histplot(top1["total_score"], bins=15, color="#3a7ca5", kde=True, ax=ax)
    ax.set_title("Distribution of best (top-1) match scores across respondents")
    ax.set_xlabel("score (0..100)")
    ax.axvline(top1["total_score"].mean(), color="red", ls="--",
               label=f"mean = {top1['total_score'].mean():.1f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "07b_score_distribution.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    breakdown_long = top1.melt(
        id_vars=["respondent_id", "respondent_cluster"],
        value_vars=["score_gardner", "score_mbti", "score_cluster", "score_roles"],
        var_name="component", value_name="score")
    breakdown_long["component"] = breakdown_long["component"].str.replace("score_", "")
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=breakdown_long, x="component", y="score",
                hue="respondent_cluster",
                palette={"balanced": "#3a7ca5", "mobilized": "#d62728",
                         "depleted": "#2ca02c"}, ax=ax)
    ax.set_title("Top-1 score breakdown by component, grouped by user cluster")
    ax.set_ylabel("component score (0..100)")
    fig.tight_layout()
    fig.savefig(FIGURES / "07c_breakdown_by_cluster.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    print("\n=== Matcher summary ===")
    print(f"  unique professions at top-1: {n_unique_top1} / {len(matcher.professions)}")
    print(f"  unique professions in top-10: {n_unique_top10} / {len(matcher.professions)}")
    print(f"  mean top-1 score: {top1['total_score'].mean():.2f}")
    print("  category distribution at top-1:")
    for c, n in cat_top1.items():
        print(f"    {c:14s} {n}")


if __name__ == "__main__":
    main()
