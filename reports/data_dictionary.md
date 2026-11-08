# Data Dictionary - Pilot Dataset (n=47)

Source: `data/raw/pilot_47x65_anon.csv`  
Rows: **47**  
Columns: **65**  
Missing values total: **0**

## Identifier

| feature   | dtype   |   n_unique |   n_missing | min   | p25   | median   | mean   | p75   | max   | std   | skew   |
|:----------|:--------|-----------:|------------:|:------|:------|:---------|:-------|:------|:------|:------|:-------|
| ФИО       | object  |         47 |           0 | -     | -     | -        | -      | -     | -     | -     | -      |

## 1. Gardner's Multiple Intelligences (9 features)

Continuous percentile scores 0..100 from a Gardner self-report battery.

| feature                              | dtype   |   n_unique |   n_missing |   min |   p25 |   median |    mean |   p75 |   max |     std |    skew |
|:-------------------------------------|:--------|-----------:|------------:|------:|------:|---------:|--------:|------:|------:|--------:|--------:|
| Натуралистический интеллект          | float64 |         42 |           0 |   0   |  48.6 |     57.4 | 57.7489 |  71.4 |  85.8 | 18.4651 | -0.8757 |
| Внутриличностный интеллект           | float64 |         43 |           0 |  19.8 |  54.2 |     63.8 | 62.7872 |  73.8 |  89.4 | 15.5322 | -0.543  |
| Логико-математический интеллект      | float64 |         45 |           0 |  13.6 |  50.9 |     69.4 | 63.8255 |  77.6 | 100   | 21.9952 | -0.5385 |
| Лингвистический интеллект            | float64 |         47 |           0 |  12.8 |  43.3 |     51.4 | 53.1404 |  61.6 |  90.4 | 16.1901 |  0.1464 |
| Телесно-кинестетический интеллект    | float64 |         42 |           0 |  14.4 |  53.5 |     68.6 | 64.3064 |  79.2 |  96.4 | 19.2578 | -0.699  |
| Пространственно-визуальный интеллект | float64 |         41 |           0 |  27   |  55.5 |     63.6 | 63.6213 |  74.3 |  94.8 | 15.1111 | -0.3176 |
| Музыкальный интеллект                | float64 |         45 |           0 |  20.8 |  46   |     61   | 64.3064 |  87.5 | 100   | 22.5905 |  0.0132 |
| Экзистенциальный интеллект           | float64 |         45 |           0 |  10   |  41.7 |     55.2 | 55.6766 |  68.1 |  90   | 18.3837 | -0.2888 |
| Межличностный интеллект              | float64 |         43 |           0 |  24.8 |  53.3 |     66   | 63.5787 |  77.5 |  92.8 | 16.5157 | -0.4472 |

## 2. MBTI - Type and Continuous Scales (1 + 10 features)

Categorical type: `MBTIabbrev` (unique values: 20).  
Each dichotomy is encoded as two complementary percentile scales summing to 100. For modeling we use one side per dichotomy (see `MBTI_INDEPENDENT_SCALES`).

**Type frequency:**

| MBTIabbrev   |   count |   pct |
|:-------------|--------:|------:|
| ENTJ-A       |       7 |  14.9 |
| ENTJ-T       |       6 |  12.8 |
| ESFJ-A       |       4 |   8.5 |
| INTJ-T       |       3 |   6.4 |
| ESTJ-A       |       3 |   6.4 |
| ENFJ-T       |       3 |   6.4 |
| ENTP-T       |       2 |   4.3 |
| INTP-T       |       2 |   4.3 |
| ENFP-A       |       2 |   4.3 |
| ENFJ-A       |       2 |   4.3 |
| INFP-T       |       2 |   4.3 |
| ESTP-T       |       2 |   4.3 |
| INFJ-T       |       2 |   4.3 |
| ESTP-A       |       1 |   2.1 |
| ISTJ-T       |       1 |   2.1 |
| ENTP-A       |       1 |   2.1 |
| ESFP-A       |       1 |   2.1 |
| ENFP-T       |       1 |   2.1 |
| ESFP-T       |       1 |   2.1 |
| INTP-A       |       1 |   2.1 |

**Continuous MBTI scales:**

| feature          | dtype   |   n_unique |   n_missing |   min |    p25 |   median |    mean |    p75 |   max |     std |    skew |
|:-----------------|:--------|-----------:|------------:|------:|-------:|---------:|--------:|-------:|------:|--------:|--------:|
| MBTIИнтроверт    | float64 |         41 |           0 |  2.86 | 31.97  |    40.28 | 41.9762 | 49.305 | 84.65 | 17.9727 |  0.3913 |
| MBTIЭкстраверт   | float64 |         41 |           0 | 15.35 | 50.695 |    59.72 | 58.0238 | 68.03  | 97.14 | 17.9727 | -0.3913 |
| MBTIРеалистичные | float64 |         40 |           0 | 11.17 | 30.595 |    41.68 | 39.7953 | 50.015 | 76.35 | 14.8599 | -0.0321 |
| MBTIИнтуитивные  | float64 |         40 |           0 | 23.65 | 49.985 |    58.32 | 60.2047 | 69.405 | 88.83 | 14.8599 |  0.0321 |
| MBTIПринципы     | float64 |         42 |           0 | 11.18 | 38.905 |    47.21 | 47.2881 | 55.545 | 77.74 | 14.4954 |  0.0826 |
| MBTIЛогика       | float64 |         42 |           0 | 22.26 | 44.455 |    52.79 | 52.7119 | 61.095 | 88.82 | 14.4954 | -0.0826 |
| MBTIИщущие       | float64 |         40 |           0 | 12.57 | 38.215 |    45.85 | 48.3189 | 61.09  | 86.05 | 17.4132 |  0.2735 |
| MBTIПланирующие  | float64 |         40 |           0 | 13.95 | 38.91  |    54.15 | 51.6811 | 61.785 | 87.43 | 17.4132 | -0.2735 |
| MBTIОсторожные   | float64 |         45 |           0 |  7.03 | 38.915 |    52.77 | 50.3813 | 62.48  | 94.36 | 18.5364 | -0.2441 |
| MBTIУверенные    | float64 |         45 |           0 |  5.64 | 37.52  |    47.23 | 49.6187 | 61.085 | 92.97 | 18.5364 |  0.2441 |

## 3. Neiry Role Rankings (20 features)

Per-respondent ranking 1..20 across 20 archetypal professional roles. Lower rank = stronger affinity. These are produced by Neiry's own proprietary model and serve as a partial ground-truth target for the supervised layer of the system.

| feature        | dtype   |   n_unique |   n_missing |   min |   p25 |   median |    mean |   p75 |   max |    std |    skew |
|:---------------|:--------|-----------:|------------:|------:|------:|---------:|--------:|------:|------:|-------:|--------:|
| Focus Expert   | int64   |         18 |           0 |     1 |   4   |       11 |  9.7872 |  14   |    20 | 5.7216 |  0.0244 |
| Optimist       | int64   |         18 |           0 |     1 |   5.5 |       10 |  9.766  |  13.5 |    19 | 4.6775 |  0.052  |
| Brainstormer   | int64   |         18 |           0 |     2 |   7   |       12 | 11.5957 |  17   |    20 | 5.6247 | -0.2048 |
| Catalyst       | int64   |         14 |           0 |     1 |   2   |        5 |  5.9787 |   9.5 |    16 | 4.3564 |  0.6049 |
| Analyst        | int64   |         18 |           0 |     1 |   5   |        9 | 10.0213 |  15.5 |    20 | 5.7991 |  0.1241 |
| Winner         | int64   |         17 |           0 |     1 |   7.5 |       12 | 11.4894 |  16.5 |    20 | 6.0032 | -0.3033 |
| Storyteller    | int64   |         19 |           0 |     1 |   6   |       12 | 11.2766 |  16   |    20 | 5.9808 | -0.122  |
| Problem Solver | int64   |         14 |           0 |     1 |   3   |        5 |  6.0426 |   8.5 |    19 | 4.2934 |  1.0575 |
| Strategist     | int64   |         15 |           0 |     1 |   3   |        6 |  7.4681 |  12   |    18 | 5.2662 |  0.4704 |
| Thinker        | int64   |         17 |           0 |     1 |   4   |        7 |  8.5957 |  13   |    19 | 5.543  |  0.372  |
| Believer       | int64   |         19 |           0 |     1 |   7.5 |       13 | 12.0851 |  16.5 |    20 | 5.4726 | -0.4646 |
| Time Keeper    | int64   |         18 |           0 |     1 |   5   |       12 | 11.0638 |  18   |    20 | 6.6575 | -0.0589 |
| Peace Keeper   | int64   |         16 |           0 |     2 |  11.5 |       16 | 14.7021 |  19   |    20 | 5.0901 | -1.0357 |
| Deliverer      | int64   |         17 |           0 |     3 |   7   |       10 | 10.2979 |  14   |    19 | 4.759  |  0.1352 |
| Commander      | int64   |         19 |           0 |     1 |   9   |       12 | 11.3617 |  14.5 |    20 | 4.5703 | -0.4385 |
| Philomath      | int64   |         19 |           0 |     1 |   5.5 |        8 |  8.8723 |  11.5 |    20 | 5.2279 |  0.6514 |
| Chameleon      | int64   |         17 |           0 |     1 |  11   |       16 | 14.4255 |  19   |    20 | 5.0851 | -0.8147 |
| Coach          | int64   |         19 |           0 |     1 |   8.5 |       15 | 12.8511 |  18   |    20 | 5.842  | -0.5338 |
| Self-Believer  | int64   |         18 |           0 |     1 |   7.5 |       10 | 11.0426 |  15   |    20 | 5.2169 | -0.1625 |
| Empathizer     | int64   |         17 |           0 |     1 |   7.5 |       11 | 11.2766 |  16   |    20 | 5.3353 | -0.1158 |

## 4. Neiry EEG Metrics (24 features)

All metrics derived by the Neiry headset firmware from a 5-minute resting-state recording with dry electrodes.  
Naming convention: `Baseline ...` = individual norm computed from a calibration window; the same metric without the prefix = current (actual) value during the test session.

| feature                           | dtype   |   n_unique |   n_missing |     min |     p25 |   median |    mean |     p75 |      max |     std |    skew |
|:----------------------------------|:--------|-----------:|------------:|--------:|--------:|---------:|--------:|--------:|---------:|--------:|--------:|
| neiryIAPF                         | float64 |         36 |           0 |  7.2    |  9.65   |  10.2    | 10.1447 | 10.6    |  12.2    |  1.0705 | -0.3824 |
| neiryIAF                          | float64 |         47 |           0 |  8.9639 |  9.6738 |   9.9359 |  9.8982 | 10.0892 |  11.0854 |  0.4513 |  0.3032 |
| neiryBaseline Fatigue score       | float64 |         47 |           0 |  0.1791 |  0.8889 |   1.5412 |  1.9273 |  2.5629 |   9.4922 |  1.6408 |  2.5094 |
| neiryFatigue score                | float64 |         47 |           0 |  0.638  |  1.5887 |   2.1889 |  7.1382 |  3.2012 | 216.155  | 31.1911 |  6.8282 |
| neiryBaseline Alpha Gravity       | float64 |         47 |           0 |  0.0758 |  0.4023 |   0.6603 |  1.0959 |  1.0497 |  13.7347 |  1.9828 |  5.8835 |
| neiryAlpha Gravity                | float64 |         47 |           0 |  0.1168 |  0.4069 |   0.6836 |  1.1552 |  0.9739 |  16.1547 |  2.3264 |  6.1008 |
| neiryBaseline Concentration index | float64 |         47 |           0 |  0.4537 |  0.9767 |   1.4504 |  1.8842 |  2.3673 |   8.1319 |  1.3966 |  2.2754 |
| neiryConcentration index          | float64 |         47 |           0 |  0.3723 |  0.9845 |   1.3363 |  1.5542 |  1.8674 |   4.5531 |  0.9204 |  1.7111 |
| neiryBaseline Relaxation index    | float64 |         47 |           0 |  0.123  |  0.4229 |   0.6895 |  0.7976 |  1.0255 |   2.2043 |  0.5048 |  1.1754 |
| neiryRelaxation index             | float64 |         47 |           0 |  0.3203 |  0.7967 |   1.0152 |  1.1214 |  1.2611 |   3.2103 |  0.5599 |  1.4775 |
| neiryBaseline Reverse Fatigue     | float64 |         47 |           0 |  0.1053 |  0.3902 |   0.6488 |  0.9524 |  1.1252 |   5.5833 |  0.9256 |  3.1115 |
| neiryReverse Fatigue              | float64 |         47 |           0 |  0.1886 |  0.4467 |   0.6296 |  0.7796 |  0.8998 |   2.5292 |  0.5449 |  1.8022 |
| neiryAccumulated Fatigue          | float64 |         47 |           0 |  0.0024 |  0.6692 |   1.3419 |  1.6834 |  2.4495 |   6.0968 |  1.471  |  1.2402 |
| neiryTheta                        | float64 |         47 |           0 |  0.1278 |  0.2372 |   0.2717 |  0.2743 |  0.3141 |   0.452  |  0.0748 |  0.21   |
| neiryAlpha                        | float64 |         47 |           0 |  0.179  |  0.2347 |   0.259  |  0.2592 |  0.2876 |   0.4034 |  0.0432 |  0.7078 |
| neiryBeta                         | float64 |         47 |           0 |  0.1264 |  0.2476 |   0.3156 |  0.3188 |  0.3908 |   0.5903 |  0.113  |  0.3171 |
| neiryTheta peak frequency         | float64 |         47 |           0 |  4.4554 |  4.8986 |   5.0212 |  5.0031 |  5.1476 |   5.5788 |  0.2133 | -0.3333 |
| neiryAlpha peak frequency         | float64 |         47 |           0 |  7.165  |  7.7926 |   8.3697 |  8.4176 |  8.747  |  10.3261 |  0.7782 |  0.6875 |
| neiryBeta peak frequency          | float64 |         47 |           0 | 16.0764 | 18.1859 |  18.9007 | 19.2104 | 20.0575 |  23.482  |  1.616  |  0.4991 |
| neiryChill                        | float64 |         47 |           0 | 29.2339 | 42.391  |  47.3249 | 47.3307 | 53.4143 |  62.2766 |  8.4089 | -0.4234 |
| neiryStress                       | float64 |         47 |           0 | 37.6804 | 49.1782 |  55.2452 | 55.2447 | 60.9247 |  73.4764 |  8.1255 |  0.0842 |
| neiryFocus                        | float64 |         47 |           0 | 35.4817 | 52.4898 |  60.3223 | 59.7509 | 66.4922 |  79.7185 |  9.7492 | -0.3648 |
| neiryAnger                        | float64 |         47 |           0 | 28.6763 | 42.1979 |  48.9141 | 48.9308 | 55.8535 |  70.3317 | 10.0499 |  0.0624 |
| neirySelf-control                 | float64 |         47 |           0 | 31.1034 | 46.3525 |  51.6245 | 53.1897 | 60.9262 |  73.7664 |  9.9194 |  0.0786 |

## 5. Outlier Detection (IQR rule, 1.5x)

Features where at least one observation lies beyond Q1-1.5xIQR or Q3+1.5xIQR. The `ratio_max_to_p99` column flags extreme tails.

| feature                              |   n_outliers_iqr |   lower_iqr |   upper_iqr |     min |      max |   ratio_max_to_p99 |
|:-------------------------------------|-----------------:|------------:|------------:|--------:|---------:|-------------------:|
| neiryFatigue score                   |                4 |     -0.83   |      5.62   |  0.638  | 216.155  |               1.79 |
| neiryBaseline Alpha Gravity          |                4 |     -0.5688 |      2.0207 |  0.0758 |  13.7347 |               1.58 |
| neiryAlpha Gravity                   |                4 |     -0.4436 |      1.8244 |  0.1168 |  16.1547 |               1.56 |
| neiryBaseline Reverse Fatigue        |                3 |     -0.7124 |      2.2278 |  0.1053 |   5.5833 |               1.28 |
| neiryBaseline Concentration index    |                2 |     -1.1092 |      4.4533 |  0.4537 |   8.1319 |               1.25 |
| neiryBaseline Fatigue score          |                2 |     -1.6222 |      5.074  |  0.1791 |   9.4922 |               1.23 |
| neiryRelaxation index                |                4 |      0.1    |      1.9578 |  0.3203 |   3.2103 |               1.12 |
| MBTIЛогика                           |                1 |     19.495  |     86.055  | 22.26   |  88.82   |               1.06 |
| neiryAccumulated Fatigue             |                2 |     -2.0013 |      5.12   |  0.0024 |   6.0968 |               1.06 |
| neiryAlpha                           |                1 |      0.1552 |      0.3671 |  0.179  |   0.4034 |               1.05 |
| Пространственно-визуальный интеллект |                1 |     27.3    |    102.5    | 27      |  94.8    |               1.04 |
| MBTIЭкстраверт                       |                3 |     24.6925 |     94.0325 | 15.35   |  97.14   |               1.04 |
| neiryConcentration index             |                3 |     -0.3398 |      3.1917 |  0.3723 |   4.5531 |               1.04 |
| neiryTheta                           |                1 |      0.122  |      0.4294 |  0.1278 |   0.452  |               1.03 |
| MBTIИнтроверт                        |                3 |      5.9675 |     75.3075 |  2.86   |  84.65   |               1.02 |
| neiryTheta peak frequency            |                3 |      4.525  |      5.5212 |  4.4554 |   5.5788 |               1.02 |
| neiryReverse Fatigue                 |                4 |     -0.233  |      1.5795 |  0.1886 |   2.5292 |               1.01 |
| neiryAlpha peak frequency            |                1 |      6.3611 |     10.1785 |  7.165  |  10.3261 |               1.01 |
| neiryBeta peak frequency             |                2 |     15.3787 |     22.8647 | 16.0764 |  23.482  |               1.01 |
| neiryIAF                             |                3 |      9.0506 |     10.7123 |  8.9639 |  11.0854 |               1.01 |
| Лингвистический интеллект            |                2 |     15.85   |     89.05   | 12.8    |  90.4    |               1.01 |
| neiryBaseline Relaxation index       |                2 |     -0.4811 |      1.9295 |  0.123  |   2.2043 |               1    |
| Внутриличностный интеллект           |                1 |     24.8    |    103.2    | 19.8    |  89.4    |               1    |
| neiryIAPF                            |                6 |      8.225  |     12.025  |  7.2    |  12.2    |               1    |
| MBTIПринципы                         |                1 |     13.945  |     80.505  | 11.18   |  77.74   |               1    |
| Телесно-кинестетический интеллект    |                1 |     14.95   |    117.75   | 14.4    |  96.4    |               1    |
| Натуралистический интеллект          |                1 |     14.4    |    105.6    |  0      |  85.8    |               1    |

> **Note.** The most extreme tail belongs to `neiryFatigue score` (max=216.1546, p99-ratio=1.79). This matches the observation in the thesis (тезис) about a single subject with max=216.15 in fatigue. Recommended handling: winsorize at p99 or apply log1p before downstream modeling.
