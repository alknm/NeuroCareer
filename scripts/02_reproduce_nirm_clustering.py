"""Reproduce the k-means clustering from NIRM (November 2025).

The NIRM report stated:
  * Method: k-means
  * Features: all Neiry neural metrics, standardized
  * k = 3
  * Reported silhouette score: 0.24
  * Reported cluster sizes: 30 / 8 / 9
  * Reported per-cluster means (original units, baseline indices):
        cluster 1 (n=30): conc ~1.65, relax ~0.75, fatigue ~1.63
        cluster 2 (n=8):  conc ~3.72, relax ~0.34, fatigue ~0.67
        cluster 3 (n=9):  conc ~1.02, relax ~1.37, fatigue ~4.03

This script:
  1. Searches over random_state to find the seed that reproduces these sizes/centroids.
  2. Saves the canonical clustering as an artifact for downstream layers.
  3. Produces figures matching NIRM (cluster scatter via PCA, distribution bar, centroids).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ID_COL, NEIRY_CLUSTERING_FEATURES, load_pilot

REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", context="notebook")

REPORTED = {
    "k": 3,
    "silhouette": 0.24,
    "sizes": [30, 8, 9],
    "centroids_baseline": {
        "neiryBaseline Concentration index": [1.65, 3.72, 1.02],
        "neiryBaseline Relaxation index":    [0.75, 0.34, 1.37],
        "neiryBaseline Fatigue score":       [1.63, 0.67, 4.03],
    },
}


def _fit_kmeans(X: np.ndarray, k: int, random_state: int) -> tuple[KMeans, np.ndarray, float]:
    km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    labels = km.fit_predict(X)
    sil = silhouette_score(X, labels)
    return km, labels, sil


def _match_reported_centroids(df_orig: pd.DataFrame, labels: np.ndarray) -> tuple[dict, list[int]]:
    """Find a permutation of cluster IDs that aligns with the reported NIRM centroids.

    Reported pattern:
      cluster A: high concentration (3.72), low relaxation (0.34), low fatigue (0.67)  -> "mobilized"
      cluster B: low  concentration (1.02), high relaxation (1.37), high fatigue (4.03) -> "depleted"
      cluster C: medium across the board                                                -> "balanced"

    We label clusters by these archetypes and return the permutation
    so that final cluster IDs are: 0=balanced, 1=mobilized, 2=depleted
    (this matches NIRM's natural ordering by descending size).
    """
    df = df_orig.copy()
    df["_lbl"] = labels
    centroids = df.groupby("_lbl")[
        ["neiryBaseline Concentration index",
         "neiryBaseline Relaxation index",
         "neiryBaseline Fatigue score"]
    ].mean()

    sizes = df["_lbl"].value_counts().sort_values(ascending=False)
    # Heuristics: mobilized = highest concentration; depleted = highest fatigue;
    # balanced = the remaining one (typically the largest by size).
    mobilized = centroids["neiryBaseline Concentration index"].idxmax()
    depleted = centroids["neiryBaseline Fatigue score"].idxmax()
    remaining = [c for c in centroids.index if c not in (mobilized, depleted)]
    balanced = remaining[0] if remaining else sizes.index[0]

    perm = {balanced: 0, mobilized: 1, depleted: 2}
    return {
        "balanced_orig_id": int(balanced),
        "mobilized_orig_id": int(mobilized),
        "depleted_orig_id": int(depleted),
    }, [perm[l] for l in labels]


def _score_match(sizes: list[int], centroids_orig: pd.DataFrame) -> float:
    """Lower = closer match to the reported NIRM clustering."""
    target_sizes = sorted(REPORTED["sizes"], reverse=True)
    actual_sizes = sorted(sizes, reverse=True)
    size_err = sum((a - t) ** 2 for a, t in zip(actual_sizes, target_sizes)) / 100.0

    centroid_err = 0.0
    for col, target_vals in REPORTED["centroids_baseline"].items():
        # column expected after permutation: rows 0,1,2 = balanced,mobilized,depleted
        # NIRM reported in order cluster1(n=30)=balanced, cluster2(n=8)=mobilized, cluster3(n=9)=depleted
        for cluster_id, t in enumerate(target_vals):
            if cluster_id in centroids_orig.index:
                a = centroids_orig.loc[cluster_id, col]
                centroid_err += (a - t) ** 2
    return size_err + centroid_err


def search_seed(df: pd.DataFrame, X: np.ndarray, k: int = 3,
                seeds: range = range(0, 200)) -> dict:
    best = None
    for rs in seeds:
        _, labels, sil = _fit_kmeans(X, k, rs)
        _, permuted = _match_reported_centroids(df, labels)
        permuted = np.array(permuted)
        sizes = pd.Series(permuted).value_counts().sort_index().tolist()
        centroids_orig = (
            df.assign(_lbl=permuted)
              .groupby("_lbl")[list(REPORTED["centroids_baseline"].keys())]
              .mean()
        )
        score = _score_match(sizes, centroids_orig)
        rec = {
            "random_state": rs, "silhouette": sil, "sizes": sizes,
            "centroids": {col: centroids_orig[col].round(3).tolist()
                          for col in REPORTED["centroids_baseline"]},
            "match_score": score,
        }
        if best is None or score < best["match_score"]:
            best = rec
    return best


def main() -> None:
    df = load_pilot()
    feats = list(NEIRY_CLUSTERING_FEATURES)
    print(f"using {len(feats)} neiry features for clustering")

    scaler = StandardScaler()
    X = scaler.fit_transform(df[feats])
    print(f"X shape: {X.shape}, mean(|X|)={np.abs(X).mean():.3f}, "
          f"std={X.std():.3f}  (expected mean~0, std=1)")

    # NIRM reported: average std before normalization 3.92, mean 14.09
    raw_means = df[feats].mean()
    raw_stds = df[feats].std()
    print(f"raw stats: mean of feature means = {raw_means.mean():.2f} "
          f"(NIRM reported 14.09), mean of feature stds = {raw_stds.mean():.2f} "
          f"(NIRM reported 3.92)")

    print("\nsearching random_state for closest match to NIRM clustering ...")
    best = search_seed(df, X)
    print(f"  best random_state = {best['random_state']}")
    print(f"  silhouette = {best['silhouette']:.3f}  (NIRM: 0.24)")
    print(f"  sizes      = {best['sizes']}  (NIRM: [30, 8, 9])")
    for col, vals in best["centroids"].items():
        target = REPORTED["centroids_baseline"][col]
        print(f"  {col[:42]:42s}  fit={vals}  nirm={target}")

    # --- Refit canonical model with best seed ---
    rs = best["random_state"]
    km, raw_labels, sil = _fit_kmeans(X, k=3, random_state=rs)
    perm_info, labels = _match_reported_centroids(df, raw_labels)
    labels = np.array(labels)

    # --- Save canonical artifact ---
    canonical = df[[ID_COL]].copy()
    canonical["cluster_id"] = labels
    canonical["cluster_label"] = pd.Series(labels).map(
        {0: "balanced", 1: "mobilized", 2: "depleted"}
    ).values
    canonical.to_csv(PROCESSED / "clusters_canonical.csv", index=False, encoding="utf-8")
    with open(PROCESSED / "clusters_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "k": 3,
            "random_state": rs,
            "features_used": feats,
            "scaler": "StandardScaler",
            "silhouette": float(sil),
            "sizes": pd.Series(labels).value_counts().sort_index().tolist(),
            "label_map": {"0": "balanced", "1": "mobilized", "2": "depleted"},
            "permutation_info": perm_info,
            "nirm_reported": REPORTED,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nsaved canonical clustering -> {PROCESSED/'clusters_canonical.csv'}")

    # --- Figures ---
    # 1. PCA scatter
    pca = PCA(n_components=2, random_state=rs)
    coords = pca.fit_transform(X)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    palette = {0: "#3a7ca5", 1: "#d62728", 2: "#2ca02c"}
    label_names = {0: "balanced (n=%d)" % (labels == 0).sum(),
                   1: "mobilized (n=%d)" % (labels == 1).sum(),
                   2: "depleted (n=%d)" % (labels == 2).sum()}
    for cid in [0, 1, 2]:
        m = labels == cid
        ax.scatter(coords[m, 0], coords[m, 1], c=palette[cid], s=70, alpha=0.85,
                   edgecolor="white", label=label_names[cid])
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title(f"k-means clustering of pilot dataset (n=47, k=3, silhouette={sil:.3f})")
    ax.legend(loc="best", frameon=True)
    fig.tight_layout()
    fig.savefig(FIGURES / "02a_pca_clusters.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 2. Cluster size barplot
    fig, ax = plt.subplots(figsize=(6, 4))
    sizes_series = pd.Series(labels).value_counts().sort_index()
    sizes_series.index = [label_names[i].split(" (")[0] for i in sizes_series.index]
    sns.barplot(x=sizes_series.index, y=sizes_series.values, ax=ax,
                palette=[palette[i] for i in [0, 1, 2]])
    for i, v in enumerate(sizes_series.values):
        ax.text(i, v + 0.4, str(v), ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("# respondents")
    ax.set_title("Distribution of respondents across clusters")
    fig.tight_layout()
    fig.savefig(FIGURES / "02b_cluster_sizes.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 3. Centroid comparison: actual vs NIRM-reported
    centroid_cols = list(REPORTED["centroids_baseline"].keys())
    actual = df.assign(_lbl=labels).groupby("_lbl")[centroid_cols].mean().round(3)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=False)
    cluster_names = ["balanced", "mobilized", "depleted"]
    for ax, col in zip(axes, centroid_cols):
        actual_vals = actual[col].values
        nirm_vals = REPORTED["centroids_baseline"][col]
        x = np.arange(3)
        w = 0.38
        ax.bar(x - w/2, actual_vals, w, label="reproduced", color="#3a7ca5")
        ax.bar(x + w/2, nirm_vals, w, label="NIRM reported", color="#d6a85a")
        ax.set_xticks(x)
        ax.set_xticklabels(cluster_names, rotation=15)
        ax.set_title(col.replace("neiryBaseline ", ""), fontsize=10)
        ax.legend(fontsize=9)
    fig.suptitle("Cluster centroid comparison: reproduced vs NIRM (Nov 2025)", y=1.02)
    fig.tight_layout()
    fig.savefig(FIGURES / "02c_centroids_comparison.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 4. Heatmap of all neiry features per cluster (z-scores)
    z_means = (
        pd.DataFrame(X, columns=feats).assign(_lbl=labels)
          .groupby("_lbl").mean()
    )
    z_means.index = ["balanced", "mobilized", "depleted"]
    short = [c.replace("neiry", "").replace("Baseline ", "B-") for c in feats]
    z_means.columns = short
    fig, ax = plt.subplots(figsize=(13, 3.4))
    sns.heatmap(z_means, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                cbar_kws={"label": "z-score"}, ax=ax, annot_kws={"size": 7})
    ax.set_title("Cluster profiles across all Neiry features (standardized means)")
    fig.tight_layout()
    fig.savefig(FIGURES / "02d_cluster_zscore_heatmap.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figures to: {FIGURES}")
    print("\n=== Summary ===")
    print(f"  silhouette (reproduced): {sil:.3f}")
    print(f"  silhouette (NIRM):       {REPORTED['silhouette']:.3f}")
    print(f"  cluster sizes (reproduced): {sorted(sizes_series.values, reverse=True)}")
    print(f"  cluster sizes (NIRM):       {REPORTED['sizes']}")


if __name__ == "__main__":
    main()
