"""Generate LLM/template explanations for sample respondent recommendations.

Produces:
  reports/explanations.md          - per-respondent top-5 with explanations
  reports/explanations_meta.json   - timing, backend used, sample sizes
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.data_loader import ID_COL, MBTI_TYPE_COL, load_pilot
from core.llm_explainer import LLMExplainer, make_user_meta
from core.matcher import build_default_matcher

REPORTS = ROOT / "reports"
PROCESSED = ROOT / "data" / "processed"


def pick_sample_respondents(pilot: pd.DataFrame, n_per_cluster: int = 1,
                            n_extra: int = 2, seed: int = 42) -> list[str]:
    rng = np.random.default_rng(seed)
    picked: list[str] = []
    for label in ["balanced", "mobilized", "depleted"]:
        sub = pilot[pilot["cluster_label"] == label]
        if len(sub) > 0:
            picked.append(sub[ID_COL].iloc[0])
    extras_pool = list(set(pilot[ID_COL]) - set(picked))
    if extras_pool and n_extra > 0:
        chosen = rng.choice(extras_pool, size=min(n_extra, len(extras_pool)), replace=False)
        picked.extend(chosen.tolist())
    return picked


def main(backend: str = "auto", top_n: int = 5) -> None:
    pilot = load_pilot()
    canonical = pd.read_csv(PROCESSED / "clusters_canonical.csv", encoding="utf-8")
    pilot = pilot.merge(canonical, on=ID_COL)

    matcher = build_default_matcher()
    explainer = LLMExplainer(backend=backend)
    actual_backend = explainer._resolved_backend()
    print(f"backend resolved to: {actual_backend}")
    if backend == "auto" and actual_backend == "template":
        print("  (Ollama not reachable on http://localhost:11434 - using template)")

    sample_ids = pick_sample_respondents(pilot)
    print(f"sample respondents: {len(sample_ids)}")

    md = ["# Profession recommendations with explanations\n"]
    md.append(f"Backend: **{actual_backend}** "
              f"(model: `{explainer.model}` if Ollama)  ")
    md.append(f"Sample size: **{len(sample_ids)} respondents x top-{top_n} professions**\n")

    timings: list[float] = []
    backend_used: list[str] = []
    for rid in sample_ids:
        row = pilot[pilot[ID_COL] == rid].iloc[0]
        user = pd.DataFrame([row])
        matches = matcher.match(user, top_k=top_n)
        user_meta = make_user_meta(row, row["cluster_label"])

        md.append(f"## {rid}")
        md.append(f"* MBTI: **{user_meta['mbti']}**, cluster: **{user_meta['cluster']}**")
        md.append("* Top intelligences: " + ", ".join(
            f"{n} ({s:.0f})" for n, s in user_meta["top_intelligences"]))
        md.append("")

        for i, m in enumerate(matches, start=1):
            t0 = time.time()
            expl = explainer.explain(user_meta, m)
            dt = time.time() - t0
            timings.append(dt)
            backend_used.append(expl.backend)
            md.append(f"### {i}. {m.name_ru} - score {m.total_score:.1f}")
            md.append(f"*Component scores: gardner={m.breakdown.gardner:.1f}, "
                      f"mbti={m.breakdown.mbti:.1f}, "
                      f"cluster={m.breakdown.cluster:.1f}, "
                      f"roles={m.breakdown.roles:.1f}*")
            md.append("")
            md.append(expl.text)
            md.append("")
        md.append("---\n")

    out_md = REPORTS / "explanations.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"saved: {out_md}")

    meta = {
        "backend_resolved": actual_backend,
        "model": explainer.model,
        "n_respondents": len(sample_ids),
        "top_n_per_respondent": top_n,
        "n_explanations": len(timings),
        "backend_used_counts": {b: backend_used.count(b) for b in set(backend_used)},
        "timing_seconds": {
            "mean": round(float(np.mean(timings)), 3),
            "median": round(float(np.median(timings)), 3),
            "min": round(float(np.min(timings)), 3),
            "max": round(float(np.max(timings)), 3),
            "total": round(float(np.sum(timings)), 2),
        },
    }
    with open(REPORTS / "explanations_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"saved meta: {REPORTS / 'explanations_meta.json'}")
    print(f"\ntotal generation time: {meta['timing_seconds']['total']:.1f} s "
          f"({meta['timing_seconds']['mean']:.2f} s per explanation)")


if __name__ == "__main__":
    backend = sys.argv[1] if len(sys.argv) > 1 else "auto"
    main(backend=backend)
