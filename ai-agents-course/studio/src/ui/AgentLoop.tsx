import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT } from "../theme";

/** Signature motif of the course: the agent loop (think -> act -> observe -> repeat), slowly orbiting. */
export const AgentLoop: React.FC<{ size: number; labels?: string[]; dim?: boolean }> = ({ size, labels = ["Think", "Act", "Observe", "Repeat"], dim }) => {
  const frame = useCurrentFrame();
  const r = size * 0.36;
  const cx = size / 2;
  const rot = frame * 0.12;
  const colors = [C.violet, C.teal, C.blue, C.amber];
  const active = Math.floor(frame / 75) % labels.length;
  return (
    <svg width={size} height={size} style={{ overflow: "visible", opacity: dim ? 0.35 : 1 }}>
      <defs>
        <radialGradient id="core" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={C.teal} stopOpacity={0.18} />
          <stop offset="100%" stopColor={C.teal} stopOpacity={0} />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cx} r={r * 0.62} fill="url(#core)" />
      <circle cx={cx} cy={cx} r={r} fill="none" stroke={C.line} strokeWidth={2} />
      <circle
        cx={cx}
        cy={cx}
        r={r}
        fill="none"
        stroke={C.teal}
        strokeWidth={3}
        strokeDasharray={`${r * 0.9} ${r * 5.4}`}
        strokeLinecap="round"
        transform={`rotate(${rot * 3} ${cx} ${cx})`}
        opacity={0.8}
      />
      <circle cx={cx} cy={cx} r={r * 1.22} fill="none" stroke={C.line} strokeWidth={1} strokeDasharray="4 10" transform={`rotate(${-rot} ${cx} ${cx})`} />
      {labels.map((label, i) => {
        const ang = ((i / labels.length) * 360 - 90) * (Math.PI / 180);
        const x = cx + Math.cos(ang) * r;
        const y = cx + Math.sin(ang) * r;
        const on = i === active;
        return (
          <g key={label}>
            <circle cx={x} cy={y} r={on ? 44 : 38} fill={C.ink2} stroke={colors[i % 4]} strokeWidth={on ? 4 : 2} />
            <circle cx={x} cy={y} r={10} fill={colors[i % 4]} opacity={on ? 1 : 0.55} />
            <text x={x} y={y + (y > cx + 1 ? 84 : -62)} textAnchor="middle" fontFamily={FONT} fontWeight={700} fontSize={28} fill={on ? C.text : C.muted}>
              {label}
            </text>
          </g>
        );
      })}
    </svg>
  );
};
