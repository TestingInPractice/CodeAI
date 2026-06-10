#!/usr/bin/env python3
"""Генератор PDF-шпаргалки по тестированию LLM (1 лист, landscape)."""
from fpdf import FPDF
import os

OUT = os.path.join(os.path.dirname(__file__), "llm-testing-cheatsheet.pdf")

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
pdf.cell(0, 20, "LLM-тестирование — Шпаргалка для QA Engineer", align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_text_color(100, 100, 100)
pdf.set_font("D", "I", 7)
pdf.cell(0, 4, "По мотивам видео: youtube.com/watch?v=9MWy0M3Wqx8", align="C", new_x="LMARGIN", new_y="NEXT")

y0, cw, cg = 27, 90, 6
xs = [8, 8+cw+cg, 8+2*(cw+cg)]

def hdr(x, y, t):
    pdf.set_fill_color(42, 87, 141)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("D", "B", 7.5)
    pdf.set_xy(x, y)
    pdf.cell(cw, 5.5, t, fill=True)

def bdy(x, y, lines, sz=7):
    pdf.set_text_color(30, 30, 30)
    for i, (st, tx) in enumerate(lines):
        pdf.set_xy(x+1, y+1+i*3.8)
        if st == "b": pdf.set_font("D", "B", sz)
        elif st == "m": pdf.set_font("M", "", sz-1)
        else: pdf.set_font("D", "", sz)
        pdf.cell(cw-2, 3.5, tx)

hdr(xs[0], y0, "1. Смена парадигмы: детерминизм → вероятность")
bdy(xs[0], y0+5.5, [
    ("b", "Было (обычное тестирование):"),
    ("", "  Кнопка X → всегда результат Y"),
    ("", "  Точное совпадение текста"),
    ("b", "Стало (LLM-тестирование):"),
    ("", "  Мысль → десятки формулировок"),
    ("", "  Проверяем намерение, а не текст"),
    ("", ""),
    ("b", "Аналогия для собеседования:"),
    ("", "  Двигатель (модель) на стенде"),
    ("", "  vs Автомобиль (система) — тест-драйв"),
    ("", ""),
    ("b", "3 популярных архитектуры:"),
    ("", "  1. RAG — модель-библиотекарь"),
    ("", "  2. Agent — ИИ-менеджер + инструменты"),
    ("", "  3. Структурированный вывод → JSON"),
])

hdr(xs[1], y0, "2. Три столпа качества (фреймворк)")
bdy(xs[1], y0+5.5, [
    ("b", "  Релевантность (Relevance)"),
    ("", "    Ответ помогает решить задачу?"),
    ("", "    Отсекаем красивый, но бесполезный"),
    ("", "    ответ"),
    ("", ""),
    ("b", "  Достоверность (Faithfulness)"),
    ("", "    Ответ строго по предоставленным"),
    ("", "    данным. Без галлюцинаций."),
    ("", "    Ключ к борьбе с выдумками модели."),
    ("", ""),
    ("b", "  Точность контекста (Context Precision)"),
    ("", "    Корректность найденной информации."),
    ("", "    Не тот фрагмент → неверный ответ"),
    ("", "    даже у умной модели."),
])

hdr(xs[2], y0, "3. LLM-as-a-Judge + Чеклист")
bdy(xs[2], y0+5.5, [
    ("b", "LLM-as-a-Judge:"),
    ("", "  Сильная модель проверяет слабую."),
    ("", "  Вход: вопрос + ответ + контекст"),
    ("", "  Выход: вердикт по 3 столпам"),
    ("", ""),
    ("b", "Чеклист №1 — Галлюцинации:"),
    ("", "  1. Термин: достоверность/обоснованность"),
    ("", "  2. RAG ограничивает модель данными"),
    ("", "  3. LLM-as-a-Judge автоматизирует"),
    ("", "  4. Измеряем в цифрах, а не на глазок"),
    ("", ""),
    ("b", "Чеклист №2 — Общее понимание:"),
    ("", "  1. Детерминизм vs Вероятность"),
    ("", "  2. Аналогия: двигатель vs автомобиль"),
    ("", "  3. Фреймворк 3 столпов"),
    ("", "  4. Вывод: смысл, а не совпадение слов"),
])

yb = H - 30
pdf.set_fill_color(30, 60, 114)
pdf.rect(0, yb-1, W, 30, "F")
pdf.set_text_color(255, 255, 255)
pdf.set_font("D", "B", 9)
pdf.set_xy(8, yb)
pdf.cell(0, 5, "Краткая шпаргалка для финальной подготовки:", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("D", "", 8)
items = [
    "1. Фокус на системе, а не на модели",
    "2. Мыслим вероятностями",
    "3. Используем фреймворк из 3 столпов",
    "4. Знаем, как автоматизировать оценку (LLM-as-a-Judge)",
    "5. Роль QA Engineer стала стратегической",
]
for i, t in enumerate(items):
    pdf.set_xy(12, yb+5.5+i*4.5)
    pdf.cell(0, 3.8, t)

pdf.output(OUT)
print(f"PDF -> {OUT}")
