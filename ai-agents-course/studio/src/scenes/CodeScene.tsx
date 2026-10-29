import React from "react";
import { useCurrentFrame } from "remotion";
import { C, CONTENT_W, FONT, SAFE, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";
import { CodeState, CodeView, codeFont, scrollFor, Tokens, visibleLines, Window } from "../ui/CodeView";

type Step = { hl: number[]; upto?: number; note?: string; tone?: string };

export const CodeScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; title?: string; tokens: Tokens; first_line: number; steps?: Step[]; badge?: string };
  const steps = s.steps ?? [];
  const { items, current } = itemProgress(s.beats, frame);
  const hasNotes = steps.some((st) => st.note);
  // notes sit beside the code unless that would shrink wide code below a readable size
  const notesBelow = hasNotes && codeFont(s.tokens, CONTENT_W - 560) < 27;
  const notesSide = hasNotes && !notesBelow;
  const panelW = notesSide ? CONTENT_W - 560 : CONTENT_W;
  const panelH = SAFE.bottom - SAFE.top - (s.heading ? 120 : 0) - 58 - (notesBelow ? 150 : 0);
  const fs = codeFont(s.tokens, panelW);
  const vis = visibleLines(panelH, fs);
  const total = s.tokens.length;
  const bodyH = Math.min(panelH, total * fs * 1.55 + 44);

  const stateAt = (k: number): CodeState => {
    const st = k < 0 ? { hl: [], upto: steps[0]?.upto } : steps[k];
    return { hl: st.hl ?? [], upto: st.upto, scroll: scrollFor(total, vis, st.hl ?? [], st.upto) };
  };
  const cur = stateAt(Math.min(current, steps.length - 1));
  const prev = stateAt(Math.min(current - 1, steps.length - 1));
  const t = current >= 0 ? appear(frame, items[current].from, 24) : 1;
  const step = current >= 0 ? steps[current] : undefined;
  const noteColor = tone(step?.tone ?? "amber");

  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <div style={{ display: "flex", flexDirection: notesBelow ? "column" : "row", gap: notesBelow ? 24 : 40, alignItems: "flex-start" }}>
        <Window title={s.title} badge={s.badge} style={{ width: panelW, opacity: appear(frame, 6, 22) }}>
          <CodeView tokens={s.tokens} firstLine={s.first_line} prev={prev} cur={cur} t={t} fontSize={fs} height={bodyH} />
        </Window>
        {hasNotes ? (
          <div style={{ width: notesBelow ? CONTENT_W : 520, position: "relative", height: notesBelow ? 126 : bodyH + 58 }}>
            {steps.map((st, k) =>
              st.note ? (
                <div
                  key={k}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    opacity: k === current ? appear(frame, items[k].from + 6, 20) : 0,
                    transform: `translateY(${k === current ? (1 - appear(frame, items[k].from + 6, 20)) * 24 : 0}px)`,
                    background: C.surface,
                    border: `1px solid ${C.line}`,
                    borderLeft: `6px solid ${noteColor}`,
                    borderRadius: 20,
                    padding: notesBelow ? "22px 32px" : "30px 32px",
                    fontFamily: FONT,
                    fontSize: notesBelow ? 31 : 33,
                    lineHeight: 1.4,
                    color: C.text,
                  }}
                >
                  <Rich text={st.note} />
                </div>
              ) : null,
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
};
