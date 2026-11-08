"""Build a standalone Word file: акт о внедрении программного продукта.

Mirrors the reference photo (доп-инфа/акт внедрения пример.jpeg):
  УТВЕРЖДАЮ block (top-right) -> АКТ title (centred) -> body paragraph ->
  signature line (bottom-left).

Tailored for the NeuroCareer product, introduced at ТОО «NovaSolutions».
Output: reports/акт внедрения NeuroCareer.docx (+ .pdf)
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1] / "reports"
DOCX = str(ROOT / "акт внедрения NeuroCareer.docx")
PDF = str(ROOT / "акт внедрения NeuroCareer.pdf")

FONT = "Times New Roman"
SIZE = 14


def _font(run, italic=False, bold=False):
    run.font.name = FONT
    run.font.size = Pt(SIZE)
    run.font.italic = italic
    run.font.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(a), FONT)


def _p(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=None,
       bold=False, space_after=0, line=1.0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if first_line is not None:
        pf.first_line_indent = Cm(first_line)
    if text:
        _font(p.add_run(text), bold=bold)
    return p


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    doc = Document()

    # page geometry (matches the dissertation format)
    sec = doc.sections[0]
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(1.5)

    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(SIZE)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    # ---- УТВЕРЖДАЮ (top-right) ----
    _p(doc, "УТВЕРЖДАЮ", align=WD_ALIGN_PARAGRAPH.RIGHT)
    _p(doc, "Директор ТОО «NovaSolutions»", align=WD_ALIGN_PARAGRAPH.RIGHT)
    _p(doc, "_______________________", align=WD_ALIGN_PARAGRAPH.RIGHT)
    _p(doc, "«____» ______________ 2026 г.", align=WD_ALIGN_PARAGRAPH.RIGHT)

    for _ in range(3):
        _p(doc)

    # ---- title ----
    _p(doc, "АКТ", align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, "о внедрении программного продукта", align=WD_ALIGN_PARAGRAPH.CENTER)

    _p(doc)

    # ---- body ----
    body = (
        "Настоящим актом подтверждается, что программный продукт «NeuroCareer» — "
        "гибридная система профориентации на основе нейронных данных и "
        "психологических тестов с использованием искусственного интеллекта — "
        "внедрён в рабочий процесс ТОО «NovaSolutions» для проведения "
        "профориентационного тестирования и опытной эксплуатации. Программный "
        "продукт был разработан и протестирован магистрантом группы МОиАД-24-1 "
        "НАО «Карагандинского технического университета имени Абылкаса Сагинова» "
        "Ғайни Әлихан Саятұлы под руководством старшего преподавателя Кожанова "
        "Мурата Галиаскаровича."
    )
    _p(doc, body, first_line=1.25, line=1.5)

    _p(doc)
    _p(doc, "Внедрение программного продукта позволило автоматизировать "
            "первичную профориентационную диагностику, повысить объективность "
            "рекомендаций за счёт совместного анализа психометрических и "
            "нейрофизиологических данных и сократить время подготовки "
            "индивидуального профориентационного заключения.",
       first_line=1.25, line=1.5)

    for _ in range(4):
        _p(doc)

    # ---- signature ----
    sign = doc.add_paragraph()
    sign.paragraph_format.space_after = Pt(0)
    _font(sign.add_run("_______________________"))
    _font(sign.add_run("\t\tДиректор ТОО «NovaSolutions»"))

    doc.save(DOCX)
    print(f"wrote {DOCX}")

    # PDF export (best-effort, via Word COM)
    try:
        import win32com.client as win32
        word = win32.gencache.EnsureDispatch("Word.Application")
        word.Visible = False
        d = word.Documents.Open(DOCX)
        d.SaveAs(PDF, FileFormat=17)
        d.Close(False)
        word.Quit()
        print(f"wrote {PDF}")
    except Exception as e:  # noqa: BLE001
        print("PDF export skipped:", e)


if __name__ == "__main__":
    main()
