#!/usr/bin/env bash
# Normalise a rendered MP4 to YouTube loudness (-14 LUFS, -1.5 dBTP), video stream copied
set -euo pipefail
f="$1"; tmp="${f%.mp4}.norm.mp4"
ffmpeg -v error -y -i "$f" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k -movflags +faststart "$tmp"
mv "$tmp" "$f"
