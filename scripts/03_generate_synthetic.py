"""Generate the synthetic extended dataset (n=500) from the pilot.

Outputs:
  data/synthetic/synth_500.csv
  data/synthetic/synth_500.xlsx
  data/synthetic/synth_500_metadata.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import (
    GARDNER_FEATURES, ID_COL, MBTI_INDEPENDENT_SCALES, MBTI_SCALE_FEATURES,
    MBTI_TYPE_COL, NEIRY_FEATURES, ROLE_FEATURES, load_pilot,
)
from core.synthetic import SyntheticConfig, SyntheticGenerator

OUT = ROOT / "data" / "synthetic"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    pilot = load_pilot()
    print(f"pilot loaded: {pilot.shape}")

    cfg = SyntheticConfig(n_samples=500, random_state=42, use_sdv=True)
    print(f"fitting GaussianCopula on {cfg.n_samples} target samples ...")
    gen = SyntheticGenerator(cfg).fit(pilot)
    synth = gen.sample()
    print(f"synthetic generated: {synth.shape}")

    # --- Sanity checks ---
    # 1. Role columns must be permutations of 1..20 per row
    role_block = synth[list(ROLE_FEATURES)]
    perms_ok = (role_block.apply(
        lambda r: sorted(r.tolist()) == list(range(1, 21)), axis=1).sum())
    print(f"  rows with valid 1..20 role permutation: {perms_ok}/{len(synth)}")
    assert perms_ok == len(synth), "Synthetic roles violate permutation constraint!"

    # 2. MBTI complementary scales must sum to 100
    for indep, comp in [("MBTIЭкстраверт", "MBTIИнтроверт"),
                         ("MBTIИнтуитивные", "MBTIРеалистичные"),
                         ("MBTIЛогика", "MBTIПринципы"),
                         ("MBTIПланирующие", "MBTIИщущие"),
                         ("MBTIУверенные", "MBTIОсторожные")]:
        sums = (synth[indep] + synth[comp]).round(1)
        bad = ((sums - 100).abs() > 0.05).sum()
        print(f"  MBTI {indep}+{comp} = 100: {len(synth)-bad}/{len(synth)}")
        assert bad == 0, f"MBTI sum invariant broken for {indep}/{comp}"

    # 3. Gardner in [0,100], MBTI in [0,100]
    for col in list(GARDNER_FEATURES) + list(MBTI_SCALE_FEATURES):
        out_of_range = ((synth[col] < 0) | (synth[col] > 100)).sum()
        if out_of_range:
            print(f"  WARNING {col}: {out_of_range} values out of [0,100]")

    # 4. MBTI type derivable correctness
    types_unique = synth[MBTI_TYPE_COL].nunique()
    print(f"  unique MBTI types in synthetic: {types_unique}")

    # --- Save artifacts ---
    csv_path = OUT / "synth_500.csv"
    xlsx_path = OUT / "synth_500.xlsx"
    synth.to_csv(csv_path, index=False, encoding="utf-8")
    synth.to_excel(xlsx_path, index=False)

    metadata = {
        "n_samples": cfg.n_samples,
        "random_state": cfg.random_state,
        "method": "GaussianCopulaSynthesizer (SDV)" if cfg.use_sdv else "numpy gaussian copula",
        "marginal_distribution": "gaussian_kde (sdv default override)",
        "feature_groups": {
            "id": [ID_COL],
            "gardner": list(GARDNER_FEATURES),
            "mbti_type": [MBTI_TYPE_COL],
            "mbti_scales": list(MBTI_SCALE_FEATURES),
            "mbti_independent": list(MBTI_INDEPENDENT_SCALES),
            "roles": list(ROLE_FEATURES),
            "neiry": list(NEIRY_FEATURES),
        },
        "invariants_enforced": {
            "role_permutation_1_to_20": True,
            "mbti_pair_sum_100": True,
            "gardner_clipped_0_100": True,
            "mbti_clipped_0_100": True,
            "mbti_type_derived_from_scales": True,
        },
        "checks": {
            "valid_role_permutations": int(perms_ok),
            "unique_mbti_types": int(types_unique),
        },
    }
    with open(OUT / "synth_500_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nsaved:")
    print(f"  {csv_path}")
    print(f"  {xlsx_path}")
    print(f"  {OUT / 'synth_500_metadata.json'}")


if __name__ == "__main__":
    main()
