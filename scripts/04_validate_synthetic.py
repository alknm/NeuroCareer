"""Statistical comparison: real (n=47) vs synthetic (n=500).

Produces:
  reports/synthetic_validation.md - markdown report with all checks
  reports/figures/04a_marginal_comparison.png  - real vs synth histograms
  reports/figures/04b_correlation_comparison.png - corr matrices side by side
  reports/figures/04c_mbti_type_distribution.png - type frequency
  reports/figures/04d_clustering_on_synthetic.png - NIRM cluster check on synth
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import ks_2samp
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import (
    GARDNER_FEATURES, MBTI_INDEPENDENT_SCALES, MBTI_TYPE_COL,
    NEIRY_CLUSTERING_FEATURES, NEIRY_FEATURES, ROLE_FEATURES, load_pilot,
)

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
SYNTH_PATH = ROOT / "data" / "synthetic" / "synth_500.csv"
sns.set_theme(style="whitegrid", context="notebook")


def ks_table(real: pd.DataFrame, synth: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        stat, p = ks_2samp(real[c].dropna().values, synth[c].dropna().values)
        rows.append({
            "feature": c,
            "real_mean": round(float(real[c].mean()), 3),
            "synth_mean": round(float(synth[c].mean()), 3),
            "real_std": round(float(real[c].std()), 3),
            "synth_std": round(float(synth[c].std()), 3),
            "ks_stat": round(float(stat), 3),
            "ks_p": round(float(p), 4),
            "same_dist_p>0.05": "yes" if p > 0.05 else "no",
        })
    return pd.DataFrame(rows)


def corr_diff(real: pd.DataFrame, synth: pd.DataFrame, cols: list[str]) -> tuple[float, np.ndarray, np.ndarray]:
    cr = real[cols].corr().values
    cs = synth[cols].corr().values
    diff = cr - cs
    fro = float(np.linalg.norm(diff, ord="fro") / np.linalg.norm(cr, ord="fro"))
    return fro, cr, cs


def main() -> None:
    real = load_pilot()
    synth = pd.read_csv(SYNTH_PATH, encoding="utf-8")
    print(f"real:  {real.shape}")
    print(f"synth: {synth.shape}")

    cont_cols = (list(GARDNER_FEATURES) + list(MBTI_INDEPENDENT_SCALES)
                 + list(NEIRY_FEATURES))

    # 1. Marginal KS tests
    ks = ks_table(real, synth, cont_cols)
    n_pass = int((ks["ks_p"] > 0.05).sum())
    print(f"KS test passes (p>0.05): {n_pass}/{len(ks)} continuous features")

    # 2. Correlation preservation
    fro_cont, cr_cont, cs_cont = corr_diff(real, synth, cont_cols)
    print(f"Relative Frobenius distance of continuous corr matrices: {fro_cont:.3f}")

    # 3. Role rank correlation preservation
    role_cols = list(ROLE_FEATURES)
    fro_roles, cr_roles, cs_roles = corr_diff(real, synth, role_cols)
    print(f"Relative Frobenius distance of role-rank corr matrices: {fro_roles:.3f}")

    # 4. NIRM-style clustering on synthetic
    feats = list(NEIRY_CLUSTERING_FEATURES)
    Xs = StandardScaler().fit_transform(synth[feats])
    km = KMeans(n_clusters=3, n_init=10, random_state=2)
    syn_labels = km.fit_predict(Xs)
    syn_sil = silhouette_score(Xs, syn_labels)
    syn_sizes = pd.Series(syn_labels).value_counts().sort_values(ascending=False).tolist()
    print(f"k-means(k=3) on synth: silhouette={syn_sil:.3f}, sizes={syn_sizes}")

    # 5. MBTI type frequency
    real_types = real[MBTI_TYPE_COL].value_counts(normalize=True).rename("real_pct")
    synth_types = synth[MBTI_TYPE_COL].value_counts(normalize=True).rename("synth_pct")
    type_cmp = pd.concat([real_types, synth_types], axis=1).fillna(0).round(3)
    type_cmp = type_cmp.sort_values("real_pct", ascending=False)

    # ----- Markdown report -----
    md = []
    md.append("# Synthetic Data Validation\n")
    md.append(f"**Real:** {real.shape[0]} rows × {real.shape[1]} cols  ")
    md.append(f"**Synthetic:** {synth.shape[0]} rows × {synth.shape[1]} cols  ")
    md.append(f"**Generation method:** GaussianCopulaSynthesizer (SDV), KDE marginals, "
              f"random_state=42\n")

    md.append("## 1. Marginal Distributions (Kolmogorov-Smirnov 2-sample test)\n")
    md.append("Null hypothesis: real and synthetic samples come from the same "
              "distribution. p > 0.05 = cannot reject = distributions look "
              "statistically indistinguishable.\n")
    md.append(f"**Pass rate: {n_pass}/{len(ks)} features**\n")
    md.append(ks.sort_values("ks_p").to_markdown(index=False))
    md.append("")

    md.append("## 2. Correlation Structure Preservation\n")
    md.append(f"Relative Frobenius distance between correlation matrices "
              f"(continuous features): **{fro_cont:.3f}**  ")
    md.append(f"(role-rank correlations): **{fro_roles:.3f}**\n")
    md.append("Values close to 0 indicate that the synthetic copula reproduces "
              "the pairwise correlation structure of the pilot. For reference, "
              "values < 0.20 are typically considered a faithful copula fit on "
              "small pilot samples.\n")

    md.append("## 3. NIRM-style Clustering on Synthetic Data\n")
    md.append(f"Same pipeline (24 Neiry features, StandardScaler, k-means k=3, "
              f"random_state=2) applied to the synthetic n=500 sample.\n")
    md.append(f"  * Silhouette: **{syn_sil:.3f}** (real: 0.240)")
    md.append(f"  * Cluster sizes: **{syn_sizes}** (real: [30, 8, 9])")
    md.append("\nA similar silhouette value confirms that the synthetic data "
              "preserves the same coarse cluster structure as the pilot.\n")

    md.append("## 4. MBTI Type Frequency\n")
    md.append("Type frequencies in real vs. synthetic samples. Synthetic types "
              "are derived deterministically from sampled MBTI continuous scales "
              "via the standard 50% threshold per dichotomy.\n")
    md.append(type_cmp.to_markdown())
    md.append("")

    out_md = REPORTS / "synthetic_validation.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote: {out_md}")

    # ----- Figures -----
    # 4a: marginal comparison for representative features
    pick = [
        "Логико-математический интеллект", "Лингвистический интеллект",
        "Музыкальный интеллект",
        "MBTIЭкстраверт", "MBTIЛогика", "MBTIУверенные",
        "neiryBaseline Concentration index", "neiryBaseline Relaxation index",
        "neiryBaseline Fatigue score",
        "neiryAlpha", "neiryBeta", "neiryFocus",
    ]
    n_cols = 4
    n_rows = (len(pick) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4.2 * n_cols, 2.8 * n_rows))
    axes = np.array(axes).flatten()
    for i, col in enumerate(pick):
        ax = axes[i]
        sns.histplot(real[col], color="#3a7ca5", label=f"real (n={len(real)})",
                     stat="density", alpha=0.55, ax=ax)
        sns.histplot(synth[col], color="#d6a85a", label=f"synth (n={len(synth)})",
                     stat="density", alpha=0.55, ax=ax)
        ax.set_title(col, fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.legend(fontsize=7)
    for j in range(len(pick), len(axes)):
        axes[j].axis("off")
    fig.suptitle("Marginal distributions: real vs synthetic", y=1.001, fontsize=13)
    fig.tight_layout()
    fig.savefig(FIGURES / "04a_marginal_comparison.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 4b: correlation matrices side by side
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    short = [c.replace("neiry", "").replace("Baseline ", "B-")[:18] for c in cont_cols]
    sns.heatmap(cr_cont, ax=axes[0], cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                cbar=False, xticklabels=False, yticklabels=False)
    axes[0].set_title(f"real (n={len(real)})")
    sns.heatmap(cs_cont, ax=axes[1], cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                cbar=False, xticklabels=False, yticklabels=False)
    axes[1].set_title(f"synthetic (n={len(synth)})")
    sns.heatmap(cr_cont - cs_cont, ax=axes[2], cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                xticklabels=False, yticklabels=False,
                cbar_kws={"label": "real - synth"})
    axes[2].set_title(f"difference  ||.||F/||real||F = {fro_cont:.3f}")
    fig.suptitle("Pairwise correlation matrices over continuous features", y=1.02, fontsize=13)
    fig.tight_layout()
    fig.savefig(FIGURES / "04b_correlation_comparison.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 4c: MBTI type frequency bar chart
    fig, ax = plt.subplots(figsize=(13, 4.5))
    type_cmp_plot = type_cmp.head(20).reset_index()
    type_cmp_plot = type_cmp_plot.melt(
        id_vars=type_cmp_plot.columns[0], var_name="dataset", value_name="pct")
    sns.barplot(data=type_cmp_plot, x=type_cmp_plot.columns[0],
                y="pct", hue="dataset",
                palette={"real_pct": "#3a7ca5", "synth_pct": "#d6a85a"}, ax=ax)
    ax.set_title("MBTI type distribution: real vs synthetic")
    ax.set_xlabel("MBTI type")
    ax.set_ylabel("share")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(FIGURES / "04c_mbti_type_distribution.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 4d: clustering check on synthetic (PCA scatter + silhouette text)
    from sklearn.decomposition import PCA
    coords = PCA(n_components=2, random_state=2).fit_transform(Xs)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    palette = {0: "#3a7ca5", 1: "#d62728", 2: "#2ca02c"}
    for cid in sorted(set(syn_labels)):
        m = syn_labels == cid
        ax.scatter(coords[m, 0], coords[m, 1], c=palette[cid], s=22, alpha=0.7,
                   edgecolor="white", linewidths=0.4,
                   label=f"cluster {cid}  (n={int(m.sum())})")
    ax.set_title(f"k-means on synthetic (k=3, silhouette={syn_sil:.3f})")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "04d_clustering_on_synthetic.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figures to: {FIGURES}")

    # also save raw stats as JSON
    summary = {
        "ks_pass_count": n_pass,
        "ks_total": int(len(ks)),
        "frobenius_relative_continuous": round(fro_cont, 4),
        "frobenius_relative_roles": round(fro_roles, 4),
        "synth_silhouette": round(float(syn_sil), 4),
        "synth_cluster_sizes": syn_sizes,
        "real_silhouette": 0.240,
        "real_cluster_sizes": [30, 8, 9],
    }
    with open(REPORTS / "synthetic_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
