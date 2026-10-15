#!/usr/bin/env bash
# Download the four EaseUS DRW source files from R2, verify, and produce a manifest.
# Records expected sizes from HEAD probes (recorded 2026-10-15):
#   EaseUS-DRW-Part-1.zip  183446644
#   EaseUS-DRW-Part-2.zip  171613300
#   DRW-mac-installer.dmg    4808563
#   DRW-win-installer.exe    2837784
set -u
BASE="/home/z/my-project/research/downloads"
mkdir -p "$BASE"
cd "$BASE" || exit 1

BASE_URL="https://pub-f1a27c5e49e74a6f8f15960475387544.r2.dev"

declare -A FILES=(
  ["EaseUS-DRW-Part-1.zip"]="$BASE_URL/EaseUS-Data-Recovery-Wizard-Part-1.zip"
  ["EaseUS-DRW-Part-2.zip"]="$BASE_URL/EaseUS-Data-Recovery-Wizard-Part-2.zip"
  ["DRW-mac-installer.dmg"]="$BASE_URL/datarecovery_free_Setup_20261015.17920523914876b6212563apz27289351.dmg"
  ["DRW-win-installer.exe"]="$BASE_URL/drw_fr_installer.17920523404316b6212556apz27289349.exe"
)

declare -A EXPECTED=(
  ["EaseUS-DRW-Part-1.zip"]=183446644
  ["EaseUS-DRW-Part-2.zip"]=171613300
  ["DRW-mac-installer.dmg"]=4808563
  ["DRW-win-installer.exe"]=2837784
)

download_one() {
  local name="$1" url="$2"
  if [ -f "$name.done" ]; then
    echo "[skip] $name already complete"
    return 0
  fi
  echo "[dl ] $name ..."
  if curl -fsSL --retry 5 --retry-delay 5 -C - -o "$name.part" "$url"; then
    mv -f "$name.part" "$name"
    local sz
    sz=$(stat -c%s "$name")
    if [ "$sz" -eq "${EXPECTED[$name]}" ]; then
      touch "$name.done"
      echo "[ok ] $name ($sz bytes, size matches)"
    else
      echo "[WARN] $name size $sz != expected ${EXPECTED[$name]}"
      echo "$sz" > "$name.badsize"
    fi
  else
    echo "[FAIL] $name download error"
  fi
}

# Launch all four in parallel
for name in "${!FILES[@]}"; do
  download_one "$name" "${FILES[$name]}" &
done
wait

# Manifest with sha256
: > MANIFEST.txt
for name in EaseUS-DRW-Part-1.zip EaseUS-DRW-Part-2.zip DRW-mac-installer.dmg DRW-win-installer.exe; do
  if [ -f "$name" ]; then
    sz=$(stat -c%s "$name")
    h=$(sha256sum "$name" | awk '{print $1}')
    printf '%s\t%s\t%s\n' "$name" "$sz" "$h" >> MANIFEST.txt
  fi
done
touch ALL_DONE
echo "=== MANIFEST ==="
cat MANIFEST.txt
