#!/usr/bin/env bash
# Сборка книги из глав в единый файл .docx через pandoc.
# Главы обнаруживаются автоматически: все *.md, кроме README.md,
# в порядке сортировки имён (00-, 01-, ... 08-, 08b-, 09-, ... 99-).
set -euo pipefail

cd "$(dirname "$0")"

OUT="Россия-после-империи.docx"
TMP="$(mktemp)"

mapfile -t FILES < <(ls -1 [0-9]*.md | sort)

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
echo "Собрано глав: ${#FILES[@]}"
echo "Готово: $OUT"
ls -la "$OUT"
