"""Collapse the table of contents of dissertation_l.docx to ~1 page.

Operates DIRECTLY on the hand-edited master `reports/dissertation_l.docx`
(NOT regenerated from the content scripts — manual edits must be kept).

What it does:
  1. Merges 48 sub-sections into 24 (4 per chapter). The first sub-section of
     each merge group stays a numbered Heading 2 (visible in the contents);
     the rest are demoted to Heading 3 "подпункты" (visible in the text, but
     NOT in the contents). All "Выводы по главе N" are also demoted.
  2. Strips the numbers from demoted sub-headings and from former level-3 items.
  3. Switches the TOC field from \o "1-3" to \o "1-2" so podpункты never come
     back on update.
  4. Excludes the "Содержание" title from its own contents (outline level 9).
  5. Updates the TOC field via Word COM, tightens it, repaginates, exports PDF,
     prints page/word statistics.

Run with:
  PYTHONIOENCODING=utf-8 <python310> -X utf8 14_collapse_toc.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parents[1] / "reports"
DOCX = str(ROOT / "dissertation_l.docx")
PDF = str(ROOT / "dissertation_l.pdf")

# original heading text (stripped)  ->  (level, new text)
#   "H2" = keep / become numbered sub-section in the contents
#   "H3" = demote to подпункт (in text, not in contents)
MAP = {
    # ---- Chapter 1 ----
    "Историческое развитие профориентации":
        ("H2", "1.1 Развитие и современные подходы к профориентации"),
    "1.2 Современные подходы к профориентации":
        ("H3", "Современные подходы к профориентации"),
    "1.3 Искусственный интеллект и машинное обучение в профориентации":
        ("H2", "1.2 Искусственный интеллект и машинное обучение в профориентации"),
    "1.4 Психологические тесты в профориентационной практике":
        ("H2", "1.3 Психологические тесты и нейронные данные"),
    "1.4.1 Тесты типологии личности (MBTI, «Большая пятёрка»)":
        ("H3", "Тесты типологии личности (MBTI, «Большая пятёрка»)"),
    "1.4.2 Тесты профессиональных интересов (RIASEC, ДДО Климова)":
        ("H3", "Тесты профессиональных интересов (RIASEC, ДДО Климова)"),
    "1.4.3 Тест множественного интеллекта Г. Гарднера":
        ("H3", "Тест множественного интеллекта Г. Гарднера"),
    "1.4.4 Тесты способностей и мотивации":
        ("H3", "Тесты способностей и мотивации"),
    "1.5 Нейронные данные в задачах профориентации":
        ("H3", "Нейронные данные в задачах профориентации"),
    "1.6 Постановка задачи и требования к системе":
        ("H2", "1.4 Постановка задачи и сравнительный анализ инструментов"),
    "1.7 Гибридные профориентационные системы":
        ("H3", "Гибридные профориентационные системы"),
    "1.8 Сравнительный анализ методик и обоснование выбора инструментов":
        ("H3", "Сравнительный анализ методик и обоснование выбора инструментов"),
    "Выводы по главе 1": ("H3", "Выводы по главе 1"),
    # ---- Chapter 2 ----
    "2.1 Шестиуровневая архитектура системы":
        ("H2", "2.1 Шестиуровневая архитектура системы"),
    "2.2 Источники данных и признаковое пространство":
        ("H2", "2.2 Источники данных и признаковое пространство"),
    "2.3 Алгоритмический состав уровней":
        ("H2", "2.3 Алгоритмический состав и поток данных"),
    "2.4 Поток данных в системе": ("H3", "Поток данных в системе"),
    "2.5 Интерфейсы взаимодействия между модулями":
        ("H3", "Интерфейсы взаимодействия между модулями"),
    "2.6 Обоснование выбора инструментов реализации":
        ("H2", "2.4 Обоснование выбора инструментов реализации"),
    "Выводы по главе 2": ("H3", "Выводы по главе 2"),
    # ---- Chapter 3 ----
    "3.1 Пилотная выборка": ("H2", "3.1 Пилотная выборка"),
    "3.1.1 Описательная статистика психометрических признаков":
        ("H3", "Описательная статистика психометрических признаков"),
    "3.1.2 Описательная статистика ЭЭГ-признаков":
        ("H3", "Описательная статистика ЭЭГ-признаков"),
    "3.2 Воспроизведение кластеризации когнитивных профилей":
        ("H2", "3.2 Кластеризация когнитивных профилей"),
    "3.3 Синтетическое расширение выборки":
        ("H2", "3.3 Синтетическое расширение выборки и её валидация"),
    "3.4 Валидация согласия синтетических и реальных данных":
        ("H3", "Валидация согласия синтетических и реальных данных"),
    "3.5 Этические и методологические аспекты использования синтетики":
        ("H2", "3.4 Методологические аспекты и воспроизводимость"),
    "3.6 Воспроизводимость обработки данных":
        ("H3", "Воспроизводимость обработки данных"),
    "Выводы по главе 3": ("H3", "Выводы по главе 3"),
    # ---- Chapter 4 ----
    "4.1 Постановка задачи ранжирования профессиональных ролей":
        ("H2", "4.1 Постановка задачи и сравнение моделей ранжирования"),
    "4.2 Сравнение пяти моделей ранжирования":
        ("H3", "Сравнение пяти моделей ранжирования"),
    "4.3 Два режима валидации":
        ("H2", "4.2 Валидация и анализ значений Шепли"),
    "4.4 Анализ значений Шепли": ("H3", "Анализ значений Шепли"),
    "4.4.1 Пер-ролевой анализ драйверов предсказания":
        ("H3", "Пер-ролевой анализ драйверов предсказания"),
    "4.5 База знаний профессий":
        ("H2", "4.3 База знаний профессий и гибридный матчер"),
    "4.6 Гибридный матчер": ("H3", "Гибридный матчер"),
    "4.7 Результаты рекомендаций на пилотной выборке":
        ("H2", "4.4 Результаты рекомендаций и их сопоставление"),
    "4.8 Сопоставление полученных результатов с известными работами":
        ("H3", "Сопоставление полученных результатов с известными работами"),
    "Выводы по главе 4": ("H3", "Выводы по главе 4"),
    # ---- Chapter 5 ----
    "5.1 Двухбэкендный компонент объяснения":
        ("H2", "5.1 Компонент объяснения рекомендаций"),
    "5.2 Структура промпта и защита от галлюцинаций":
        ("H3", "Структура промпта и защита от галлюцинаций"),
    "5.3 Пример сгенерированного объяснения":
        ("H3", "Пример сгенерированного объяснения"),
    "5.4 Пользовательский интерфейс":
        ("H2", "5.2 Пользовательский интерфейс и экспорт отчёта"),
    "5.5 Экспорт персонального PDF-отчёта":
        ("H3", "Экспорт персонального PDF-отчёта"),
    "5.6 Сценарий демонстрации работы системы":
        ("H2", "5.3 Сценарий демонстрации работы системы"),
    "5.7 Сравнение шаблонного и LLM-режимов генерации":
        ("H2", "5.4 Режимы генерации и сценарии пользователей"),
    "5.8 Сценарии работы для разных категорий пользователей":
        ("H3", "Сценарии работы для разных категорий пользователей"),
    "Выводы по главе 5": ("H3", "Выводы по главе 5"),
    # ---- Chapter 6 ----
    "6.1 Содержательная интерпретация ключевых результатов":
        ("H2", "6.1 Интерпретация результатов и ограничения выборки"),
    "6.2 Ограничения, обусловленные объёмом выборки":
        ("H3", "Ограничения, обусловленные объёмом выборки"),
    "6.3 Ограничения, обусловленные структурой целевой переменной":
        ("H3", "Ограничения, обусловленные структурой целевой переменной"),
    "6.4 Ограничения, обусловленные базой знаний профессий":
        ("H2", "6.2 База знаний и этические аспекты"),
    "6.5 Этические аспекты": ("H3", "Этические аспекты"),
    "6.6 Перспективы развития": ("H2", "6.3 Перспективы развития"),
    "6.7 Правовые аспекты использования системы в Республике Казахстан":
        ("H2", "6.4 Правовые аспекты использования системы"),
    "6.8 Технологические перспективы развития":
        ("H3", "Технологические перспективы развития"),
    "Выводы по главе 6": ("H3", "Выводы по главе 6"),
}


def _set_text(p, text: str) -> None:
    """Replace the paragraph text, keeping the first run's formatting."""
    runs = p.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def _set_outline_body(p) -> None:
    """Force outline level 9 (body text) so the paragraph is not in the TOC."""
    pPr = p._p.get_or_add_pPr()
    for old in pPr.findall(qn("w:outlineLvl")):
        pPr.remove(old)
    lvl = OxmlElement("w:outlineLvl")
    lvl.set(qn("w:val"), "9")
    pPr.append(lvl)


def transform() -> dict:
    doc = Document(DOCX)
    h2 = doc.styles["Heading 2"]
    h3 = doc.styles["Heading 3"]
    stats = {"H2": 0, "H3": 0, "missed": []}
    seen = set()

    for p in doc.paragraphs:
        st = p.style.name
        txt = p.text.strip()
        if st == "Heading 1" and txt == "Содержание":
            _set_outline_body(p)
            continue
        if st not in ("Heading 2", "Heading 3"):
            continue
        if txt in MAP:
            level, new = MAP[txt]
            p.style = h2 if level == "H2" else h3
            _set_text(p, new)
            stats[level] += 1
            seen.add(txt)

    for key in MAP:
        if key not in seen:
            stats["missed"].append(key)

    # switch the TOC field to levels 1-2 only
    for instr in doc.element.body.iter(qn("w:instrText")):
        if instr.text and "TOC" in instr.text and '\\o "1-3"' in instr.text:
            instr.text = instr.text.replace('\\o "1-3"', '\\o "1-2"')
            stats["toc_field"] = instr.text.strip()

    doc.save(DOCX)
    return stats


def finalize() -> None:
    import win32com.client as win32
    WD_SINGLE = 0
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    d = word.Documents.Open(DOCX)
    try:
        for toc in d.TablesOfContents:
            toc.Update()
        d.Fields.Update()
        n_toc = 0
        for p in d.Paragraphs:
            nm = p.Style.NameLocal.lower()
            if nm.startswith("toc") or nm.startswith("оглавление") or nm.startswith("содержание"):
                pf = p.Format
                pf.LineSpacingRule = WD_SINGLE
                pf.SpaceBefore = 0
                pf.SpaceAfter = 0
                fnt = p.Range.Font
                fnt.Name = "Times New Roman"
                fnt.Size = 14
                n_toc += 1
        d.Repaginate()
        pages = d.ComputeStatistics(2)
        words = d.ComputeStatistics(0)
        d.Save()
        d.SaveAs(PDF, FileFormat=17)
    finally:
        d.Close(False)
        word.Quit()
    print(f"TOC paragraphs reformatted: {n_toc}")
    print(f"PAGES: {pages}   WORDS: {words}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    s = transform()
    print("Heading 2 kept:", s["H2"], " Heading 3 demoted:", s["H3"])
    print("TOC field:", s.get("toc_field"))
    if s["missed"]:
        print("!! NOT MATCHED:")
        for m in s["missed"]:
            print("   ", m)
    finalize()


if __name__ == "__main__":
    main()
