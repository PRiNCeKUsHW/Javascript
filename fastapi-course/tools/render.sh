#!/usr/bin/env bash
# Render built chapters one after another: tools/render.sh 0 2 3
set -euo pipefail
cd "$(dirname "$0")/.."
for n in "$@"; do
  ch=$(printf "ch%02d" "$n")
  echo "== $ch $(date +%T)"
  (cd "build/$ch" && npx --yes hyperframes@0.8.193 render -o "../../renders/$ch.mp4" --workers 4 2>&1 \
     | sed 's/\x1b\[[0-9;]*m//g' | grep -E "Render complete|failed|Error|MB ·" || true)
  tools/loudnorm.sh "renders/$ch.mp4"
  cp "build/$ch/subtitles.srt" "renders/$ch.srt"
  echo "== $ch done $(date +%T)"
done
