import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { appear, SceneBase } from "../ui/anim";
import { Rich } from "../ui/Rich";

export const SectionScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { number?: string; title: string; subtitle?: string };
  const a = appear(frame, 4, 30);
  const b = appear(frame, 18, 26);
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 40 }}>
        {s.number ? (
          <div style={{ opacity: a, fontFamily: MONO, fontWeight: 700, fontSize: 220, color: "transparent", WebkitTextStroke: `3px ${C.teal}`, lineHeight: 1 }}>{s.number}</div>
        ) : null}
        <div style={{ opacity: b, transform: `translateX(${(1 - b) * 40}px)` }}>
          <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 92, color: C.text, letterSpacing: -2, lineHeight: 1.05 }}>
            <Rich text={s.title} accent={C.teal} />
          </div>
          {s.subtitle ? <div style={{ fontFamily: FONT, fontSize: 38, color: C.muted, marginTop: 20 }}><Rich text={s.subtitle} /></div> : null}
        </div>
      </div>
      <div style={{ marginTop: 60, height: 4, width: `${b * 100}%`, background: `linear-gradient(90deg, ${C.teal}, transparent)`, borderRadius: 2 }} />
    </div>
  );
};
