"""Reusable helpers for the Streamlit UI (charts, profile loaders, PDF export)."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Iterable

import pandas as pd
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .data_loader import (GARDNER_FEATURES, ID_COL, MBTI_INDEPENDENT_SCALES,
                          MBTI_TYPE_COL, NEIRY_FEATURES, ROLE_FEATURES)
from .matcher import ProfessionMatch

# A short label per role for compact tables / bars
ROLE_SHORT = {
    "Focus Expert": "Focus", "Optimist": "Optimist", "Brainstormer": "Brainstorm",
    "Catalyst": "Catalyst", "Analyst": "Analyst", "Winner": "Winner",
    "Storyteller": "Storyteller", "Problem Solver": "Solver",
    "Strategist": "Strategist", "Thinker": "Thinker", "Believer": "Believer",
    "Time Keeper": "TimeKeeper", "Peace Keeper": "PeaceKeeper",
    "Deliverer": "Deliverer", "Commander": "Commander",
    "Philomath": "Philomath", "Chameleon": "Chameleon", "Coach": "Coach",
    "Self-Believer": "Self-Bel.", "Empathizer": "Empathizer",
}

CLUSTER_DESCRIPTION = {
    "balanced":  "сбалансированный профиль: умеренные показатели концентрации, "
                 "релаксации и утомляемости.",
    "mobilized": "мобилизованный профиль: высокая концентрация, низкий уровень "
                 "релаксации, низкая утомляемость - готовность к интенсивной "
                 "умственной работе.",
    "depleted":  "истощённый профиль: пониженная концентрация, повышенная "
                 "релаксация, выраженная утомляемость - подходят более щадящие "
                 "режимы деятельности.",
}


# ---------------------------------------------------------------------------
# Charts (Plotly)
# ---------------------------------------------------------------------------

def gardner_radar(intel_values: dict[str, float]) -> go.Figure:
    """Polar radar of the 9 Gardner intelligences."""
    cats = list(intel_values.keys())
    vals = [intel_values[c] for c in cats]
    short = [c.replace(" интеллект", "") for c in cats]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=short + [short[0]],
        fill="toself",
        line=dict(color="#3a7ca5"),
        fillcolor="rgba(58, 124, 165, 0.30)",
        name="profile",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=380,
        margin=dict(t=20, b=20, l=40, r=40),
    )
    return fig


_MBTI_DICHOTOMIES = [
    ("MBTIЭкстраверт",   "Экстраверт (E)", "Интроверт (I)"),
    ("MBTIИнтуитивные",  "Интуиция (N)",   "Сенсорика (S)"),
    ("MBTIЛогика",       "Логика (T)",     "Этика (F)"),
    ("MBTIПланирующие",  "Планирующий (J)","Воспринимающий (P)"),
    ("MBTIУверенные",    "Уверенный (-A)", "Турбулентный (-T)"),
]


def mbti_bars(row: pd.Series) -> go.Figure:
    """Diverging horizontal bar of the 5 MBTI dichotomies.

    Each row in `row` provides a 0..100 score for the *left* pole. The chart
    shows how the user leans on each axis around the 50/50 midpoint.
    """
    labels, lefts, rights, signed = [], [], [], []
    for col, left, right in _MBTI_DICHOTOMIES:
        v = float(row[col]) if col in row.index else 50.0
        labels.append(f"{left}  ↔  {right}")
        lefts.append(left)
        rights.append(right)
        signed.append(v - 50.0)  # negative = right pole, positive = left pole

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=signed,
        y=labels,
        orientation="h",
        marker_color=["#3a7ca5" if v >= 0 else "#d6a85a" for v in signed],
        text=[f"{50 + v:.0f} : {50 - v:.0f}" for v in signed],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(title="отклонение от центра, 0 = 50:50",
                   range=[-55, 55], zeroline=True, zerolinecolor="#888"),
        yaxis=dict(autorange="reversed"),
        height=320,
        margin=dict(t=20, b=20, l=160, r=40),
        showlegend=False,
    )
    return fig


_NEIRY_INDEX_PAIRS = [
    ("Концентрация",  "neiryBaseline Concentration index", "neiryConcentration index"),
    ("Релаксация",    "neiryBaseline Relaxation index",    "neiryRelaxation index"),
    ("Утомление",     "neiryBaseline Fatigue score",       "neiryFatigue score"),
    ("Alpha Gravity", "neiryBaseline Alpha Gravity",       "neiryAlpha Gravity"),
    ("Reverse Fatigue", "neiryBaseline Reverse Fatigue",   "neiryReverse Fatigue"),
]

_NEIRY_BANDS = [
    ("Theta (4–8 Гц)", "neiryTheta"),
    ("Alpha (8–13 Гц)", "neiryAlpha"),
    ("Beta (13–30 Гц)", "neiryBeta"),
]

_NEIRY_EMOTIONS = [
    ("Chill",        "neiryChill"),
    ("Stress",       "neiryStress"),
    ("Focus",        "neiryFocus"),
    ("Anger",        "neiryAnger"),
    ("Self-control", "neirySelf-control"),
]


def neiry_indices_bar(row: pd.Series) -> go.Figure:
    """Baseline vs actual cognitive indices."""
    labels, baseline, actual = [], [], []
    for name, base_col, act_col in _NEIRY_INDEX_PAIRS:
        labels.append(name)
        baseline.append(float(row[base_col]) if base_col in row.index else 0.0)
        actual.append(float(row[act_col]) if act_col in row.index else 0.0)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="baseline", x=labels, y=baseline,
                         marker_color="#9b59b6"))
    fig.add_trace(go.Bar(name="actual",   x=labels, y=actual,
                         marker_color="#26b8a0"))
    fig.update_layout(
        barmode="group",
        height=300,
        margin=dict(t=20, b=40, l=40, r=20),
        yaxis=dict(title="индекс"),
        legend=dict(orientation="h", y=1.12),
    )
    return fig


def neiry_bands_pie(row: pd.Series) -> go.Figure:
    """Relative power of Theta / Alpha / Beta bands."""
    vals = [float(row[c]) if c in row.index else 0.0 for _, c in _NEIRY_BANDS]
    labels = [n for n, _ in _NEIRY_BANDS]
    fig = go.Figure(go.Pie(
        labels=labels, values=vals,
        marker=dict(colors=["#3a7ca5", "#26b8a0", "#d6a85a"]),
        hole=0.45,
        textinfo="label+percent",
    ))
    fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                      showlegend=False)
    return fig


def neiry_emotions_radar(row: pd.Series) -> go.Figure:
    """Radar of 5 emotion markers."""
    labels = [n for n, _ in _NEIRY_EMOTIONS]
    vals = [float(row[c]) if c in row.index else 0.0 for _, c in _NEIRY_EMOTIONS]
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=labels + [labels[0]],
        fill="toself",
        line=dict(color="#26b8a0"),
        fillcolor="rgba(38, 184, 160, 0.30)",
    ))
    auto_max = max(vals + [1.0]) * 1.15
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, auto_max])),
        showlegend=False,
        height=300,
        margin=dict(t=20, b=20, l=40, r=40),
    )
    return fig


def role_ranking_bar(predicted_ranks: pd.Series, top_n: int = 10) -> go.Figure:
    """Horizontal bar of the user's top-N predicted Neiry roles (rank 1..N)."""
    sorted_roles = predicted_ranks.sort_values()
    sub = sorted_roles.head(top_n)
    fig = go.Figure(go.Bar(
        x=[21 - r for r in sub.values],
        y=[ROLE_SHORT.get(r, r) for r in sub.index],
        orientation="h",
        marker_color="#3a7ca5",
        text=[f"#{int(r)}" for r in sub.values],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis=dict(title="affinity (21 - rank)", range=[0, 22]),
        yaxis=dict(autorange="reversed"),
        height=320,
        margin=dict(t=20, b=20, l=40, r=40),
    )
    return fig


def breakdown_bar(matches: list[ProfessionMatch], top_n: int = 10) -> go.Figure:
    """Stacked-style bar of component scores per profession."""
    matches = matches[:top_n]
    names = [m.name_ru for m in matches]
    g = [m.breakdown.gardner for m in matches]
    mb = [m.breakdown.mbti for m in matches]
    cl = [m.breakdown.cluster for m in matches]
    rl = [m.breakdown.roles for m in matches]
    total = [m.total_score for m in matches]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Gardner",  x=names, y=g,  marker_color="#3a7ca5"))
    fig.add_trace(go.Bar(name="MBTI",     x=names, y=mb, marker_color="#d6a85a"))
    fig.add_trace(go.Bar(name="Cluster",  x=names, y=cl, marker_color="#9b59b6"))
    fig.add_trace(go.Bar(name="Roles",    x=names, y=rl, marker_color="#2ca02c"))
    fig.add_trace(go.Scatter(
        name="Total", x=names, y=total, mode="markers+text",
        marker=dict(color="black", size=8, symbol="diamond"),
        text=[f"{t:.0f}" for t in total], textposition="top center",
    ))
    fig.update_layout(
        barmode="group",
        xaxis_tickangle=-30,
        yaxis=dict(title="score (0..100)", range=[0, 105]),
        height=420,
        margin=dict(t=10, b=120, l=40, r=40),
        legend=dict(orientation="h", y=1.07),
    )
    return fig


def single_match_breakdown(m: ProfessionMatch) -> go.Figure:
    """Vertical bar of one profession's components."""
    labels = ["Gardner", "MBTI", "Cluster", "Roles", "Total"]
    vals = [m.breakdown.gardner, m.breakdown.mbti, m.breakdown.cluster,
            m.breakdown.roles, m.total_score]
    colors_ = ["#3a7ca5", "#d6a85a", "#9b59b6", "#2ca02c", "#222"]
    fig = go.Figure(go.Bar(x=labels, y=vals, marker_color=colors_,
                           text=[f"{v:.1f}" for v in vals],
                           textposition="outside"))
    fig.update_layout(
        yaxis=dict(range=[0, 110], title="score (0..100)"),
        height=300,
        margin=dict(t=30, b=10, l=40, r=40),
    )
    return fig


# ---------------------------------------------------------------------------
# Profile parsers
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = (
    [ID_COL, MBTI_TYPE_COL]
    + list(GARDNER_FEATURES)
    + list(MBTI_INDEPENDENT_SCALES)
    + list(ROLE_FEATURES)
    + list(NEIRY_FEATURES)
)


def validate_uploaded_profile(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """Return (ok, missing_columns)."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return (len(missing) == 0, missing)


def respondent_options(df: pd.DataFrame) -> list[str]:
    return df[ID_COL].astype(str).tolist()


# ---------------------------------------------------------------------------
# PDF report builder (ReportLab)
# ---------------------------------------------------------------------------

def _try_register_cyrillic_font() -> str:
    """Try to register a Cyrillic-capable TTF; return font name to use."""
    candidates = [
        ("DejaVuSans", r"C:\Windows\Fonts\DejaVuSans.ttf"),
        ("ArialUnicode", r"C:\Windows\Fonts\arial.ttf"),
        ("Verdana", r"C:\Windows\Fonts\verdana.ttf"),
        ("Tahoma", r"C:\Windows\Fonts\tahoma.ttf"),
    ]
    for name, path in candidates:
        try:
            pdfmetrics.registerFont(TTFont(name, path))
            return name
        except Exception:
            continue
    return "Helvetica"


def build_pdf_report(user_meta: dict, matches: list[ProfessionMatch],
                     explanations: dict[str, str], top_n: int = 5) -> bytes:
    font = _try_register_cyrillic_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("title", parent=styles["Title"],
                              fontName=font, fontSize=16, leading=20)
    h2_st = ParagraphStyle("h2", parent=styles["Heading2"],
                           fontName=font, fontSize=12, leading=16,
                           spaceBefore=12, spaceAfter=4)
    body_st = ParagraphStyle("body", parent=styles["BodyText"],
                             fontName=font, fontSize=10, leading=13)
    small_st = ParagraphStyle("small", parent=body_st, fontSize=9, leading=11,
                              textColor=colors.grey)

    story = []
    story.append(Paragraph("NeuroCareer - персональный отчёт", title_st))
    story.append(Spacer(1, 6))
    today = datetime.now().strftime("%d.%m.%Y %H:%M")
    story.append(Paragraph(f"Сгенерировано: {today}", small_st))
    story.append(Spacer(1, 12))

    # Profile block
    story.append(Paragraph("Профиль", h2_st))
    intel = ", ".join(f"{n} ({v:.0f})" for n, v in user_meta["top_intelligences"])
    story.append(Paragraph(
        f"<b>Идентификатор:</b> {user_meta.get('id', '—')}<br/>"
        f"<b>MBTI:</b> {user_meta['mbti']}<br/>"
        f"<b>Когнитивный кластер:</b> {user_meta['cluster']} - "
        f"{CLUSTER_DESCRIPTION.get(user_meta['cluster'], '')}<br/>"
        f"<b>Ведущие интеллекты:</b> {intel}",
        body_st,
    ))

    # Recommendations table
    story.append(Paragraph(f"Топ-{top_n} рекомендаций", h2_st))
    data = [["#", "Профессия", "Категория", "Score", "Gardner", "MBTI",
             "Cluster", "Roles"]]
    for i, m in enumerate(matches[:top_n], start=1):
        data.append([
            str(i),
            Paragraph(m.name_ru, body_st),
            m.category,
            f"{m.total_score:.1f}",
            f"{m.breakdown.gardner:.0f}",
            f"{m.breakdown.mbti:.0f}",
            f"{m.breakdown.cluster:.0f}",
            f"{m.breakdown.roles:.0f}",
        ])
    tbl = Table(data, colWidths=[0.7*cm, 6.5*cm, 2.4*cm, 1.3*cm, 1.5*cm,
                                  1.3*cm, 1.5*cm, 1.4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3a7ca5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ]))
    story.append(tbl)

    # Explanations
    story.append(Paragraph("Обоснование рекомендаций", h2_st))
    for i, m in enumerate(matches[:top_n], start=1):
        story.append(Paragraph(
            f"<b>{i}. {m.name_ru}</b> - {m.total_score:.1f} баллов",
            body_st,
        ))
        text = explanations.get(m.profession_id, "(объяснение недоступно)")
        story.append(Paragraph(text, body_st))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Отчёт сформирован системой NeuroCareer. Рекомендации носят "
        "ориентировочный характер и не заменяют консультацию специалиста.",
        small_st,
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


__all__ = [
    "ROLE_SHORT", "CLUSTER_DESCRIPTION", "REQUIRED_COLUMNS",
    "gardner_radar", "role_ranking_bar", "breakdown_bar", "single_match_breakdown",
    "validate_uploaded_profile", "respondent_options", "build_pdf_report",
]
