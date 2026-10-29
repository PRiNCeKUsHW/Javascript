import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";

export const LinksScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; items: { title: string; url: string }[] };
  const { items } = itemProgress(s.beats, frame);
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow ?? "Official documentation"} />
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {s.items.map((it, i) => {
          const at = items[i]?.from ?? 10 + i * 8;
          const a = frame >= at ? appear(frame, at, 18) : 0;
          return (
            <div key={i} style={{ opacity: a, transform: `translateX(${(1 - a) * 30}px)`, display: "flex", alignItems: "center", gap: 30, background: C.surface, border: `1px solid ${C.line}`, borderRadius: 18, padding: "20px 30px" }}>
              <div style={{ fontFamily: MONO, fontSize: 24, color: C.teal, width: 40 }}>{String(i + 1).padStart(2, "0")}</div>
              <div style={{ fontFamily: FONT, fontSize: 34, fontWeight: 700, color: C.text, width: 640 }}>
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
