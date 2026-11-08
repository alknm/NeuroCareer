# NeuroCareer - Hybrid Career Guidance System

Practical part of the master's dissertation
**"Research and development of a hybrid career guidance system based on neural data and psychological tests using AI"**.

## Project layout

```
system/
├── core/                          reusable Python modules
│   ├── data_loader.py             pilot dataset loader and feature group definitions
│   └── synthetic.py               Gaussian-copula synthetic data generator
├── data/
│   ├── raw/pilot_47x65_anon.csv              pilot dataset (n=47, pseudonymized R-01..R-47)
│   ├── processed/                 derived artifacts (cluster assignments, etc.)
│   └── synthetic/                 generated extended dataset (n=500)
├── scripts/                       one-shot analysis / generation scripts
│   ├── 01_data_dictionary.py
│   ├── 02_reproduce_nirm_clustering.py
│   ├── 03_generate_synthetic.py
│   └── 04_validate_synthetic.py
└── reports/                       human-readable artifacts
    ├── data_dictionary.md
    ├── synthetic_validation.md
    ├── synthetic_validation_summary.json
    └── figures/                   PNG figures for the dissertation text
```

## Stage 0+1 status (completed)

| # | Step | Result |
|---|---|---|
| 0 | Project structure + raw data copy | done |
| 1 | Data dictionary (`reports/data_dictionary.md`) | 65 columns, 0 missing values, outliers documented |
| 2 | NIRM k-means reproduction | **silhouette = 0.240, sizes [30, 8, 9], centroids match to 3 decimals** with `random_state=2` |
| 3 | Synthetic data generator (Gaussian copula, n=500) | all invariants enforced (role permutations, MBTI sums, ranges) |
| 4 | Synthetic validation | **35/38 KS-tests pass (p>0.05)**, Frobenius corr-distance 0.134 (continuous) / 0.227 (roles) |

## How to reproduce

```powershell
# from the system/ directory
python scripts/01_data_dictionary.py
python scripts/02_reproduce_nirm_clustering.py
python scripts/03_generate_synthetic.py
python scripts/04_validate_synthetic.py
```

## Dependencies

```
pandas, openpyxl, numpy, scipy, scikit-learn, matplotlib, seaborn,
sdv (>=1.36), tabulate
```

## Stage status

| Stage | Goal | Status |
|---|---|:---:|
| 0+1 | Data dictionary + reproduce NIRM clustering + synthetic generator | done |
| 2 | Supervised role-prediction layer (5 models, 2 evaluation regimes, SHAP) | done |
| 3 | Profession knowledge base (64 careers) + hybrid matcher | done |
| 4 | LLM explainer via local Ollama / template fallback | done |
| 5 | Streamlit UI + PDF export | done |

## Launching the system

```bash
git clone https://github.com/alknm/NeuroCareer.git
cd NeuroCareer
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
streamlit run app.py
# opens http://localhost:8501
```

Alternatively, run `run.cmd` (Windows) or `./run.sh` (Linux/macOS) from the
project folder - they create the environment and start the app automatically.

For natural-language explanations, install Ollama once (one-time manual step):
see [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md). The system also works without it
(template fallback) - useful when offline.

## Per-stage reports

* [`reports/stage_01_summary.md`](reports/stage_01_summary.md) - foundation + synthetic data
* [`reports/stage_02_summary.md`](reports/stage_02_summary.md) - role prediction
* [`reports/stage_03_summary.md`](reports/stage_03_summary.md) - knowledge base + matcher
* [`reports/stage_04_summary.md`](reports/stage_04_summary.md) - LLM explainer
* [`reports/stage_05_summary.md`](reports/stage_05_summary.md) - UI
