"""Synthetic data generator for the hybrid career-guidance system.

Strategy
--------
The pilot dataset has only n=47 - too small for the supervised layer of the
system. We synthesize an extended dataset (n_default=500) that statistically
mirrors the pilot:

  * Continuous backbone (Gardner + independent MBTI scales + Neiry metrics)
    is sampled via a Gaussian copula fit to the real data. This preserves
    marginal distributions AND the full pairwise correlation structure.

  * Role rankings are not fed as raw 1..20 integers (that would destroy the
    permutation constraint). Instead each respondent's rank vector is
    converted to a continuous preference score per role; these scores are
    included in the copula. After sampling, the 20 generated scores per row
    are re-ranked back to 1..20, restoring the permutation invariant while
    preserving cross-role correlations.

  * Complementary MBTI scales (e.g. MBTIИнтроверт = 100 - MBTIЭкстраверт)
    are reconstructed exactly to preserve the sum-to-100 invariant.

  * The categorical MBTI type is derived deterministically from the sampled
    continuous scales using the standard 50% threshold per dichotomy.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from .data_loader import (
    GARDNER_FEATURES, ID_COL, MBTI_INDEPENDENT_SCALES, MBTI_TYPE_COL,
    NEIRY_FEATURES, ROLE_FEATURES,
)

# Maps independent MBTI scale -> its complement column name.
_MBTI_COMPLEMENT = {
    "MBTIЭкстраверт": "MBTIИнтроверт",
    "MBTIИнтуитивные": "MBTIРеалистичные",
    "MBTIЛогика": "MBTIПринципы",
    "MBTIПланирующие": "MBTIИщущие",
    "MBTIУверенные": "MBTIОсторожные",
}

# Maps independent MBTI scale -> letter pair (high-side, low-side, suffix?)
# Convention: when scale value >= 50, take the "high" letter, otherwise "low".
_MBTI_LETTER_RULES = [
    ("MBTIЭкстраверт", "E", "I"),     # E vs I
    ("MBTIИнтуитивные", "N", "S"),    # N vs S
    ("MBTIЛогика", "T", "F"),         # T vs F (Russian "Логика" = thinking)
    ("MBTIПланирующие", "J", "P"),    # J vs P
    ("MBTIУверенные", "A", "T"),      # A vs T (assertive vs turbulent suffix)
]


def _ranks_to_scores(rank_df: pd.DataFrame) -> pd.DataFrame:
    """Convert per-row rank-permutations (1..N) into continuous preference scores.

    Uses the inverse-normal (probit) transform of the cumulative rank, which
    spreads ranks symmetrically around zero and gives a Gaussian-friendly
    representation suitable for copula fitting.
    """
    n = rank_df.shape[1]
    # rank-percentile in (0, 1) using midpoint:  (rank - 0.5) / N
    pct = (rank_df.values - 0.5) / n
    # invert to get scores; high rank (good fit) -> high score
    scores = norm.ppf(1.0 - pct)
    return pd.DataFrame(scores, columns=rank_df.columns, index=rank_df.index)


def _scores_to_ranks(score_df: pd.DataFrame) -> pd.DataFrame:
    """Per-row ranking that restores valid 1..N permutations.

    The role with the highest score gets rank 1 (best fit), down to N (worst).
    """
    # rank descending so that the strongest score => rank 1
    ranks = (-score_df.values).argsort(axis=1).argsort(axis=1) + 1
    return pd.DataFrame(ranks, columns=score_df.columns, index=score_df.index)


def _derive_mbti_type(scales: pd.DataFrame) -> pd.Series:
    """Derive 4-letter MBTI type with -A/-T suffix from the 5 independent scales."""
    out = []
    for _, row in scales.iterrows():
        letters = ""
        for col, hi, lo in _MBTI_LETTER_RULES[:4]:
            letters += hi if row[col] >= 50 else lo
        suffix = "-A" if row["MBTIУверенные"] >= 50 else "-T"
        out.append(letters + suffix)
    return pd.Series(out, index=scales.index, name=MBTI_TYPE_COL)


@dataclass
class SyntheticConfig:
    n_samples: int = 500
    random_state: int = 42
    name_prefix: str = "Synthetic-"
    use_sdv: bool = True            # if False, fall back to a pure-numpy Gaussian copula


class SyntheticGenerator:
    """Trains on the pilot dataframe and produces synthetic samples."""

    def __init__(self, config: SyntheticConfig | None = None):
        self.config = config or SyntheticConfig()
        self._sdv_synth = None
        self._copula_params: dict | None = None
        self._continuous_features: list[str] = []
        self._role_score_features: list[str] = []

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------
    def fit(self, df: pd.DataFrame) -> "SyntheticGenerator":
        # 1. Build the wide continuous frame
        wide = self._build_continuous_frame(df)
        self._continuous_features = list(wide.columns)

        if self.config.use_sdv:
            self._fit_sdv(wide)
        else:
            self._fit_numpy_copula(wide)
        return self

    def _build_continuous_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        gardner = df[list(GARDNER_FEATURES)]
        mbti_indep = df[list(MBTI_INDEPENDENT_SCALES)]
        neiry = df[list(NEIRY_FEATURES)]
        role_scores = _ranks_to_scores(df[list(ROLE_FEATURES)])
        # disambiguate role-score columns
        role_scores.columns = [f"_score_{c}" for c in role_scores.columns]
        self._role_score_features = list(role_scores.columns)
        wide = pd.concat([gardner, mbti_indep, neiry, role_scores], axis=1)
        return wide

    def _fit_sdv(self, wide: pd.DataFrame) -> None:
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer

        meta = SingleTableMetadata()
        meta.detect_from_dataframe(wide)
        for col in wide.columns:
            meta.update_column(column_name=col, sdtype="numerical")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            synth = GaussianCopulaSynthesizer(meta, default_distribution="gaussian_kde")
            synth.fit(wide)
        self._sdv_synth = synth

    def _fit_numpy_copula(self, wide: pd.DataFrame) -> None:
        # Empirical CDF -> normal scores via probit, then estimate correlation.
        ranks = wide.rank(method="average") / (len(wide) + 1)
        z = norm.ppf(ranks.values)
        rho = np.corrcoef(z, rowvar=False)
        # Regularize for numerical stability
        rho = (rho + np.eye(rho.shape[0]) * 1e-3) / (1 + 1e-3)
        self._copula_params = {
            "rho": rho,
            "marginals": {col: wide[col].values for col in wide.columns},
        }

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------
    def sample(self, n: int | None = None) -> pd.DataFrame:
        n = n or self.config.n_samples
        rng = np.random.default_rng(self.config.random_state)

        if self._sdv_synth is not None:
            wide = self._sdv_synth.sample(num_rows=n)
        else:
            wide = self._sample_numpy_copula(n, rng)

        return self._post_process(wide, rng)

    def _sample_numpy_copula(self, n: int, rng: np.random.Generator) -> pd.DataFrame:
        params = self._copula_params
        L = np.linalg.cholesky(params["rho"])
        z = rng.standard_normal(size=(n, params["rho"].shape[0])) @ L.T
        u = norm.cdf(z)  # to uniforms
        # invert through empirical marginals via quantile
        cols = list(self._continuous_features)
        out = np.empty_like(z)
        for j, col in enumerate(cols):
            sample_vals = np.quantile(params["marginals"][col], u[:, j])
            out[:, j] = sample_vals
        return pd.DataFrame(out, columns=cols)

    def _post_process(self, wide: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
        # 1. Clip Gardner and MBTI scales to their natural ranges
        for col in GARDNER_FEATURES:
            wide[col] = wide[col].clip(0, 100)
        for col in MBTI_INDEPENDENT_SCALES:
            wide[col] = wide[col].clip(0, 100)

        # 2. Reconstruct complementary MBTI scales (sum-to-100 invariant)
        for indep, comp in _MBTI_COMPLEMENT.items():
            wide[comp] = (100.0 - wide[indep]).round(2)
            wide[indep] = wide[indep].round(2)

        # 3. Convert role scores -> ranks (1..20 permutations)
        role_score_df = wide[self._role_score_features]
        role_score_df.columns = list(ROLE_FEATURES)
        role_ranks = _scores_to_ranks(role_score_df)
        wide[list(ROLE_FEATURES)] = role_ranks
        wide = wide.drop(columns=self._role_score_features)

        # 4. Derive MBTI type
        mbti_type = _derive_mbti_type(wide[list(MBTI_INDEPENDENT_SCALES)])
        wide[MBTI_TYPE_COL] = mbti_type

        # 5. Add fake IDs
        n = len(wide)
        wide.insert(0, ID_COL, [f"{self.config.name_prefix}{i+1:04d}" for i in range(n)])

        # 6. Order columns to match pilot
        from .data_loader import (
            GARDNER_FEATURES as G, MBTI_SCALE_FEATURES as M,
            NEIRY_FEATURES as N, ROLE_FEATURES as R,
        )
        ordered = ([ID_COL] + list(G) + [MBTI_TYPE_COL] + list(M)
                   + list(R) + list(N))
        return wide[ordered].reset_index(drop=True)


def generate_synthetic(df_real: pd.DataFrame, n: int = 500,
                       random_state: int = 42, use_sdv: bool = True) -> pd.DataFrame:
    cfg = SyntheticConfig(n_samples=n, random_state=random_state, use_sdv=use_sdv)
    gen = SyntheticGenerator(cfg).fit(df_real)
    return gen.sample(n)


__all__ = ["SyntheticConfig", "SyntheticGenerator", "generate_synthetic"]
