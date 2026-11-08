"""Build the supervisor's review (отзыв) and the reviewer's recension (рецензия)
for the NeuroCareer dissertation, mirroring the reference examples
disser/1 Отзыв.docx and disser/2 Рецензия.docx.

Layout copied from the references:
  margins T/B/L/R = 1.5 / 1.0 / 3.0 / 1.0 cm, Times New Roman 14, single
  spacing, justified body with a 0.75 cm first-line indent, and a borderless
  1-row / 2-col signature table (position on the left, name on the right).

Отзыв carries TWO supervisor signatures (Томилова Н.И. + Кожанов М.Г.).
Рецензия keeps the example reviewer (Муратхан Райхан).

Output: disser/1 Отзыв Гайни.docx (+ .pdf), disser/2 Рецензия Гайни.docx (+ .pdf)
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2] / "disser_final"

FONT = "Times New Roman"
SIZE = 14
FIRST = 0.75  # cm

STUDENT = "Ғайни Әлихан Саятұлы"
STUDENT_SHORT = "Ғайни Ә.С."
GROUP = "МОиАД-24-1"
PROGRAM = "7М06103 «Машинное обучение и анализ данных»"
TOPIC = ("«Исследование и разработка гибридной системы профориентации на "
         "основе нейронных данных и психологических тестов с использованием "
         "искусственного интеллекта»")


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
       bold=False, space_after=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.0
    if first_line is not None:
        pf.first_line_indent = Cm(first_line)
    if text:
        _font(p.add_run(text), bold=bold)
    return p


def _cell_lines(cell, lines, align=WD_ALIGN_PARAGRAPH.LEFT):
    """Fill a table cell with one paragraph per line (TNR 14)."""
    first = True
    for ln in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.alignment = align
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        _font(p.add_run(ln))


def _signature(doc, left_lines, name, gap_before=0):
    """Borderless 1-row/2-col signature block: position left, name right."""
    t = doc.add_table(rows=1, cols=2)
    t.autofit = False
    t.columns[0].width = Cm(11.0)
    t.columns[1].width = Cm(5.0)
    t.rows[0].cells[0].width = Cm(11.0)
    t.rows[0].cells[1].width = Cm(5.0)
    _cell_lines(t.rows[0].cells[0], left_lines, WD_ALIGN_PARAGRAPH.LEFT)
    _cell_lines(t.rows[0].cells[1], [name], WD_ALIGN_PARAGRAPH.RIGHT)
    if gap_before:
        for c in (0, 1):
            t.rows[0].cells[c].paragraphs[0].paragraph_format.space_before = Pt(gap_before)
    return t


def _tiny_tail(doc):
    """Add a 2 pt trailing paragraph so Word does not push a full empty
    paragraph mark onto a fresh page after the final table."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(2)
    _font(p.add_run(" "))
    p.runs[0].font.size = Pt(1)


def _setup(doc):
    sec = doc.sections[0]
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.0)
    sec.left_margin = Cm(3.0)
    sec.right_margin = Cm(1.0)
    st = doc.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(SIZE)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)


# --------------------------------------------------------------------------- #
def build_otzyv(path):
    doc = Document()
    _setup(doc)

    _p(doc, "Отзыв", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    _p(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, f"о магистерской диссертации магистранта гр. {GROUP}",
       align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, STUDENT, align=WD_ALIGN_PARAGRAPH.CENTER)

    _p(doc,
       "Магистерская диссертация посвящена исследованию и разработке гибридной "
       "системы профессиональной ориентации «NeuroCareer», объединяющей "
       "результаты психологических тестов и нейрофизиологические (ЭЭГ) "
       "показатели для формирования индивидуальных профориентационных "
       "рекомендаций.",
       first_line=FIRST)

    _p(doc,
       "Целью работы является создание и экспериментальная проверка программной "
       "системы, которая на основе совместного анализа психометрических и "
       "нейронных данных ранжирует профессиональные роли и формирует "
       "объяснимые профориентационные рекомендации. Научная новизна состоит в "
       "гибридном объединении разнородных источников данных — результатов "
       "психологических методик и признаков ЭЭГ — в единую воспроизводимую "
       "модель, а также в применении локальной большой языковой модели для "
       "генерации объяснений рекомендаций.",
       first_line=FIRST)

    _p(doc,
       "В теоретической части проведён анализ современных подходов к "
       "профессиональной ориентации, методов искусственного интеллекта и "
       "машинного обучения, психологических тестов и нейронных данных, на "
       "основе которого обоснованы архитектура системы и состав применяемых "
       "методов.",
       first_line=FIRST)

    _p(doc,
       "В практической части разработана шестиуровневая архитектура системы. "
       "На пилотной выборке выполнена кластеризация когнитивных профилей "
       "методом k-средних с выделением трёх устойчивых типов респондентов. Для "
       "компенсации ограниченного объёма выборки реализовано синтетическое "
       "расширение данных методом гауссовой копулы с последующей статистической "
       "валидацией согласия синтетических и реальных распределений. Реализован "
       "слой ранжирования профессиональных ролей со сравнением пяти моделей в "
       "двух режимах валидации; честно показан разрыв между результатами на "
       "синтетических и реальных данных, а анализ значений Шепли подтвердил "
       "доминирующую роль психометрических признаков. Система дополнена базой "
       "знаний профессий, гибридным матчером, компонентом объяснения на основе "
       "локальной языковой модели и пользовательским интерфейсом с экспортом "
       "персонального отчёта.",
       first_line=FIRST)

    _p(doc,
       "Магистерская диссертация выполнена в соответствии с индивидуальным "
       "планом работы магистранта. Все поставленные задачи решены, цель работы "
       "достигнута. Следует отметить выраженную практическую направленность "
       "работы и честную интерпретацию автором полученных результатов с учётом "
       "ограничений объёма выборки. "
       f"{STUDENT} допускается к защите магистерской диссертации по "
       f"образовательной программе {PROGRAM}.",
       first_line=FIRST)

    _signature(doc,
               ["Научный руководитель", "к.т.н., доцент кафедры ИВС"],
               "Томилова Н.И.", gap_before=10)
    _signature(doc,
               ["Научный руководитель", "м.т.н., ст. преподаватель кафедры ИВС"],
               "Кожанов М.Г.", gap_before=8)
    _tiny_tail(doc)

    doc.save(str(path))
    print("wrote", path)


def build_recenzia(path):
    doc = Document()
    _setup(doc)

    _p(doc, "Рецензия", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True)
    _p(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, f"на магистерскую диссертацию магистранта группы {GROUP}",
       align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, STUDENT, align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc, f"по теме: {TOPIC}", align=WD_ALIGN_PARAGRAPH.CENTER)
    _p(doc)

    _p(doc,
       "Представленная магистерская диссертация состоит из введения, шести "
       "основных глав, заключения и списка использованных источников, "
       "дополненных приложениями и иллюстративным материалом в виде таблиц, "
       "рисунков и визуализаций результатов.",
       first_line=FIRST)

    _p(doc,
       "Актуальность исследования обусловлена потребностью в объективных и "
       "персонализированных инструментах профессиональной ориентации. "
       "Объединение психологических методик с нейрофизиологическими данными и "
       "средствами искусственного интеллекта позволяет повысить обоснованность "
       "рекомендаций и снизить субъективность традиционного "
       "профконсультирования, что определяет высокую практическую "
       "востребованность работы. Научная новизна состоит в разработке гибридной "
       "воспроизводимой системы «NeuroCareer», совместно использующей "
       "психометрические и ЭЭГ-признаки для ранжирования профессиональных "
       "ролей, и в применении локальной большой языковой модели для генерации "
       "объяснимых рекомендаций.",
       first_line=FIRST)

    _p(doc,
       "В первой и второй главах систематизированы современные подходы к "
       "профориентации, методы машинного обучения и психологического "
       "тестирования, обоснован выбор инструментов и предложена шестиуровневая "
       "архитектура системы с описанием источников данных и потоков их "
       "обработки.",
       first_line=FIRST)

    _p(doc,
       "В третьей главе описаны пилотная выборка и методология обработки "
       "данных. Проведена кластеризация когнитивных профилей методом k-средних "
       "с выделением трёх типов респондентов; для компенсации ограниченного "
       "объёма выборки реализовано синтетическое расширение данных методом "
       "гауссовой копулы, прошедшее статистическую валидацию согласия с "
       "реальными распределениями.",
       first_line=FIRST)

    _p(doc,
       "В четвёртой главе решена задача ранжирования двадцати профессиональных "
       "ролей. Выполнено сравнение пяти моделей в двух режимах валидации; автор "
       "корректно фиксирует и интерпретирует разрыв между метриками на "
       "синтетических и реальных данных. Анализ значений Шепли показал, что "
       "ключевыми драйверами предсказаний являются психометрические признаки, "
       "тогда как ЭЭГ-признаки играют вспомогательную роль.",
       first_line=FIRST)

    _p(doc,
       "В пятой и шестой главах представлены компонент объяснения рекомендаций "
       "на основе локальной языковой модели с защитой от галлюцинаций, "
       "пользовательский интерфейс с экспортом персонального PDF-отчёта, а "
       "также обсуждение результатов, ограничений, этических и правовых "
       "аспектов применения системы.",
       first_line=FIRST)

    _p(doc,
       f"{STUDENT_SHORT} продемонстрировал владение современным "
       "инструментарием машинного обучения и обработки данных, навыки "
       "критического анализа результатов и способность к самостоятельной "
       "исследовательской работе. Материал изложен последовательно, между "
       "разделами прослеживается чёткая логическая связь.",
       first_line=FIRST)

    _p(doc, "В качестве замечаний предлагается следующее:", first_line=FIRST)

    _p(doc,
       "Выводы об эффективности системы получены преимущественно на пилотной "
       "выборке ограниченного объёма; для практического внедрения целесообразно "
       "расширение выборки реальных респондентов и независимая валидация "
       "рекомендаций.",
       first_line=FIRST)

    _p(doc,
       "Целесообразно более подробно обосновать выбор весовых коэффициентов "
       "гибридного матчера и привести оценку их влияния на итоговые "
       "рекомендации.",
       first_line=FIRST)

    _p(doc,
       "Указанные замечания не снижают общего положительного впечатления от "
       "работы. Поставленная цель достигнута, задачи решены в полном объёме. "
       "Диссертация выполнена на высоком уровне, соответствует требованиям, "
       "предъявляемым к квалификационным работам уровня магистратуры, и "
       "заслуживает оценки «А». "
       f"{STUDENT} заслуживает присвоения академической степени магистра "
       f"технических наук по образовательной программе {PROGRAM}.",
       first_line=FIRST)

    _p(doc)
    _p(doc)
    _signature(doc,
               ["Рецензент",
                "PhD, асс. проф. кафедры ПМИ КарУ имени Е.А. Букетова"],
               "Муратхан Райхан", gap_before=18)
    _tiny_tail(doc)

    doc.save(str(path))
    print("wrote", path)


def to_pdf(docx_path):
    pdf_path = str(Path(docx_path).with_suffix(".pdf"))
    try:
        import win32com.client as win32
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        d = word.Documents.Open(str(docx_path))
        d.SaveAs(pdf_path, FileFormat=17)
        d.Close(False)
        word.Quit()
        print("wrote", pdf_path)
    except Exception as e:  # noqa: BLE001
        print("PDF export skipped:", e)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    otzyv = ROOT / "1 Отзыв Гайни.docx"
    recen = ROOT / "2 Рецензия Гайни.docx"
    build_otzyv(otzyv)
    build_recenzia(recen)
    to_pdf(otzyv)
    to_pdf(recen)


if __name__ == "__main__":
    main()
