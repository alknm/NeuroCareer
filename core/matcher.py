"""Hybrid career matcher - Layer 4 of the system.

Combines three sources of evidence into a single per-profession score:
  * trait fit  - Gardner intelligences + MBTI dimensions vs. profession ideal
  * cluster fit - alignment between user's cognitive cluster and profession's
                  preferred cluster (any/balanced/mobilized/depleted)
  * role fit   - overlap between Layer 3's predicted top-roles and the
                  profession's required roles

Default weighting (sum to 1.0):
  gardner: 0.30
  mbti:    0.20
  cluster: 0.10
  roles:   0.40

Each component is bounded in [0, 100], so the total is also in [0, 100].
The breakdown is preserved in the output to power the LLM explainer
(Layer 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from .data_loader import (
    GARDNER_FEATURES, MBTI_INDEPENDENT_SCALES, NEIRY_CLUSTERING_FEATURES,
    ROLE_FEATURES,
)
from .professions import Profession, load_professions
from .role_predictor import INPUT_FEATURES, RolePredictor

# Map signed MBTI dimension name -> column in the input frame and direction.
# Direction +1 means "user_signed = scale - 50" (high column value -> +).
_MBTI_DIM_TO_COL = {
    "extraversion": ("MBTIЭкстраверт", +1),
    "intuition":    ("MBTIИнтуитивные", +1),
    "thinking":     ("MBTIЛогика", +1),
    "judging":      ("MBTIПланирующие", +1),
    "assertive":    ("MBTIУверенные", +1),
}


@dataclass
class WeightConfig:
    gardner: float = 0.30
    mbti: float = 0.20
    cluster: float = 0.10
    roles: float = 0.40

    def normalized(self) -> "WeightConfig":
        s = self.gardner + self.mbti + self.cluster + self.roles
        return WeightConfig(self.gardner/s, self.mbti/s, self.cluster/s, self.roles/s)

    def as_dict(self) -> dict[str, float]:
        return {"gardner": self.gardner, "mbti": self.mbti,
                "cluster": self.cluster, "roles": self.roles}


@dataclass
class MatchBreakdown:
    gardner: float = 0.0
    mbti: float = 0.0
    cluster: float = 0.0
    roles: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {"gardner": self.gardner, "mbti": self.mbti,
                "cluster": self.cluster, "roles": self.roles}


@dataclass
class ProfessionMatch:
    profession_id: str
    name_ru: str
    name_en: str
    category: str
    total_score: float
    breakdown: MatchBreakdown
    matched_intelligences: list[tuple[str, float, float]] = field(default_factory=list)
    matched_mbti: list[tuple[str, float, float]] = field(default_factory=list)
    matched_roles: list[tuple[str, int]] = field(default_factory=list)
    cluster_match_kind: str = ""

    def as_dict(self) -> dict:
        return {
            "profession_id": self.profession_id,
            "name_ru": self.name_ru,
            "name_en": self.name_en,
            "category": self.category,
            "total_score": round(self.total_score, 2),
            "breakdown": {k: round(v, 2) for k, v in self.breakdown.as_dict().items()},
            "matched_intelligences": [
                {"name": n, "user": round(u, 1), "ideal": round(i, 1)}
                for n, u, i in self.matched_intelligences
            ],
            "matched_mbti": [
                {"dim": n, "user_signed": round(u, 1), "preference": round(p, 1)}
                for n, u, p in self.matched_mbti
            ],
            "matched_roles": [{"role": r, "predicted_rank": int(rk)}
                              for r, rk in self.matched_roles],
            "cluster_match_kind": self.cluster_match_kind,
        }


# ----------------------------------------------------------------------
# Component scorers (each returns 0..100)
# ----------------------------------------------------------------------

def _score_gardner(user_intel: pd.Series, p: Profession) -> tuple[float, list]:
    if not p.gardner_ideal:
        return 50.0, []
    aligns = []
    matched: list[tuple[str, float, float]] = []
    for name, ideal in p.gardner_ideal.items():
        u = float(user_intel[name])
        # alignment is 100 minus the absolute deviation, weighted by how
        # extreme the ideal is (caring more when ideal > 70 or < 30).
        deviation = abs(u - ideal)
        align = max(0.0, 100.0 - deviation)
        aligns.append(align)
        matched.append((name, u, ideal))
    return float(np.mean(aligns)), matched


def _score_mbti(user_scales: pd.Series, p: Profession) -> tuple[float, list]:
    if not p.mbti_preference:
        return 50.0, []
    aligns = []
    matched: list[tuple[str, float, float]] = []
    for dim, pref in p.mbti_preference.items():
        col, direction = _MBTI_DIM_TO_COL[dim]
        # user_signed in [-100, +100]: column 0..100, centered at 50 then x2
        user_signed = (float(user_scales[col]) - 50.0) * 2.0 * direction
        deviation = abs(user_signed - pref)  # 0..200
        align = max(0.0, 100.0 - deviation / 2.0)  # 0..100
        aligns.append(align)
        matched.append((dim, user_signed, pref))
    return float(np.mean(aligns)), matched


def _score_cluster(user_cluster_label: str, p: Profession) -> tuple[float, str]:
    pref = p.cluster_preference
    if pref == "any":
        return 70.0, "any"
    if user_cluster_label == pref:
        return 100.0, "exact"
    return 40.0, "mismatch"


def _score_roles(predicted_ranks: pd.Series, p: Profession) -> tuple[float, list]:
    """Score how well the profession's top_roles match the user's predicted ranking.

    For each role in p.top_roles, contribution = max(0, (21 - rank)/20 * 100).
    rank=1 -> 100, rank=11 -> 50, rank=20 -> 5, rank>20 -> 0.
    """
    contribs = []
    matched = []
    for role in p.top_roles:
        rank = int(predicted_ranks[role])
        c = max(0.0, (21 - rank) / 20.0 * 100.0)
        contribs.append(c)
        matched.append((role, rank))
    return float(np.mean(contribs)), matched


# ----------------------------------------------------------------------
# Hybrid matcher
# ----------------------------------------------------------------------

class HybridMatcher:
    def __init__(
        self,
        professions: list[Profession] | None = None,
        weights: WeightConfig | None = None,
        cluster_pipeline: tuple[StandardScaler, KMeans, dict[int, str]] | None = None,
        role_predictor: RolePredictor | None = None,
    ):
        self.professions = professions or load_professions()
        self.weights = (weights or WeightConfig()).normalized()
        self.cluster_pipeline = cluster_pipeline
        self.role_predictor = role_predictor

    # -------- helpers --------

    def _assign_cluster(self, user_neiry: pd.DataFrame) -> str:
        scaler, kmeans, label_map = self.cluster_pipeline
        Xn = scaler.transform(user_neiry[list(NEIRY_CLUSTERING_FEATURES)])
        cid = int(kmeans.predict(Xn)[0])
        return label_map.get(cid, "balanced")

    def _predict_roles(self, user_features: pd.DataFrame) -> pd.Series:
        ranks = self.role_predictor.predict_ranks(user_features[INPUT_FEATURES])[0]
        return pd.Series(ranks, index=list(ROLE_FEATURES))

    # -------- public API --------

    def match(self, user_row: pd.DataFrame, top_k: int = 10) -> list[ProfessionMatch]:
        """Score all professions and return the top-k matches."""
        # 1. derive cluster & role prediction
        cluster_label = self._assign_cluster(user_row)
        predicted_ranks = self._predict_roles(user_row)

        # 2. score every profession
        intel = user_row.iloc[0][list(GARDNER_FEATURES)]
        mbti  = user_row.iloc[0][list(MBTI_INDEPENDENT_SCALES)]
        results: list[ProfessionMatch] = []
        for p in self.professions:
            g, gm = _score_gardner(intel, p)
            m, mm = _score_mbti(mbti, p)
            c, ck = _score_cluster(cluster_label, p)
            r, rm = _score_roles(predicted_ranks, p)
            total = (self.weights.gardner * g
                     + self.weights.mbti   * m
                     + self.weights.cluster * c
                     + self.weights.roles  * r)
            results.append(ProfessionMatch(
                profession_id=p.id,
                name_ru=p.name_ru,
                name_en=p.name_en,
                category=p.category,
                total_score=total,
                breakdown=MatchBreakdown(g, m, c, r),
                matched_intelligences=gm,
                matched_mbti=mm,
                matched_roles=rm,
                cluster_match_kind=ck,
            ))
        results.sort(key=lambda x: x.total_score, reverse=True)
        return results[:top_k]


def build_default_matcher(models_dir: str | None = None,
                          weights: WeightConfig | None = None) -> HybridMatcher:
    """Build the matcher using the canonical artifacts produced by stages 1-2."""
    from pathlib import Path
    import json

    root = Path(__file__).resolve().parents[1]
    models_dir = Path(models_dir) if models_dir else root / "data" / "processed"

    # --- cluster pipeline reconstruction ---
    # We refit the canonical k-means on the pilot's neiry features (random_state=2)
    # to recover the same model that produced clusters_canonical.csv.
    from .data_loader import load_pilot
    pilot = load_pilot()
    scaler = StandardScaler()
    Xn = scaler.fit_transform(pilot[list(NEIRY_CLUSTERING_FEATURES)])
    km = KMeans(n_clusters=3, n_init=10, random_state=2).fit(Xn)

    with open(models_dir / "clusters_metadata.json", encoding="utf-8") as f:
        meta = json.load(f)
    perm = meta["permutation_info"]
    label_map = {
        perm["balanced_orig_id"]: "balanced",
        perm["mobilized_orig_id"]: "mobilized",
        perm["depleted_orig_id"]: "depleted",
    }
    cluster_pipeline = (scaler, km, label_map)

    # --- role predictor: pick Random Forest (best on real CV) ---
    rf = joblib.load(models_dir / "role_models" / "random_forest_synth_to_real.joblib")

    return HybridMatcher(
        weights=weights,
        cluster_pipeline=cluster_pipeline,
        role_predictor=rf,
    )


__all__ = [
    "WeightConfig", "MatchBreakdown", "ProfessionMatch",
    "HybridMatcher", "build_default_matcher",
]
