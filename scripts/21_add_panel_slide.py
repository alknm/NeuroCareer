# -*- coding: utf-8 -*-
"""Insert a 'control panel (sidebar)' explanation slide before the live-demo
slides. Left: anonymized sidebar screenshot. Right: detailed explanation of
every section. Reuses style helpers from 18_build_slides.py; edits deck in place.
"""
import sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "system" / "scripts"
SHOTS = ROOT / "system" / "reports" / "figures" / "app_shots"
DECK = ROOT / "disser_final" / "Презентация_Ғайни Ә.С._ МОиАД-24-1.pptx"

spec = importlib.util.spec_from_file_location("build18", SCRIPTS / "18_build_slides.py")
b = importlib.util.module_from_spec(spec)
sys.modules["build18"] = b
spec.loader.exec_module(b)

from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN

INK, SUB, ACCENT = b.INK, b.SUB, b.ACCENT


def main():
    prs = Presentation(str(DECK))
    n0 = len(prs.slides)

    s = b.new_slide(prs, 0)
    b.title(s, "Панель управления системой (боковая панель)")

    # left: sidebar screenshot
    b.pic_fit(s, SHOTS / "vp_sidebar.png", 0.7, 1.55, 2.3, 5.7, frame=True)

    # right: detailed explanation
    _, tf = b.textbox(s, 3.3, 1.62, 9.4, 5.6)

    def para(first=False):
        return tf.paragraphs[0] if first else tf.add_paragraph()

    def head_body(p, head, body, size=14):
        b._run(p, head, size, ACCENT, bold=True)
        if body:
            b._run(p, body, size, INK)
        p.space_after = Pt(6); p.line_spacing = 1.04

    def sub(p, text, size=13):
        b._run(p, "   •  ", size, ACCENT, bold=True)
        b._run(p, text, size, INK)
        p.space_after = Pt(3); p.line_spacing = 1.04

    p = para(True)
    head_body(p, "Боковая панель — единая точка управления. ",
              "Пользователь задаёт вход, настраивает модель и сразу видит "
              "пересчёт результата.", size=14)

    head_body(para(), "Язык интерфейса — ",
              "двуязычный режим (русский/английский); рекомендации и объяснения "
              "формируются на выбранном языке.")

    head_body(para(), "1. Источник профиля — ",
              "три способа задать входные данные:")
    sub(para(), "Пилотный респондент (n=47) — реальный респондент из пилотной "
                "выборки, для демонстрации на защите;")
    sub(para(), "Загрузить Neiry-выгрузку (.xlsx/.csv) — файл с теми же 65 "
                "признаками для нового пользователя;")
    sub(para(), "Пройти короткий онлайн-тест — ввод профиля без нейрогарнитуры.")

    head_body(para(), "2. Веса компонентов — ",
              "вклад каждого источника в итоговую оценку: Гарднер 0,30, MBTI 0,20, "
              "кластер 0,10, роли 0,40 (сумма нормализуется к 1,00). Сдвиг ползунка "
              "мгновенно пересчитывает рекомендации — параметры системы открыты "
              "и настраиваемы, а не скрыты.")

    head_body(para(), "3. LLM-объяснитель — ",
              "выбор движка текстовых объяснений: auto (автовыбор), ollama "
              "(локальная языковая модель) или template (детерминированный "
              "шаблон-фолбэк, работает без интернета).")

    # bottom note
    _, tf2 = b.textbox(s, 0.7, 7.02, 12.0, 0.42)
    pn = tf2.paragraphs[0]; pn.alignment = PP_ALIGN.CENTER
    b._run(pn, "Снимок экрана работающего веб-приложения (Streamlit). "
               "Данные респондента обезличены.", 11, SUB, italic=True)

    # move appended slide to position 14 (index 13), before the demo slides
    lst = prs.slides._sldIdLst
    nodes = list(lst)
    new = nodes[n0]
    lst.remove(new)
    lst.insert(13, new)

    prs.save(str(DECK))
    print("saved deck with", len(prs.slides), "slides (was", n0, ")")


if __name__ == "__main__":
    main()
