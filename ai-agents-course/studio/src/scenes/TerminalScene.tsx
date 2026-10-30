import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, CONTENT_W, MONO, SAFE } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Window } from "../ui/CodeView";

type Pair = { cmd: string; out: string[] };
type Step = { pairs: Pair[] };

const colorFor = (line: string) => {
  if (/^\s*(x |error|Error|Traceback|E |FAILED)/.test(line) || /Error:/.test(line)) return C.coral;
  if (/^\s*(warning|WARNING)/.test(line)) return C.amber;
  if (/passed|^# |valid, 0 invalid|written to|saved \d+/.test(line)) return C.teal;
  return C.codeText;
};

export const TerminalScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; title?: string; steps: Step[]; prompt?: string; font?: number; repl?: boolean };
  const { items, current } = itemProgress(s.beats, frame);
  const fs = s.font ?? 28;
  const lh = fs * 1.5;
  const bodyH = SAFE.bottom - SAFE.top - (s.heading ? 120 : 0) - 58 - 8;
  const maxLines = Math.floor((bodyH - 40) / lh);
  const prompt = s.prompt ?? (s.repl ? ">>>" : "$");
  const maxChars = Math.floor((CONTENT_W - 70) / (fs * 0.602));
  const wrap = (line: string): string[] => {
    const out: string[] = [];
    let rest = line;
    let width = maxChars;
    while (rest.length > width) {
      const cut = rest.lastIndexOf(" ", width);
      const at = cut > width * 0.5 ? cut : width;
      out.push((out.length ? "  " : "") + rest.slice(0, at));
      rest = rest.slice(at).trimStart();
      width = maxChars - 2;
    }
    out.push((out.length ? "  " : "") + rest);
    return out;
  };

  // build the visible transcript up to the current step
  const rows: { text: string; kind: "cmd" | "out"; typed?: number; at: number }[] = [];
  s.steps.forEach((st, k) => {
    if (k > current || !items[k]) return;
    let at = items[k].from;
    st.pairs.forEach((pair) => {
      const typeFrames = Math.min(50, 10 + pair.cmd.length * 1.2);
      const typed = Math.floor(interpolate(frame, [at + 6, at + 6 + typeFrames], [0, pair.cmd.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
      if (frame >= at) rows.push({ text: pair.cmd, kind: "cmd", typed, at });
      const outAt = at + 10 + typeFrames;
      const lines = pair.out.flatMap(wrap);
      lines.forEach((line, j) => {
        if (frame >= outAt + j * 2) rows.push({ text: line, kind: "out", at: outAt + j * 2 });
      });
      at = outAt + lines.length * 2 + 14;
    });
  });
  const scroll = Math.max(0, rows.length - (maxLines - 1)); // keep a line free for the prompt
  const lastCmd = [...rows].reverse().find((r) => r.kind === "cmd");
  const cursorOn = Math.floor(frame / 30) % 2 === 0;

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <Window title={s.title ?? "terminal"} accent={C.blue} style={{ width: CONTENT_W, opacity: appear(frame, 6, 22) }}>
        <div style={{ height: bodyH, overflow: "hidden", padding: "20px 34px", fontFamily: MONO, fontSize: fs }}>
          {rows.slice(scroll).map((r, i) =>
            r.kind === "cmd" ? (
              <div key={i} style={{ height: lh, whiteSpace: "pre", display: "flex", alignItems: "center" }}>
                <span style={{ color: C.teal, marginRight: 16 }}>{prompt}</span>
                <span style={{ color: C.text }}>{r.text.slice(0, r.typed)}</span>
                {r === lastCmd && (r.typed ?? 0) < r.text.length ? <span style={{ width: fs * 0.6, height: fs * 1.1, background: C.teal, opacity: 0.8 }} /> : null}
              </div>
            ) : (
              <div key={i} style={{ height: lh, whiteSpace: "pre", color: colorFor(r.text), display: "flex", alignItems: "center", opacity: appear(frame, r.at, 6) }}>
                {r.text}
              </div>
            ),
          )}
          {lastCmd && (lastCmd.typed ?? 0) >= lastCmd.text.length && rows[rows.length - 1].kind === "out" && current === s.steps.length - 1 ? (
            <div style={{ height: lh, display: "flex", alignItems: "center" }}>
              <span style={{ color: C.teal, marginRight: 16 }}>{prompt}</span>
              <span style={{ width: fs * 0.6, height: fs * 1.1, background: C.teal, opacity: cursorOn ? 0.8 : 0 }} />
            </div>
          ) : null}
        </div>
      </Window>
    </div>
  );
};
