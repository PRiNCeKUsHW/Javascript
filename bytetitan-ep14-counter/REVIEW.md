# REVIEW — Ep 14 delivery render

Render: `renders/bytetitan-ep14-counter.mp4` (not committed) — 1080x1920, 30 fps, 1800 frames, 60.000 s, 14.9 MB.

## Picture (checked on frames pulled from the MP4)
- 0.5 s thumbnail: BREAKING NEWS + "COUNTING VOTES / THE HARD WAY?" fully on screen, inside the 250/350 px safe zones.
- 10.6 s: old-way code (9 lines, 48 px) with the "6 LINES" stamp clear of the code; clerk, tally marks and ballot pile read.
- 13.0 s / 24 s / 36 s / 46 s / 54.4 s: swoosh, bar-chart, ballot-drop, reverse swoosh and camera-flash transitions fully cover their cuts.
- 17.8 s: Counter code and output box separated; robot below the box. 21 s: bars 3/2/1 with mascots, stamp clear of the bars.
- 27.5 s winner + confetti; 31.6 s ranked rows sorted highest first; 40.5 s letters landing in b/a/n bins with live counts.
- 49.4 s KeyError? chip, then → 0; 52.6 s safe-check panel and robot.
- `npx hyperframes check`: passes (0 errors). Remaining warnings are intended: decorative desk/sheen overflow and the ticker crawl.

## Sound (measured, not listened to)
- Integrated −15.5 LUFS, true peak −1.1 dBTP, no clipping.
- Music 0.24, ducked to 0.12 under every voice phrase; effects at 0.2–0.75 on their on-screen actions.

## Known gaps
- Logo is a placeholder (`assets/bytetitan-logo.svg`).
- Music and five effects are synthesised (no music/SFX catalogue reachable from the build machine).
- Voice is Kokoro `hf_alpha`; accent and pronunciation were not checked by ear.
- Outro starts at 54.4 s (not 55 s) so the "Follow ByteTitan…" line fits before 60 s.
