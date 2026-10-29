import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";

type Card = { tag?: string; title: string; body?: string; code?: string; tone?: string };

export const CardsScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; cards: Card[]; columns?: number };
  const { items, current } = itemProgress(s.beats, frame);
  const n = s.cards.length;
  const cols = s.columns ?? (n <= 2 ? 2 : n === 4 ? 2 : 3);
  const rows = Math.ceil(n / cols);
  const compact = rows > 1;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} />
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gridAutoRows: "1fr", gap: 28, minHeight: 0 }}>
        {s.cards.map((card, i) => {
          const at = items[i]?.from ?? 0;
          const a = appear(frame, at, 22);
          const on = i === current;
          const color = tone(card.tone ?? ["teal", "blue", "violet", "amber", "coral", "teal"][i % 6]);
          const shown = frame >= at;
          return (
            <div
              key={i}
              style={{
                opacity: shown ? a * (on || current < 0 ? 1 : 0.7) : 0,
                transform: `translateY(${(1 - a) * 30}px) scale(${0.97 + 0.03 * a})`,
                background: C.surface,
                borderRadius: 24,
                border: `2px solid ${on ? color : C.line}`,
                padding: compact ? "28px 32px" : "40px 40px",
                display: "flex",
                flexDirection: "column",
                gap: 14,
                boxShadow: on ? `0 0 0 6px ${color}18` : "none",
                overflow: "hidden",
              }}
            >
              {card.tag ? (
                <div style={{ alignSelf: "flex-start", fontFamily: MONO, fontSize: 22, fontWeight: 700, color, background: `${color}1A`, borderRadius: 999, padding: "6px 16px" }}>{card.tag}</div>
              ) : null}
              <div style={{ fontFamily: FONT, fontSize: compact ? 38 : 46, fontWeight: 800, color: C.text, lineHeight: 1.15 }}>
                <Rich text={card.title} />
              </div>
              {card.body ? (
                <div style={{ fontFamily: FONT, fontSize: compact ? 27 : 31, color: C.muted, lineHeight: 1.4 }}>
                  <Rich text={card.body} />
                </div>
              ) : null}
              {card.code ? (
                <div style={{ marginTop: "auto", fontFamily: MONO, fontSize: compact ? 25 : 28, color: "#CFE9FF", background: C.ink, border: `1px solid ${C.line}`, borderRadius: 14, padding: "14px 18px", whiteSpace: "pre" }}>
                  {card.code}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
};
