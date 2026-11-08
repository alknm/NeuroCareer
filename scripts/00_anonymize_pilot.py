"""Stage 0: pseudonymize the pilot dataset before publication.

Reads the original export `data/raw/47.xlsx` (contains respondents' full names,
kept locally and never committed), replaces every name with a stable code
R-01..R-47 (row order of the original file) and writes:

  * data/raw/pilot_47x65_anon.csv        - the dataset used by the pipeline
  * data/raw/id_mapping_PRIVATE.csv       - name <-> code key (local only!)

It also rewrites already generated artefacts (processed CSV/JSON, markdown
reports, dissertation text module) so that no real name remains in the repo.
The script is idempotent: a second run finds nothing to replace.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ID_COL  # noqa: E402

SRC = ROOT / "data" / "raw" / "47.xlsx"
DST = ROOT / "data" / "raw" / "pilot_47x65_anon.csv"
KEY = ROOT / "data" / "raw" / "id_mapping_PRIVATE.csv"

TEXT_TARGETS = [
    "data/processed/clusters_canonical.csv",
    "data/processed/recommendations.csv",
    "data/processed/clusters_metadata.json",
    "data/synthetic/synth_500_metadata.json",
    "reports/explanations.md",
    "reports/explanations_meta.json",
    "reports/matcher_examples.md",
    "reports/matcher_summary.json",
    "reports/stage_01_summary.md",
    "reports/stage_02_summary.md",
    "reports/stage_03_summary.md",
    "reports/stage_04_summary.md",
    "reports/stage_05_summary.md",
    "REVIEWER_README.md",
    "README.md",
    "scripts/dissertation_content/chapter5.py",
]


def main() -> None:
    df = pd.read_excel(SRC, sheet_name=0)
    assert df.shape == (47, 65), df.shape
    names = df[ID_COL].astype(str).str.strip().tolist()
    codes = [f"R-{i + 1:02d}" for i in range(len(names))]
    mapping = dict(zip(names, codes))

    out = df.copy()
    out[ID_COL] = codes
    out.to_csv(DST, index=False, encoding="utf-8")
    pd.DataFrame({"name": names, "code": codes}).to_csv(KEY, index=False, encoding="utf-8")
    print(f"wrote {DST.relative_to(ROOT)} {out.shape}")
    print(f"wrote {KEY.relative_to(ROOT)} (keep private)")

    # Full names first, then surname-only mentions (only unambiguous surnames).
    surname_counts = Counter(n.split()[0] for n in names)
    surname_map = {n.split()[0]: c for n, c in mapping.items()
                   if surname_counts[n.split()[0]] == 1}
    # Some original names carry leading/trailing spaces - map the raw form too.
    raw_names = df[ID_COL].astype(str).tolist()
    mapping.update(zip(raw_names, codes))
    full_re = re.compile("|".join(re.escape(n) for n in sorted(mapping, key=len, reverse=True)))
    sur_re = re.compile(r"(?<!\w)(" + "|".join(re.escape(s) for s in surname_map) + r")(?!\w)")

    for rel in TEXT_TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        new = full_re.sub(lambda m: mapping[m.group(0)], text)
        new = sur_re.sub(lambda m: surname_map[m.group(1)], new)
        if new != text:
            p.write_text(new, encoding="utf-8")
            print(f"pseudonymized {rel}")


if __name__ == "__main__":
    main()
