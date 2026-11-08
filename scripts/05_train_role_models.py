"""Train and evaluate role-prediction models for the supervised layer.

Two evaluation regimes are reported:

  1) PRIMARY  - Train on synthetic (n=500), test on real (n=47).
                Demonstrates that a model fit on the augmented distribution
                generalizes to the real pilot.

  2) SECONDARY - Stratified 5-fold cross-validation on real (n=47).
                Honest in-distribution performance with a tiny sample;
                metrics will be noisy but informative as a lower bound.

Outputs:
  data/processed/role_models/<name>.joblib    - fitted pipelines
  reports/role_prediction_metrics.json        - all metrics
  reports/figures/05a_metric_comparison.png   - bar chart per metric per model
  reports/figures/05b_per_role_mae.png        - per-role MAE for best model
  reports/figures/05c_predicted_vs_true.png   - scatter on real holdout
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
from sklearn.model_selection import KFold

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ROLE_FEATURES, load_pilot
from core.ranking_metrics import evaluate_all
from core.role_predictor import (
    MarginalBaseline, RolePredictor, baseline_marginal_predictor,
    make_default_zoo, make_lightgbm_predictor, split_X_y_ranks,
)

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
MODELS = ROOT / "data" / "processed" / "role_models"
MODELS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")

SYNTH_PATH = ROOT / "data" / "synthetic" / "synth_500.csv"
ROLE_NAMES = list(ROLE_FEATURES)

warnings.filterwarnings("ignore", category=UserWarning)


def _eval_predictor(predictor, X_test: pd.DataFrame, Y_ranks_test: np.ndarray) -> dict:
    """Evaluate predictor, supporting both RolePredictor and MarginalBaseline."""
    if isinstance(predictor, MarginalBaseline):
        pred_ranks = predictor.predict_ranks(X_test)
    else:
        pred_ranks = predictor.predict_ranks(X_test)
    return evaluate_all(Y_ranks_test, pred_ranks, ROLE_NAMES)


def primary_evaluation(synth: pd.DataFrame, real: pd.DataFrame) -> dict:
    """Train on synthetic, test on real."""
    X_train, Y_ranks_train, Y_scores_train = split_X_y_ranks(synth)
    X_test, Y_ranks_test, _ = split_X_y_ranks(real)

    print(f"\n[PRIMARY] train: {X_train.shape}, test: {X_test.shape}")
    results = {}

    # 0. Marginal baseline
    base = baseline_marginal_predictor(Y_ranks_train)
    metrics = _eval_predictor(base, X_test, Y_ranks_test)
    print(f"  marginal_baseline  spearman={metrics['spearman_mean']:+.3f}  "
          f"ndcg@5={metrics['ndcg@5_mean']:.3f}  "
          f"top1_acc={metrics['top1_top1_acc']:.3f}  "
          f"MARE={metrics['mean_abs_rank_error']:.2f}")
    results["marginal_baseline"] = metrics

    # 1-3. Ridge / RF / GB
    zoo = make_default_zoo()
    try:
        zoo.append(make_lightgbm_predictor())
    except ImportError:
        pass

    fitted = {}
    for predictor in zoo:
        predictor.fit(X_train, Y_scores_train)
        m = _eval_predictor(predictor, X_test, Y_ranks_test)
        results[predictor.name] = m
        fitted[predictor.name] = predictor
        print(f"  {predictor.name:18s} spearman={m['spearman_mean']:+.3f}  "
              f"ndcg@5={m['ndcg@5_mean']:.3f}  "
              f"top1_acc={m['top1_top1_acc']:.3f}  "
              f"MARE={m['mean_abs_rank_error']:.2f}")

    # save fitted models
    for name, predictor in fitted.items():
        joblib.dump(predictor, MODELS / f"{name}_synth_to_real.joblib")
    joblib.dump(base, MODELS / "marginal_baseline.joblib")
    return results


def secondary_evaluation(real: pd.DataFrame, n_splits: int = 5,
                         random_state: int = 42) -> dict:
    """K-fold CV on real-only."""
    X, Y_ranks, Y_scores = split_X_y_ranks(real)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    print(f"\n[SECONDARY] {n_splits}-fold CV on real (n={len(real)})")

    # Aggregator: for each model, collect predictions over all folds, then
    # compute global metrics on the assembled predictions.
    model_names = ["marginal_baseline", "ridge", "random_forest",
                   "gradient_boosting", "lightgbm"]

    fold_preds = {n: np.zeros_like(Y_ranks) for n in model_names}

    for fold_i, (tr, te) in enumerate(kf.split(X)):
        X_tr, X_te = X.iloc[tr], X.iloc[te]
        Y_ranks_tr = Y_ranks[tr]
        Y_scores_tr = Y_scores[tr]

        # marginal baseline
        base = MarginalBaseline().fit(Y_ranks_tr)
        fold_preds["marginal_baseline"][te] = base.predict_ranks(X_te)

        # zoo
        zoo = make_default_zoo()
        try:
            zoo.append(make_lightgbm_predictor())
        except ImportError:
            pass
        for p in zoo:
            p.fit(X_tr, Y_scores_tr)
            fold_preds[p.name][te] = p.predict_ranks(X_te)

    results = {}
    for name in model_names:
        if name not in fold_preds:
            continue
        m = evaluate_all(Y_ranks, fold_preds[name], ROLE_NAMES)
        results[name] = m
        print(f"  {name:18s} spearman={m['spearman_mean']:+.3f}  "
              f"ndcg@5={m['ndcg@5_mean']:.3f}  "
              f"top1_acc={m['top1_top1_acc']:.3f}  "
              f"MARE={m['mean_abs_rank_error']:.2f}")
    return results


def _plot_metric_comparison(primary: dict, secondary: dict) -> None:
    metrics = [
        ("spearman_mean", "Spearman ρ (mean per row)"),
        ("ndcg@5_mean", "NDCG@5"),
        ("top1_top1_acc", "Top-1 accuracy"),
        ("top5_overlap_in_top5", "Top-5 set overlap"),
        ("mean_abs_rank_error", "Mean |Δrank| (lower = better)"),
    ]
    model_order = ["marginal_baseline", "ridge", "random_forest",
                   "gradient_boosting", "lightgbm"]
    model_labels = {
        "marginal_baseline": "marginal\n(baseline)",
        "ridge": "Ridge",
        "random_forest": "Random\nForest",
        "gradient_boosting": "Gradient\nBoosting",
        "lightgbm": "LightGBM",
    }
    rows = []
    for regime_name, regime_data in [("synth->real", primary), ("CV on real", secondary)]:
        for name in model_order:
            if name not in regime_data:
                continue
            for mkey, mlabel in metrics:
                rows.append({
                    "regime": regime_name,
                    "model": model_labels[name],
                    "metric": mlabel,
                    "value": regime_data[name][mkey],
                })
    df = pd.DataFrame(rows)

    fig, axes = plt.subplots(1, len(metrics), figsize=(4.2 * len(metrics), 4.5),
                             sharey=False)
    palette = {"synth->real": "#3a7ca5", "CV on real": "#d6a85a"}
    for ax, (mkey, mlabel) in zip(axes, metrics):
        sub = df[df["metric"] == mlabel]
        sns.barplot(data=sub, x="model", y="value", hue="regime",
                    palette=palette, ax=ax)
        ax.set_title(mlabel, fontsize=10)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.legend(fontsize=8)
        ax.tick_params(axis="x", labelsize=8)
    fig.suptitle("Role-prediction metrics across models and evaluation regimes",
                 fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES / "05a_metric_comparison.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def _plot_per_role_mae(primary: dict) -> str:
    """Bar chart of per-role MAE for the best model in primary regime."""
    # pick best by spearman
    best_name = max(
        (n for n in primary if n != "marginal_baseline"),
        key=lambda n: primary[n]["spearman_mean"],
    )
    per_role = primary[best_name]["per_role_mae"]
    base_per_role = primary["marginal_baseline"]["per_role_mae"]

    df = pd.DataFrame({
        "role": list(per_role.keys()),
        f"{best_name}": list(per_role.values()),
        "marginal baseline": [base_per_role[r] for r in per_role.keys()],
    })
    df = df.sort_values(best_name)

    fig, ax = plt.subplots(figsize=(11, 5))
    melted = df.melt(id_vars="role", var_name="model", value_name="mae")
    sns.barplot(data=melted, x="role", y="mae", hue="model",
                palette={best_name: "#3a7ca5", "marginal baseline": "#d6a85a"},
                ax=ax)
    ax.set_title(f"Per-role MAE on real holdout (best: {best_name})")
    ax.set_xlabel("")
    ax.set_ylabel("MAE (rank units)")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURES / "05b_per_role_mae.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return best_name


def _plot_predicted_vs_true(real: pd.DataFrame, best_name: str) -> None:
    """Scatter: predicted rank vs true rank, all (subject, role) pairs."""
    predictor = joblib.load(MODELS / f"{best_name}_synth_to_real.joblib")
    X, Y_ranks, _ = split_X_y_ranks(real)
    pred = predictor.predict_ranks(X)

    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.scatter(Y_ranks.flatten(), pred.flatten(),
               alpha=0.35, s=18, c="#3a7ca5", edgecolor="white", linewidths=0.4)
    lim = (0.5, 20.5)
    ax.plot(lim, lim, color="grey", lw=1, ls="--", label="perfect")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("true rank"); ax.set_ylabel("predicted rank")
    ax.set_title(f"Predicted vs true ranks on real holdout - {best_name}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "05c_predicted_vs_true.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    real = load_pilot()
    synth = pd.read_csv(SYNTH_PATH, encoding="utf-8")
    print(f"real:  {real.shape}")
    print(f"synth: {synth.shape}")

    primary = primary_evaluation(synth, real)
    secondary = secondary_evaluation(real)

    summary = {"primary_synth_to_real": primary, "secondary_cv_on_real": secondary}
    out_json = REPORTS / "role_prediction_metrics.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nwrote: {out_json}")

    _plot_metric_comparison(primary, secondary)
    best = _plot_per_role_mae(primary)
    _plot_predicted_vs_true(real, best)
    print(f"saved figures (best model: {best})")


if __name__ == "__main__":
    main()
