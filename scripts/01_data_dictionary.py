"""Generate a data dictionary report for the pilot dataset (47 respondents).

Produces:
  reports/data_dictionary.md  - feature-by-feature description with stats
  reports/figures/01_feature_distributions.png - histograms by group
  reports/figures/01_outlier_overview.png - boxplots of neiry features
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import (
    GARDNER_FEATURES, ID_COL, MBTI_SCALE_FEATURES, MBTI_TYPE_COL,
    NEIRY_FEATURES, ROLE_FEATURES, load_pilot,
)

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
REPORTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")


def _stats_row(s: pd.Series) -> dict:
    if pd.api.types.is_numeric_dtype(s):
        return {
            "n_unique": int(s.nunique()),
            "n_missing": int(s.isna().sum()),
            "min": round(float(s.min()), 4),
            "p25": round(float(s.quantile(0.25)), 4),
            "median": round(float(s.median()), 4),
            "mean": round(float(s.mean()), 4),
            "p75": round(float(s.quantile(0.75)), 4),
            "max": round(float(s.max()), 4),
            "std": round(float(s.std()), 4),
            "skew": round(float(s.skew()), 4),
        }
    return {
        "n_unique": int(s.nunique()),
        "n_missing": int(s.isna().sum()),
        "min": "-", "p25": "-", "median": "-", "mean": "-",
        "p75": "-", "max": "-", "std": "-", "skew": "-",
    }


def _group_table(df: pd.DataFrame, columns: list[str]) -> str:
    rows = []
    for col in columns:
        s = df[col]
        stats = _stats_row(s)
        stats["feature"] = col
        stats["dtype"] = str(s.dtype)
        rows.append(stats)
    out = pd.DataFrame(rows)[
        ["feature", "dtype", "n_unique", "n_missing",
         "min", "p25", "median", "mean", "p75", "max", "std", "skew"]
    ]
    return out.to_markdown(index=False)


def _detect_outliers_iqr(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        s = df[col].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (s < lower) | (s > upper)
        if mask.any():
            rows.append({
                "feature": col,
                "n_outliers_iqr": int(mask.sum()),
                "lower_iqr": round(float(lower), 4),
                "upper_iqr": round(float(upper), 4),
                "min": round(float(s.min()), 4),
                "max": round(float(s.max()), 4),
                "ratio_max_to_p99": round(float(s.max() / max(s.quantile(0.99), 1e-9)), 2),
            })
    return pd.DataFrame(rows)


def _plot_grid(df: pd.DataFrame, columns: list[str], title: str, out_path: Path,
               n_cols: int = 4) -> None:
    n = len(columns)
    n_rows = (n + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 2.6 * n_rows))
    axes = np.array(axes).flatten()
    for i, col in enumerate(columns):
        ax = axes[i]
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#3a7ca5")
        ax.set_title(col, fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle(title, fontsize=13, y=1.001)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = load_pilot()
    print(f"loaded shape: {df.shape}")

    # --- Markdown report ---
    lines: list[str] = []
    lines.append("# Data Dictionary - Pilot Dataset (n=47)\n")
    lines.append(f"Source: `data/raw/pilot_47x65_anon.csv`  \nRows: **{df.shape[0]}**  \n"
                 f"Columns: **{df.shape[1]}**  \nMissing values total: "
                 f"**{int(df.isna().sum().sum())}**\n")

    lines.append("## Identifier\n")
    lines.append(_group_table(df, [ID_COL]))
    lines.append("")

    lines.append("## 1. Gardner's Multiple Intelligences (9 features)\n")
    lines.append("Continuous percentile scores 0..100 from a Gardner self-report battery.\n")
    lines.append(_group_table(df, GARDNER_FEATURES))
    lines.append("")

    lines.append("## 2. MBTI - Type and Continuous Scales (1 + 10 features)\n")
    lines.append(f"Categorical type: `{MBTI_TYPE_COL}` "
                 f"(unique values: {df[MBTI_TYPE_COL].nunique()}).  \n"
                 "Each dichotomy is encoded as two complementary percentile scales summing "
                 "to 100. For modeling we use one side per dichotomy "
                 "(see `MBTI_INDEPENDENT_SCALES`).\n")
    lines.append("**Type frequency:**\n")
    type_counts = df[MBTI_TYPE_COL].value_counts().to_frame("count")
    type_counts["pct"] = (type_counts["count"] / len(df) * 100).round(1)
    lines.append(type_counts.to_markdown())
    lines.append("\n**Continuous MBTI scales:**\n")
    lines.append(_group_table(df, MBTI_SCALE_FEATURES))
    lines.append("")

    lines.append("## 3. Neiry Role Rankings (20 features)\n")
    lines.append("Per-respondent ranking 1..20 across 20 archetypal professional roles. "
                 "Lower rank = stronger affinity. These are produced by Neiry's own "
                 "proprietary model and serve as a partial ground-truth target for the "
                 "supervised layer of the system.\n")
    lines.append(_group_table(df, ROLE_FEATURES))
    lines.append("")

    lines.append("## 4. Neiry EEG Metrics (24 features)\n")
    lines.append("All metrics derived by the Neiry headset firmware from a 5-minute "
                 "resting-state recording with dry electrodes.  \n"
                 "Naming convention: `Baseline ...` = individual norm computed from a "
                 "calibration window; the same metric without the prefix = current "
                 "(actual) value during the test session.\n")
    lines.append(_group_table(df, NEIRY_FEATURES))
    lines.append("")

    lines.append("## 5. Outlier Detection (IQR rule, 1.5x)\n")
    lines.append("Features where at least one observation lies beyond Q1-1.5xIQR or "
                 "Q3+1.5xIQR. The `ratio_max_to_p99` column flags extreme tails.\n")
    outliers = _detect_outliers_iqr(df, GARDNER_FEATURES + MBTI_SCALE_FEATURES + NEIRY_FEATURES)
    if outliers.empty:
        lines.append("No IQR outliers detected.\n")
    else:
        outliers = outliers.sort_values("ratio_max_to_p99", ascending=False)
        lines.append(outliers.to_markdown(index=False))
        worst = outliers.iloc[0]
        lines.append(f"\n> **Note.** The most extreme tail belongs to "
                     f"`{worst['feature']}` (max={worst['max']}, "
                     f"p99-ratio={worst['ratio_max_to_p99']}). This matches the "
                     "observation in the thesis (тезис) about a single subject with "
                     "max=216.15 in fatigue. Recommended handling: winsorize at "
                     "p99 or apply log1p before downstream modeling.\n")

    out_md = REPORTS / "data_dictionary.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote: {out_md}")

    # --- Figures ---
    _plot_grid(df, list(GARDNER_FEATURES), "Gardner Multiple Intelligences",
               FIGURES / "01a_gardner_distributions.png", n_cols=3)
    _plot_grid(df, list(MBTI_SCALE_FEATURES), "MBTI Continuous Scales",
               FIGURES / "01b_mbti_distributions.png", n_cols=5)
    _plot_grid(df, list(NEIRY_FEATURES), "Neiry EEG Metrics",
               FIGURES / "01c_neiry_distributions.png", n_cols=5)

    # outlier boxplot for neiry
    fig, ax = plt.subplots(figsize=(11, 7))
    melted = df[list(NEIRY_FEATURES)].melt(var_name="feature", value_name="value")
    sns.boxplot(data=melted, y="feature", x="value", ax=ax, color="#3a7ca5",
                fliersize=3, linewidth=0.8)
    ax.set_title("Neiry features - boxplot overview (raw, before normalization)")
    ax.set_xscale("symlog")
    ax.set_xlabel("value (symlog scale)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIGURES / "01d_neiry_outliers_boxplot.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    print(f"wrote figures to: {FIGURES}")


if __name__ == "__main__":
    main()
