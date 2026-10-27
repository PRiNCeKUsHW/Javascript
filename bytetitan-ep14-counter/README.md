# ByteTitan · Python in 60 Seconds · Ep 14 — `collections.Counter`

60-second vertical Reel (1080x1920, 30 fps) built with [HyperFrames](https://hyperframes.heygen.com).
Theme: a fun election-night results studio where fruit mascots run for "Best Snack" and Counter, a robot, tallies the votes.

```bash
npm install                 # local GSAP (the page loads it from node_modules)
npm run dev                 # preview / edit in the Studio
npm run check               # lint + runtime + layout + contrast
npx hyperframes render -o renders/bytetitan-ep14-counter.mp4
```

## Files

- `index.html` — root: scene hosts, chrome, transitions, captions, and every `<audio>` cue.
- `compositions/` — `studio` (set + curved results wall), `chrome` (logo, LIVE badge, ticker), `fx` (transitions),
  `captions`, and one file per scene: `hook`, `oldway`, `counter`, `winner`, `strings`, `bonus`, `outro`.
- `assets/bytetitan-logo.svg` — **placeholder** mark. Replace it with the channel logo (same file name) and re-render.
- `assets/audio/vo.wav`, `assets/vo_words.json` — voiceover and its word timings.
- `assets/audio/music.wav` — original synthesised news-theme bed. Put a licensed track at `assets/music.mp3` and re-run `tools/build_audio.py` to use it instead.
- `assets/sfx/` — HyperFrames' bundled effects plus synthesised thup, tally scratch, cheer, shutter and buzzer.

## Rebuilding audio and captions

The voice uses Kokoro (the model `npx hyperframes tts` downloads). In a Python venv with `kokoro-onnx soundfile numpy`:

```bash
python tools/build_vo.py        # edit tools/vo_script.json first to change the narration
python tools/build_captions.py  # regenerates compositions/captions.html from the word timings
python tools/build_audio.py     # music + SFX, rewrites the AUDIO block in index.html (music ducked under the voice)
```
