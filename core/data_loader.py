"""Loader for the pilot dataset (47 respondents) and feature group definitions.

The dataset combines three measurement instruments:
  * Gardner's Multiple Intelligences (9 scales, 0..100)
  * MBTI (categorical type + 10 continuous percentile scales over 5 dichotomies)
  * Neiry EEG headset metrics (24 features) and 20 derived role rankings
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "pilot_47x65_anon.csv"


ID_COL = "ФИО"

GARDNER_FEATURES = [
    "Натуралистический интеллект",
    "Внутриличностный интеллект",
    "Логико-математический интеллект",
    "Лингвистический интеллект",
    "Телесно-кинестетический интеллект",
    "Пространственно-визуальный интеллект",
    "Музыкальный интеллект",
    "Экзистенциальный интеллект",
    "Межличностный интеллект",
]

MBTI_TYPE_COL = "MBTIabbrev"
MBTI_SCALE_FEATURES = [
    "MBTIИнтроверт", "MBTIЭкстраверт",
    "MBTIРеалистичные", "MBTIИнтуитивные",
    "MBTIПринципы", "MBTIЛогика",
    "MBTIИщущие", "MBTIПланирующие",
    "MBTIОсторожные", "MBTIУверенные",
]

# Each scale pair sums to 100 - keep one side per dichotomy to avoid collinearity.
MBTI_INDEPENDENT_SCALES = [
    "MBTIЭкстраверт",
    "MBTIИнтуитивные",
    "MBTIЛогика",
    "MBTIПланирующие",
    "MBTIУверенные",
]

ROLE_FEATURES = [
    "Focus Expert", "Optimist", "Brainstormer", "Catalyst", "Analyst",
    "Winner", "Storyteller", "Problem Solver", "Strategist", "Thinker",
    "Believer", "Time Keeper", "Peace Keeper", "Deliverer", "Commander",
    "Philomath", "Chameleon", "Coach", "Self-Believer", "Empathizer",
]

NEIRY_FEATURES = [
    # Spectral peak frequencies
    "neiryIAPF", "neiryIAF",
    # Cognitive indices: baseline + actual
    "neiryBaseline Fatigue score", "neiryFatigue score",
    "neiryBaseline Alpha Gravity", "neiryAlpha Gravity",
    "neiryBaseline Concentration index", "neiryConcentration index",
    "neiryBaseline Relaxation index", "neiryRelaxation index",
    "neiryBaseline Reverse Fatigue", "neiryReverse Fatigue",
    "neiryAccumulated Fatigue",
    # Spectral band power
    "neiryTheta", "neiryAlpha", "neiryBeta",
    "neiryTheta peak frequency", "neiryAlpha peak frequency", "neiryBeta peak frequency",
    # Emotion markers
    "neiryChill", "neiryStress", "neiryFocus", "neiryAnger", "neirySelf-control",
]

# Subset used by NIRM (November 2025) for k-means clustering.
# NIRM described "neural features (Neiry), pre-normalized via standardization".
NEIRY_CLUSTERING_FEATURES = NEIRY_FEATURES.copy()


@dataclass(frozen=True)
class FeatureGroups:
    id: str = ID_COL
    gardner: tuple[str, ...] = tuple(GARDNER_FEATURES)
    mbti_type: str = MBTI_TYPE_COL
    mbti_scales: tuple[str, ...] = tuple(MBTI_SCALE_FEATURES)
    mbti_independent: tuple[str, ...] = tuple(MBTI_INDEPENDENT_SCALES)
    roles: tuple[str, ...] = tuple(ROLE_FEATURES)
    neiry: tuple[str, ...] = tuple(NEIRY_FEATURES)


def load_pilot(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the 47-respondent pilot dataset (pseudonymized CSV, or original xlsx)."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path, encoding="utf-8")
    return pd.read_excel(path, sheet_name=0)


def feature_groups() -> FeatureGroups:
    return FeatureGroups()


__all__ = [
    "PROJECT_ROOT", "RAW_DATA_PATH",
    "ID_COL", "GARDNER_FEATURES", "MBTI_TYPE_COL", "MBTI_SCALE_FEATURES",
    "MBTI_INDEPENDENT_SCALES", "ROLE_FEATURES", "NEIRY_FEATURES",
    "NEIRY_CLUSTERING_FEATURES",
    "FeatureGroups", "load_pilot", "feature_groups",
]
