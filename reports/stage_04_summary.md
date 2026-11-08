# Stage 4 Summary - LLM Natural Language Explainer (Layer 5)

This stage adds the explanation layer of the system: every recommendation
returned by the matcher (Stage 3) gets a 3-5 sentence natural-language
justification that cites the specific intelligences, MBTI traits, cognitive
cluster and roles that drove the score.

## 1. Two-backend architecture

The explainer (`core/llm_explainer.py`) ships with two backends and
auto-selects the best one available:

| Backend | When used | Output style |
|---|---|---|
| `ollama` | local Ollama server is reachable on `http://localhost:11434` | conversational, varied phrasing, cites context |
| `template` | Ollama unreachable (or `backend="template"` is forced) | deterministic, formal, structurally identical across runs |

The `auto` resolver probes Ollama via `GET /api/tags` with a 3-second
timeout. If that probe fails (or any subsequent generation request raises),
the explainer transparently falls back to the template - the rest of the
system never sees an error.

This dual design is deliberate:

* The **template** is fully reproducible and works offline, so the
  dissertation can be defended even if Ollama is down on the day. It also
  serves as a **baseline reference** in the methodology section: any
  improvement contributed by the LLM is visible against this baseline.

* The **LLM backend** (default model: `qwen2.5:7b-instruct`) makes the
  explanations more natural and personalized while staying on-device, free
  and explainable.

## 2. The Russian prompt

The prompt is built on a fixed system message that constrains the model to:

1. Speak as a career counselor.
2. Write 3-5 sentences in Russian.
3. Cite *only* facts present in the structured input - no hallucinated
   traits.
4. Avoid filler ("you are unique"), headers, bullet lists.

Following the system message, the prompt provides:

* a compact user block (MBTI type, cognitive cluster, top-3 Gardner
  intelligences),
* a structured profession block listing the matched intelligences with both
  user and ideal scores, the matched MBTI dimensions with signed values,
  the matched roles with predicted ranks, and the four component scores.

This deterministic structure lets the LLM ground every claim it makes in
explicit numbers, which is the main lever against hallucination on a small
local model.

## 3. Status of the current run

```
backend resolved to: template
n_respondents:       5
n_explanations:      25
total time:          ~0.0 s (template is essentially free)
```

The Ollama backend is **not yet active** because Ollama is not installed on
the development machine. Installation is a one-time manual step requiring
the user to run a Windows installer; the procedure is documented in
[`OLLAMA_SETUP.md`](../OLLAMA_SETUP.md). After that step the same script
re-runs in 5-25 seconds per explanation depending on model choice and
produces noticeably more natural prose.

## 4. Sample template output

For respondent **R-01** (`INFP-T`, cluster *mobilized*),
top-1 recommendation **Физик** (score 91.3):

> Профессия «Физик» получила итоговую оценку соответствия 91 из 100.
> Ваш когнитивный профиль соответствует требованиям профессии. Ваш
> логико-математический интеллект (91 из 100) близок к идеальному уровню
> для этой профессии (92). По типу MBTI совпадают значимые черты:
> интроверсия, интуиция. Прогнозируемый ролевой профиль выделяет у вас
> сильные стороны для этой профессии: Thinker, Analyst, Philomath.
> Это рекомендация-ориентир; окончательный выбор стоит делать с учётом
> личных предпочтений и опыта.

Notable properties:

* Names the **profession** explicitly.
* Cites a **concrete intelligence with both user and ideal numbers**.
* Names the **specific side** of the MBTI dichotomy that matches
  ("интроверсия" not just "extraversion") - this is the bug fix made
  during this stage.
* Lists the **specific top-ranked roles** that drove the role score.
* Closes with a calibration disclaimer.

The full set of 25 template explanations is in
[`reports/explanations.md`](explanations.md).

## 5. What the LLM upgrade adds

When Ollama is wired in, expected improvements (to be confirmed empirically
once installed):

* **Variation across professions** - same user gets distinct phrasings for
  each top-N item rather than five copies of the same template.
* **Synthesis of multiple traits** - "сочетание сильной логики и интуиции
  делает вас способным к фундаментальной науке" instead of separately
  listing the dichotomies.
* **Brief contextualization** - mentions of typical day-to-day work in
  the profession, drawn from the model's general knowledge but anchored in
  the user's profile.

The dissertation can present a side-by-side comparison: same user, same
top-1 profession, template vs. LLM. This is methodologically clean because
both run on identical structured inputs.

## 6. Honest limitations

* The local LLM may occasionally drift toward generic career-advice cliches
  despite the prompt; the template is immune to this.
* Russian quality of small open-weights models is good but uneven; a brief
  manual review of generated text is recommended before using it in final
  user-facing reports.
* All numbers in the explanations come from the matcher's structured
  output. The LLM should *only* paraphrase them. Any claim not present in
  the input block is a hallucination that should be flagged in evaluation.

## 7. Artifacts produced

```
core/llm_explainer.py                 explainer + Ollama client + template
scripts/08_generate_explanations.py   batch generator over sample respondents
reports/explanations.md               25 explanations across 5 respondents
reports/explanations_meta.json        backend used, timings, sample sizes
OLLAMA_SETUP.md                       one-time installation guide
```

## 8. Next stage

Stage 5 builds the **Streamlit UI** (Layer 6 of the architecture). The UI
will:

* accept a user profile via either CSV/XLSX upload (Neiry export format) or
  inline editing of the 38 features,
* run the full pipeline (cluster -> roles -> matcher -> explainer),
* show top-N professions with an interactive breakdown chart and the LLM
  explanation,
* offer PDF export of a personal recommendation report.

After Stage 5 the system is end-to-end and ready for the defense
demonstration.
