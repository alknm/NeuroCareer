"""NeuroCareer - Streamlit UI for the hybrid career-guidance system.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.data_loader import (GARDNER_FEATURES, ID_COL, MBTI_INDEPENDENT_SCALES,
                              MBTI_TYPE_COL, NEIRY_FEATURES, ROLE_FEATURES,
                              load_pilot)
from core.i18n import LANG_CODES, LANG_LABELS, cluster_description, t
from core.llm_explainer import LLMExplainer, make_user_meta
from core.matcher import (HybridMatcher, ProfessionMatch, WeightConfig,
                          build_default_matcher)
from core.mini_test import (GARDNER_QUESTIONS, MBTI_QUESTIONS,
                            build_mini_test_profile, likert_labels,
                            mini_test_disclaimer, mini_test_intro)
from core.role_predictor import INPUT_FEATURES
from core.test_descriptions import (SCORING_FORMULA, about_dataset,
                                    about_developer, about_functionality,
                                    about_model, all_tests, scoring_details,
                                    scoring_notes)
from core.ui_helpers import (breakdown_bar, build_pdf_report, gardner_radar,
                             mbti_bars, neiry_bands_pie, neiry_emotions_radar,
                             neiry_indices_bar, role_ranking_bar,
                             respondent_options, single_match_breakdown,
                             validate_uploaded_profile)

PROCESSED = ROOT / "data" / "processed"
ASSETS = ROOT / "app_assets"

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(page_title="NeuroCareer",
                   page_icon=":dna:",
                   layout="wide",
                   initial_sidebar_state="expanded")


# --------------------------------------------------------------------------
# Cached resources
# --------------------------------------------------------------------------

@st.cache_data
def _load_pilot_with_clusters() -> pd.DataFrame:
    pilot = load_pilot()
    canonical = pd.read_csv(PROCESSED / "clusters_canonical.csv", encoding="utf-8")
    return pilot.merge(canonical, on=ID_COL)


@st.cache_resource
def _build_matcher(weights_tuple: tuple[float, float, float, float]) -> HybridMatcher:
    weights = WeightConfig(*weights_tuple)
    return build_default_matcher(weights=weights)


@st.cache_resource
def _build_explainer(backend: str) -> LLMExplainer:
    return LLMExplainer(backend=backend)


def _read_asset(name: str) -> str:
    path = ASSETS / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    logo_svg = _read_asset("logo_compact.svg")
    if logo_svg:
        st.markdown(logo_svg, unsafe_allow_html=True)
    else:
        st.title("NeuroCareer")

    # Language picker — first thing in the sidebar
    lang = st.selectbox(
        label="🌐",
        options=list(LANG_CODES),
        format_func=lambda c: LANG_LABELS[c],
        index=0,
        key="lang",
    )

    st.caption(t("app_subtitle", lang))

    with st.expander(t("about_section", lang), expanded=False):
        st.markdown(f"**{t('about_purpose',  lang)}.** " + about_functionality(lang))
        st.markdown(f"**{t('about_dataset',  lang)}.** " + about_dataset(lang))
        st.markdown(f"**{t('about_model',    lang)}.** " + about_model(lang))
        st.markdown(f"**{t('about_developer',lang)}.** " + about_developer(lang))

    st.subheader(t("source_section", lang))
    mode = st.radio(
        t("source_choose", lang),
        [
            t("source_pilot", lang),
            t("source_upload", lang),
            t("source_mini_test", lang),
        ],
        label_visibility="collapsed",
        help=t("source_hint", lang),
    )

    pilot = _load_pilot_with_clusters()

    selected_row: pd.Series | None = None
    upload_error: str = ""
    upload_df: pd.DataFrame | None = None
    mini_test_meta: dict | None = None

    if mode == t("source_pilot", lang):
        respondent_id = st.selectbox(t("respondent", lang),
                                     respondent_options(pilot))
        selected_row = pilot[pilot[ID_COL] == respondent_id].iloc[0]
    elif mode == t("source_upload", lang):
        up = st.file_uploader(t("upload_label", lang), type=["xlsx", "csv"])
        if up is not None:
            try:
                if up.name.endswith(".csv"):
                    upload_df = pd.read_csv(up, encoding="utf-8")
                else:
                    upload_df = pd.read_excel(up)
            except Exception as exc:
                upload_error = f"{t('upload_error_read', lang)}: {exc}"
        if upload_df is not None and not upload_error:
            ok, missing = validate_uploaded_profile(upload_df)
            if not ok:
                upload_error = (
                    f"{t('upload_error_columns', lang)} "
                    f"({len(missing)}): {', '.join(missing[:5])}"
                    + (" …" if len(missing) > 5 else "")
                )
            else:
                idx = st.selectbox(t("upload_respondent", lang),
                                   upload_df[ID_COL].astype(str).tolist())
                selected_row = upload_df[upload_df[ID_COL].astype(str) == idx].iloc[0]
    else:  # mini-test mode
        result = st.session_state.get("mini_test_result")
        if result is None:
            st.info(t("mini_test_not_done", lang))
        else:
            selected_row = result.profile_row
            mini_test_meta = {"synthetic_eeg": result.synthetic_eeg,
                              "has_role_data": result.has_role_data}
            if st.button(t("mini_test_redo", lang)):
                st.session_state.pop("mini_test_result", None)
                st.rerun()

    st.divider()
    st.subheader(t("weights_section", lang), help=t("weights_hint", lang))
    w_g = st.slider("Gardner",  0.0, 1.0, 0.30, 0.05, help=t("weight_gardner_help", lang))
    w_m = st.slider("MBTI",     0.0, 1.0, 0.20, 0.05, help=t("weight_mbti_help", lang))
    w_c = st.slider("Cluster",  0.0, 1.0, 0.10, 0.05, help=t("weight_cluster_help", lang))
    w_r = st.slider("Roles",    0.0, 1.0, 0.40, 0.05, help=t("weight_roles_help", lang))
    w_total = w_g + w_m + w_c + w_r
    if w_total == 0:
        st.error(t("weights_sum_error", lang))
        st.stop()
    st.caption(f"{t('weights_sum_caption', lang)}: {w_total:.2f} "
               f"({t('weights_normalised', lang)})")

    st.divider()
    st.subheader(t("llm_section", lang))
    backend_choice = st.radio(t("backend_label", lang),
                              ["auto", "ollama", "template"],
                              horizontal=True, help=t("backend_hint", lang))

    explainer = _build_explainer(backend_choice)
    actual_backend = explainer._resolved_backend()
    if actual_backend == "ollama":
        st.success(f"{t('ollama_active', lang)} ({explainer.model})",
                   icon=":material/check:")
    else:
        if backend_choice == "auto":
            st.info(t("ollama_unavailable", lang), icon=":material/info:")
        else:
            st.info(t("template_active", lang), icon=":material/info:")

    st.divider()
    top_n = st.slider(t("top_n_label", lang), 3, 15, 8,
                      help=t("top_n_hint", lang))

    st.divider()
    with st.expander(t("instructions", lang), expanded=False):
        st.markdown(t("instructions_body", lang))


# --------------------------------------------------------------------------
# Mini-test form (shown when user picks the 3rd mode and hasn't finished it yet)
# --------------------------------------------------------------------------
if mode == t("source_mini_test", lang) and selected_row is None:
    st.title(t("mini_test_title", lang))
    st.write(mini_test_intro(lang))
    st.warning(mini_test_disclaimer(lang))

    with st.form("mini_test_form", clear_on_submit=False):
        name = st.text_input(t("mini_test_name_label", lang),
                             value=t("mini_test_guest", lang), max_chars=60)

        st.subheader(t("mini_test_part1", lang, n=len(GARDNER_QUESTIONS)))
        st.caption(t("mini_test_caption", lang))
        gardner_answers: list[int] = []
        for i, q in enumerate(GARDNER_QUESTIONS, start=1):
            ans = st.radio(f"**{i}.** {q.text(lang)}",
                           options=[1, 2, 3, 4, 5], horizontal=True,
                           index=2, key=f"g_{i}",
                           format_func=lambda v: str(v))
            gardner_answers.append(int(ans))

        st.subheader(t("mini_test_part2", lang, n=len(MBTI_QUESTIONS)))
        mbti_answers: list[int] = []
        for i, q in enumerate(MBTI_QUESTIONS, start=1):
            ans = st.radio(f"**{i}.** {q.text(lang)}",
                           options=[1, 2, 3, 4, 5], horizontal=True,
                           index=2, key=f"m_{i}",
                           format_func=lambda v: str(v))
            mbti_answers.append(int(ans))

        st.caption(t("mini_test_scale_caption_prefix", lang)
                   + " · ".join(likert_labels(lang)))

        submitted = st.form_submit_button(t("mini_test_submit", lang),
                                          type="primary")

    if submitted:
        result = build_mini_test_profile(
            gardner_answers, mbti_answers,
            display_name=name.strip() or t("mini_test_guest", lang),
        )
        st.session_state["mini_test_result"] = result
        st.rerun()

    st.stop()


# --------------------------------------------------------------------------
# Stop if no profile selected yet
# --------------------------------------------------------------------------
if upload_error:
    st.error(upload_error)
    st.stop()
if selected_row is None:
    st.info(t("select_profile_hint", lang))
    st.stop()


# --------------------------------------------------------------------------
# Build matcher and run pipeline
# --------------------------------------------------------------------------
matcher = _build_matcher((w_g, w_m, w_c, w_r))
user_df = pd.DataFrame([selected_row])

cluster_label = matcher._assign_cluster(user_df)
predicted_ranks = matcher._predict_roles(user_df)
matches = matcher.match(user_df, top_k=top_n)
user_meta = make_user_meta(selected_row, cluster_label)
user_meta["id"] = str(selected_row[ID_COL])


# --------------------------------------------------------------------------
# Top header
# --------------------------------------------------------------------------
hdr = st.columns([3, 1, 1, 1])
hdr[0].markdown(f"### {user_meta['id']}")
hdr[1].metric("MBTI", user_meta["mbti"])
hdr[2].metric(t("cluster_label", lang), cluster_label)
hdr[3].metric(t("top1_score", lang), f"{matches[0].total_score:.1f}")

st.caption(cluster_description(cluster_label, lang))

if mini_test_meta is not None:
    notes = []
    if mini_test_meta.get("synthetic_eeg"):
        notes.append(t("mini_test_warning_eeg", lang))
    if not mini_test_meta.get("has_role_data"):
        notes.append(t("mini_test_warning_roles", lang))
    if notes:
        st.warning("\n\n".join("• " + n for n in notes))


# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_profile, tab_recs, tab_detail, tab_export = st.tabs([
    t("tab_profile", lang), t("tab_recs", lang),
    t("tab_detail", lang),  t("tab_export", lang),
])

TESTS = all_tests(lang)


# ---------- Tab 1: profile ----------
with tab_profile:
    sub_tabs = st.tabs([
        t("subtab_gardner", lang), t("subtab_mbti", lang),
        t("subtab_neiry", lang),   t("subtab_roles", lang),
        t("subtab_about", lang),
    ])

    with sub_tabs[0]:
        st.markdown(f"**{TESTS[0].name}**")
        st.caption(TESTS[0].short)
        col1, col2 = st.columns([1, 1])
        with col1:
            intel_dict = {k: float(selected_row[k]) for k in GARDNER_FEATURES}
            st.plotly_chart(gardner_radar(intel_dict),
                            use_container_width=True)
        with col2:
            df = pd.DataFrame({
                t("intelligence_col", lang): list(GARDNER_FEATURES),
                t("score_col", lang):
                    [float(selected_row[k]) for k in GARDNER_FEATURES],
            }).sort_values(t("score_col", lang), ascending=False)
            st.dataframe(df, hide_index=True, use_container_width=True,
                         height=380)

    with sub_tabs[1]:
        st.markdown(f"**{TESTS[1].name}**")
        st.caption(TESTS[1].short)
        st.plotly_chart(mbti_bars(selected_row), use_container_width=True)
        st.caption(f"{t('mbti_type_label', lang)}: **{user_meta['mbti']}**. "
                   + t("mbti_caption", lang))

    with sub_tabs[2]:
        st.markdown(f"**{TESTS[2].name}**")
        st.caption(TESTS[2].short)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{t('indices_baseline_actual', lang)}**")
            st.plotly_chart(neiry_indices_bar(selected_row),
                            use_container_width=True)
        with col2:
            st.markdown(f"**{t('bands_title', lang)}**")
            st.plotly_chart(neiry_bands_pie(selected_row),
                            use_container_width=True)
        st.markdown(f"**{t('emotions_title', lang)}**")
        st.plotly_chart(neiry_emotions_radar(selected_row),
                        use_container_width=True)
        with st.expander(t("full_neiry_table", lang), expanded=False):
            rows = [{"feature": k, "value": float(selected_row[k])}
                    for k in NEIRY_FEATURES]
            st.dataframe(pd.DataFrame(rows), hide_index=True,
                         use_container_width=True, height=400)

    with sub_tabs[3]:
        st.markdown(f"**{t('predicted_roles_top10', lang)}**")
        st.caption(t("predicted_roles_caption", lang))
        st.plotly_chart(role_ranking_bar(predicted_ranks, top_n=10),
                        use_container_width=True)

    with sub_tabs[4]:
        for ti in TESTS:
            st.markdown(f"### {ti.name}")
            st.markdown(f"**{ti.short}**")
            st.markdown(f"- ✅ {ti.strengths}")
            st.markdown(f"- ⚠️ {ti.weaknesses}")
            st.markdown(f"- 🔧 {ti.use_in_system}")
            st.markdown(f"[{ti.link_label}]({ti.link})")
            st.divider()


# ---------- Tab 2: recommendations ----------
with tab_recs:
    with st.expander(t("scoring_expander", lang), expanded=False):
        st.markdown(f"**{t('scoring_formula_label', lang)}** `{SCORING_FORMULA}`")
        for name, descr in scoring_details(lang):
            st.markdown(f"- **{name}.** {descr}")
        st.caption(scoring_notes(lang))

    st.subheader(t("top_n_section", lang, n=top_n))

    df_rec = pd.DataFrame([{
        t("rank_col", lang): i + 1,
        t("prof_col", lang): m.name_ru,
        t("category_col", lang): m.category,
        "total":   round(m.total_score, 1),
        "gardner": round(m.breakdown.gardner, 1),
        "mbti":    round(m.breakdown.mbti, 1),
        "cluster": round(m.breakdown.cluster, 1),
        "roles":   round(m.breakdown.roles, 1),
    } for i, m in enumerate(matches)])
    st.dataframe(
        df_rec, hide_index=True, use_container_width=True,
        column_config={
            "total": st.column_config.ProgressColumn(
                "total", min_value=0, max_value=100, format="%.1f"),
        },
    )

    st.subheader(t("composition_section", lang))
    st.plotly_chart(breakdown_bar(matches, top_n=top_n),
                    use_container_width=True)


# ---------- Tab 3: detail ----------
with tab_detail:
    name_to_match = {f"{i+1}. {m.name_ru}": m for i, m in enumerate(matches)}
    pick = st.selectbox(t("pick_profession", lang), list(name_to_match.keys()))
    m: ProfessionMatch = name_to_match[pick]

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(t("breakdown_section", lang))
        st.plotly_chart(single_match_breakdown(m), use_container_width=True)
        st.markdown(f"**{t('category_field', lang)}:** {m.category}  \n"
                    f"**{t('cluster_match_field', lang)}:** {m.cluster_match_kind}")
    with col2:
        st.subheader(t("matches_section", lang))
        if m.matched_intelligences:
            st.markdown(f"*{t('intel_subhead', lang)}*")
            df_i = pd.DataFrame([
                {"intelligence": n, "user": round(u, 1), "ideal": round(i, 1),
                 "Δ": round(abs(u - i), 1)}
                for n, u, i in m.matched_intelligences
            ])
            st.dataframe(df_i, hide_index=True, use_container_width=True)
        if m.matched_mbti:
            st.markdown(f"*{t('mbti_subhead', lang)}*")
            df_m = pd.DataFrame([
                {"dim": d, "user (signed)": round(u, 1),
                 "preference": round(p, 1)}
                for d, u, p in m.matched_mbti
            ])
            st.dataframe(df_m, hide_index=True, use_container_width=True)
        if m.matched_roles:
            st.markdown(f"*{t('roles_subhead', lang)}*")
            df_r = pd.DataFrame([
                {"role": r, "predicted rank": int(rk)}
                for r, rk in m.matched_roles
            ])
            st.dataframe(df_r, hide_index=True, use_container_width=True)

    st.subheader(t("explain_section", lang))
    with st.spinner(
        t("explain_spin_ollama", lang) if actual_backend == "ollama"
        else t("explain_spin_template", lang)
    ):
        explanation = explainer.explain(user_meta, m)
    st.info(explanation.text)
    st.caption(f"{t('backend_label_caption', lang)} {explanation.backend}")


# ---------- Tab 4: export ----------
with tab_export:
    st.subheader(t("pdf_section", lang))
    st.write(t("pdf_descr", lang, n=top_n))
    st.caption(t("pdf_caption", lang, b=actual_backend))

    if st.button(t("build_pdf_btn", lang), type="primary"):
        with st.spinner(t("build_pdf_spin", lang)):
            explanations: dict[str, str] = {}
            for m in matches:
                explanations[m.profession_id] = explainer.explain(user_meta, m).text
            pdf_bytes = build_pdf_report(user_meta, matches, explanations,
                                         top_n=top_n)
        st.success(t("done", lang))
        st.download_button(
            label=t("download_pdf", lang),
            data=pdf_bytes,
            file_name=f"neurocareer_{user_meta['id']}.pdf".replace(" ", "_"),
            mime="application/pdf",
        )

    st.divider()
    st.subheader(t("csv_section", lang))
    csv_bytes = df_rec.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t("download_csv", lang),
        data=csv_bytes,
        file_name=f"neurocareer_{user_meta['id']}_top.csv".replace(" ", "_"),
        mime="text/csv",
    )


# --------------------------------------------------------------------------
# Footer
# --------------------------------------------------------------------------
st.divider()
st.caption(t("footer", lang))
