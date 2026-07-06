#!/usr/bin/env python3
"""Считает слова ОСНОВНОГО ТЕКСТА книги, исключая сноски.

Главы обнаруживаются автоматически: все файлы вида [0-9]*.md в директории,
в порядке сортировки имён.

Из подсчёта основного текста исключаются:
  - строки-определения сносок (начинаются с '[^...]:')  -> считаются отдельно
  - inline-маркеры сносок в тексте ('[^...]')
  - блоки кода (raw openxml и т.п.)

Порог книги — 80 000 слов основного текста (без сносок).
"""
import re
import glob
import os

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
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if FOOTNOTE_DEF.match(line):
                fn_words += len(WORD.findall(FOOTNOTE_MARK.sub("", line)))
                continue
            clean = FOOTNOTE_MARK.sub("", line)
            body_words += len(WORD.findall(clean))
    return body_words, fn_words


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(base, "[0-9]*.md")))
    total_body = 0
    total_fn = 0
    print(f"{'Файл':<32}{'Основной':>10}{'Сноски':>10}")
    print("-" * 52)
    for path in files:
        b, f = count_file(path)
        total_body += b
        total_fn += f
        print(f"{os.path.basename(path):<32}{b:>10}{f:>10}")
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
