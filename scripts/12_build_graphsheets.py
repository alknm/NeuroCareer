"""Build the graphic sheets file «граф листы.docx».

A graphic sheet (граф лист) is a formal A4 landscape engineering sheet that
carries ONE diagram plus an ЕСКД title block (основная надпись, ГОСТ 2.104,
форма 1) in the bottom-right corner — exactly like the reference example
`примеры-диссера/.../граф лист 1.docx`. These sheets are printed, slipped
into plastic sleeves and presented at the defense; they are NOT part of the
dissertation body (which is why they live in a separate file).

The diagrams are drawn here with matplotlib so they stay reproducible and
match the real six-layer architecture of the system.

Run:
    python 12_build_graphsheets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION_START
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]            # system/
FIGDIR = ROOT / "reports" / "figures" / "graphsheets"
OUT_DOCX = ROOT / "reports" / "граф листы.docx"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12,
    "axes.linewidth": 0,
})

BLUE = "#1f4e79"
TEAL = "#2e8b8b"
LIGHT = "#eaf2f8"
LIGHT2 = "#e6f2f1"
GREY = "#444444"


# --------------------------------------------------------------------- drawing

def _box(ax, x, y, w, h, text, *, fc=LIGHT, ec=BLUE, fs=12, bold=False):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.6, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color="#101010", zorder=3,
            fontweight="bold" if bold else "normal", wrap=True)


def _arrow(ax, x1, y1, x2, y2, ec=GREY):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
        linewidth=1.6, color=ec, zorder=1))


def _new_ax(w=16, h=9):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    return fig, ax


def draw_architecture(path: Path):
    """Граф лист 1 — six-layer architecture."""
    fig, ax = _new_ax()
    layers = [
        ("Слой 6. Пользовательский интерфейс",
         "Streamlit: ввод профиля, веса, переключатель LLM; экспорт PDF-отчёта", TEAL),
        ("Слой 5. Объяснение рекомендаций",
         "Локальная LLM Qwen2.5-7B (Ollama) + детерминированный шаблон-фолбэк", BLUE),
        ("Слой 4. Гибридный матчер",
         "База знаний 64 профессий; интегральная оценка из четырёх компонентов", TEAL),
        ("Слой 3. Предсказание ролей",
         "Ранжирование 20 ролей: Ridge / Random Forest / GBM / LightGBM; SHAP", BLUE),
        ("Слой 2. Кластеризация когнитивных профилей",
         "k-means, k = 3 (сбалансированный / мобилизованный / истощённый)", TEAL),
        ("Слой 1. Ввод и подготовка данных",
         "Пилотная выборка 47×65; копул-синтез GaussianCopula (n = 500)", BLUE),
    ]
    n = len(layers)
    gap = 1.6
    h = (96 - gap * (n - 1)) / n
    for i, (title, desc, col) in enumerate(layers):
        y = 2 + i * (h + gap)
        _box(ax, 6, y, 88, h, "", fc=LIGHT if i % 2 == 0 else LIGHT2, ec=col)
        ax.text(50, y + h * 0.64, title, ha="center", va="center",
                fontsize=19, fontweight="bold", color=col)
        ax.text(50, y + h * 0.28, desc, ha="center", va="center",
                fontsize=14, color="#202020")
        if i < n - 1:
            _arrow(ax, 50, y + h + gap, 50, y + h + 0.2)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def draw_pipeline(path: Path):
    """Граф лист 2 — data processing and ML pipeline (snake layout)."""
    fig, ax = _new_ax()
    steps = [
        ("Пилотные данные\n47 × 65", BLUE),
        ("Очистка и\nкодирование", TEAL),
        ("Кластеризация\nk-means, k = 3", BLUE),
        ("Копул-синтез\nGaussianCopula\nn = 500", TEAL),
        ("Ранжирование ролей\nRidge / RF / GBM /\nLightGBM", BLUE),
        ("Интерпретация\nSHAP", TEAL),
        ("Гибридный матчер\n64 профессии", BLUE),
        ("LLM-объяснение\nQwen2.5-7B", TEAL),
        ("Интерфейс и PDF\nStreamlit", BLUE),
    ]
    cols, rows = 3, 3
    bw, bh = 24, 16
    xs = [8, 38, 68]
    ys = [70, 40, 10]
    centers = []
    for idx, (text, col) in enumerate(steps):
        r, c = divmod(idx, cols)
        if r % 2 == 1:
            c = cols - 1 - c
        x, y = xs[c], ys[r]
        _box(ax, x, y, bw, bh, text, fc=LIGHT if idx % 2 == 0 else LIGHT2,
             ec=col, fs=12, bold=True)
        centers.append((x + bw / 2, y + bh / 2, x, y))
    # connect in order with arrows
    for idx in range(len(steps) - 1):
        cx1, cy1, x1, y1 = centers[idx]
        cx2, cy2, x2, y2 = centers[idx + 1]
        r1 = idx // cols
        r2 = (idx + 1) // cols
        if r1 == r2:  # horizontal within a row
            if cx2 > cx1:
                _arrow(ax, x1 + bw, cy1, x2, cy2)
            else:
                _arrow(ax, x1, cy1, x2 + bw, cy2)
        else:  # drop down to next row
            _arrow(ax, cx1, y1, cx2, y2 + bh)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def draw_matcher(path: Path):
    """Граф лист 3 — four-component hybrid matcher score."""
    fig, ax = _new_ax()
    inputs = [
        ("Тест Гарднера\n(множественный\nинтеллект)", "0,30", TEAL),
        ("MBTI\n(тип личности)", "0,20", BLUE),
        ("Кластер\nкогнитивного\nпрофиля", "0,10", TEAL),
        ("Предсказанные\nроли (20)", "0,40", BLUE),
    ]
    bw, bh = 19, 14
    x0 = 4
    gap = (96 - len(inputs) * bw) / (len(inputs) - 1)
    centerx = []
    for i, (text, w, col) in enumerate(inputs):
        x = x0 + i * (bw + gap)
        _box(ax, x, 74, bw, bh, text, fc=LIGHT if i % 2 == 0 else LIGHT2,
             ec=col, fs=15, bold=True)
        cx = x + bw / 2
        centerx.append(cx)
        ax.text(cx + 6, 70, f"× {w}", ha="left", va="center",
                fontsize=18, fontweight="bold", color=col)

    # central aggregation box
    _box(ax, 24, 38, 52, 16,
         "Интегральная оценка соответствия\n"
         "score = 0,30·Гарднер + 0,20·MBTI + 0,10·Кластер + 0,40·Роли",
         fc="#fff7e6", ec="#b8860b", fs=15, bold=True)
    for cx in centerx:
        _arrow(ax, cx, 74, 50, 54)

    _box(ax, 28, 8, 44, 14,
         "Топ-N рекомендованных профессий\nс разбивкой вклада компонентов",
         fc=LIGHT2, ec=TEAL, fs=15, bold=True)
    _arrow(ax, 50, 38, 50, 22)
    fig.tight_layout(pad=0.3)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------- docx layout

def _set_cell_text(cell, text, *, bold=False, italic=False, size=10,
                   align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")


def _set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")        # 1 pt
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)


WORK_TITLE = ("Исследование и разработка гибридной системы профориентации "
              "на основе нейронных данных и психологических тестов "
              "с использованием искусственного интеллекта")
ORG_LINE = "«ҚарТУ им. А. Сагинова» НАО, кафедра ИВС, гр. МОиАД-24-1"
FRAME_W = Cm(26.6)   # inner width of the ГОСТ frame (landscape, usable)


def _add_page_border(section) -> None:
    """ГОСТ-рамка вокруг всего листа."""
    sectPr = section._sectPr
    pgBorders = OxmlElement("w:pgBorders")
    pgBorders.set(qn("w:offsetFrom"), "page")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "18")        # ~2.25 pt
        el.set(qn("w:space"), "20")     # ~7 mm from the page edge
        el.set(qn("w:color"), "000000")
        pgBorders.append(el)
    sectPr.append(pgBorders)


def _top_title_box(doc: Document, text: str) -> None:
    """Рамка с полным названием работы в верхней части листа."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.columns[0].width = FRAME_W
    table.cell(0, 0).width = FRAME_W
    _set_cell_text(table.cell(0, 0), text, italic=True, size=11,
                   align=WD_ALIGN_PARAGRAPH.CENTER)
    _set_table_borders(table)


def _title_block_footer(section, title: str, sheet_no: int, sheet_total: int):
    """ЕСКД основная надпись (форма 1), прикреплённая к низу листа."""
    footer = section.footer
    footer.is_linked_to_previous = False
    # remove default empty paragraph spacing
    footer.paragraphs[0].paragraph_format.space_after = Pt(0)

    table = footer.add_table(rows=5, cols=6, width=FRAME_W)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    widths = [Cm(2.6), Cm(3.4), Cm(1.4), Cm(1.4), Cm(11.8), Cm(6.0)]
    for r in table.rows:
        for i, c in enumerate(r.cells):
            c.width = widths[i]

    # header row (over роль-блок)
    _set_cell_text(table.cell(0, 0), "", size=8)
    _set_cell_text(table.cell(0, 1), "", size=8)
    _set_cell_text(table.cell(0, 2), "Подп.", size=8)
    _set_cell_text(table.cell(0, 3), "Дата", size=8)

    roles = [
        ("Разраб.", "Ғайни Ә.С."),
        ("Пров.", "Томилова Н.И."),
        ("Н.контр.", "Кожанов М.Г."),
        ("Утв.", "Абильдаева Г.Б."),
    ]
    for i, (role, name) in enumerate(roles, start=1):
        _set_cell_text(table.cell(i, 0), role, size=9, align=WD_ALIGN_PARAGRAPH.LEFT)
        _set_cell_text(table.cell(i, 1), name, size=9, align=WD_ALIGN_PARAGRAPH.LEFT)
        _set_cell_text(table.cell(i, 2), "", size=9)
        _set_cell_text(table.cell(i, 3), "", size=9)

    # title — center cell, rows 0..2 of col 4
    title_cell = table.cell(0, 4).merge(table.cell(2, 4))
    _set_cell_text(title_cell, title, bold=True, size=13,
                   align=WD_ALIGN_PARAGRAPH.CENTER)

    # right info column
    _set_cell_text(table.cell(0, 5), "Лит.        Масса        Масштаб", size=8)
    _set_cell_text(table.cell(1, 5),
                   f"Лист  {sheet_no}        Листов  {sheet_total}", size=8)
    _set_cell_text(table.cell(2, 5), "", size=8)

    # organization — bottom-right, rows 3..4 of cols 4..5
    org_cell = table.cell(3, 4).merge(table.cell(4, 5))
    _set_cell_text(org_cell, ORG_LINE, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)

    _set_table_borders(table)


def _add_sheet(doc: Document, img: Path, title: str, sheet_no: int, total: int,
               first: bool):
    if first:
        section = doc.sections[0]
    else:
        section = doc.add_section(WD_SECTION_START.NEW_PAGE)
    # landscape A4
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Cm(29.7)
    section.page_height = Cm(21.0)
    section.top_margin = Cm(1.4)
    section.bottom_margin = Cm(4.6)     # reserve room for the main inscription
    section.left_margin = Cm(1.9)
    section.right_margin = Cm(1.0)
    section.footer_distance = Cm(0.75)

    _add_page_border(section)

    # top title box with the full work title
    _top_title_box(doc, WORK_TITLE)

    # diagram (centered, filling the frame width)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    run = p.add_run()
    run.add_picture(str(img), width=Cm(23.0))

    # main inscription pinned to the bottom of the frame
    _title_block_footer(section, title, sheet_no, total)


# ------------------------------------------------------------------------ main

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    FIGDIR.mkdir(parents=True, exist_ok=True)

    p1 = FIGDIR / "gs1_architecture.png"
    p2 = FIGDIR / "gs2_pipeline.png"
    p3 = FIGDIR / "gs3_matcher.png"
    draw_architecture(p1)
    draw_pipeline(p2)
    draw_matcher(p3)

    sheets = [
        (p1, "Шестиуровневая архитектура гибридной системы профориентации"),
        (p2, "Конвейер обработки данных и обучения моделей"),
        (p3, "Гибридный матчер: четырёхкомпонентная оценка соответствия"),
    ]

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)

    total = len(sheets)
    for i, (img, title) in enumerate(sheets):
        _add_sheet(doc, img, title, sheet_no=i + 1, total=total, first=(i == 0))

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DOCX))
    print(f"wrote {OUT_DOCX}  ({OUT_DOCX.stat().st_size / 1024:.1f} KB), "
          f"{total} sheets")


if __name__ == "__main__":
    main()
