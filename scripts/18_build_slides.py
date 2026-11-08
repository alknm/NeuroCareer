"""Build the defense presentation for the NeuroCareer dissertation.

Style mirrors the SOTA reference (Шумаков_защита 1.pptx): 16:9, muted
slate-blue / grey palette, decorative circles, a bold title per slide.
Unlike the reference (baked-in images), this deck uses NATIVE editable text
and embeds the project's own honest figures from system/reports/figures.

Numbers are taken only from the stage reports (no invented metrics):
  k-means k=3 silhouette 0.240, sizes [30,8,9];
  Ridge synth->real Spearman 0.823 vs Random Forest CV-on-real 0.354;
  synthetic n=500 GaussianCopula, 35/38 KS pass, Frobenius 0.134 / 0.227;
  64 professions / 9 categories; matcher weights 0.30/0.20/0.10/0.40;
  SHAP: psychometric features dominate, neiryChill only EEG in top-10.

Output: disser_final/Гайни_защита.pptx
"""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "system" / "reports" / "figures"
OUT = ROOT / "disser_final" / "Гайни_защита.pptx"

# ---- palette -------------------------------------------------------------- #
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF5, 0xF6, 0xF7)
INK = RGBColor(0x26, 0x34, 0x3C)        # titles / dark body
SUB = RGBColor(0x5E, 0x6B, 0x73)        # muted text
SLATE = RGBColor(0x7C, 0x97, 0xA6)      # decorative accent
SLATE_LT = RGBColor(0xDD, 0xE4, 0xE8)   # light panels / faint circles
SLATE_DK = RGBColor(0x51, 0x64, 0x6E)   # dark panel
ACCENT = RGBColor(0x1F, 0x6F, 0x8B)     # emphasis (numbers)
LINE = RGBColor(0xC2, 0xCD, 0xD3)

TITLE_FONT = "Segoe UI Semibold"
BODY_FONT = "Segoe UI"

EMU_IN = 914400
SW, SH = 13.333, 7.5  # inches


# --------------------------------------------------------------------------- #
def _set_font(run, name):
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:latin", "a:cs", "a:ea"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", name)


def _no_line(shape):
    shape.line.fill.background()


def _fill(shape, color, line=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line is None:
        _no_line(shape)
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    shape.shadow.inherit = False


def bg(slide):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                               Inches(SW), Inches(SH))
    _fill(r, BG)
    r._element.addprevious(r._element)  # keep at back (no-op safe)
    return r


def oval(slide, cx, cy, d, color):
    """Circle centred at (cx,cy) inches, diameter d inches."""
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                               Inches(cx - d / 2), Inches(cy - d / 2),
                               Inches(d), Inches(d))
    _fill(s, color)
    return s


def decor(slide, variant=0):
    """A couple of off-canvas decorative circles, alternating corners."""
    if variant % 2 == 0:
        oval(slide, SW - 0.3, 0.2, 2.6, SLATE_LT)
        oval(slide, SW - 0.1, 0.4, 1.1, SLATE)
        oval(slide, 0.2, SH - 0.2, 1.8, SLATE_LT)
    else:
        oval(slide, 0.1, 0.3, 2.2, SLATE_LT)
        oval(slide, SW - 0.2, SH - 0.1, 2.4, SLATE_LT)
        oval(slide, SW - 0.5, SH - 0.4, 1.0, SLATE)


def textbox(slide, left, top, width, height, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top),
                                  Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Pt(2)
    tf.margin_top = tf.margin_bottom = Pt(2)
    return tb, tf


def _run(p, text, size, color, bold=False, font=BODY_FONT, italic=False):
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    _set_font(r, font)
    return r


def title(slide, text, size=30):
    # accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.7), Inches(0.62),
                                 Inches(0.13), Inches(0.62))
    _fill(bar, ACCENT)
    tb, tf = textbox(slide, 0.95, 0.5, 11.4, 1.0)
    p = tf.paragraphs[0]
    _run(p, text, size, INK, bold=True, font=TITLE_FONT)
    return tb


def bullets(slide, left, top, width, height, items, size=16,
            color=INK, space=10, marker="•  "):
    tb, tf = textbox(slide, left, top, width, height)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        p.line_spacing = 1.05
        if isinstance(it, tuple):  # (lead_bold, rest)
            _run(p, marker, size, ACCENT, bold=True)
            _run(p, it[0], size, color, bold=True)
            if it[1]:
                _run(p, it[1], size, color)
        else:
            _run(p, marker, size, ACCENT, bold=True)
            _run(p, it, size, color)
    return tb


def panel(slide, left, top, w, h, color=WHITE, line=LINE, radius=True):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(w), Inches(h))
    _fill(shp, color, line=line)
    return shp


def pic_fit(slide, path, left, top, maxw, maxh, frame=True):
    w, h = Image.open(path).size
    ar = w / h
    bw, bh = maxw, maxw / ar
    if bh > maxh:
        bh, bw = maxh, maxh * ar
    px = left + (maxw - bw) / 2
    py = top + (maxh - bh) / 2
    if frame:
        panel(slide, px - 0.08, py - 0.08, bw + 0.16, bh + 0.16,
              color=WHITE, line=LINE)
    slide.shapes.add_picture(str(path), Inches(px), Inches(py),
                             Inches(bw), Inches(bh))


def new_slide(prs, variant=0):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    bg(s)
    decor(s, variant)
    return s


# --------------------------------------------------------------------------- #
def build():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)

    # ===== 1. TITLE ======================================================== #
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    oval(s, SW + 0.3, SH + 0.3, 3.4, SLATE_LT)
    oval(s, SW - 0.4, SH - 0.3, 1.2, SLATE)
    # university emblem (top-left, like the reference deck)
    logo = FIG / "saginov_logo.png"
    if logo.exists():
        lw, lh = Image.open(logo).size
        disp_w = 1.85
        disp_h = disp_w * lh / lw
        s.shapes.add_picture(str(logo), Inches(0.55), Inches(0.45),
                             Inches(disp_w), Inches(disp_h))
    # university
    _, tf = textbox(s, 1.0, 0.55, 11.3, 1.1, anchor=MSO_ANCHOR.TOP)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "«Әбілқас Сағынов атындағы Қарағанды техникалық университеті» КеАҚ",
         13, SUB, bold=True)
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    _run(p2, "НАО «Карагандинский технический университет имени Абылкаса Сагинова»",
         13, SUB, bold=True)
    # title
    _, tf = textbox(s, 0.9, 2.25, 11.5, 2.2, anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.line_spacing = 1.08
    _run(p, "Исследование и разработка гибридной системы профориентации "
            "на основе нейронных данных и психологических тестов "
            "с использованием искусственного интеллекта",
         27, INK, bold=True, font=TITLE_FONT)
    # divider
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.4), Inches(5.05),
                            Inches(1.6), Inches(0.04))
    _fill(ln, ACCENT)
    _, tf = textbox(s, 6.0, 5.2, 6.6, 1.4)
    for i, (lead, rest) in enumerate([
        ("Магистрант: ", "Ғайни Ә.С.  (гр. МОиАД-24-1)"),
        ("Руководитель: ", "к.т.н., доцент Томилова Н.И."),
        ("Руководитель: ", "м.т.н., ст. преподаватель Кожанов М.Г."),
    ]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.RIGHT; p.space_after = Pt(2)
        _run(p, lead, 15, SUB)
        _run(p, rest, 15, INK, bold=True)
    _, tf = textbox(s, 0.8, 6.35, 4.0, 0.7)
    p = tf.paragraphs[0]
    _run(p, "Караганда, Казахстан", 14, INK, bold=True)
    p2 = tf.add_paragraph(); _run(p2, "2026 г.", 14, SUB)

    # ===== 2. ЦЕЛЬ И ЗАДАЧИ ================================================ #
    s = new_slide(prs, 0)
    title(s, "Цель и задачи")
    panel(s, 0.7, 1.7, 5.1, 5.1, color=SLATE_DK, line=None)
    _, tf = textbox(s, 1.0, 1.95, 4.5, 4.6)
    p = tf.paragraphs[0]; _run(p, "Цель", 18, WHITE, bold=True, font=TITLE_FONT)
    p2 = tf.add_paragraph(); p2.space_before = Pt(8); p2.line_spacing = 1.1
    _run(p2, "Разработать и экспериментально проверить гибридную систему "
             "профессиональной ориентации, которая на основе совместного "
             "анализа психологических тестов и нейрофизиологических (ЭЭГ) "
             "данных формирует объяснимые рекомендации по выбору профессии.",
         15, SLATE_LT)
    _, tf = textbox(s, 6.2, 1.7, 0.1, 0.4)
    bullets(s, 6.15, 1.75, 6.5, 5.1, [
        "Проанализировать подходы к профориентации, методы ИИ/МО "
        "и психологические тесты",
        "Разработать шестиуровневую архитектуру гибридной системы",
        "Подготовить данные: пилотная выборка и синтетическое расширение",
        "Построить слой кластеризации когнитивных профилей",
        "Реализовать ранжирование профессиональных ролей и сравнить модели",
        "Создать базу знаний профессий и гибридный матчер",
        "Разработать LLM-объяснитель и пользовательский интерфейс",
    ], size=15, space=9)
    _, tf = textbox(s, 6.15, 1.72, 4, 0.4)

    # ===== 3. ОБЪЕКТ И ПРЕДМЕТ ============================================= #
    s = new_slide(prs, 1)
    title(s, "Объект и предмет исследования")
    panel(s, 0.7, 1.9, 5.6, 4.4, color=WHITE)
    _, tf = textbox(s, 1.0, 2.15, 5.0, 3.9)
    p = tf.paragraphs[0]; _run(p, "Объект", 18, ACCENT, bold=True, font=TITLE_FONT)
    p2 = tf.add_paragraph(); p2.space_before = Pt(8); p2.line_spacing = 1.1
    _run(p2, "Процессы профессиональной ориентации на основе совместного "
             "анализа психологических и нейрофизиологических данных.",
         16, INK)
    panel(s, 6.6, 1.9, 5.9, 4.4, color=SLATE_DK, line=None)
    _, tf = textbox(s, 6.9, 2.15, 5.3, 3.9)
    p = tf.paragraphs[0]; _run(p, "Предмет", 18, WHITE, bold=True, font=TITLE_FONT)
    p2 = tf.add_paragraph(); p2.space_before = Pt(8); p2.line_spacing = 1.1
    _run(p2, "Методы, модели и алгоритмы построения гибридной рекомендательной "
             "системы профориентации с использованием искусственного "
             "интеллекта.",
         16, SLATE_LT)

    # ===== 4. АКТУАЛЬНОСТЬ / НОВИЗНА / ЗНАЧИМОСТЬ =========================== #
    s = new_slide(prs, 0)
    title(s, "Актуальность, новизна, значимость")
    rows = [
        ("Актуальность",
         "Традиционная профориентация субъективна; растёт потребность "
         "в объективных, персонализированных и масштабируемых инструментах "
         "поддержки выбора профессии.", SLATE),
        ("Научная новизна",
         "Гибридное объединение психометрических и ЭЭГ-признаков в единую "
         "воспроизводимую модель ранжирования ролей и применение локальной "
         "большой языковой модели для объяснимых рекомендаций.", SLATE_DK),
        ("Практическая значимость",
         "Работающая система NeuroCareer (Streamlit) для школьников, "
         "выпускников колледжей, родителей и профконсультантов; автоматизация "
         "первичной диагностики и экспорт персонального отчёта.", ACCENT),
    ]
    y = 1.75
    for name, txt, col in rows:
        c = oval(s, 2.0, y + 0.75, 1.5, col)
        _, tf = textbox(s, 1.27, y + 0.32, 1.46, 0.95, anchor=MSO_ANCHOR.MIDDLE)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; p.line_spacing = 0.95
        _run(p, name, 12, WHITE, bold=True, font=TITLE_FONT)
        _, tf = textbox(s, 3.3, y + 0.18, 9.2, 1.5, anchor=MSO_ANCHOR.MIDDLE)
        p = tf.paragraphs[0]; p.line_spacing = 1.08
        _run(p, txt, 15.5, INK)
        y += 1.68

    # ===== 5. НАЗНАЧЕНИЕ И ЦЕЛЕВАЯ АУДИТОРИЯ ================================ #
    s = new_slide(prs, 1)
    title(s, "Назначение и целевая аудитория")
    panel(s, 0.7, 1.75, 11.8, 1.55, color=SLATE_DK, line=None)
    _, tf = textbox(s, 1.05, 1.9, 11.2, 1.3, anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.line_spacing = 1.08
    _run(p, "Назначение:  ", 16, SLATE_LT, bold=True)
    _run(p, "гибридная рекомендательная система выбора будущей профессии "
            "на основе оценки знаний, умений, возможностей и "
            "предрасположенностей.", 16, WHITE)
    cards = ["Выпускники школ", "Учащиеся и выпускники колледжей",
             "Родители", "Психологи и профконсультанты",
             "Центры профориентации"]
    cw, gap = 2.16, 0.18
    x = 0.7
    for c in cards:
        panel(s, x, 3.7, cw, 2.7, color=WHITE)
        oval(s, x + cw / 2, 4.5, 0.7, SLATE_LT)
        _, tf = textbox(s, x + 0.12, 5.05, cw - 0.24, 1.25,
                        anchor=MSO_ANCHOR.TOP)
        for i, ln in enumerate(c.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER; p.line_spacing = 1.0
            _run(p, ln, 14, INK, bold=True)
        x += cw + gap

    # ===== 6. ГИБРИДНЫЙ ПОДХОД ============================================= #
    s = new_slide(prs, 0)
    title(s, "Обоснование гибридности")
    box_y, box_h = 2.5, 2.0
    # input box
    panel(s, 0.7, box_y, 3.7, box_h, color=WHITE)
    _, tf = textbox(s, 0.85, box_y + 0.12, 3.4, box_h - 0.2,
                    anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "1. Оценка человеком", 15, ACCENT, bold=True, font=TITLE_FONT)
    for t in ["Психологические тесты:", "Гарднер · MBTI · интересы",
              "+ нейроданные ЭЭГ (Neiry)"]:
        pp = tf.add_paragraph(); pp.alignment = PP_ALIGN.CENTER
        pp.line_spacing = 1.0; pp.space_before = Pt(2)
        _run(pp, t, 13, INK)
    # model box
    panel(s, 5.0, box_y, 3.4, box_h, color=SLATE_DK, line=None)
    _, tf = textbox(s, 5.15, box_y + 0.12, 3.1, box_h - 0.2,
                    anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "2. Предсказание модели", 15, WHITE, bold=True, font=TITLE_FONT)
    for t in ["Машинное обучение", "ранжирует 20", "профессиональных ролей"]:
        pp = tf.add_paragraph(); pp.alignment = PP_ALIGN.CENTER
        pp.line_spacing = 1.0; pp.space_before = Pt(2)
        _run(pp, t, 13, SLATE_LT)
    # output box
    panel(s, 9.0, box_y, 3.5, box_h, color=SLATE)
    _, tf = textbox(s, 9.15, box_y + 0.12, 3.2, box_h - 0.2,
                    anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "Гибридный матчер", 15, WHITE, bold=True, font=TITLE_FONT)
    for t in ["объединяет сигналы", "→ объяснимая", "рекомендация профессий"]:
        pp = tf.add_paragraph(); pp.alignment = PP_ALIGN.CENTER
        pp.line_spacing = 1.0; pp.space_before = Pt(2)
        _run(pp, t, 13, WHITE)
    # arrows
    for ax in (4.45, 8.45):
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(ax),
                               Inches(box_y + box_h / 2 - 0.18),
                               Inches(0.5), Inches(0.36))
        _fill(a, ACCENT)
    _, tf = textbox(s, 0.7, 5.1, 11.8, 1.4, anchor=MSO_ANCHOR.TOP)
    p = tf.paragraphs[0]; p.line_spacing = 1.1
    _run(p, "Гибридность = объективная оценка тестов, выполненных человеком, "
            "усиленная предсказанием ML-модели. Ни один источник не "
            "используется изолированно: итоговая рекомендация формируется "
            "их совместной взвешенной агрегацией.", 15, INK)

    # ===== 7. АРХИТЕКТУРА ================================================== #
    s = new_slide(prs, 1)
    title(s, "Шестиуровневая архитектура системы")
    pic_fit(s, FIG / "graphsheets" / "gs1_architecture.png",
            0.8, 1.6, 11.7, 5.6)

    # ===== 8. ДАННЫЕ ====================================================== #
    s = new_slide(prs, 0)
    title(s, "Данные и датасет")
    bullets(s, 0.7, 1.75, 6.0, 5.2, [
        ("Пилотная выборка: ", "47 респондентов, 65 признаков"),
        ("Признаки: ", "Гарднер, MBTI, ЭЭГ-Neiry"),
        ("Целевая переменная: ", "рейтинги 20 ролей Neiry"),
        ("Синтетика: ", "GaussianCopula, n = 500"),
        ("Валидация: ", "35/38 KS-тестов проходят (α = 0,05)"),
        ("Согласие корреляций: ", "расстояние Фробениуса 0,134 / 0,227"),
    ], size=16, space=12)
    pic_fit(s, FIG / "04a_marginal_comparison.png", 6.8, 1.8, 5.8, 4.0)
    _, tf = textbox(s, 6.8, 5.95, 5.8, 0.8)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "Сравнение распределений: реальные и синтетические данные",
         12, SUB, italic=True)

    # ===== 9. КЛАСТЕРИЗАЦИЯ ================================================ #
    s = new_slide(prs, 1)
    title(s, "Кластеризация когнитивных профилей")
    bullets(s, 0.7, 1.8, 5.6, 5.0, [
        ("Метод: ", "k-средних, k = 3 (random_state = 2)"),
        ("Силуэт: ", "0,240"),
        ("Размеры кластеров: ", "[30, 8, 9]"),
        ("Профили: ", "сбалансированный, мобилизованный, истощённый"),
    ], size=16, space=14)
    pic_fit(s, FIG / "02a_pca_clusters.png", 6.5, 1.8, 6.0, 5.0)

    # ===== 10. СРАВНЕНИЕ МОДЕЛЕЙ (TABLE) =================================== #
    s = new_slide(prs, 0)
    title(s, "Ранжирование ролей: сравнение моделей")
    data = [
        ["Модель", "Режим", "Spearman ρ", "NDCG@5", "Top-1"],
        ["marginal baseline", "synth→real", "0,374", "0,757", "0,170"],
        ["Ridge (лучшая)", "synth→real", "0,823", "0,928", "0,404"],
        ["Random Forest", "CV на реальных", "0,354", "0,730", "0,128"],
        ["marginal baseline", "CV на реальных", "0,289", "0,729", "0,021"],
    ]
    rows, cols = len(data), len(data[0])
    gt = s.shapes.add_table(rows, cols, Inches(0.8), Inches(1.85),
                            Inches(11.7), Inches(3.0)).table
    gt.columns[0].width = Inches(3.1)
    gt.columns[1].width = Inches(2.6)
    for c in range(2, cols):
        gt.columns[c].width = Inches(2.0)
    for r in range(rows):
        for c in range(cols):
            cell = gt.cell(r, c)
            cell.margin_left = Pt(7); cell.margin_right = Pt(5)
            cell.margin_top = Pt(4); cell.margin_bottom = Pt(4)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            hd = r == 0
            best = (r == 2) or (r == 3)  # highlight the two reported rows
            _run(p, data[r][c], 14 if hd else 13.5,
                 WHITE if hd else INK, bold=hd or (best and c == 0))
            if hd:
                cell.fill.solid(); cell.fill.fore_color.rgb = SLATE_DK
            elif best:
                cell.fill.solid(); cell.fill.fore_color.rgb = SLATE_LT
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
    _, tf = textbox(s, 0.8, 5.25, 11.7, 1.6)
    p = tf.paragraphs[0]; p.line_spacing = 1.12
    _run(p, "Честный разрыв: ", 16, ACCENT, bold=True)
    _run(p, "Spearman ρ = 0,823 достигается при доступе к синтетическим "
            "данным (n = 500), тогда как на честной 5-блочной кросс-валидации "
            "только по реальным n = 47 лучшая модель (Random Forest) даёт "
            "ρ = 0,354. Разрыв явно зафиксирован и интерпретирован в работе.",
         16, INK)

    # ===== 11. SHAP ======================================================= #
    s = new_slide(prs, 1)
    title(s, "Значимость признаков (SHAP)")
    _, tf = textbox(s, 0.7, 1.85, 5.6, 5.0)
    shap_rows = [
        ("b", "Метод: ", "TreeExplainer на Random Forest"),
        ("b", "Доминируют психометрические признаки:", ""),
        ("s", "MBTI Экстраверт", " — 2,31"),
        ("s", "Логико-математический интеллект", " — 2,30"),
        ("s", "MBTI Планирующие", " — 1,44"),
        ("b", "ЭЭГ — вспомогательный сигнал:", ""),
        ("s", "единственный в топ-10 — neiry Chill", " (ранг 10)"),
    ]
    for i, (kind, lead, rest) in enumerate(shap_rows):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(9); p.line_spacing = 1.05
        if kind == "b":
            _run(p, "•  ", 15, ACCENT, bold=True)
            _run(p, lead, 15, INK, bold=True)
            if rest:
                _run(p, rest, 15, INK)
        else:
            p.level = 1
            _run(p, "—  ", 14, SLATE, bold=True)
            _run(p, lead, 14, INK)
            if rest:
                _run(p, rest, 14, ACCENT, bold=True)
    pic_fit(s, FIG / "06b_shap_global_importance.png", 6.5, 1.8, 6.0, 5.0)

    # ===== 12. МАТЧЕР ===================================================== #
    s = new_slide(prs, 0)
    title(s, "Гибридный матчер и база знаний")
    pic_fit(s, FIG / "graphsheets" / "gs3_matcher.png", 0.8, 1.55, 8.0, 5.6)
    panel(s, 9.0, 1.8, 3.5, 5.0, color=SLATE_DK, line=None)
    _, tf = textbox(s, 9.25, 2.05, 3.05, 4.6)
    p = tf.paragraphs[0]
    _run(p, "База знаний", 16, WHITE, bold=True, font=TITLE_FONT)
    for lead, rest in [("64", " профессии"), ("9", " категорий")]:
        pp = tf.add_paragraph(); pp.space_before = Pt(3)
        _run(pp, lead, 15, SLATE_LT, bold=True); _run(pp, rest, 15, WHITE)
    pp = tf.add_paragraph(); pp.space_before = Pt(12)
    _run(pp, "Интегральная оценка", 15, WHITE, bold=True, font=TITLE_FONT)
    for t in ["0,30 · Гарднер", "0,20 · MBTI", "0,10 · Кластер",
              "0,40 · Роли"]:
        pp = tf.add_paragraph(); pp.space_before = Pt(2)
        _run(pp, t, 14, SLATE_LT)
    pp = tf.add_paragraph(); pp.space_before = Pt(10); pp.line_spacing = 1.05
    _run(pp, "Веса настраиваемые. Выход — топ-N профессий с разбивкой "
             "вклада компонентов.", 13, WHITE)

    # ===== 13. LLM + UI =================================================== #
    s = new_slide(prs, 1)
    title(s, "Объяснение рекомендаций и интерфейс")
    bullets(s, 0.7, 1.75, 6.0, 5.2, [
        ("LLM-объяснитель: ", "локальная модель Qwen2.5-7B (Ollama) "
         "+ детерминированный шаблон-фолбэк"),
        ("Защита от галлюцинаций: ", "объяснение опирается только "
         "на структурированный вывод системы"),
        ("Интерфейс Streamlit: ", "профиль, рекомендации, объяснение, "
         "экспорт персонального PDF-отчёта"),
        ("Стек: ", "полностью бесплатный локальный (без платных сервисов)"),
    ], size=15.5, space=12)
    pic_fit(s, FIG / "07a_top_categories.png", 6.8, 2.1, 5.8, 3.6)
    _, tf = textbox(s, 6.8, 5.85, 5.8, 0.8)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "Пример выхода: топ-категории рекомендаций", 12, SUB, italic=True)

    # ===== 14. ЗАКЛЮЧЕНИЕ ================================================= #
    s = new_slide(prs, 0)
    title(s, "Заключение")
    bullets(s, 0.7, 1.9, 11.8, 5.0, [
        "Разработана и протестирована работающая гибридная система "
        "профориентации NeuroCareer из шести уровней",
        "Подтверждена ведущая роль психометрических признаков; ЭЭГ — "
        "вспомогательный сигнал (анализ SHAP)",
        "Реализованы кластеризация профилей, ранжирование ролей, база знаний "
        "профессий, гибридный матчер, LLM-объяснитель и интерфейс",
        "Результаты получены честно, с явным указанием ограничений объёма "
        "пилотной выборки",
        "Все поставленные задачи решены, цель работы достигнута",
    ], size=17, space=14)

    # ===== 15. АПРОБАЦИЯ ================================================== #
    s = new_slide(prs, 1)
    title(s, "Апробация работы")
    bullets(s, 0.7, 1.9, 11.8, 4.8, [
        "Научно-исследовательская работа магистранта (НИРМ) — отчёты "
        "по семестрам",
        "Научная статья по теме диссертации",
        "Тезис доклада на научной конференции",
        "Программная реализация системы NeuroCareer (Streamlit, открытый код)",
    ], size=17, space=14)
    _, tf = textbox(s, 0.7, 6.3, 11.8, 0.7)
    p = tf.paragraphs[0]
    _run(p, "Примечание: точные выходные данные публикаций указать "
            "при оформлении.", 13, SUB, italic=True)

    # ===== 16. СПИСОК НАУЧНЫХ ТРУДОВ ====================================== #
    s = new_slide(prs, 0)
    title(s, "Список научных трудов")
    _, tf = textbox(s, 0.7, 1.65, 11.8, 0.6)
    p = tf.paragraphs[0]
    _run(p, "Научные публикации по теме диссертации за период обучения "
            "2024–2026 гг.:", 15, INK)
    # framed placeholder for the screenshot the user will paste
    panel(s, 0.8, 2.35, 11.7, 4.55, color=WHITE, line=LINE)
    _, tf = textbox(s, 1.0, 4.1, 11.3, 1.0, anchor=MSO_ANCHOR.MIDDLE)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    _run(p, "Место для скриншота списка трудов (2024–2026)", 16, SUB,
         italic=True)
    p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.CENTER
    _run(p2, "вставьте изображение поверх этой области", 12, SLATE,
         italic=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print("wrote", OUT, "| slides:", len(prs.slides._sldIdLst))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    build()


if __name__ == "__main__":
    main()
