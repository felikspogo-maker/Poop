#!/usr/bin/env python3
"""Собирает альтернативную версию книги, где сноски вынесены ВИДИМЫМ текстом
в конец каждой главы (раздел «Источники»), а в тексте остаются надстрочные
номера. Такая версия читается в любом приложении, включая те, что не
поддерживают сноски Word.

Выход: Россия-после-империи-источники-в-тексте.docx
"""
import re
import glob
import os
import subprocess
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
FN_DEF = re.compile(r'^\s*\[\^([^\]]+)\]:\s*(.*)$')
FN_REF = re.compile(r'\[\^([^\]]+)\]')

PAGEBREAK = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'


def process_chapter(path):
    body_lines = []
    defs = {}  # id -> text
    for line in open(path, encoding='utf-8'):
        m = FN_DEF.match(line)
        if m:
            defs[m.group(1)] = m.group(2).strip()
        else:
            body_lines.append(line.rstrip('\n'))

    # порядок нумерации — по первому появлению ссылки в тексте
    order = []
    seen = set()
    for line in body_lines:
        for fid in FN_REF.findall(line):
            if fid not in seen:
                seen.add(fid)
                order.append(fid)
    # добавить определения, на которые нет ссылок (на всякий случай)
    for fid in defs:
        if fid not in seen:
            order.append(fid)
            seen.add(fid)

    num = {fid: i + 1 for i, fid in enumerate(order)}

    # заменить ссылки в тексте на надстрочный номер
    def repl(m):
        fid = m.group(1)
        n = num.get(fid)
        return f'^{n}^' if n else ''
    new_body = [FN_REF.sub(repl, line) for line in body_lines]

    text = '\n'.join(new_body).rstrip() + '\n'

    # добавить раздел «Источники», если есть сноски
    if order:
        text += '\n\n### Источники\n\n'
        for fid in order:
            n = num[fid]
            src = defs.get(fid, '(источник не указан)')
            text += f'{n}. {src}\n\n'
    return text


def main():
    files = sorted(glob.glob(os.path.join(BASE, '[0-9]*.md')))
    parts = [process_chapter(f) for f in files]
    combined = PAGEBREAK.join(parts)

    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False,
                                     encoding='utf-8') as tmp:
        tmp.write(combined)
        tmp_path = tmp.name

    out = os.path.join(BASE, 'Россия-после-империи-источники-в-тексте.docx')
    subprocess.run([
        'pandoc',
        os.path.join(BASE, 'metadata.yaml'), tmp_path,
        '--from=markdown',
        '--toc', '--toc-depth=2',
        '-o', out,
    ], check=True)
    os.unlink(tmp_path)
    print('Готово:', out)


if __name__ == '__main__':
    main()
