#!/usr/bin/env bash
# Wait for each chapter build to finish, lint it, then render it: tools/pipeline.sh 3 4 5 ...
set -uo pipefail
cd "$(dirname "$0")/.."
for n in "$@"; do
  ch=$(printf "ch%02d" "$n")
  until grep -qh "^$ch: .* scenes" build/build_*.log 2>/dev/null; do sleep 20; done
  (cd "build/$ch" && npx --yes hyperframes@0.8.193 check --json > "../check_$ch.json" 2>/dev/null)
  ok=$(python3 -c "import json;d=json.load(open('build/check_$ch.json'));print(d['ok'], d['lint']['errorCount'])" 2>&1)
  echo "== $ch check: $ok"
  tools/render.sh "$n"
done
