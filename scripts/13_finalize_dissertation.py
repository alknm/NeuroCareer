"""Finalize the dissertation .docx via Word COM.

Steps:
  1. Open reports/dissertation.docx in Word (invisible).
  2. Update every Table-of-Contents field.
  3. Tighten the contents: single line spacing, no space before/after,
     Times New Roman 14 pt — to match the reference (Shumakov) format.
  4. Repaginate, export PDF, print page/word statistics and the start page
     of every top-level (Heading 1) section.

Requires pywin32 and a local Word installation. Run AFTER 09_build_dissertation.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[1] / "reports"
DOCX = str(ROOT / "dissertation.docx")
PDF = str(ROOT / "dissertation.pdf")

# Word enum constants
WD_SINGLE = 0          # wdLineSpaceSingle
WD_STAT_PAGES = 2
WD_STAT_WORDS = 0
WD_PAGE_INFO = 3       # wdActiveEndPageNumber
PDF_FORMAT = 17        # wdFormatPDF


def _is_toc_style(name: str) -> bool:
    n = name.lower()
    return n.startswith("toc") or n.startswith("оглавление") or n.startswith("содержание")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(DOCX)
    try:
        for toc in d.TablesOfContents:
            toc.Update()
        d.Fields.Update()

        # tighten the table of contents
        n_toc = 0
        for p in d.Paragraphs:
            if _is_toc_style(p.Style.NameLocal):
                pf = p.Format
                pf.LineSpacingRule = WD_SINGLE
                pf.SpaceBefore = 0
                pf.SpaceAfter = 0
                fnt = p.Range.Font
                fnt.Name = "Times New Roman"
                fnt.Size = 14
                n_toc += 1

        d.Repaginate()
        pages = d.ComputeStatistics(WD_STAT_PAGES)
        words = d.ComputeStatistics(WD_STAT_WORDS)

        sections = []
        for p in d.Paragraphs:
            nm = p.Style.NameLocal
            if nm.startswith("Heading 1") or nm.startswith("Заголовок 1"):
                t = p.Range.Text.strip()
                if t:
                    sections.append((p.Range.Information(WD_PAGE_INFO), t[:48]))

        d.Save()
        d.SaveAs(PDF, FileFormat=PDF_FORMAT)
    finally:
        d.Close(False)
        word.Quit()

    print(f"TOC paragraphs reformatted: {n_toc}")
    print(f"PAGES: {pages}   WORDS: {words}")
    print("--- Heading-1 sections / start page ---")
    for pg, t in sections:
        print(f"  p{pg:>3}  {t}")


if __name__ == "__main__":
    main()
