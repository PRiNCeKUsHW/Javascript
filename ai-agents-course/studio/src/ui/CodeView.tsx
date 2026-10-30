import React from "react";
import { C, MONO, SYNTAX, alpha } from "../theme";
import { lerp } from "./anim";

export type Tokens = [string, string][][];

export type CodeState = { hl: number[]; upto?: number; scroll: number };

const lineOpacity = (s: CodeState, i: number) => {
  if (s.upto !== undefined && i > s.upto) return 0;
  if (!s.hl.length) return 1;
  return s.hl.includes(i) ? 1 : 0.34;
};

/** Pick a font size so the longest line fits the panel width, within readable bounds. */
export const codeFont = (tokens: Tokens, width: number, max = 32, min = 22) => {
  const longest = Math.max(20, ...tokens.map((l) => l.reduce((n, [t]) => n + t.length, 0)));
  return Math.max(min, Math.min(max, Math.floor((width - 150) / (longest * 0.602))));
};

export const visibleLines = (height: number, fontSize: number) => Math.floor((height - 40) / (fontSize * 1.55));

/** Scroll position that keeps the highlighted (or newest) lines in view. */
export const scrollFor = (total: number, visible: number, hl: number[], upto?: number) => {
  if (total <= visible) return 0;
  const focus = hl.length ? (Math.min(...hl) + Math.max(...hl)) / 2 : upto ?? 1;
  const top = hl.length && Math.max(...hl) - Math.min(...hl) >= visible ? Math.min(...hl) - 1 : focus - visible / 2;
  return Math.round(Math.max(0, Math.min(total - visible, top)));
};

export const CodeView: React.FC<{
  tokens: Tokens;
  firstLine?: number;
  prev: CodeState;
  cur: CodeState;
  t: number; // 0..1 transition from prev to cur
  fontSize: number;
  height: number;
  lineNumbers?: boolean;
  diff?: Record<number, "add" | "del">;
}> = ({ tokens, firstLine = 1, prev, cur, t, fontSize, height, lineNumbers = true, diff }) => {
  const lh = fontSize * 1.55;
  const scroll = lerp(prev.scroll, cur.scroll, t);
  const gutter = lineNumbers ? fontSize * 2.6 : 0;
  return (
    <div
      style={{
        position: "relative",
        height,
        overflow: "hidden",
        // fade the padding bands so a scrolled panel never shows half-cut lines at its edges
        maskImage: "linear-gradient(180deg, transparent 0px, #000 20px, #000 calc(100% - 20px), transparent 100%)",
      }}
    >
      <div style={{ position: "absolute", left: 0, right: 0, top: 20 - scroll * lh }}>
        {tokens.map((line, idx) => {
          const i = idx + 1;
          const op = lerp(lineOpacity(prev, i), lineOpacity(cur, i), t);
          const isHl = cur.hl.includes(i);
          const wasHl = prev.hl.includes(i);
          const bg = lerp(wasHl ? 1 : 0, isHl ? 1 : 0, t);
          const mark = diff?.[i];
          return (
            <div
              key={idx}
              style={{
                position: "relative",
                height: lh,
                display: "flex",
                alignItems: "center",
                opacity: op,
                fontFamily: MONO,
                fontSize,
                whiteSpace: "pre",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  inset: "0 0 0 0",
                  background: mark === "add" ? alpha(C.teal, 0.10) : mark === "del" ? alpha(C.coral, 0.10) : alpha(C.amber, 0.12 * bg),
                  borderLeft: `4px solid ${mark === "add" ? C.teal : mark === "del" ? C.coral : alpha(C.amber, bg)}`,
                }}
              />
              {lineNumbers ? (
                <div style={{ width: gutter, textAlign: "right", paddingRight: fontSize * 0.9, color: C.faint, flexShrink: 0, position: "relative" }}>
                  {firstLine + idx}
                </div>
              ) : (
                <div style={{ width: fontSize * 0.8 }} />
              )}
              <div style={{ position: "relative" }}>
                {line.map(([text, cls], k) => (
                  <span key={k} style={{ color: SYNTAX[cls] ?? SYNTAX[""], fontStyle: cls === "com" ? "italic" : "normal" }}>
                    {text}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const Window: React.FC<{ title?: string; children: React.ReactNode; style?: React.CSSProperties; accent?: string; badge?: string }> = ({
  title,
  children,
  style,
  accent = C.teal,
  badge,
}) => (
  <div
    style={{
      background: C.code,
      border: `1px solid ${C.line}`,
      borderRadius: 22,
      boxShadow: `0 18px 50px ${C.shadow}`,
      overflow: "hidden",
      ...style,
    }}
  >
    <div style={{ height: 58, display: "flex", alignItems: "center", gap: 10, padding: "0 22px", borderBottom: `1px solid ${C.line}`, background: C.codeHead }}>
      {["#FF5F57", "#FEBC2E", "#28C840"].map((c) => (
        <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.85 }} />
      ))}
      <div style={{ marginLeft: 16, fontFamily: MONO, fontSize: 22, color: C.muted, display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ width: 8, height: 8, borderRadius: 4, background: accent }} />
        {title}
      </div>
      {badge ? (
        <div style={{ marginLeft: "auto", fontFamily: MONO, fontSize: 18, color: accent, border: `1px solid ${accent}55`, borderRadius: 999, padding: "4px 14px" }}>{badge}</div>
      ) : null}
    </div>
    {children}
  </div>
);
