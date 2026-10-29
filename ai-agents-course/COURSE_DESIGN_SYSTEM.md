# Course Design System — "Agent Console"

Chosen for an international developer audience watching long technical lessons: a calm, dark,
high-contrast developer look where **code and diagrams are the hero**. Decoration is limited to a
faint dot grid, two slow ambient glows and one signature motif. Source of truth for values:
`studio/src/theme.ts`.

## Signature motif

**The agent loop ring** (`AgentLoop` component): four nodes, Think, Act, Observe, Repeat, slowly
orbiting a soft teal core. It appears on lesson title cards and thumbnails and ties every module back to
the course's central idea. Project lessons may relabel the nodes (e.g. Plan · Model · Validate · Report).

## Colour

| Token | Hex | Meaning |
|---|---|---|
| `ink` | `#0A0E17` | background |
| `surface` / `surface2` | `#131A29` / `#1A2335` | cards, panels |
| `line` | `#28344D` | borders, idle edges |
| `text` / `muted` / `faint` | `#E9EEF8` / `#93A0BA` / `#5C6884` | text hierarchy |
| `teal` | `#2EE6A8` | **primary**: the agent, success, correct answers, active data flow |
| `amber` | `#FFB547` | attention: highlighted code lines, emphasis, quiz badge |
| `blue` | `#6CA8FF` | information, terminals, data |
| `violet` | `#B595FF` | the language model |
| `coral` | `#FF6B7A` | errors, wrong answers, "avoid" panels |

Colour always carries meaning (the model is violet, errors are coral) and is never the only signal:
icons, labels ("Avoid"/"Prefer") and position repeat it.

## Typography

- **Inter** (OFL): headings 52–104 px ExtraBold, tight tracking; body 33–42 px.
- **JetBrains Mono** (OFL): code 22–32 px, auto-sized so the longest line fits; ligatures disabled
  so `==`, `->`, `!=` look exactly as typed.
- Minimum on-screen size: 22 px code and 22 px labels at 1080p. Project code is kept ≤ 84 characters
  per line so it stays ≥ 27 px.

## Layout

- 1920×1080, 60 fps. Safe content box: x 96–1824, y 132–950.
- Header (y≈44): course mark · "Module NN · Lesson N" · current chapter (top right).
- Footer: 6 px lesson progress bar; speaking indicator (five bars driven by the narration envelope).
- Every scene fades and lifts in (20 frames) and fades out (14 frames); the background never cuts.

## Scene vocabulary

`title`, `section`, `objectives`, `bullets`, `steps`, `recap`, `cards`, `code` (line highlights,
smooth scrolling, side or bottom notes), `terminal` (real captured output; bash or `>>>` REPL),
`diagram` (nodes, animated edges, moving data packets, focus/dim), `compare` (avoid/prefer, code or
lists), `callout` (error, warn, tip, info, challenge), `quiz` (countdown, reveal, explanation), `links`.

## Motion and sound

- Reveals are tied to narration beats, never to fixed timers. Eased (cubic out), 18–26 frames.
- No flashing, no fast zooms, no decorative motion competing with code.
- Audio: one instructor voice (Kokoro `am_michael`), mixed to −16 LUFS integrated, −1.5 dBTP.
  Original synthesized music bed (`tools/make_audio_assets.py`) ducked to roughly −20 dB under speech.
  Sound effects: soft whoosh on scene changes, a quiet tick on reveals, a chime on quiz answers, a sting on title cards.

## Thumbnails

1280×720 still (`studio/src/Thumbnail.tsx`): module chip, three-line title (one line in teal),
amber tagline, real output from the project in a code card, agent-loop ring. No fake logos, no
claims about jobs, salaries or views.
