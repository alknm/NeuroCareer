"""Profession knowledge base loader and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

from .data_loader import GARDNER_FEATURES, ROLE_FEATURES

KB_PATH = Path(__file__).resolve().parents[1] / "data" / "professions.yaml"

VALID_CATEGORIES = {"it", "engineering", "science", "healthcare",
                    "education", "arts", "business", "social", "trades"}
VALID_CLUSTERS = {"balanced", "mobilized", "depleted", "any"}
VALID_MBTI_KEYS = {"extraversion", "intuition", "thinking", "judging", "assertive"}
VALID_INTELLIGENCES = set(GARDNER_FEATURES)
VALID_ROLES = set(ROLE_FEATURES)


@dataclass
class Profession:
    id: str
    name_ru: str
    name_en: str
    category: str
    description_ru: str
    cluster_preference: Literal["balanced", "mobilized", "depleted", "any"]
    gardner_ideal: dict[str, float]      # only listed intelligences
    mbti_preference: dict[str, float]    # signed [-100, +100], only listed dims
    top_roles: list[str]

    @classmethod
    def from_dict(cls, d: dict) -> "Profession":
        return cls(
            id=d["id"],
            name_ru=d["name_ru"],
            name_en=d["name_en"],
            category=d["category"],
            description_ru=d.get("description_ru", ""),
            cluster_preference=d.get("cluster_preference", "any"),
            gardner_ideal=dict(d.get("gardner_ideal", {})),
            mbti_preference=dict(d.get("mbti_preference", {})),
            top_roles=list(d.get("top_roles", [])),
        )


def load_professions(path: str | Path = KB_PATH) -> list[Profession]:
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    items = raw["professions"]
    profs = [Profession.from_dict(d) for d in items]
    _validate(profs)
    return profs


def _validate(profs: list[Profession]) -> None:
    seen_ids: set[str] = set()
    errs: list[str] = []
    for p in profs:
        if p.id in seen_ids:
            errs.append(f"duplicate id: {p.id}")
        seen_ids.add(p.id)
        if p.category not in VALID_CATEGORIES:
            errs.append(f"{p.id}: bad category '{p.category}'")
        if p.cluster_preference not in VALID_CLUSTERS:
            errs.append(f"{p.id}: bad cluster_preference '{p.cluster_preference}'")
        for k in p.gardner_ideal:
            if k not in VALID_INTELLIGENCES:
                errs.append(f"{p.id}: unknown intelligence '{k}'")
        for k in p.mbti_preference:
            if k not in VALID_MBTI_KEYS:
                errs.append(f"{p.id}: unknown MBTI dim '{k}'")
        for r in p.top_roles:
            if r not in VALID_ROLES:
                errs.append(f"{p.id}: unknown role '{r}'")
        for v in p.gardner_ideal.values():
            if not (0 <= v <= 100):
                errs.append(f"{p.id}: gardner score out of [0,100]")
        for v in p.mbti_preference.values():
            if not (-100 <= v <= 100):
                errs.append(f"{p.id}: mbti pref out of [-100,100]")
        if not (3 <= len(p.top_roles) <= 5):
            errs.append(f"{p.id}: top_roles must have 3..5 items, got {len(p.top_roles)}")
    if errs:
        raise ValueError("Profession KB validation failed:\n  " + "\n  ".join(errs))


__all__ = ["Profession", "load_professions", "KB_PATH"]
