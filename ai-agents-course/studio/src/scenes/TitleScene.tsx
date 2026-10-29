import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { appear, SceneBase } from "../ui/anim";
import { Rich } from "../ui/Rich";
import { AgentLoop } from "../ui/AgentLoop";

export const TitleScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { kicker?: string; title: string; subtitle?: string; tags?: string[] };
  const a = appear(frame, 6, 26);
  const b = appear(frame, 22, 26);
  const c = appear(frame, 40, 26);
  const size = s.title.length > 34 ? 88 : 104;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center" }}>
      <div style={{ width: 1080, display: "flex", flexDirection: "column" }}>
        {s.kicker ? (
          <div style={{ opacity: a, transform: `translateX(${(1 - a) * -30}px)`, display: "flex", alignItems: "center", gap: 16, marginBottom: 34 }}>
            <div style={{ width: 54, height: 4, background: C.teal, borderRadius: 2 }} />
            <div style={{ fontFamily: MONO, fontSize: 28, color: C.teal, letterSpacing: 3, textTransform: "uppercase" }}>{s.kicker}</div>
          </div>
        ) : null}
        <div style={{ opacity: b, transform: `translateY(${(1 - b) * 30}px)`, fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1.03, color: C.text, letterSpacing: -2.5 }}>
          <Rich text={s.title} accent={C.teal} />
        </div>
        {s.subtitle ? (
          <div style={{ opacity: c, marginTop: 34, fontFamily: FONT, fontSize: 40, lineHeight: 1.35, color: C.muted, maxWidth: 1000 }}>
            <Rich text={s.subtitle} />
          </div>
        ) : null}
        {s.tags ? (
          <div style={{ opacity: c, display: "flex", gap: 14, marginTop: 44, flexWrap: "wrap" }}>
            {s.tags.map((t) => (
              <div key={t} style={{ fontFamily: MONO, fontSize: 24, color: C.text, border: `1px solid ${C.line}`, background: C.surface, borderRadius: 999, padding: "10px 22px" }}>
                {t}
              </div>
            ))}
          </div>
        ) : null}
      </div>
      <div style={{ position: "absolute", right: -40, top: "50%", transform: "translateY(-50%)", opacity: appear(frame, 10, 40) }}>
        <AgentLoop size={680} labels={(scene.loop as string[]) ?? undefined} />
      </div>
    </div>
  );
};
