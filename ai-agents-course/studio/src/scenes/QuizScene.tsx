import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, FONT, MONO, alpha } from "../theme";
import { appear, beatStart, SceneBase } from "../ui/anim";
import { Rich } from "../ui/Rich";

export const QuizScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { number: number; of?: number; question: string; code?: string; options: string[]; answer: number; explain: string };
  const thinkAt = beatStart(s.beats, "think");
  const revealAt = beatStart(s.beats, "reveal");
  const thinkLen = revealAt - thinkAt;
  const revealed = frame >= revealAt;
  const r = appear(frame, revealAt, 20);
  const left = Math.ceil(interpolate(frame, [thinkAt, revealAt], [thinkLen / 60, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const ring = interpolate(frame, [thinkAt, revealAt], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 26, opacity: appear(frame, 2, 18) }}>
        <div style={{ fontFamily: MONO, fontSize: 26, fontWeight: 700, color: C.ink, background: C.amber, borderRadius: 999, padding: "8px 22px" }}>QUIZ</div>
        <div style={{ fontFamily: MONO, fontSize: 26, color: C.muted }}>
          Question {s.number}
          {s.of ? ` of ${s.of}` : ""}
        </div>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 16, opacity: frame >= thinkAt && !revealed ? 1 : 0 }}>
          <div style={{ fontFamily: FONT, fontSize: 28, color: C.muted }}>Pause and think</div>
          <svg width={76} height={76}>
            <circle cx={38} cy={38} r={32} stroke={C.line} strokeWidth={6} fill="none" />
            <circle cx={38} cy={38} r={32} stroke={C.amber} strokeWidth={6} fill="none" strokeDasharray={`${2 * Math.PI * 32 * ring} 999`} transform="rotate(-90 38 38)" strokeLinecap="round" />
            <text x={38} y={48} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={30} fill={C.text}>
              {left}
            </text>
          </svg>
        </div>
      </div>
      <div style={{ fontFamily: FONT, fontSize: s.question.length > 90 ? 46 : 54, fontWeight: 800, color: C.text, lineHeight: 1.2, opacity: appear(frame, 6, 22) }}>
        <Rich text={s.question} />
      </div>
      {s.code ? (
        <div style={{ marginTop: 24, fontFamily: MONO, fontSize: 30, color: C.codeText, background: C.code, border: `1px solid ${C.line}`, borderRadius: 16, padding: "20px 28px", whiteSpace: "pre", opacity: appear(frame, 12, 22) }}>{s.code}</div>
      ) : null}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginTop: 34 }}>
        {s.options.map((opt, i) => {
          const correct = i === s.answer;
          const a = appear(frame, 18 + i * 6, 18);
          const col = revealed ? (correct ? C.teal : C.line) : C.line;
          return (
            <div
              key={i}
              style={{
                opacity: a * (revealed && !correct ? 1 - 0.55 * r : 1),
                display: "flex",
                alignItems: "center",
                gap: 22,
                background: revealed && correct ? alpha(C.teal, 0.12 * r) : C.surface,
                border: `2px solid ${col}`,
                borderRadius: 20,
                padding: "22px 28px",
              }}
            >
              <div style={{ width: 52, height: 52, borderRadius: 14, flexShrink: 0, background: revealed && correct ? C.teal : C.surface2, color: revealed && correct ? C.ink : C.muted, fontFamily: MONO, fontWeight: 700, fontSize: 28, display: "flex", alignItems: "center", justifyContent: "center" }}>
                {revealed && correct ? "✓" : "ABCD"[i]}
              </div>
              <div style={{ fontFamily: FONT, fontSize: 32, color: C.text, lineHeight: 1.3 }}>
                <Rich text={opt} />
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: 30, opacity: r, transform: `translateY(${(1 - r) * 20}px)`, fontFamily: FONT, fontSize: 33, color: C.text, lineHeight: 1.4, background: C.surface2, borderLeft: `6px solid ${C.teal}`, borderRadius: 16, padding: "22px 30px" }}>
        <Rich text={s.explain} />
      </div>
    </div>
  );
};
