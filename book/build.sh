#!/usr/bin/env bash
# Сборка книги из глав в единый файл .docx через pandoc.
# Использование: bash build.sh
set -euo pipefail

cd "$(dirname "$0")"

OUT="Россия-после-империи.docx"
TMP="$(mktemp)"

# Порядок глав
FILES=(
  00-введение.md
  01-perestroika.md
  02-devyanostye.md
  03-oligarhi.md
  04-preemnik.md
  05-vzryvy-voyna.md
  06-televidenie.md
  07-yukos.md
  08-vertikal.md
  09-medvedev.md
  10-bolotnaya.md
  11-zakruchivanie.md
  12-krym.md
  13-propaganda.md
  14-korrupciya.md
  15-ubijstva.md
  16-obnulenie.md
  17-naval-ny.md
  18-vtorzhenie.md
  19-voennoe-obshchestvo.md
  20-prigozhin.md
  21-anatomiya.md
  22-budushchee.md
  99-zaklyuchenie.md
)

# Разрыв страницы между главами (raw OpenXML для docx)
PAGEBREAK=$'\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'

first=1
for f in "${FILES[@]}"; do
  if [[ -f "$f" ]]; then
    if [[ $first -eq 0 ]]; then
      printf '%s' "$PAGEBREAK" >> "$TMP"
    fi
    cat "$f" >> "$TMP"
    printf '\n\n' >> "$TMP"
    first=0
  fi
done

pandoc metadata.yaml "$TMP" \
  --from=markdown \
  --toc --toc-depth=2 \
  --top-level-division=default \
  -o "$OUT"

rm -f "$TMP"
echo "Готово: $OUT"
ls -la "$OUT"
