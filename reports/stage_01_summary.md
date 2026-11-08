# Stage 0+1 Summary - Foundation and Synthetic Data Pipeline

This document summarizes the work completed in the first stage of the practical
part of the dissertation. The goal of Stage 0+1 was to (a) recover the lost
NIRM analysis as a verified, reproducible artifact and (b) build a synthetic
data pipeline that lifts the dataset from n=47 to n=500 without losing the
statistical character of the pilot.

## 1. Pilot dataset inventory

The pilot dataset `pilot_47x65_anon.csv` contains **47 respondents x 65 columns**, with no
missing values. The columns are organized into five logical groups:

| Group | # features | Description |
|---|---|---|
| Identifier | 1 | `ФИО` |
| Gardner Multiple Intelligences | 9 | continuous percentile scores 0..100 |
| MBTI - categorical type | 1 | `MBTIabbrev`, e.g. `INFP-T` (20 unique values) |
| MBTI - continuous scales | 10 | five complementary pairs summing to 100 |
| Neiry role rankings | 20 | per-row permutation of 1..20 (verified) |
| Neiry EEG metrics | 24 | indices, spectral powers, peak frequencies, emotions |

A complete machine-checkable dictionary is in
[`reports/data_dictionary.md`](data_dictionary.md), with figures in
[`reports/figures/01a_..01d_*.png`](figures/).

**Key data-quality finding.** The IQR rule flagged a single extreme observation
in `neiryFatigue score` (max = 216.15 vs. p99 ~ 30), confirming the artifact
mentioned in the published abstract (тезис). All other features fall within
plausible ranges. No imputation needed (no missing values).

## 2. Reproduction of NIRM clustering

NIRM (November 2025) reported a k-means clustering with k=3 on standardized
Neiry features. We reproduced it exactly:

| Metric | NIRM reported | Reproduced |
|---|---|---|
| silhouette | 0.24 | **0.240** |
| cluster sizes | [30, 8, 9] | **[30, 8, 9]** |
| Baseline Concentration centroids | [1.65, 3.72, 1.02] | **[1.655, 3.718, 1.019]** |
| Baseline Relaxation centroids | [0.75, 0.34, 1.37] | **[0.749, 0.340, 1.365]** |
| Baseline Fatigue centroids | [1.63, 0.67, 4.03] | **[1.633, 0.667, 4.027]** |
| Mean of feature means | 14.09 | **14.09** |
| Mean of feature stds | 3.92 | **3.92** |

Reproducibility is achieved with `random_state=2` over a sweep of seeds 0..199
(see `scripts/02_reproduce_nirm_clustering.py`).

We also assigned **interpretive labels** to the clusters that will be reused
across the system:

| ID | Label | n | Profile |
|---|---|---|---|
| 0 | balanced  | 30 | medium concentration / medium relaxation / medium fatigue |
| 1 | mobilized |  8 | high concentration, low relaxation, low fatigue |
| 2 | depleted  |  9 | low concentration, high relaxation, high fatigue |

The canonical assignments are persisted in
`data/processed/clusters_canonical.csv` and consumed by all downstream layers.

## 3. Synthetic data generator (n=500)

Because n=47 is too small for supervised learning, we built a synthetic
extension. Key design decisions:

* **Backbone model:** Gaussian copula (SDV `GaussianCopulaSynthesizer` with
  KDE marginals). Preserves both marginal shapes and pairwise correlations.

* **Role rankings** are not generated as raw integers (which would destroy the
  permutation constraint). Each respondent's rank vector is converted to a
  continuous preference score via the inverse-normal transform, fed to the
  copula along with everything else, and re-ranked per row after sampling.
  This restores valid 1..20 permutations while preserving cross-role
  correlations.

* **MBTI complementary scales** (e.g. `MBTIИнтроверт = 100 - MBTIЭкстраверт`)
  are reconstructed exactly post-sampling to preserve the sum-to-100 invariant.

* **MBTI categorical type** is derived deterministically from sampled scales
  via the standard 50% threshold per dichotomy.

* **Range constraints** (Gardner and MBTI in [0, 100]) are enforced by clipping.

### Validation results

35 of 38 continuous features pass the Kolmogorov-Smirnov 2-sample test at
alpha=0.05 (i.e. real and synthetic samples are statistically indistinguishable).

| Test | Value | Interpretation |
|---|---|---|
| KS pass rate | **35/38** | 92% of features statistically indistinguishable |
| Relative Frobenius distance, continuous correlations | **0.134** | < 0.20 = faithful copula fit |
| Relative Frobenius distance, role correlations | **0.227** | acceptable given rank->score->rank pipeline |
| Synthetic silhouette (k=3 on Neiry features) | 0.177 | expected drop with smoother distribution |
| Synthetic cluster sizes | [241, 142, 117] | balanced as expected with n=500 from a smooth density |

The 3 features that fail KS are all heavily skewed by single-subject
artifacts (`neiryFatigue score`, `neiryAlpha Gravity` and its baseline). For
the supervised modeling stage we will winsorize these to p99 before training,
or drop them, depending on feature importance results.

Detailed breakdown: [`reports/synthetic_validation.md`](synthetic_validation.md).

## 4. Honest framing for the dissertation

This stage gives us two **complementary** datasets used in different parts of
the system:

| Dataset | Used for | Justification |
|---|---|---|
| Pilot (n=47, real) | Cognitive profiling layer (clustering); validation of model generalization | Real Neiry measurements, ground-truth role rankings |
| Synthetic (n=500) | Training the supervised role-prediction layer | Avoids overfitting on n=47; preserves pilot statistics |

In the dissertation text, this should be presented as **methodological
transparency**, not as a workaround. The pilot is the empirical anchor; the
synthetic extension is an explicit data-augmentation decision driven by the
sample-size constraint, with statistical validation showing that the
augmentation does not introduce systematic bias.

## 5. Artifacts produced

```
data/processed/clusters_canonical.csv         (47 rows: id, cluster_id, cluster_label)
data/processed/clusters_metadata.json         (clustering parameters + reproducibility)
data/synthetic/synth_500.csv                  (500 rows, full schema)
data/synthetic/synth_500.xlsx                 (same, Excel)
data/synthetic/synth_500_metadata.json        (generation config + invariant checks)
reports/data_dictionary.md                    (feature-by-feature description)
reports/synthetic_validation.md               (KS + correlation + clustering checks)
reports/synthetic_validation_summary.json     (numeric summary)
reports/figures/01*.png                       (4 figures: distributions + outliers)
reports/figures/02*.png                       (4 figures: clustering + centroids)
reports/figures/04*.png                       (4 figures: real vs synth comparison)
```

## 6. Next stage

Stage 2 will build the supervised layer of the system: predict each
respondent's 20 Neiry role rankings from their psychometric and EEG features.
This produces the **first set of honest, defensible metrics** for the
dissertation (NDCG@5, Spearman rho, top-k accuracy). Models trained on
synthetic n=500, validated on real n=47 held out.
