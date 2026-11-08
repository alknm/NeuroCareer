# -*- coding: utf-8 -*-
"""Insert two 'live system demo' slides (real Streamlit screenshots) into the
defense deck, right after the interface slide (#13). Reuses the visual style
helpers from 18_build_slides.py and edits the existing pptx in place so any
manual edits to other slides are preserved.

Run with the interpreter that has python-pptx + Pillow installed.
"""
import sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "system" / "scripts"
SHOTS = ROOT / "system" / "reports" / "figures" / "app_shots"
DECK = ROOT / "disser_final" / "Презентация_Ғайни Ә.С._ МОиАД-24-1.pptx"

# --- import the style helpers from the (digit-prefixed) build script ---------
spec = importlib.util.spec_from_file_location("build18", SCRIPTS / "18_build_slides.py")
b = importlib.util.module_from_spec(spec)
sys.modules["build18"] = b
spec.loader.exec_module(b)

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

INK, SUB, ACCENT = b.INK, b.SUB, b.ACCENT


def caption(slide, left, top, w, text):
    _, tf = b.textbox(slide, left, top, w, 0.5)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    b._run(p, text, 12.5, SUB, italic=True)


def two_up(prs, variant, title_text, left_img, left_cap, right_img, right_cap):
    s = b.new_slide(prs, variant)
    b.title(s, title_text)
    band_top, band_h = 1.62, 4.78
    colw = 6.02
    lx, rx = 0.5, 6.81
    b.pic_fit(s, left_img, lx, band_top, colw, band_h, frame=True)
    b.pic_fit(s, right_img, rx, band_top, colw, band_h, frame=True)
    caption(s, lx, band_top + band_h + 0.06, colw, left_cap)
    caption(s, rx, band_top + band_h + 0.06, colw, right_cap)
    # bottom note
    _, tf = b.textbox(s, 0.7, 7.02, 12.0, 0.42)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    b._run(p, "Снимки экрана работающего веб-приложения (Streamlit). "
              "Данные респондента обезличены.", 11, SUB, italic=True)
    return s


def main():
    prs = Presentation(str(DECK))
    n0 = len(prs.slides)

    # Slide A: profile + neuro-data
    two_up(prs, 0,
           "Работающая система: профиль и нейроданные",
           str(SHOTS / "vp_overview.png"),
           "Боковая панель ввода и радар-профиль интеллектов Гарднера",
           str(SHOTS / "vp_neiry.png"),
           "ЭЭГ-индексы Neiry: спектр, эмоциональные маркеры, baseline vs actual")

    # Slide B: recommendations + explanation
    two_up(prs, 1,
           "Работающая система: рекомендации и разбор",
           str(SHOTS / "vp_recommendations.png"),
           "Топ-рекомендации с разложением итогового скора по компонентам",
           str(SHOTS / "vp_detail.png"),
           "Детальный разбор: совпадения по интеллектам, MBTI и ролям")

    # The two new slides are appended at the end. Interface slide is #13
    # (index 12). Place the demos right after it -> positions 14 and 15.
    lst = prs.slides._sldIdLst
    nodes = list(lst)
    new_a, new_b = nodes[n0], nodes[n0 + 1]   # references to the appended slides
    lst.remove(new_a); lst.remove(new_b)
    lst.insert(13, new_a)                      # -> position 14 (after interface)
    new_a.addnext(new_b)                       # -> position 15, immediately after A

    prs.save(str(DECK))
    order = []
    for i, s in enumerate(prs.slides, 1):
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                order.append(f"{i:2d}. {sh.text_frame.text.strip().splitlines()[0][:45]}")
                break
    print("saved deck with", len(prs.slides), "slides (was", n0, ")")
    print("\n".join(order))


if __name__ == "__main__":
    main()
