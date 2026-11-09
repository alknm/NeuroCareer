# NeuroCareer — reanalysis for the journal article

Scripts that reproduce the additional analyses reported in the article
"Explainable AI in Student Career Guidance" (Sections 3.4 and 4.2–4.3).

## Contents

| File | Purpose |
| --- | --- |
| `common.py` | Data loading, feature sets, rank transforms, metrics (Spearman ρ, NDCG@5, top-1, MAE), models, Gaussian copula sampler |
| `run_cv.py` | 20 × five-fold cross-validation: baseline, ridge, random forest, gradient boosting, LightGBM; feature sets *all*, *self-report only*, *EEG only* |
| `run_aug.py` | Synthetic augmentation: *leaky* (copula fitted on all 47) vs *honest* (copula fitted inside each training fold) |
| `run_weights.py` | Sensitivity of profession rankings to matcher weights and to dropping EEG inputs (re-implements `core/matcher.py`; out-of-fold role predictions) |
| `summarize.py` | Participant-level means, 95% bootstrap CIs, paired Wilcoxon tests |
| `results/results_summary.txt` | Output of `summarize.py` used in the article |
| `results/weights_results.csv` | Output of `run_weights.py` (Table 4 of the article) |

## Data

The scripts expect `pilot_47x65_anon.csv` (47 de-identified participants, IDs R01–R47):
9 multiple-intelligences scales, 10 MBTI-type scales + type, 20 reference role ranks, 24 EEG markers.
The dataset is not included in this repository; it is available from the authors on reasonable request.

## How to run

```bash
pip install -r requirements.txt
python run_cv.py  data/pilot_47x65_anon.csv . 20 cv_records.csv
python run_aug.py data/pilot_47x65_anon.csv . 20 aug_records.csv
python summarize.py cv_records.csv aug_records.csv
python run_weights.py data/pilot_47x65_anon.csv ../data/professions.yaml . weights_results.csv
```

Each script takes about 10 minutes on a laptop. Random seeds are fixed (repetition r uses `KFold(random_state=r)`).

## Notes

- Role ranks are converted to scores with Φ⁻¹((20 − r + 0.5)/20) and re-ranked after prediction.
- The extreme `neiryFatigue score` value is winsorised at the 99th percentile of each training fold.
- Self-report features: 9 Gardner scales and 5 MBTI poles (Extravert, Intuitive, Thinking, Judging, Assertive).
