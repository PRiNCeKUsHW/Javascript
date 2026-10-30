import React from "react";
import { useCurrentFrame } from "remotion";
import { C, CONTENT_W, FONT, MONO, SAFE, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Heading } from "../ui/Heading";
import { Rich } from "../ui/Rich";

type Node = { id: string; label: string; sub?: string; x: number; y: number; w?: number; h?: number; tone?: string; mono?: boolean; shape?: "pill" | "box" | "db"; align?: "top" };
type Edge = { from: string; to: string; label?: string; dashed?: boolean; bend?: number };
type Step = { show?: string[]; focus?: string[]; flow?: string[]; caption?: string };

const edgeId = (e: Edge) => `${e.from}->${e.to}`;

/** Point where the segment from the centre of `n` towards (tx, ty) leaves its rectangle. */
const exitPoint = (n: Node, tx: number, ty: number) => {
  const w = (n.w ?? 300) / 2 + 8;
  const h = (n.h ?? 120) / 2 + 8;
  const dx = tx - n.x;
  const dy = ty - n.y;
  const s = Math.min(Math.abs(dx) > 0 ? w / Math.abs(dx) : Infinity, Math.abs(dy) > 0 ? h / Math.abs(dy) : Infinity);
  return [n.x + dx * s, n.y + dy * s];
};

export const DiagramScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { heading?: string; eyebrow?: string; nodes: Node[]; edges?: Edge[]; steps: Step[]; initial?: string[] };
  const { items, current } = itemProgress(s.beats, frame);
  const canvasH = SAFE.bottom - SAFE.top - (s.heading ? 120 : 0);
  const byId = Object.fromEntries(s.nodes.map((n) => [n.id, n]));
  const edges = s.edges ?? [];

  // first frame each element becomes visible
  const shownAt: Record<string, number> = {};
  (s.initial ?? []).forEach((id) => (shownAt[id] = 8));
  s.steps.forEach((st, k) => {
    if (!items[k]) return;
    (st.show ?? []).forEach((id) => {
      if (shownAt[id] === undefined) shownAt[id] = items[k].from;
    });
  });
  const visible = (id: string) => shownAt[id] !== undefined && frame >= shownAt[id];
  const step = current >= 0 ? s.steps[current] : undefined;
  const focus = new Set(step?.focus ?? []);
  const flow = new Set(step?.flow ?? []);
  const anyFocus = focus.size > 0;

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <Heading text={s.heading} eyebrow={s.eyebrow} size={52} />
      <div style={{ position: "absolute", left: 0, top: s.heading ? 120 : 0, width: CONTENT_W, height: canvasH }}>
        <svg width={CONTENT_W} height={canvasH} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          <defs>
            {["teal", "blue", "amber", "violet", "coral", "muted"].map((t) => (
              <marker key={t} id={`arrow-${t}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M0,0 L10,5 L0,10 z" fill={t === "muted" ? C.faint : tone(t)} />
              </marker>
            ))}
          </defs>
          {edges.map((e) => {
            const id = edgeId(e);
            if (!visible(id)) return null;
            const a = byId[e.from];
            const b = byId[e.to];
            const bend = e.bend ?? 0;
            const mx = (a.x + b.x) / 2 - (b.y - a.y) * bend;
            const my = (a.y + b.y) / 2 + (b.x - a.x) * bend;
            const [x1, y1] = exitPoint(a, bend ? mx : b.x, bend ? my : b.y);
            const [x2, y2] = exitPoint(b, bend ? mx : a.x, bend ? my : a.y);
            const d = bend ? `M${x1},${y1} Q${mx},${my} ${x2},${y2}` : `M${x1},${y1} L${x2},${y2}`;
            const len = Math.hypot(x2 - x1, y2 - y1) * (bend ? 1.25 : 1);
            // label on the curve itself (a quadratic's midpoint), not at its control point
            const lx = bend ? 0.25 * x1 + 0.5 * mx + 0.25 * x2 : (x1 + x2) / 2;
            const ly = bend ? 0.25 * y1 + 0.5 * my + 0.25 * y2 : (y1 + y2) / 2;
            const p = appear(frame, shownAt[id], 26);
            const active = flow.has(id);
            const col = active ? C.teal : anyFocus && !(focus.has(e.from) || focus.has(e.to)) ? C.line : C.faint;
            const u = ((frame - shownAt[id]) % 60) / 60; // packet position along the edge, deterministic per frame
            const dotX = bend ? (1 - u) ** 2 * x1 + 2 * (1 - u) * u * mx + u * u * x2 : x1 + (x2 - x1) * u;
            const dotY = bend ? (1 - u) ** 2 * y1 + 2 * (1 - u) * u * my + u * u * y2 : y1 + (y2 - y1) * u;
            return (
              <g key={id}>
                <path d={d} fill="none" stroke={col} strokeWidth={active ? 4 : 3} strokeDasharray={e.dashed ? "10 10" : `${len} ${len}`} strokeDashoffset={e.dashed ? 0 : len * (1 - p)} opacity={e.dashed ? p : 1} markerEnd={p > 0.95 ? `url(#arrow-${active ? "teal" : "muted"})` : undefined} />
                {active && p > 0.95 ? (
                  <circle cx={dotX} cy={dotY} r={9} fill={C.teal} />
                ) : null}
                {e.label && p > 0.5 ? (
                  <g opacity={(p - 0.5) * 2}>
                    <rect x={lx - e.label.length * 7.6 - 14} y={ly - 21} width={e.label.length * 15.2 + 28} height={42} rx={21} fill={C.ink} stroke={C.line} />
                    <text x={lx} y={ly + 8} textAnchor="middle" fontFamily={MONO} fontSize={23} fill={active ? C.teal : C.muted}>
                      {e.label}
                    </text>
                  </g>
                ) : null}
              </g>
            );
          })}
        </svg>
        {s.nodes.map((n) => {
          if (!visible(n.id)) return null;
          const a = appear(frame, shownAt[n.id], 22);
          const w = n.w ?? 300;
          const h = n.h ?? 120;
          const col = tone(n.tone ?? "blue");
          const dim = anyFocus && !focus.has(n.id);
          const on = focus.has(n.id);
          return (
            <div
              key={n.id}
              style={{
                position: "absolute",
                left: n.x - w / 2,
                top: n.y - h / 2,
                width: w,
                height: h,
                opacity: a * (dim ? 0.38 : 1),
                transform: `scale(${0.85 + 0.15 * a})`,
                borderRadius: n.shape === "pill" ? h / 2 : n.shape === "db" ? "24px 24px 50% 50% / 24px 24px 18% 18%" : 22,
                background: on ? `${col}22` : C.surface,
                border: `${on ? 3 : 2}px solid ${col}`,
                boxShadow: on ? `0 0 0 8px ${col}14, 0 20px 50px ${C.shadow}` : `0 12px 30px ${C.shadow}`,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: n.align === "top" ? "flex-start" : "center",
                textAlign: "center",
                padding: n.align === "top" ? "18px 18px 0" : "0 18px",
              }}
            >
              <div style={{ fontFamily: n.mono ? MONO : FONT, fontSize: n.mono ? 28 : 32, fontWeight: 700, color: C.text, lineHeight: 1.15 }}>
                <Rich text={n.label} />
              </div>
              {n.sub ? <div style={{ fontFamily: FONT, fontSize: 22, color: C.muted, marginTop: 6, lineHeight: 1.25 }}><Rich text={n.sub} /></div> : null}
            </div>
          );
        })}
        {step?.caption ? (
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              bottom: 0,
              display: "flex",
              justifyContent: "center",
              opacity: appear(frame, items[current].from + 8, 18),
            }}
          >
            <div style={{ fontFamily: FONT, fontSize: 32, color: C.text, background: C.surface2, border: `1px solid ${C.line}`, borderRadius: 999, padding: "14px 34px" }}>
              <Rich text={step.caption} />
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
