"""SHAP feature importance for the role-prediction layer.

Uses TreeExplainer on the trained Random Forest (chosen because it has the
strongest CV-on-real performance among non-baseline models, and tree
explainers are exact and fast).

Outputs:
  reports/figures/06a_shap_feature_role_heatmap.png  (38 features x 20 roles)
  reports/figures/06b_shap_global_importance.png     (top features overall)
  reports/figures/06c_shap_top_role_drivers.png      (per-role top drivers)
  reports/shap_top_drivers.json                       (machine-readable)
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ROLE_FEATURES, load_pilot
from core.role_predictor import INPUT_FEATURES, split_X_y_ranks

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
MODELS = ROOT / "data" / "processed" / "role_models"
sns.set_theme(style="whitegrid", context="notebook")
warnings.filterwarnings("ignore")

ROLE_NAMES = list(ROLE_FEATURES)


def _short_feature_name(name: str) -> str:
    return (name
            .replace("neiry", "")
            .replace("Baseline ", "B-")
            .replace(" интеллект", " intel.")
            .replace("MBTI", "MBTI-")[:28])


def main() -> None:
    real = load_pilot()
    X, _, _ = split_X_y_ranks(real)
    print(f"real shape: {real.shape}, X shape: {X.shape}")

    # Load Random Forest fitted on synthetic
    rf_path = MODELS / "random_forest_synth_to_real.joblib"
    rf_predictor = joblib.load(rf_path)
    pipeline = rf_predictor.pipeline
    scaler = pipeline.named_steps["scaler"]
    regressor = pipeline.named_steps["regressor"]

    X_scaled = scaler.transform(X)
    print("computing SHAP values via TreeExplainer ...")
    explainer = shap.TreeExplainer(regressor)
    shap_values = explainer.shap_values(X_scaled, check_additivity=False)

    # Multi-output: shap_values is either (n_samples, n_features, n_outputs)
    # or list of length n_outputs. Normalize to ndarray (n_samples, n_features, n_outputs).
    if isinstance(shap_values, list):
        sv = np.stack(shap_values, axis=-1)
    else:
        sv = np.asarray(shap_values)
    if sv.ndim == 2:
        sv = sv[..., np.newaxis]
    print(f"SHAP shape: {sv.shape}  (samples, features, roles)")

    # mean |SHAP| per (feature, role) -> 2D matrix
    abs_mean = np.abs(sv).mean(axis=0)  # shape (n_features, n_roles)
    # If shap returned (samples, features), abs_mean shape might be (features,) - reshape
    if abs_mean.ndim == 1:
        abs_mean = abs_mean[:, np.newaxis]
    print(f"abs_mean shape: {abs_mean.shape}")

    feat_names_short = [_short_feature_name(c) for c in INPUT_FEATURES]
    importance_df = pd.DataFrame(abs_mean, index=feat_names_short, columns=ROLE_NAMES)
    importance_df.to_csv(REPORTS / "shap_feature_role_matrix.csv", encoding="utf-8")

    # ----- Figure 1: heatmap features x roles -----
    fig, ax = plt.subplots(figsize=(13, 11))
    sns.heatmap(importance_df, annot=False, cmap="rocket_r",
                cbar_kws={"label": "mean |SHAP|"}, ax=ax,
                xticklabels=True, yticklabels=True)
    ax.set_title("SHAP feature importance per role (Random Forest, real holdout)")
    ax.set_xlabel(""); ax.set_ylabel("feature")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
    plt.setp(ax.get_yticklabels(), fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "06a_shap_feature_role_heatmap.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ----- Figure 2: global feature importance (sum over roles) -----
    global_imp = importance_df.sum(axis=1).sort_values(ascending=True)
    top_n = 20
    global_top = global_imp.tail(top_n)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.barh(global_top.index, global_top.values, color="#3a7ca5")
    ax.set_xlabel("sum of mean |SHAP| over 20 roles")
    ax.set_title(f"Top-{top_n} most influential features overall")
    fig.tight_layout()
    fig.savefig(FIGURES / "06b_shap_global_importance.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ----- Figure 3: top 3 driver features per role -----
    top_drivers: dict[str, list[dict]] = {}
    for role in ROLE_NAMES:
        col = importance_df[role].sort_values(ascending=False)
        # also recover sign of the average effect by checking mean signed SHAP
        role_idx = ROLE_NAMES.index(role)
        signed_mean = sv[:, :, role_idx].mean(axis=0)  # (n_features,)
        top_drivers[role] = []
        for f_short in col.head(3).index:
            f_idx = feat_names_short.index(f_short)
            top_drivers[role].append({
                "feature": INPUT_FEATURES[f_idx],
                "feature_short": f_short,
                "abs_importance": float(col[f_short]),
                "signed_mean_shap": float(signed_mean[f_idx]),
                "direction": "high feature -> better rank" if signed_mean[f_idx] < 0
                              else "high feature -> worse rank",
            })

    # plot: 4 rows x 5 cols of small horizontal bars
    n_cols = 5
    n_rows = (len(ROLE_NAMES) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 1.7 * n_rows))
    axes = np.array(axes).flatten()
    for i, role in enumerate(ROLE_NAMES):
        ax = axes[i]
        feats = [d["feature_short"] for d in top_drivers[role]]
        vals = [d["abs_importance"] for d in top_drivers[role]]
        colors = ["#2ca02c" if d["signed_mean_shap"] < 0 else "#d62728"
                  for d in top_drivers[role]]
        ax.barh(feats[::-1], vals[::-1], color=colors[::-1])
        ax.set_title(role, fontsize=9)
        ax.tick_params(axis="y", labelsize=7)
        ax.tick_params(axis="x", labelsize=7)
    for j in range(len(ROLE_NAMES), len(axes)):
        axes[j].axis("off")
    fig.suptitle("Top-3 SHAP drivers per role  "
                 "(green = high feature -> stronger rank; "
                 "red = high feature -> weaker rank)", y=1.005, fontsize=12)
    fig.tight_layout()
    fig.savefig(FIGURES / "06c_shap_top_role_drivers.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # ----- machine-readable export -----
    with open(REPORTS / "shap_top_drivers.json", "w", encoding="utf-8") as f:
        json.dump(top_drivers, f, ensure_ascii=False, indent=2)

    print(f"saved figures to: {FIGURES}")
    print(f"top global features:")
    for f, v in global_imp.tail(10)[::-1].items():
        print(f"  {f:30s}  importance={v:.4f}")


if __name__ == "__main__":
    main()
