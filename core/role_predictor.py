"""Role prediction models for the supervised layer of the hybrid system.

The system predicts a per-respondent ranking over 20 Neiry archetypal roles
from psychometric (Gardner + MBTI) and EEG features.

Pipeline (per row):
  features ->  scaler ->  multi-output regressor ->  20 continuous role scores
                                                  -> per-row argsort -> 1..20 ranks

Training target: continuous "preference scores" derived from ground-truth
ranks via the inverse-normal transform (matches the synthetic generator).
This makes the regression target Gaussian-friendly without changing the
final integer ranking.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data_loader import (
    GARDNER_FEATURES, MBTI_INDEPENDENT_SCALES, NEIRY_FEATURES, ROLE_FEATURES,
)
from .ranking_metrics import scores_to_ranks


# Feature columns the model receives, in a stable order.
INPUT_FEATURES: list[str] = (
    list(GARDNER_FEATURES) + list(MBTI_INDEPENDENT_SCALES) + list(NEIRY_FEATURES)
)


def ranks_to_preference_scores(ranks: np.ndarray) -> np.ndarray:
    """Probit-transform per-row ranks (1..K) into continuous preference scores.

    Best fit (rank 1) -> high positive score, worst fit (rank K) -> negative.
    """
    n = ranks.shape[1]
    pct = (ranks - 0.5) / n            # in (0, 1)
    return norm.ppf(1.0 - pct)         # invert so rank 1 -> high


def preference_scores_to_ranks(scores: np.ndarray) -> np.ndarray:
    """Inverse: per-row argsort restores valid 1..K permutations."""
    return scores_to_ranks(scores)


def split_X_y_ranks(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Return (features X, integer ranks Y_ranks, continuous preference scores Y_scores)."""
    X = df[INPUT_FEATURES].copy()
    Y_ranks = df[list(ROLE_FEATURES)].values.astype(int)
    Y_scores = ranks_to_preference_scores(Y_ranks)
    return X, Y_ranks, Y_scores


@dataclass
class RolePredictor:
    """Fit a multi-output regressor on preference scores; predict integer ranks."""
    name: str
    estimator: BaseEstimator
    scale_features: bool = True

    def __post_init__(self) -> None:
        steps = []
        if self.scale_features:
            steps.append(("scaler", StandardScaler()))
        steps.append(("regressor", self.estimator))
        self._pipe: Pipeline = Pipeline(steps)
        self._fitted = False

    def fit(self, X: pd.DataFrame, Y_scores: np.ndarray) -> "RolePredictor":
        self._pipe.fit(X, Y_scores)
        self._fitted = True
        return self

    def predict_scores(self, X: pd.DataFrame) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("RolePredictor not fitted")
        return np.asarray(self._pipe.predict(X))

    def predict_ranks(self, X: pd.DataFrame) -> np.ndarray:
        return preference_scores_to_ranks(self.predict_scores(X))

    @property
    def pipeline(self) -> Pipeline:
        return self._pipe


def make_default_zoo(random_state: int = 42) -> list[RolePredictor]:
    """The standard model line-up reported in the dissertation."""
    return [
        RolePredictor(
            name="ridge",
            estimator=Ridge(alpha=1.0, random_state=random_state),
        ),
        RolePredictor(
            name="random_forest",
            estimator=RandomForestRegressor(
                n_estimators=300, max_depth=None, min_samples_leaf=2,
                n_jobs=-1, random_state=random_state,
            ),
        ),
        RolePredictor(
            name="gradient_boosting",
            estimator=MultiOutputRegressor(
                GradientBoostingRegressor(
                    n_estimators=200, max_depth=3, learning_rate=0.05,
                    subsample=0.85, random_state=random_state,
                ),
                n_jobs=-1,
            ),
            scale_features=False,  # tree-based, scaling not required
        ),
    ]


def make_lightgbm_predictor(random_state: int = 42) -> RolePredictor:
    """Optional LightGBM addition (one regressor per role)."""
    from lightgbm import LGBMRegressor
    return RolePredictor(
        name="lightgbm",
        estimator=MultiOutputRegressor(
            LGBMRegressor(
                n_estimators=400, learning_rate=0.05, num_leaves=31,
                min_child_samples=5, subsample=0.85, colsample_bytree=0.85,
                random_state=random_state, verbose=-1, n_jobs=1,
            ),
            n_jobs=-1,
        ),
        scale_features=False,
    )


def baseline_marginal_predictor(Y_ranks_train: np.ndarray) -> "MarginalBaseline":
    """Trivial baseline: always predict the average rank per role."""
    return MarginalBaseline().fit(Y_ranks_train)


class MarginalBaseline(BaseEstimator, RegressorMixin):
    """Predicts the same per-role rank for every input.

    Useful as a sanity floor: any real model must beat this.
    """
    def fit(self, Y_ranks_train: np.ndarray) -> "MarginalBaseline":
        self.mean_ranks_ = np.asarray(Y_ranks_train).mean(axis=0)
        # Convert to ranks of the means (so output is itself a permutation)
        self.tied_rank_ = (self.mean_ranks_.argsort().argsort() + 1).astype(int)
        return self

    def predict_ranks(self, X: pd.DataFrame) -> np.ndarray:
        n = len(X)
        return np.tile(self.tied_rank_, (n, 1))


__all__ = [
    "INPUT_FEATURES", "RolePredictor", "MarginalBaseline",
    "make_default_zoo", "make_lightgbm_predictor", "baseline_marginal_predictor",
    "ranks_to_preference_scores", "preference_scores_to_ranks",
    "split_X_y_ranks",
]
