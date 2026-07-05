#!/usr/bin/env python3
"""Считает слова ОСНОВНОГО ТЕКСТА книги, исключая сноски.

Из подсчёта исключаются:
  - строки-определения сносок (начинаются с '[^...]:')
  - inline-маркеры сносок в тексте ('[^...]')
  - строки метаданных YAML и заголовки Markdown-разметки (#, - оглавления)
  - блоки кода (raw openxml и т.п.)

Порог книги — 80 000 слов основного текста (без сносок).
"""
import re
import sys
import glob
import os

ORDER = [
    "00-введение.md",
    "01-perestroika.md", "02-devyanostye.md", "03-oligarhi.md", "04-preemnik.md",
    "05-vzryvy-voyna.md", "06-televidenie.md", "07-yukos.md", "08-vertikal.md",
    "09-medvedev.md", "10-bolotnaya.md",
    "11-zakruchivanie.md", "12-krym.md", "13-propaganda.md", "14-korrupciya.md", "15-ubijstva.md",
    "16-obnulenie.md", "17-naval-ny.md", "18-vtorzhenie.md", "19-voennoe-obshchestvo.md", "20-prigozhin.md",
    "21-anatomiya.md", "22-budushchee.md",
    "99-zaklyuchenie.md",
]

FOOTNOTE_DEF = re.compile(r'^\s*\[\^[^\]]+\]:')
FOOTNOTE_MARK = re.compile(r'\[\^[^\]]+\]')
WORD = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-’'][A-Za-zА-Яа-яЁё0-9]+)*")


def count_file(path):
    body_words = 0
    fn_words = 0
    in_code = False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            # блоки кода
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            # определения сносок -> считаем отдельно
            if FOOTNOTE_DEF.match(line):
                fn_words += len(WORD.findall(FOOTNOTE_MARK.sub("", line)))
                continue
            # заголовки не исключаем (это часть текста книги), но убираем маркеры
            clean = FOOTNOTE_MARK.sub("", line)
            body_words += len(WORD.findall(clean))
    return body_words, fn_words


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    total_body = 0
    total_fn = 0
    print(f"{'Файл':<32}{'Основной':>10}{'Сноски':>10}")
    print("-" * 52)
    for name in ORDER:
        path = os.path.join(base, name)
        if os.path.exists(path):
            b, f = count_file(path)
            total_body += b
            total_fn += f
            print(f"{name:<32}{b:>10}{f:>10}")
    print("-" * 52)
    print(f"{'ИТОГО основной текст':<32}{total_body:>10}{total_fn:>10}")
    print()
    pct = total_body / 80000 * 100
    print(f"Основной текст: {total_body:,} слов из 80 000 ({pct:.1f}%)")
    print(f"Сноски (сверх зачёта): {total_fn:,} слов")
    remaining = max(0, 80000 - total_body)
    print(f"Осталось написать: {remaining:,} слов")


if __name__ == "__main__":
    main()
