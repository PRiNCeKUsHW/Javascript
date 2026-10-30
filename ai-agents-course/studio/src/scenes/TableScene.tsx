import React from "react";
import { useCurrentFrame } from "remotion";
import { C, CONTENT_W, FONT, MONO, alpha, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";

// A table that fills in one row per beat: dry runs (variables changing step by step) and comparisons.
type Row = { cells: string[]; tone?: string; note?: string };

export const TableScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; columns: string[]; rows: Row[]; widths?: number[]; mono?: boolean; caption?: string };
  const { items, current } = itemProgress(s.beats, frame);
  const n = s.columns.length;
  const widths = s.widths ?? s.columns.map(() => 1);
  const total = widths.reduce((a, b) => a + b, 0);
  const fs = s.rows.length > 6 ? 28 : 31;
  const cellFont = s.mono ? MONO : FONT;
  const note = current >= 0 ? s.rows[current]?.note : undefined;
  const grid = { display: "grid", gridTemplateColumns: widths.map((w) => `${(w / total) * 100}%`).join(" ") } as const;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <div style={{ width: CONTENT_W, background: C.surface, border: `1px solid ${C.line}`, borderRadius: 22, overflow: "hidden", boxShadow: `0 18px 50px ${C.shadow}`, opacity: appear(frame, 6, 22) }}>
        <div style={{ ...grid, background: C.surface2, borderBottom: `2px solid ${C.line}` }}>
          {s.columns.map((c, i) => (
            <div key={i} style={{ padding: "18px 26px", fontFamily: FONT, fontSize: 25, fontWeight: 800, letterSpacing: 1, color: C.muted, textTransform: "uppercase" }}>
              <Rich text={c} />
            </div>
          ))}
        </div>
        {s.rows.map((r, k) => {
          const shown = k <= current && items[k];
          const a = shown ? appear(frame, items[k].from, 16) : 0;
          const on = k === current;
          const col = tone(r.tone ?? "amber");
          return (
            <div
              key={k}
              style={{
                ...grid,
                opacity: a * (on || current < 0 ? 1 : 0.62),
                transform: `translateY(${(1 - a) * 12}px)`,
                background: on ? alpha(col, 0.1) : "transparent",
                borderLeft: `6px solid ${on ? col : "transparent"}`,
                borderBottom: k < s.rows.length - 1 ? `1px solid ${C.line}` : "none",
              }}
            >
              {r.cells.slice(0, n).map((c, i) => (
                <div key={i} style={{ padding: "16px 26px", fontFamily: i === 0 && !s.mono ? FONT : cellFont, fontSize: fs, color: C.text, fontWeight: i === 0 ? 700 : 400, lineHeight: 1.35 }}>
                  <Rich text={c} />
                </div>
              ))}
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 26, minHeight: 60, fontFamily: FONT, fontSize: 31, color: C.muted, opacity: note ? appear(frame, items[current].from + 8, 18) : s.caption ? 1 : 0 }}>
        <Rich text={note ?? s.caption ?? ""} />
      </div>
    </div>
  );
};
