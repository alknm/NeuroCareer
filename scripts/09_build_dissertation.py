"""Build the master's dissertation .docx.

Replicates the formatting of the NIRM-may-2026 template (used as reference
by the supervisor): A4, margins 2/2/3/1.5 cm, Times New Roman 14 pt, single
line spacing, justified body with 0.75 cm first-line indent, page numbers
centered in the footer, title page without a number, automatic Word TOC.

Content lives in the sibling `dissertation_content` package, one module per
section. Adding new content never requires touching this script.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]        # system/
sys.path.insert(0, str(Path(__file__).parent))    # so we can import dissertation_content

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from dissertation_content import all_sections, annotation_blocks

OUT_DOCX = ROOT / "reports" / "dissertation.docx"

NSMAP = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

# ------------------------------------------------------------------ formatting

def _set_page(section) -> None:
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(1.5)
    section.header_distance = Cm(1.27)
    section.footer_distance = Cm(1.27)
    section.different_first_page_header_footer = True
    # mark title page (no number on page 1)
    sectPr = section._sectPr
    if sectPr.find(qn("w:titlePg")) is None:
        sectPr.append(OxmlElement("w:titlePg"))


def _set_styles(doc: Document) -> None:
    """Configure Normal / Heading 1 / Heading 2 / Heading 3 to match the
    NIRM template. Body: TNR 14, single-line, justified, first-line 0.75 cm.
    Headings: TNR 14 bold, centered, with spacing before.
    """
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(14)
    # ensure Cyrillic font fallback (eastAsia / cs)
    rPr = normal.element.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    for name, before, italic in [
        ("Heading 1", Pt(18), False),
        ("Heading 2", Pt(12), False),
        ("Heading 3", Pt(8), False),
    ]:
        st = doc.styles[name]
        st.font.name = "Times New Roman"
        st.font.size = Pt(14)
        st.font.bold = False  # Shumakov: headings are Normal-weight 14 pt
        st.font.italic = italic
        st.font.color.rgb = RGBColor(0, 0, 0)
        rPr = st.element.get_or_add_rPr()
        rfonts = rPr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rPr.append(rfonts)
        for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rfonts.set(qn(k), "Times New Roman")
        pf = st.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
        pf.space_before = before
        pf.space_after = Pt(6)
        pf.keep_with_next = True


def _add_field(paragraph, instr: str, default_text: str = "") -> None:
    """Insert a Word field (PAGE, TOC, ...) into a paragraph."""
    r = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    r._r.append(fldChar1)

    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = " " + instr + " "
    r._r.append(instrText)

    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    r._r.append(fldChar2)

    if default_text:
        t = OxmlElement("w:t")
        t.text = default_text
        r._r.append(t)

    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    r._r.append(fldChar3)


def _set_footer_page_number(section) -> None:
    # default footer (every page except first) - centered "PAGE" field
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.text = ""  # clear default empty paragraph
    for run in p.runs:
        run.text = ""
    _add_field(p, "PAGE", "1")

    # first-page footer left blank
    first = section.first_page_footer
    first.is_linked_to_previous = False
    for p in list(first.paragraphs):
        for run in p.runs:
            run.text = ""


# ---------------------------------------------------------------- block writer

def _body_paragraph(doc: Document, text: str, *,
                    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                    first_line_indent_cm: float = 0.75,
                    bold: bool = False,
                    italic: bool = False) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.alignment = align
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if first_line_indent_cm:
        p.paragraph_format.first_line_indent = Cm(first_line_indent_cm)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = bold
    run.italic = italic
    # ensure font set in rPr for Cyrillic
    rPr = run._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")


def _heading(doc: Document, level: int, text: str) -> None:
    p = doc.add_paragraph(style=f"Heading {level}")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = False
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    rPr = run._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")


def _subheading_notoc(doc: Document, text: str) -> None:
    """Looks like a heading but uses Normal style so Word's TOC ignores it.

    Used for inner sub-blocks of the Introduction and appendices that must
    not appear in the Table of Contents.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)
    run.bold = False
    rPr = run._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")


def _figure(doc: Document, rel_path: str, caption: str, width_cm: float = 14.5) -> None:
    img_path = ROOT / rel_path
    if not img_path.exists():
        # leave a placeholder paragraph so the document still renders
        _body_paragraph(doc, f"[Рисунок не найден: {rel_path}]",
                        align=WD_ALIGN_PARAGRAPH.CENTER, first_line_indent_cm=0)
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run()
        run.add_picture(str(img_path), width=Cm(width_cm))
    if caption:
        _body_paragraph(doc, caption,
                        align=WD_ALIGN_PARAGRAPH.CENTER,
                        first_line_indent_cm=0,
                        italic=False)


def _table(doc: Document, headers: list[str], rows: list[list[str]],
           caption: str = "", widths_cm: list[float] | None = None) -> None:
    if caption:
        _body_paragraph(doc, caption,
                        align=WD_ALIGN_PARAGRAPH.CENTER,
                        first_line_indent_cm=0)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # widths
    if widths_cm and len(widths_cm) == len(headers):
        for col_idx, w in enumerate(widths_cm):
            for cell in table.columns[col_idx].cells:
                cell.width = Cm(w)

    # header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        cell = hdr_cells[i]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.first_line_indent = Cm(0)
        run = para.add_run(h)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
    # body
    for r_idx, row in enumerate(rows, start=1):
        cells = table.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            cell = cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            cell.text = ""
            para = cell.paragraphs[0]
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.first_line_indent = Cm(0)
            run = para.add_run(str(val))
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)


def _pagebreak(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._r.append(br)


def _render(doc: Document, block: tuple) -> None:
    kind = block[0]
    if kind == "h1":
        _heading(doc, 1, block[1])
    elif kind == "h2":
        _heading(doc, 2, block[1])
    elif kind == "h3":
        _heading(doc, 3, block[1])
    elif kind == "h_notoc":
        _subheading_notoc(doc, block[1])
    elif kind == "p":
        _body_paragraph(doc, block[1])
    elif kind == "p_center":
        _body_paragraph(doc, block[1],
                        align=WD_ALIGN_PARAGRAPH.CENTER,
                        first_line_indent_cm=0)
    elif kind == "p_noindent":
        _body_paragraph(doc, block[1], first_line_indent_cm=0)
    elif kind == "p_right":
        _body_paragraph(doc, block[1],
                        align=WD_ALIGN_PARAGRAPH.RIGHT,
                        first_line_indent_cm=0)
    elif kind == "p_bold_center":
        _body_paragraph(doc, block[1],
                        align=WD_ALIGN_PARAGRAPH.CENTER,
                        first_line_indent_cm=0,
                        bold=True)
    elif kind == "fig":
        _, rel_path, caption = block
        _figure(doc, rel_path, caption)
    elif kind == "table":
        _, headers, rows, caption = block
        _table(doc, headers, rows, caption)
    elif kind == "pagebreak":
        _pagebreak(doc)
    elif kind == "blank":
        _body_paragraph(doc, "", first_line_indent_cm=0)
    else:
        raise ValueError(f"unknown block kind: {kind}")


# ------------------------------------------------------------------ title page

def _line(doc: Document, text: str, *, center=False, bold=False,
          right=False, size=14):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif right:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._r.get_or_add_rPr()
    rfonts = rPr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rPr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(k), "Times New Roman")
    return p


def _title_page(doc: Document) -> None:
    """First title page — Russian layout following the Shumakov 2025 example."""
    line = lambda *a, **kw: _line(doc, *a, **kw)

    line("НЕКОММЕРЧЕСКОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО", center=True, bold=True)
    line("«КАРАГАНДИНСКИЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ", center=True, bold=True)
    line("ИМЕНИ АБЫЛКАСА САГИНОВА»", center=True, bold=True)
    for _ in range(3):
        line("")
    # UDC line with right-aligned "На правах рукописи" via tabs
    line("УДК 004.8:159.9.072:331.548\t\t\t\tНа правах рукописи")
    for _ in range(3):
        line("")
    line("Ғайни Әлихан Саятұлы", center=True, bold=True)
    for _ in range(2):
        line("")
    line("ИССЛЕДОВАНИЕ И РАЗРАБОТКА ГИБРИДНОЙ СИСТЕМЫ ПРОФОРИЕНТАЦИИ",
         center=True, bold=True)
    line("НА ОСНОВЕ НЕЙРОННЫХ ДАННЫХ И ПСИХОЛОГИЧЕСКИХ ТЕСТОВ",
         center=True, bold=True)
    line("С ИСПОЛЬЗОВАНИЕМ ИИ", center=True, bold=True)
    for _ in range(2):
        line("")
    line("МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ", center=True, bold=True)
    line("НА СОИСКАНИЕ СТЕПЕНИ", center=True)
    line("МАГИСТРА ТЕХНИЧЕСКИХ НАУК", center=True)
    line("ПО ОБРАЗОВАТЕЛЬНОЙ ПРОГРАММЕ", center=True)
    line("7M06103 — «Машинное обучение и анализ данных»", center=True, bold=True)
    for _ in range(3):
        line("")
    line("Научные руководители:", center=True)
    line("к.т.н., доцент Томилова Н.И.", center=True)
    line("м.т.н., ст. преподаватель Кожанов М.Г.", center=True)
    for _ in range(4):
        line("")
    line("Республика Казахстан", center=True)
    line("Караганда", center=True)
    line("2026", center=True)


def _second_title_page(doc: Document) -> None:
    """Second title page (Допущен к защите) — Russian layout, Shumakov example."""
    line = lambda *a, **kw: _line(doc, *a, **kw)

    line("НЕКОММЕРЧЕСКОЕ АКЦИОНЕРНОЕ ОБЩЕСТВО", center=True, bold=True)
    line("«КАРАГАНДИНСКИЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ", center=True, bold=True)
    line("ИМЕНИ АБЫЛКАСА САГИНОВА»", center=True, bold=True)
    for _ in range(2):
        line("")
    line("\t\t\t\t\t\t\t«Допущен к защите»")
    line("\t\t\t\t\t\t\tЗав. кафедрой ИВС")
    line("\t\t\t\t\t\t\t_________ Абилдаева Г.Б.")
    line("\t\t\t\t\t\t\t«___»__________2026 г.")
    for _ in range(3):
        line("")
    line("МАГИСТЕРСКАЯ ДИССЕРТАЦИЯ", center=True, bold=True)
    line("")
    line("на тему:", center=True)
    line("«Исследование и разработка гибридной системы профориентации",
         center=True, bold=True)
    line("на основе нейронных данных и психологических тестов",
         center=True, bold=True)
    line("с использованием ИИ»", center=True, bold=True)
    line("")
    line("7M06103 «Машинное обучение и анализ данных»",
         center=True, bold=True)
    for _ in range(3):
        line("")
    line("Магистрант\t\t\t\t\tҒайни Ә.С.")
    line("")
    line("Группа\t\t\t\t\t\tМОиАД-24-1")
    line("")
    line("Научные руководители:")
    line("к.т.н., доцент\t\t\t\t\tТомилова Н.И.")
    line("м.т.н., ст. преподаватель\t\t\tКожанов М.Г.")
    for _ in range(5):
        line("")
    line("Республика Казахстан", center=True)
    line("Караганда 2026", center=True)


# ------------------------------------------------------------------------- TOC

def _toc(doc: Document) -> None:
    _heading(doc, 1, "Содержание")
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    # TOC field — Word fills it on first open (Ctrl+A then F9)
    _add_field(
        p,
        'TOC \\o "1-3" \\h \\z \\u',
        "\nЧтобы обновить содержание, в Word выделите этот блок "
        "и нажмите F9 (или «Обновить поле»).\n",
    )


# ---------------------------------------------------------------------- driver

def main() -> None:
    doc = Document()

    section = doc.sections[0]
    _set_page(section)
    _set_styles(doc)
    _set_footer_page_number(section)

    # 1. First title page
    _title_page(doc)
    _pagebreak(doc)

    # 1b. Second title page (Қорғауға жіберіледі)
    _second_title_page(doc)
    _pagebreak(doc)

    # 1c. Резюме / Түйіндеме / Summary — before the contents (Shumakov order)
    for block in annotation_blocks():
        _render(doc, block)
    _pagebreak(doc)

    # 2. Table of contents (auto, Word will populate)
    _toc(doc)
    _pagebreak(doc)

    # 3. Content
    for section_blocks in all_sections():
        for block in section_blocks:
            _render(doc, block)
        # page break between top-level sections (between chapters/parts)

    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_DOCX)
    print(f"wrote {OUT_DOCX}  ({OUT_DOCX.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
