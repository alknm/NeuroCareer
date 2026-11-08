"""Ranking metrics for evaluating role-prediction models.

All metrics treat each row independently as a permutation of 1..K and then
average across rows. Conventions:

  * rank 1 = best fit, rank K = worst fit (per Neiry's role rankings).
  * "score" = continuous preference (higher = better fit), so the
    relationship is rank = K + 1 - argsort(score).
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr


def scores_to_ranks(scores: np.ndarray) -> np.ndarray:
    """Per-row ranking. Highest score -> rank 1."""
    return (-scores).argsort(axis=1).argsort(axis=1) + 1


def ranks_to_scores(ranks: np.ndarray, n: int | None = None) -> np.ndarray:
    """Cheap inverse: turn rank-1..K into a monotone score (K+1-rank)."""
    if n is None:
        n = ranks.shape[1]
    return (n + 1 - ranks).astype(float)


def spearman_per_row(true_ranks: np.ndarray, pred_ranks: np.ndarray) -> np.ndarray:
    """Spearman rho computed per row. Returns array of length n_rows."""
    out = np.empty(true_ranks.shape[0])
    for i in range(true_ranks.shape[0]):
        rho, _ = spearmanr(true_ranks[i], pred_ranks[i])
        out[i] = rho if not np.isnan(rho) else 0.0
    return out


def ndcg_at_k(true_ranks: np.ndarray, pred_ranks: np.ndarray, k: int = 5) -> np.ndarray:
    """Normalized discounted cumulative gain at k.

    Relevance per item = (n + 1 - true_rank), so the strongest true role
    has the highest relevance. We sort items by predicted rank ascending
    (best predicted first) and take top-k.
    """
    n_rows, n_items = true_ranks.shape
    rels = (n_items + 1) - true_ranks  # relevance >= 1
    out = np.empty(n_rows)
    discounts = 1.0 / np.log2(np.arange(2, k + 2))  # log2(2), log2(3), ...
    for i in range(n_rows):
        order = np.argsort(pred_ranks[i])  # ascending: best predicted first
        top_k_relevances = rels[i, order[:k]]
        dcg = float(np.sum(top_k_relevances * discounts))
        ideal = np.sort(rels[i])[::-1][:k]
        idcg = float(np.sum(ideal * discounts))
        out[i] = dcg / idcg if idcg > 0 else 0.0
    return out


def top_k_accuracy(true_ranks: np.ndarray, pred_ranks: np.ndarray, k: int = 1,
                   from_true: int = 1) -> np.ndarray:
    """Fraction of rows where true top-`from_true` role is in predicted top-k.

    Default (k=1, from_true=1): exact top-1 match.
    """
    n_rows = true_ranks.shape[0]
    out = np.zeros(n_rows)
    for i in range(n_rows):
        true_top = set(np.where(true_ranks[i] <= from_true)[0])
        pred_top_k = set(np.argsort(pred_ranks[i])[:k])
        out[i] = 1.0 if true_top & pred_top_k else 0.0
    return out


def mean_absolute_rank_error(true_ranks: np.ndarray, pred_ranks: np.ndarray) -> np.ndarray:
    """Mean over the K roles of |true_rank - predicted_rank|, per row."""
    return np.abs(true_ranks - pred_ranks).mean(axis=1)


def per_role_mae(true_ranks: np.ndarray, pred_ranks: np.ndarray,
                 role_names: list[str]) -> dict[str, float]:
    """Per-role mean absolute rank error."""
    abs_err = np.abs(true_ranks - pred_ranks)
    return {role_names[j]: float(abs_err[:, j].mean()) for j in range(len(role_names))}


def evaluate_all(true_ranks: np.ndarray, pred_ranks: np.ndarray,
                 role_names: list[str]) -> dict:
    """Compute the standard metric panel and return as a dict."""
    spearman = spearman_per_row(true_ranks, pred_ranks)
    ndcg5 = ndcg_at_k(true_ranks, pred_ranks, k=5)
    ndcg3 = ndcg_at_k(true_ranks, pred_ranks, k=3)
    top1 = top_k_accuracy(true_ranks, pred_ranks, k=1, from_true=1)
    top3 = top_k_accuracy(true_ranks, pred_ranks, k=3, from_true=1)
    top5_in_5 = np.array([
        len(set(np.argsort(true_ranks[i])[:5]) & set(np.argsort(pred_ranks[i])[:5])) / 5.0
        for i in range(true_ranks.shape[0])
    ])
    mare = mean_absolute_rank_error(true_ranks, pred_ranks)
    return {
        "spearman_mean": float(spearman.mean()),
        "spearman_std": float(spearman.std()),
        "ndcg@5_mean": float(ndcg5.mean()),
        "ndcg@3_mean": float(ndcg3.mean()),
        "top1_top1_acc": float(top1.mean()),
        "top1_top3_acc": float(top3.mean()),
        "top5_overlap_in_top5": float(top5_in_5.mean()),
        "mean_abs_rank_error": float(mare.mean()),
        "per_role_mae": per_role_mae(true_ranks, pred_ranks, role_names),
        "n_rows": int(true_ranks.shape[0]),
    }


__all__ = [
    "scores_to_ranks", "ranks_to_scores", "spearman_per_row",
    "ndcg_at_k", "top_k_accuracy", "mean_absolute_rank_error",
    "per_role_mae", "evaluate_all",
]
