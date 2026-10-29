import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { appear, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";

export const LinksScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; items: { title: string; url: string }[] };
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow ?? "Official documentation"} />
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {s.items.map((it, i) => {
          const at = 14 + i * 10; // staggered while the narration introduces the list
          const a = frame >= at ? appear(frame, at, 18) : 0;
          return (
            <div key={i} style={{ opacity: a, transform: `translateX(${(1 - a) * 30}px)`, display: "flex", alignItems: "center", gap: 30, background: C.surface, border: `1px solid ${C.line}`, borderRadius: 16, padding: "13px 30px" }}>
              <div style={{ fontFamily: MONO, fontSize: 24, color: C.teal, width: 40 }}>{String(i + 1).padStart(2, "0")}</div>
              <div style={{ fontFamily: FONT, fontSize: 31, fontWeight: 700, color: C.text, width: 600 }}>
                <Rich text={it.title} />
              </div>
              <div style={{ fontFamily: MONO, fontSize: 25, color: C.blue }}>{it.url}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
