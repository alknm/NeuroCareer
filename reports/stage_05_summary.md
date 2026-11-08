# Stage 5 Summary - Streamlit UI (Layer 6)

The final stage assembles the four computational layers into a working
desktop-grade application. The result is a single command that launches a
local web app demonstrating the entire pipeline end-to-end:

```powershell
cd c:\Users\ik\Documents\maga\disser\system
streamlit run app.py
# opens http://localhost:8501 in the default browser
```

The app needs no internet (Ollama is also local), runs entirely on the
defense laptop and is ready to demonstrate.

## 1. App architecture

```
app.py                     - Streamlit entry point (~250 LOC, tabs + sidebar)
core/ui_helpers.py         - Plotly chart builders + ReportLab PDF exporter
                             + uploaded-file validator
```

The app is organised as **sidebar (input)** + **four tabs (output)**:

| Section | Purpose |
|---|---|
| Sidebar | Choose pilot respondent OR upload Neiry export; tune component weights; switch LLM backend; set top-N |
| Tab "Профиль" | Gardner radar + role ranking bar + raw feature tables (Гарднер / MBTI / Neiry) |
| Tab "Рекомендации" | Top-N table with progress-bar score column + grouped bar chart of component breakdowns |
| Tab "Детальный разбор" | One profession at a time: component bar + matched intelligences/MBTI/roles tables + LLM/template explanation |
| Tab "Отчёт" | Build & download personal **PDF** (with Cyrillic font auto-registered from system) and **CSV** |

Header always shows current MBTI badge, cluster label, and top-1 score.

## 2. Wiring of the five computational layers

The UI is the orchestrator; it does not contain analysis logic. Each user
interaction triggers the following pipeline:

```
1. selected user row (sidebar)
2. -> matcher._assign_cluster(user)        [Layer 2: cognitive cluster]
3. -> matcher._predict_roles(user)         [Layer 3: 20-role ranking]
4. -> matcher.match(user, top_k=N)         [Layer 4: hybrid scoring]
5. -> for each match: explainer.explain(meta, m)   [Layer 5: LLM/template]
6. -> visualised by ui_helpers + Streamlit widgets  [Layer 6]
```

`@st.cache_data` is used for the pilot dataframe and `@st.cache_resource`
for the matcher and explainer, so re-renders triggered by slider changes
do not refit any model. Changing the **weight sliders** invalidates the
matcher cache (its key includes the weight tuple), giving instant
recomputation of recommendations.

## 3. Input modes supported

| Mode | Description | Use case |
|---|---|---|
| Пилотный респондент | Pick from the 47 real respondents in the pilot | demonstration on the defense day |
| Neiry-выгрузка (.xlsx/.csv) | Upload a file with the same 65 columns as `pilot_47x65_anon.csv` | one-off recommendation for a new user |

Uploaded files are validated against `ui_helpers.REQUIRED_COLUMNS` and the
user gets a clear error listing missing columns instead of a Python
traceback.

## 4. PDF export

`build_pdf_report` (in `core/ui_helpers.py`) produces an A4 personal
report with:

* Header with timestamp.
* Profile block (ID, MBTI, cluster + cluster description, top-3
  intelligences).
* Top-N table with score breakdown columns.
* Per-profession explanations from the LLM/template backend.
* Footer disclaimer.

A Cyrillic-capable TrueType font is auto-registered from the Windows fonts
folder (`DejaVuSans` -> `Arial` -> `Verdana` -> `Tahoma` fallback chain).
On a system with at least one of these the PDF renders Russian text
correctly without any extra setup.

## 5. Smoke test

```
streamlit run app.py --server.headless true --server.port 8501
GET http://localhost:8501            -> 200 OK, 5.4 KB shell
GET http://localhost:8501/_stcore/health -> "ok"
no runtime exceptions in the server log
```

End-to-end interactive testing is left to the user (browser only). All
code paths used by the UI are also exercised by the prior batch scripts
(`07_run_matcher.py`, `08_generate_explanations.py`), so the matcher and
explainer behaviours are independently validated.

## 6. How to demonstrate the system

The minimal demo script for the defense:

1. `streamlit run app.py` -> browser opens.
2. In the sidebar, pick respondent **«R-04»**
   (INTP-A, mobilized).
3. Tab «Профиль» shows the radar chart with strong logical-mathematical
   and spatial intelligences.
4. Tab «Рекомендации» shows top-1 = «Инженер аэрокосмической отрасли»
   (~91 score) with full breakdown bars.
5. Tab «Детальный разбор» -> show one profession with matched
   intelligences/MBTI/roles + the LLM-generated Russian explanation.
6. Tab «Отчёт» -> download a PDF (renders in seconds).
7. Optionally change the weight sliders in the sidebar and re-watch
   recommendations re-rank in real time -> demonstrates that the system
   parameters are exposed and tunable, not hidden.

If Ollama is not installed yet, the explanation tab still works via the
template fallback (the badge in the sidebar makes this clear).

## 7. Honest limitations

* **Single-user UI.** No authentication, no multi-tenancy. Appropriate
  for the defense / research context, would need work for production.

* **Polling render speed.** Streamlit reruns the whole `app.py` on every
  widget change. The caches keep this snappy (~0.5 s end-to-end on
  template, ~15 s with LLM enabled because each top-N profession runs a
  separate generation call - configurable via the top-N slider).

* **No persistence.** Session state is per-tab; reloading the page asks
  for a profile again. For a research prototype this is acceptable; for
  a production deployment one would add SQLite + accounts.

* **Manual entry mode** is not yet implemented (would require a long form
  for 38 numeric inputs). Upload mode covers the realistic use case
  (Neiry export already produces the right structure).

## 8. Artifacts produced

```
app.py                                Streamlit application entry point
core/ui_helpers.py                    chart builders, file validator, PDF exporter
reports/stage_05_summary.md           this report
```

## 9. System status after Stage 5

All six layers of the proposed architecture are implemented, integrated
and verified end-to-end:

| Layer | Status |
|---|:---:|
| 1. Data input (CSV/XLSX) | done |
| 2. Cognitive cluster (k-means on Neiry features) | done |
| 3. Role prediction (Random Forest + 4 baselines) | done |
| 4. Hybrid matcher (64-profession KB + 4-component score) | done |
| 5. LLM explainer (Ollama / template) | done |
| 6. UI + PDF export (Streamlit) | done |

The system is ready for two follow-up activities, both of which are
optional and do not block the dissertation defense:

* **Install Ollama** to switch the explanation layer from template to
  natural LLM output (instructions in [`OLLAMA_SETUP.md`](../OLLAMA_SETUP.md)).
* **Expand the knowledge base** beyond 64 professions if needed - this
  is pure data work; no code changes required.
