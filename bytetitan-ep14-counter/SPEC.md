# SPEC — ByteTitan · Python in 60 Seconds · Ep 14: `collections.Counter`

GOAL:    The viewer leaves knowing `Counter(iterable)` counts in one line, `most_common(n)` ranks, and a missing key returns 0.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps (Instagram Reel)
TIME:    60 s x 30 fps = 1800 frames. Music 120 BPM (beat = 15 frames, bar = 60 frames).

LOOK (theme: "Fun Election Vote Count", live election-night studio, strictly non-political)
- Ground: studio back wall #FFFFFF → #CFD7E1 with 120 px glossy panel seams; light truss and three lamps in the top 230 px.
- Results wall: curved LED wall x 50–1030, y 410–1200, top/bottom edges bowed 70 px; screen #1B3170 → #0A1638, panel seams every 162 px, side shading 55%, glossy top band 16%.
- Team colours (one per fictional candidate): saffron #FF8A1F (Team Mango), teal #13B5A6 (Team Banana), magenta #E0218A (Team Grape). Navy ticker #13265C. Ink #0E1B3D.
- Type: titles Archivo Black 70–100 px; labels/ticker Oswald 600–700 30–40 px; code JetBrains Mono 700 48 px (never under 48 px); captions Archivo Black 64 px.
- Code colours on the wall: keywords #FF6EC7, strings #FFB35C, numbers/results #3DE0CF, calls #7CC4FF.

OBJECTS (all original drawings)
- Fruit mascots running for "Best Snack": Mango (saffron rosette), Banana (teal rosette), Grape (magenta rosette); Kiwi (not on the ballot, the missing key).
- Counter: round white robot, navy visor with teal eyes, chest tally-mark display, magenta antenna bulb, wheel base.
- Tired clerk at a desk with a tally sheet; paper ballot slips with a ticked box; a "BALLOT" box on the anchor desk.
- No real parties, flags, symbols, politicians or logos anywhere.

SAFE ZONES
- Nothing important above y 250 or below y 1570 (Instagram UI). Header 262–392, wall 410–1200, characters to 1330, captions 1336–1460, ticker 1478–1550.

MOTION
- Enter: back.out(1.8–2.4) on pops, power3.out on slides; exit: power2.in/power3.in.
- Code types in with steps(n) clip reveal, 22 ms per character (max 0.5 s).
- Something changes every 1–2 s; LIVE dot blinks every 0.45 s; ticker crawls at 65 px/s for the whole film.

SHOTS (abs. seconds)
- 0.0–3.3  HOOK: BREAKING NEWS bar + "COUNTING VOTES / THE HARD WAY?" on screen at frame 0; emojis pop 0.7; ballots drop into the box 1.55–2.7; mascots peek 1.9.
- 3.3      ticker slide: navy "THE OLD WAY" panel crosses right→left.
- 3.3–13   OLD WAY: 9 code lines type on the VO's words; clerk draws six tally marks (5.4–11.4) as ballots pile; "6 LINES" stamp 9.75; clerk nods off 12.0.
- 13.0     news swoosh: saffron/teal/magenta bands left→right.
- 13–24    COUNTER: robot rolls in 13.3; 3 lines + output 14.4–17.0; chart bars grow 18.5/19.0/19.5 (ding each); "COUNTER: INSTANT TALLY ✅" 20.6.
- 24.0     bar-chart grow wipe.
- 24–36    WINNER: most_common(1) → camera flash 27.0, Mango + WINNER ribbon + confetti; most_common(2) 28.1 → ranked rows 30.15/30.45; "SORTED · HIGHEST FIRST" 31.5.
- 36.0     ballot drop wipe.
- 36–46    STRINGS: Counter("banana"); letter tiles 38.9; drop into b/a/n bins 39.6–41.1; output 41.4; "Works on strings, lists, any iterable" 42.85.
- 46.0     news swoosh right→left.
- 46–54.4  BONUS: count["mango"] → 3; count["kiwi"] → KeyError? chip + buzzer 49.15, struck → 0 at 49.95; safe-check panel 50.9; robot thumbs-up 52.35.
- 54.4     camera flash.
- 54.4–60  OUTRO: logo + BYTETITAN, confetti, "Follow @bytetitan 🐍" 55.2, NEXT card "is vs ==" 56.45, cast pops 57.7, final hit 59.0.

SOUND
- VO: Kokoro hf_alpha (female, Indian-accented), speed 1.2 (hook 1.32, outro 1.35), phrase by phrase; captions are word-timed from the phrase audio.
- Music: original 120 BPM brass-and-drums theme, 0.24 gain, ducked to 0.12 under every VO phrase; the old-way section drops to half-time without brass, the full theme returns with Counter.
- SFX: paper thup per ballot, tally scratch per mark, whoosh on transitions, ding per total, cheer + confetti pop for the winner, buzzer on the KeyError warning.

BANNED: real political imagery of any kind; a dark void ground; glow/neon; everything fading in at once; code under 48 px; text in the top 250 / bottom 350 px.

QA frames: 0 (thumbnail reads), 10.5 (6 LINES), 17.6 (output), 21.5 (chart), 27.4 (winner), 30.8 (ranking), 42.6 (bins), 50.2 (KeyError → 0), 52.8 (safe panel), 58.2 (outro).
