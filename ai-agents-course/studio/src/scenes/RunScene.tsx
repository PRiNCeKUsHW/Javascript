import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, CONTENT_W, FONT, MONO, SAFE, tone, alpha } from "../theme";
import { appear, itemProgress, lerp, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";
import { CodeState, CodeView, codeFont, scrollFor, Tokens, visibleLines, Window } from "../ui/CodeView";

// Code on the left, the real output of running it on the right. A step's `ohl` points at
// output lines: the command is typed at the first such step, and output appears up to the
// furthest line pointed at so far, so narration can tie a line of code to the line it printed.
type Step = { hl: number[]; ohl?: number[]; note?: string; tone?: string };

const outColor = (line: string) => {
  if (/^\s*(x |error|Error|Traceback|E |FAILED)/.test(line) || /Error:/.test(line)) return C.coral;
  if (/passed|^# /.test(line)) return C.teal;
  return C.codeText;
};

export const RunScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & {
    heading?: string; eyebrow?: string; title?: string; tokens: Tokens; first_line: number;
    steps?: Step[]; out: string[]; cmd: string; prompt?: string; font?: number; split?: number;
  };
  const steps = s.steps ?? [];
  const { items, current } = itemProgress(s.beats, frame);
  const hasNotes = steps.some((st) => st.note);
  const gap = 36;
  // give the code the width its longest line needs at a readable size, within 50-66% of the row
  const longest = Math.max(20, ...s.tokens.map((l) => l.reduce((n, [txt]) => n + txt.length, 0)));
  const fit = (longest * 0.602 * 23 + 150) / (CONTENT_W - gap);
  const leftW = Math.round((CONTENT_W - gap) * (s.split ?? Math.max(0.5, Math.min(0.66, fit))));
  const rightW = CONTENT_W - gap - leftW;
  const panelH = SAFE.bottom - SAFE.top - (s.heading ? 120 : 0) - 58 - (hasNotes ? 140 : 0);

  // ---- left: the code
  const fitH = Math.floor((panelH - 44) / (s.tokens.length * 1.55));
  const fsW = codeFont(s.tokens, leftW, 28, 19);
  const fs = fitH >= 22 ? Math.min(fsW, fitH) : fsW;
  const vis = visibleLines(panelH, fs);
  const total = s.tokens.length;
  const stateAt = (k: number): CodeState => {
    const hl = k < 0 ? [] : steps[k]?.hl ?? [];
    return { hl, scroll: scrollFor(total, vis, hl) };
  };
  const k = Math.min(current, steps.length - 1);
  const cur = stateAt(k);
  const prev = stateAt(Math.min(current - 1, steps.length - 1));
  const t = current >= 0 ? appear(frame, items[current].from, 24) : 1;

  // ---- right: the terminal
  const tfs = s.font ?? 22;
  const lh = tfs * 1.5;
  const maxChars = Math.floor((rightW - 56) / (tfs * 0.602));
  const rows: { text: string; src: number }[] = [];
  s.out.forEach((line, i) => {
    let rest = line;
    let first = true;
    do {
      const width = first ? maxChars : maxChars - 2;
      let at = rest.length;
      if (rest.length > width) {
        const cut = rest.lastIndexOf(" ", width);
        at = cut > width * 0.5 ? cut : width;
      }
      rows.push({ text: (first ? "" : "  ") + rest.slice(0, at), src: i + 1 });
      rest = rest.slice(at).trimStart();
      first = false;
    } while (rest.length);
  });
  const runStep = steps.findIndex((st) => st.ohl?.length);
  const runAt = runStep >= 0 && items[runStep] ? items[runStep].from : Infinity;
  const typeFrames = Math.min(45, 10 + s.cmd.length * 1.2);
  const typed = Math.floor(interpolate(frame, [runAt + 4, runAt + 4 + typeFrames], [0, s.cmd.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const outAt = runAt + 10 + typeFrames;
  // furthest output line any step so far has pointed at
  const shownUpTo = Math.max(0, ...steps.slice(0, k + 1).flatMap((st) => st.ohl ?? []));
  const ohl = k >= 0 ? steps[k].ohl ?? [] : [];
  const prevOhl = current > 0 ? steps[Math.min(current - 1, steps.length - 1)].ohl ?? [] : [];
  const visible = rows.filter((r) => r.src <= shownUpTo);
  const termLines = Math.floor((panelH - 40) / lh) - 1; // the command line takes one row
  const focusRows = visible.map((r, i) => (ohl.includes(r.src) ? i : -1)).filter((i) => i >= 0);
  const scrollTo = (idx: number[]) => {
    if (visible.length <= termLines) return 0;
    const last = idx.length ? Math.max(...idx) : visible.length - 1;
    return Math.max(0, Math.min(visible.length - termLines, last - termLines + 2));
  };
  const scroll = scrollTo(focusRows);
  const cursorOn = Math.floor(frame / 30) % 2 === 0;
  const noteColor = tone(k >= 0 ? steps[k].tone ?? "amber" : "amber");

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <div style={{ display: "flex", gap, alignItems: "flex-start" }}>
        <Window title={s.title} badge="code" style={{ width: leftW, opacity: appear(frame, 6, 22) }}>
          <CodeView tokens={s.tokens} firstLine={s.first_line} prev={prev} cur={cur} t={t} fontSize={fs} height={panelH} />
        </Window>
        <Window title="output" accent={C.blue} badge={frame >= outAt ? "ran" : undefined} style={{ width: rightW, opacity: appear(frame, 10, 22) }}>
          <div style={{ height: panelH, overflow: "hidden", padding: "20px 28px", fontFamily: MONO, fontSize: tfs }}>
            <div style={{ height: lh, whiteSpace: "pre", display: "flex", alignItems: "center" }}>
              <span style={{ color: C.teal, marginRight: 14 }}>{s.prompt ?? "$"}</span>
              <span style={{ color: C.text }}>{s.cmd.slice(0, typed)}</span>
              {typed < s.cmd.length || frame < outAt ? (
                <span style={{ width: tfs * 0.6, height: tfs * 1.1, background: C.teal, opacity: typed < s.cmd.length || cursorOn ? 0.8 : 0 }} />
              ) : null}
            </div>
            {visible.slice(scroll, scroll + termLines).map((r, i) => {
              const j = visible.indexOf(r);
              const at = outAt + j * 2;
              const isHl = ohl.includes(r.src);
              const wasHl = prevOhl.includes(r.src);
              const dim = ohl.length ? 0.4 : 1;
              const bg = lerp(wasHl ? 1 : 0, isHl ? 1 : 0, t);
              return (
                <div
                  key={`${scroll}-${i}`}
                  style={{
                    position: "relative",
                    height: lh,
                    whiteSpace: "pre",
                    display: "flex",
                    alignItems: "center",
                    color: outColor(r.text),
                    opacity: (frame >= at ? appear(frame, at, 6) : 0) * (isHl ? 1 : lerp(1, dim, t)),
                  }}
                >
                  <div style={{ position: "absolute", inset: "0 -28px", background: alpha(C.blue, 0.10 * bg), borderLeft: `4px solid ${alpha(C.blue, bg)}` }} />
                  <span style={{ position: "relative" }}>{r.text}</span>
                </div>
              );
            })}
          </div>
        </Window>
      </div>
      {hasNotes ? (
        <div style={{ position: "relative", height: 116, marginTop: 24 }}>
          {steps.map((st, n) =>
            st.note ? (
              <div
                key={n}
                style={{
                  position: "absolute",
                  inset: 0,
                  opacity: n === current ? appear(frame, items[n].from + 6, 20) : 0,
                  transform: `translateY(${n === current ? (1 - appear(frame, items[n].from + 6, 20)) * 16 : 0}px)`,
                  background: C.surface,
                  border: `1px solid ${C.line}`,
                  borderLeft: `6px solid ${noteColor}`,
                  borderRadius: 18,
                  padding: "0 32px",
                  display: "flex",
                  alignItems: "center",
                  fontFamily: FONT,
                  fontSize: 31,
                  color: C.text,
                }}
              >
                <div>
                  <Rich text={st.note} />
                </div>
              </div>
            ) : null,
          )}
        </div>
      ) : null}
    </div>
  );
};
