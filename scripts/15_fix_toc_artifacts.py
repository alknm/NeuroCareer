"""Fix two artefacts left after 14_collapse_toc.py:

  1. The "1.1 Развитие..." heading carried a manual list auto-number (numPr),
     producing a doubled "1.1  1.1 ..." in the contents -> remove the numPr.
  2. The "Содержание" title was a Heading 1 and listed itself in the contents
     -> convert it to a centred, non-bold, 14 pt Times New Roman Normal
     paragraph (same look as the other section titles, but not a TOC heading).

Then re-update the TOC field, tighten it, repaginate and export the PDF.
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1] / "reports"
DOCX = str(ROOT / "dissertation_l.docx")
PDF = str(ROOT / "dissertation_l.pdf")


def patch() -> None:
    doc = Document(DOCX)
    normal = doc.styles["Normal"]

    removed_num = 0
    fixed_title = 0
    for p in doc.paragraphs:
        st = p.style.name
        txt = p.text.strip()

        # 1. drop the stray auto-number on the merged 1.1 heading
        if st == "Heading 2":
            pPr = p._p.find(qn("w:pPr"))
            if pPr is not None:
                numPr = pPr.find(qn("w:numPr"))
                if numPr is not None:
                    pPr.remove(numPr)
                    removed_num += 1

        # 2. turn the "Содержание" title into a non-heading centred paragraph
        if st == "Heading 1" and txt == "Содержание":
            p.style = normal
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.first_line_indent = Cm(0)
            pf.space_before = Pt(18)
            pf.space_after = Pt(6)
            for r in p.runs:
                r.bold = False
                r.font.size = Pt(14)
                r.font.name = "Times New Roman"
                rpr = r._element.get_or_add_rPr()
                rfonts = rpr.find(qn("w:rFonts"))
                if rfonts is None:
                    rfonts = rpr.makeelement(qn("w:rFonts"), {})
                    rpr.append(rfonts)
                for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                    rfonts.set(qn(a), "Times New Roman")
            fixed_title += 1

    doc.save(DOCX)
    print(f"numPr removed: {removed_num}   title fixed: {fixed_title}")


def finalize() -> None:
    import win32com.client as win32
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(DOCX)
    try:
        for toc in d.TablesOfContents:
            toc.Update()
        d.Fields.Update()
        n = 0
        for p in d.Paragraphs:
            nm = p.Style.NameLocal.lower()
            if nm.startswith("toc") or nm.startswith("оглавление") or nm.startswith("содержание"):
                pf = p.Format
                pf.LineSpacingRule = 0
                pf.SpaceBefore = 0
                pf.SpaceAfter = 0
                fnt = p.Range.Font
                fnt.Name = "Times New Roman"
                fnt.Size = 14
                n += 1
        d.Repaginate()
        pages = d.ComputeStatistics(2)
        words = d.ComputeStatistics(0)
        d.Save()
        d.SaveAs(PDF, FileFormat=17)
    finally:
        d.Close(False)
        word.Quit()
    print(f"TOC paragraphs reformatted: {n}")
    print(f"PAGES: {pages}   WORDS: {words}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    patch()
    finalize()


if __name__ == "__main__":
    main()
