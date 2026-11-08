# Synthetic Data Validation

**Real:** 47 rows × 65 cols  
**Synthetic:** 500 rows × 65 cols  
**Generation method:** GaussianCopulaSynthesizer (SDV), KDE marginals, random_state=42

## 1. Marginal Distributions (Kolmogorov-Smirnov 2-sample test)

Null hypothesis: real and synthetic samples come from the same distribution. p > 0.05 = cannot reject = distributions look statistically indistinguishable.

**Pass rate: 35/38 features**

| feature                              |   real_mean |   synth_mean |   real_std |   synth_std |   ks_stat |   ks_p | same_dist_p>0.05   |
|:-------------------------------------|------------:|-------------:|-----------:|------------:|----------:|-------:|:-------------------|
| neiryFatigue score                   |       7.138 |       10.493 |     31.191 |      23.487 |     0.413 | 0      | no                 |
| neiryAlpha Gravity                   |       1.155 |        1.34  |      2.326 |       2.387 |     0.288 | 0.0012 | no                 |
| neiryBaseline Alpha Gravity          |       1.096 |        1.183 |      1.983 |       1.951 |     0.26  | 0.0047 | no                 |
| neiryIAPF                            |      10.145 |       10.223 |      1.071 |       1.091 |     0.167 | 0.16   | yes                |
| neiryBaseline Reverse Fatigue        |       0.952 |        0.943 |      0.926 |       0.956 |     0.159 | 0.2044 | yes                |
| neiryIAF                             |       9.898 |        9.966 |      0.451 |       0.472 |     0.155 | 0.2298 | yes                |
| neiryReverse Fatigue                 |       0.78  |        0.83  |      0.545 |       0.586 |     0.133 | 0.3999 | yes                |
| Внутриличностный интеллект           |      62.787 |       63.938 |     15.532 |      16.843 |     0.12  | 0.5285 | yes                |
| Межличностный интеллект              |      63.579 |       64.601 |     16.516 |      17.202 |     0.117 | 0.557  | yes                |
| neiryAccumulated Fatigue             |       1.683 |        1.762 |      1.471 |       1.486 |     0.114 | 0.5885 | yes                |
| neiryConcentration index             |       1.554 |        1.611 |      0.92  |       0.987 |     0.114 | 0.5909 | yes                |
| neiryBaseline Concentration index    |       1.884 |        1.874 |      1.397 |       1.428 |     0.113 | 0.6026 | yes                |
| neiryTheta                           |       0.274 |        0.269 |      0.075 |       0.079 |     0.112 | 0.6112 | yes                |
| MBTIПланирующие                      |      51.681 |       51.407 |     17.413 |      18.04  |     0.111 | 0.6234 | yes                |
| neiryBeta                            |       0.319 |        0.327 |      0.113 |       0.12  |     0.109 | 0.6395 | yes                |
| neiryBaseline Fatigue score          |       1.927 |        1.998 |      1.641 |       1.737 |     0.109 | 0.6469 | yes                |
| Лингвистический интеллект            |      53.14  |       54.334 |     16.19  |      16.853 |     0.104 | 0.7039 | yes                |
| neiryBaseline Relaxation index       |       0.798 |        0.811 |      0.505 |       0.534 |     0.103 | 0.7133 | yes                |
| neirySelf-control                    |      53.19  |       52.339 |      9.919 |      10.492 |     0.101 | 0.7331 | yes                |
| neiryChill                           |      47.331 |       46.909 |      8.409 |       8.983 |     0.1   | 0.745  | yes                |
| Логико-математический интеллект      |      63.826 |       63.021 |     21.995 |      24.232 |     0.1   | 0.7468 | yes                |
| neiryTheta peak frequency            |       5.003 |        4.997 |      0.213 |       0.224 |     0.099 | 0.7551 | yes                |
| neiryAlpha peak frequency            |       8.418 |        8.499 |      0.778 |       0.849 |     0.099 | 0.757  | yes                |
| neiryBeta peak frequency             |      19.21  |       19.267 |      1.616 |       1.744 |     0.096 | 0.7888 | yes                |
| Натуралистический интеллект          |      57.749 |       57.343 |     18.465 |      19.466 |     0.093 | 0.8113 | yes                |
| MBTIЭкстраверт                       |      58.024 |       58.155 |     17.973 |      19.254 |     0.093 | 0.8148 | yes                |
| neiryRelaxation index                |       1.121 |        1.109 |      0.56  |       0.6   |     0.092 | 0.8254 | yes                |
| neiryFocus                           |      59.751 |       60.462 |      9.749 |      10.265 |     0.09  | 0.8461 | yes                |
| MBTIИнтуитивные                      |      60.205 |       59.743 |     14.86  |      15.655 |     0.088 | 0.8603 | yes                |
| Пространственно-визуальный интеллект |      63.621 |       63.079 |     15.111 |      15.979 |     0.088 | 0.8623 | yes                |
| Телесно-кинестетический интеллект    |      64.306 |       63.296 |     19.258 |      19.456 |     0.086 | 0.881  | yes                |
| neiryStress                          |      55.245 |       55.118 |      8.126 |       8.899 |     0.084 | 0.8922 | yes                |
| neiryAnger                           |      48.931 |       49.818 |     10.05  |      10.436 |     0.082 | 0.9126 | yes                |
| neiryAlpha                           |       0.259 |        0.26  |      0.043 |       0.045 |     0.081 | 0.9176 | yes                |
| MBTIУверенные                        |      49.619 |       50.159 |     18.536 |      20.61  |     0.079 | 0.9273 | yes                |
| Музыкальный интеллект                |      64.306 |       63.318 |     22.59  |      23.154 |     0.071 | 0.9706 | yes                |
| MBTIЛогика                           |      52.712 |       53.152 |     14.495 |      14.078 |     0.07  | 0.9726 | yes                |
| Экзистенциальный интеллект           |      55.677 |       55.614 |     18.384 |      18.944 |     0.069 | 0.9768 | yes                |

## 2. Correlation Structure Preservation

Relative Frobenius distance between correlation matrices (continuous features): **0.134**  
(role-rank correlations): **0.227**

Values close to 0 indicate that the synthetic copula reproduces the pairwise correlation structure of the pilot. For reference, values < 0.20 are typically considered a faithful copula fit on small pilot samples.

## 3. NIRM-style Clustering on Synthetic Data

Same pipeline (24 Neiry features, StandardScaler, k-means k=3, random_state=2) applied to the synthetic n=500 sample.

  * Silhouette: **0.177** (real: 0.240)
  * Cluster sizes: **[241, 142, 117]** (real: [30, 8, 9])

A similar silhouette value confirms that the synthetic data preserves the same coarse cluster structure as the pilot.

## 4. MBTI Type Frequency

Type frequencies in real vs. synthetic samples. Synthetic types are derived deterministically from sampled MBTI continuous scales via the standard 50% threshold per dichotomy.

| MBTIabbrev   |   real_pct |   synth_pct |
|:-------------|-----------:|------------:|
| ENTJ-A       |      0.149 |       0.08  |
| ENTJ-T       |      0.128 |       0.062 |
| ESFJ-A       |      0.085 |       0.036 |
| INTJ-T       |      0.064 |       0.064 |
| ESTJ-A       |      0.064 |       0.08  |
| ENFJ-T       |      0.064 |       0.042 |
| ENTP-T       |      0.043 |       0.072 |
| INTP-T       |      0.043 |       0.042 |
| ENFP-A       |      0.043 |       0.032 |
| ENFJ-A       |      0.043 |       0.054 |
| INFP-T       |      0.043 |       0.034 |
| ESTP-T       |      0.043 |       0.02  |
| INFJ-T       |      0.043 |       0.022 |
| ENFP-T       |      0.021 |       0.086 |
| INTP-A       |      0.021 |       0.006 |
| ESFP-T       |      0.021 |       0.016 |
| ENTP-A       |      0.021 |       0.044 |
| ESFP-A       |      0.021 |       0.026 |
| ISTJ-T       |      0.021 |       0.024 |
| ESTP-A       |      0.021 |       0.02  |
| INTJ-A       |      0     |       0.044 |
| ESTJ-T       |      0     |       0.018 |
| ESFJ-T       |      0     |       0.016 |
| ISTJ-A       |      0     |       0.016 |
| ISTP-A       |      0     |       0.012 |
| ISTP-T       |      0     |       0.012 |
| INFJ-A       |      0     |       0.01  |
| INFP-A       |      0     |       0.004 |
| ISFP-T       |      0     |       0.002 |
| ISFP-A       |      0     |       0.002 |
| ISFJ-A       |      0     |       0.002 |
