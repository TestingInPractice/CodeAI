#!/usr/bin/env python3
"""Generate 1-page landscape PDF cheat sheet for LLM Testing (based on video 9MWy0M3Wqx8)."""
from fpdf import FPDF
import os

OUT = os.path.join(os.path.dirname(__file__), "llm-testing-cheatsheet.pdf")
R = str.maketrans({"\u2014":"-","\u2013":"-","\u2018":"'","\u2019":"'","\u201c":'"',"\u201d":'"',"\u2192":"->"})
def _(t): return t.translate(R)

pdf = FPDF(orientation="L", unit="mm", format="A4")
pdf.add_font("D", "", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
pdf.add_font("D", "B", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
pdf.add_font("D", "I", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
pdf.add_font("M", "", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
pdf.add_page()
pdf.set_auto_page_break(auto=False)
W, H = 297, 210

pdf.set_fill_color(245, 247, 250)
pdf.rect(0, 0, W, H, "F")

pdf.set_fill_color(30, 60, 114)
pdf.rect(0, 0, W, 20, "F")
pdf.set_text_color(255, 255, 255)
pdf.set_font("D", "B", 14)
pdf.cell(0, 20, _("LLM Testing - Shpargalka dlya QA Engineer"), align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_text_color(100, 100, 100)
pdf.set_font("D", "I", 7)
pdf.cell(0, 4, _("Po motivam video: youtube.com/watch?v=9MWy0M3Wqx8"), align="C", new_x="LMARGIN", new_y="NEXT")

y0, cw, cg = 27, 90, 6
xs = [8, 8+cw+cg, 8+2*(cw+cg)]

def hdr(x, y, t):
    pdf.set_fill_color(42, 87, 141)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("D", "B", 7.5)
    pdf.set_xy(x, y)
    pdf.cell(cw, 5.5, _(t), fill=True)

def bdy(x, y, lines, sz=7):
    pdf.set_text_color(30, 30, 30)
    for i, (st, tx) in enumerate(lines):
        pdf.set_xy(x+1, y+1+i*3.8)
        if st == "b": pdf.set_font("D", "B", sz)
        elif st == "m": pdf.set_font("M", "", sz-1)
        else: pdf.set_font("D", "", sz)
        pdf.cell(cw-2, 3.5, _(tx))

hdr(xs[0], y0, "1. Smena paradigmy: Determinizm -> Veroyatnost")
bdy(xs[0], y0+5.5, [
    ("b", "Bylo (obychnoe testirovanie):"),
    ("", "  Knopka X -> vsegda rezultat Y"),
    ("", "  Tochnoe sovpadenie texta"),
    ("b", "Stalo (LLM testirovanie):"),
    ("", "  Ta zhe mysl -> desyatki formulirovok"),
    ("", "  Proveryaem namerenie, a ne text"),
    ("", ""),
    ("b", "Analogiya dlya sobesedovaniya:"),
    ("", "  Dvigatel (model) na stende"),
    ("", "  vs Avtomobil (sistema) - test-drayv"),
    ("", ""),
    ("b", "3 populyarnyh arhitektury:"),
    ("", "  1. RAG - model-bibliotekar"),
    ("", "  2. Agent - II-menedzher + instrumenty"),
    ("", "  3. Structured output -> JSON"),
])

hdr(xs[1], y0, "2. Tri stolpa kachestva (freymvork)")
bdy(xs[1], y0+5.5, [
    ("b", "  Relevance (Relevantnost)"),
    ("", "    Otvet pomogaet reshit zadachu?"),
    ("", "    Otsekaem krasivyj, no bespoleznyj"),
    ("", ""),
    ("b", "  Faithfulness (Dostovernost)"),
    ("", "    Otvet strogo po predostavlennym"),
    ("", "    dannym. Bez gallyutsinatsij."),
    ("", "    Klyuch k borbe s vydumkami modeli."),
    ("", ""),
    ("b", "  Context Precision (Tochnost kontexta)"),
    ("", "    Kachestvo najdennoj informatsii."),
    ("", "    Ne tot fragment -> nevernyj otvet"),
    ("", "    dazhe u umnoj modeli."),
])

hdr(xs[2], y0, "3. LLM-as-a-Judge + Cheklist")
bdy(xs[2], y0+5.5, [
    ("b", "LLM-as-a-Judge:"),
    ("", "  Silnaya model proveryaet slabuyu."),
    ("", "  Vhod: vopros + otvet + kontext"),
    ("", "  Vyhod: verdikt po 3 stolpam"),
    ("", ""),
    ("b", "Cheklist #1 - Gallyutsinatsii:"),
    ("", "  1. Termin: dostovernost/obosnovannost"),
    ("", "  2. RAG ogranichivaet model dannymi"),
    ("", "  3. LLM-as-a-Judge avtomatiziruet"),
    ("", "  4. Izmeryaem v tsifrah, ne na glazok"),
    ("", ""),
    ("b", "Cheklist #2 - Obshchee ponimanie:"),
    ("", "  1. Determinizm vs Veroyatnost"),
    ("", "  2. Analogiya dvigatel vs avtomobil"),
    ("", "  3. Freymvork 3 stolpov"),
    ("", "  4. Vyvod: smysl, a ne sovpadenie slov"),
])

yb = H - 30
pdf.set_fill_color(30, 60, 114)
pdf.rect(0, yb-1, W, 30, "F")
pdf.set_text_color(255, 255, 255)
pdf.set_font("D", "B", 9)
pdf.set_xy(8, yb)
pdf.cell(0, 5, _("Kratkaya shpargalka dlya finalnoj podgotovki:"), new_x="LMARGIN", new_y="NEXT")

pdf.set_font("D", "", 8)
its = [
    "1. Fokus na sisteme, a ne na modeli",
    "2. Myslim veroyatnostyami",
    "3. Ispolzuem freymvork iz 3 stolpov",
    "4. Znaem, kak avtomatizirovat otsenku (LLM-as-a-Judge)",
    "5. Rol QA Engineer stala strategicheskoj",
]
for i, t in enumerate(its):
    pdf.set_xy(12, yb+5.5+i*4.5)
    pdf.cell(0, 3.8, _(t))

pdf.output(OUT)
print(f"PDF -> {OUT}")
