import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO, alpha } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Rich } from "../ui/Rich";

// Interview corner: the question, an answer you can say out loud, and the trap to avoid.
// Beats: [intro], then per item: question, answer (and the trap shows with the answer).
type Item = { q: string; a: string; trap?: string };

export const InterviewScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { items: Item[]; of?: number; start?: number };
  const { items: beats, current } = itemProgress(s.beats, frame);
  const k = Math.max(0, Math.floor(current / 2));
  const item = s.items[Math.min(k, s.items.length - 1)];
  const qAt = beats[k * 2]?.from ?? 0;
  const aAt = beats[k * 2 + 1]?.from ?? Infinity;
  const qa = current >= 0 ? appear(frame, qAt, 20) : appear(frame, 6, 20) * 0.0;
  const aa = frame >= aAt ? appear(frame, aAt, 22) : 0;
  const number = (s.start ?? 1) + k;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center", gap: 30 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 18, opacity: appear(frame, 4, 20) }}>
        <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 4, color: C.violet, fontWeight: 700, textTransform: "uppercase" }}>Interview corner</div>
        <div style={{ fontFamily: MONO, fontSize: 24, color: C.faint }}>
          question {number}
          {s.of ? ` of ${s.of}` : ""}
        </div>
      </div>
      <div style={{ opacity: qa, transform: `translateY(${(1 - qa) * 16}px)`, fontFamily: FONT, fontSize: 54, fontWeight: 800, color: C.text, lineHeight: 1.18, letterSpacing: -0.5 }}>
        “<Rich text={item.q} />”
      </div>
      <div
        style={{
          opacity: aa,
          transform: `translateY(${(1 - aa) * 16}px)`,
          background: C.surface,
          border: `1px solid ${C.line}`,
          borderLeft: `8px solid ${C.teal}`,
          borderRadius: 22,
          padding: "30px 40px",
          boxShadow: `0 18px 50px ${C.shadow}`,
        }}
      >
        <div style={{ fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: C.teal, fontWeight: 700, marginBottom: 12 }}>A GOOD ANSWER</div>
        <div style={{ fontFamily: FONT, fontSize: 36, color: C.text, lineHeight: 1.42 }}>
          <Rich text={item.a} />
        </div>
      </div>
      {item.trap ? (
        <div style={{ opacity: aa, display: "flex", gap: 18, alignItems: "baseline", background: alpha(C.coral, 0.07), border: `1px solid ${alpha(C.coral, 0.3)}`, borderRadius: 18, padding: "20px 30px" }}>
          <div style={{ fontFamily: MONO, fontSize: 22, letterSpacing: 3, color: C.coral, fontWeight: 700, flexShrink: 0 }}>TRAP</div>
          <div style={{ fontFamily: FONT, fontSize: 31, color: C.text, lineHeight: 1.4 }}>
            <Rich text={item.trap} />
          </div>
        </div>
      ) : null}
    </div>
  );
};
