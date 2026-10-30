import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";
import { CodeView, codeFont, Tokens, Window } from "../ui/CodeView";

type Item = { text: string; sub?: string; tone?: string };
type Aside = { title?: string; tokens?: Tokens; lang?: string };

const Marker: React.FC<{ variant: string; i: number; color: string; on: boolean }> = ({ variant, i, color, on }) => {
  const box: React.CSSProperties = {
    width: 56,
    height: 56,
    borderRadius: variant === "steps" ? 16 : 28,
    flexShrink: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    border: `2px solid ${color}`,
    background: on ? color : "transparent",
    color: on ? C.ink : color,
    fontFamily: MONO,
    fontWeight: 700,
    fontSize: 26,
  };
  if (variant === "steps") return <div style={box}>{i + 1}</div>;
  if (variant === "recap" || variant === "objectives")
    return (
      <div style={box}>
        <svg width={26} height={26} viewBox="0 0 24 24">
          <path d="M4 12.5l5 5L20 6.5" stroke={on ? C.ink : color} strokeWidth={3.2} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    );
  return <div style={{ ...box, width: 22, height: 22, marginTop: 17, marginLeft: 17, marginRight: 17, background: color, border: "none" }} />;
};

export const BulletsScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; items: Item[]; aside?: Aside };
  const { items, count, current } = itemProgress(s.beats, frame);
  const variant = s.type;
  const n = s.items.length;
  const textSize = n > 5 ? 36 : 42;
  const aside = s.aside;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow ?? (variant === "objectives" ? "By the end of this lesson" : variant === "recap" ? "Recap" : undefined)} />
      <div style={{ display: "flex", gap: 56, flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: n > 5 ? 22 : 30 }}>
          {s.items.map((item, i) => {
            const at = items[i]?.from ?? 0;
            const a = appear(frame, at, 20);
            const on = i === current;
            const done = i < count;
            const color = tone(item.tone ?? (variant === "recap" ? "teal" : variant === "steps" ? "blue" : "teal"));
            return (
              <div
                key={i}
                style={{
                  opacity: done ? (on ? 1 : 0.62) * a : 0,
                  transform: `translateX(${(1 - a) * 40}px)`,
                  display: "flex",
                  gap: 26,
                  alignItems: "flex-start",
                  padding: "14px 24px",
                  borderRadius: 18,
                  background: on ? C.surface : "transparent",
                  border: `1px solid ${on ? C.line : "transparent"}`,
                }}
              >
                <Marker variant={variant} i={i} color={color} on={on} />
                <div style={{ paddingTop: 4 }}>
                  <div style={{ fontFamily: FONT, fontSize: textSize, fontWeight: 600, color: C.text, lineHeight: 1.3 }}>
                    <Rich text={item.text} />
                  </div>
                  {item.sub ? (
                    <div style={{ fontFamily: FONT, fontSize: textSize * 0.68, color: C.muted, marginTop: 8, lineHeight: 1.35 }}>
                      <Rich text={item.sub} />
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
        {aside?.tokens ? (
          <div style={{ width: 780, opacity: appear(frame, 10, 24) }}>
            <Window title={aside.title}>
              <CodeView
                tokens={aside.tokens}
                prev={{ hl: [], scroll: 0 }}
                cur={{ hl: [], scroll: 0 }}
                t={1}
                fontSize={codeFont(aside.tokens, 780, 30)}
                height={Math.min(640, aside.tokens.length * codeFont(aside.tokens, 780, 30) * 1.55 + 44)}
              />
            </Window>
          </div>
        ) : null}
      </div>
    </div>
  );
};
