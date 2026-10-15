#!/usr/bin/env bash
# Inventory sweep: every file under research/extracted -> CSV with size, sha256, file type.
# Also produces extension histogram and directory counts for quick statistics.
set -u
ROOT="/home/z/my-project/research/extracted"
OUT="/home/z/my-project/research/inventory"
mkdir -p "$OUT"

CSV="$OUT/files.csv"
: > "$CSV"
echo 'relpath,size_bytes,sha256,filetype' >> "$CSV"

find "$ROOT" -type f | while read -r f; do
  rel="${f#"$ROOT"/}"
  sz=$(stat -c%s "$f")
  ft=$(file -b "$f" | sed 's/,/\;/g' | cut -c1-140)
  h=$(sha256sum "$f" | awk '{print $1}')
  printf '"%s",%s,"%s","%s"\n' "$rel" "$sz" "$h" "$ft" >> "$CSV"
done

# Extension histogram
find "$ROOT" -type f | sed 's/.*\.//' | tr 'A-Z' 'a-z' | sort | uniq -c | sort -rn > "$OUT/ext-histogram.txt"

# Per-directory file counts and sizes
(cd "$ROOT" && du -s --apparent-size . */ 2>/dev/null) | sort -rn > "$OUT/dir-sizes.txt"

# PE binaries list (quick file-type based)
grep -i "PE32\|MS Windows" "$CSV" | cut -d',' -f1 > "$OUT/pe-files.txt"

echo "files inventoried: $(($(wc -l < "$CSV") - 1))"
echo "--- ext histogram (top 25) ---"
head -25 "$OUT/ext-histogram.txt"
