# Stage 3 Summary - Profession Knowledge Base + Hybrid Matcher

This stage delivers the **knowledge base of careers** and the **hybrid matcher**
that converts a user profile into a ranked list of profession recommendations.

## 1. Profession knowledge base

`data/professions.yaml` defines **64 professions** across **9 categories**:

| Category | Count | Example |
|---|---:|---|
| it | 8 | Инженер-программист, Data Scientist, ML Engineer, ... |
| engineering | 8 | Инженер-механик, аэрокосмической отрасли, ... |
| science | 7 | Математик, Физик, Биолог, Статистик, ... |
| healthcare | 7 | Врач, Хирург, Психолог, ... |
| education | 6 | Школьный учитель, Преподаватель вуза, ... |
| arts | 8 | Графический дизайнер, UX-дизайнер, Музыкант, ... |
| business | 8 | Project / Product Manager, Бизнес-аналитик, ... |
| social | 6 | Социальный работник, Журналист, Юрист, ... |
| trades | 6 | Пилот, Шеф-повар, Спортсмен, ... |

**Schema per profession** (validated at load time):

```yaml
- id: data_scientist
  name_ru: "Data Scientist"
  name_en: "Data Scientist"
  category: it
  description_ru: "Анализ больших данных, ..."
  cluster_preference: mobilized       # balanced | mobilized | depleted | any
  gardner_ideal:                       # only intelligences that matter
    Логико-математический интеллект: 92
    Лингвистический интеллект: 65
    Внутриличностный интеллект: 70
  mbti_preference:                     # signed [-100..+100]
    extraversion: -10                  # mild introversion
    intuition: 40                      # mild N
    thinking: 60                       # strong T
    judging: 20                        # mild J
  top_roles:
    - Analyst
    - Problem Solver
    - Strategist
    - Thinker
    - Philomath
```

**Trait estimates** are grounded in three sources: Holland's RIASEC theory,
Gardner's Multiple Intelligences mapping, and consensus MBTI-career profiles
(Tieger et al., 16Personalities-style summaries). They are reasonable
starting points for the prototype, not clinically validated norms - the
methodology section of the dissertation should state this explicitly.

The KB is fully extensible: adding a new profession is a pure-data change
(append a YAML block, validation runs at load).

## 2. Hybrid matcher

`core/matcher.py` exposes the `HybridMatcher` class. It combines four
sources of evidence into a single 0..100 score per profession:

| Component | Computation | Default weight |
|---|---|---:|
| **Gardner fit** | mean alignment between user's intelligences and the profession's `gardner_ideal`; alignment_i = 100 - \|user - ideal\|, clipped | 30% |
| **MBTI fit** | mean alignment over the dimensions where the profession has a non-zero `mbti_preference`; user values are mapped to signed [-100, +100] | 20% |
| **Cluster fit** | 100 if user's cognitive cluster matches `cluster_preference`, 70 if profession says "any", 40 otherwise | 10% |
| **Role fit** | mean(`(21 - predicted_rank)/20 * 100`) over the profession's `top_roles`, using the Stage 2 Random Forest as the role predictor | 40% |

Weights default to (0.30, 0.20, 0.10, 0.40) but are exposed as a
`WeightConfig` so the dissertation can run sensitivity analyses. Roles get
the heaviest weight because the Stage 2 SHAP analysis showed psychometrics
already drive role rankings - so role fit acts as a learned compression of
the psychometric signal.

The matcher returns a `ProfessionMatch` for each candidate, preserving the
**per-component breakdown** plus the matched intelligences/MBTI dims/roles.
This breakdown is what the LLM explainer (Stage 5) will verbalize.

## 3. Pilot run results (n=47)

```
weights: {gardner: 0.30, mbti: 0.20, cluster: 0.10, roles: 0.40}
n_professions_in_kb: 64
unique professions at top-1:    24 / 64
unique professions in top-10:   54 / 64
mean top-1 score:               85.0   (std 3.8, range 76.6 .. 91.6)
mean top-10 score:              81.8
```

**Top-1 category distribution** (which categories win the #1 slot):

| Category | # respondents at top-1 |
|---|---:|
| it | 14 |
| science | 8 |
| engineering | 6 |
| trades | 6 |
| arts | 4 |
| business | 4 |
| education | 3 |
| healthcare | 1 |
| social | 1 |

The IT/engineering skew is consistent with the pilot composition (students of
"7M06103 Machine Learning and Data Analysis"). The fact that arts, education
and trades all reach the top-1 spot for some respondents shows the matcher
is **discriminating across users**, not collapsing onto one category.

**Most recommended at top-1:**

| Profession | Times at #1 |
|---|---:|
| Инженер по тестированию | 5 |
| UX-дизайнер | 3 |
| Статистик | 3 |
| Инженер-программист | 3 |
| Frontend разработчик | 3 |
| Маркетинг-менеджер | 3 |
| Автомеханик | 3 |
| Карьерный консультант | 3 |

No single profession dominates - the most popular gets only 5/47 = 11% of
the top-1 slots. With 24 distinct top-1 picks across 47 users we have a
**diversity ratio of 0.51**, which is healthy.

Detailed examples for 5 illustrative respondents (one per cognitive cluster
plus two random) are in [`reports/matcher_examples.md`](matcher_examples.md).

## 4. Sanity check on individual recommendations

Spot-checking the examples against expectations:

| User | MBTI | Cluster | Top-1 | Plausible? |
|---|---|---|---|---|
| R-18 | ISTJ-T | balanced | Инженер по тестированию (91.6) | ✅ ISTJ + meticulous = QA fits |
| R-04 | INTP-A | mobilized | Инженер аэрокосмической отрасли (91.4) | ✅ INTP + math + spatial = engineering fits |
| R-38 | ENTJ-A | depleted | Спец. по кибербезопасности (84.6) | ✅ analytical leadership |
| R-28 | ESTP-T | balanced | Геолог (83.4) | ✅ active naturalistic profile |
| R-26 | INTP-T | mobilized | Математик (90.8) | ✅ textbook fit |

The cluster_preference penalty correctly drops scores when the user is
"depleted" but the profession requires "mobilized" (down to 40 from 100),
and this propagates to total - R-38's top-1 score (84.6) is visibly
lower than R-04's (91.4) for analogous IT/engineering picks because
of the cluster mismatch.

## 5. Where the design is honest

* **Gardner alignment is generous.** With many intelligences defaulting
  to 50 and ideals between 60 and 90, alignment scores naturally land
  in the 70-90 range. This inflates absolute totals (~85 mean) but does
  not affect *relative* ranking, which is what matters for recommendation.
  Reported scores should be interpreted as "fit percentile" not "fit
  probability".

* **64 professions is a prototype scope.** The schema scales to hundreds
  with no architectural change; the dissertation should frame this as
  "demonstration KB" with extension being a maintenance task, not a
  research one.

* **No ground truth for matcher quality.** Unlike Stage 2 (which has Neiry
  role rankings as targets), there is no "correct profession" label per
  user. Stage 4 of the dissertation can address this with expert review
  of N respondents (career counselor agreement) or self-report follow-up.

## 6. Artifacts produced

```
core/professions.py                            schema + loader + validator
core/matcher.py                                HybridMatcher + scorers + weights
data/professions.yaml                          64-profession knowledge base
data/processed/recommendations.csv             top-10 per respondent (47*10 = 470 rows)
reports/matcher_summary.json                   global stats
reports/matcher_examples.md                    5 illustrative cases
reports/figures/07a_top_categories.png         category distribution at top-1 / top-10
reports/figures/07b_score_distribution.png     histogram of best-match scores
reports/figures/07c_breakdown_by_cluster.png   per-component scores by user cluster
```

## 7. Next stage

Stage 4 will add the **LLM explainer** (Layer 5 of the architecture).
For each top-N profession the explainer will turn the structured breakdown
into a 3-5 sentence natural-language explanation in Russian, citing the
specific intelligences / MBTI traits / roles that drove the score. We use a
locally hosted Llama 3.1 8B (or Qwen 2.5 7B) via Ollama - free, offline,
demonstrable on the defense day without an internet connection.
