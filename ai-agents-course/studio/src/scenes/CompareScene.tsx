import React from "react";
import { useCurrentFrame } from "remotion";
import { C, CONTENT_W, FONT, SAFE, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";
import { CodeView, codeFont, Tokens, Window } from "../ui/CodeView";

type Side = { title: string; tone?: string; label?: string; tokens?: Tokens; items?: string[]; text?: string };
type Step = { show: "left" | "right" | "both"; hl_left?: number[]; hl_right?: number[] };

const Panel: React.FC<{ side: Side; width: number; height: number; a: number; hl: number[] }> = ({ side, width, height, a, hl }) => {
  const col = tone(side.tone ?? "blue");
  const label = side.label;
  const body = side.tokens ? (
    <Window title={side.title} accent={col} badge={label} style={{ width, borderColor: `${col}66` }}>
      <CodeView
        tokens={side.tokens}
        prev={{ hl, scroll: 0 }}
        cur={{ hl, scroll: 0 }}
        t={1}
        fontSize={codeFont(side.tokens, width, 30)}
        height={Math.min(height - 58, side.tokens.length * codeFont(side.tokens, width, 30) * 1.55 + 44)}
      />
    </Window>
  ) : (
    <div style={{ width, background: C.surface, border: `2px solid ${col}66`, borderRadius: 22, padding: "34px 38px", display: "flex", flexDirection: "column", gap: 22 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ width: 16, height: 16, borderRadius: 8, background: col }} />
        <div style={{ fontFamily: FONT, fontSize: 40, fontWeight: 800, color: C.text }}>
          <Rich text={side.title} />
        </div>
      </div>
      {side.text ? <div style={{ fontFamily: FONT, fontSize: 32, color: C.muted, lineHeight: 1.4 }}><Rich text={side.text} /></div> : null}
      {(side.items ?? []).map((it, i) => (
        <div key={i} style={{ display: "flex", gap: 18, fontFamily: FONT, fontSize: 33, color: C.text, lineHeight: 1.35 }}>
          <span style={{ color: col, fontWeight: 800 }}>•</span>
          <span>
            <Rich text={it} />
          </span>
        </div>
      ))}
    </div>
  );
  return <div style={{ opacity: a, transform: `translateY(${(1 - a) * 30}px)` }}>{body}</div>;
};

export const CompareScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; left: Side; right: Side; steps?: Step[] };
  const steps = s.steps ?? [{ show: "both" }];
  const { items, current } = itemProgress(s.beats, frame);
  const firstShow = (side: "left" | "right") => {
    const k = steps.findIndex((st) => st.show === side || st.show === "both");
    if (k < 0 || !items[k]) return s.beats[0]?.from ?? 0;
    return items[k].from;
  };
  const st = current >= 0 ? steps[current] : undefined;
  const width = (CONTENT_W - 48) / 2;
  const height = SAFE.bottom - SAFE.top - (s.heading ? 120 : 0);
  const la = frame >= firstShow("left") ? appear(frame, firstShow("left"), 22) : 0;
  const ra = frame >= firstShow("right") ? appear(frame, firstShow("right"), 22) : 0;
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <div style={{ display: "flex", gap: 48, alignItems: "flex-start" }}>
        <Panel side={s.left} width={width} height={height} a={la} hl={st?.hl_left ?? []} />
        <Panel side={s.right} width={width} height={height} a={ra} hl={st?.hl_right ?? []} />
      </div>
    </div>
  );
};
