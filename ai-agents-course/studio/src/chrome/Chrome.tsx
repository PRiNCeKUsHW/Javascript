import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, FONT, MONO, SAFE, W } from "../theme";

export const Header: React.FC<{ module: number; lesson: number; chapter?: string }> = ({ module, lesson, chapter }) => (
  <div style={{ position: "absolute", left: SAFE.x, right: SAFE.x, top: 44, height: 44, display: "flex", alignItems: "center", gap: 18 }}>
    <svg width={34} height={34} viewBox="0 0 34 34">
      <circle cx={17} cy={17} r={13} fill="none" stroke={C.teal} strokeWidth={3} />
      <circle cx={17} cy={4} r={4} fill={C.teal} />
      <circle cx={17} cy={17} r={4} fill={C.text} />
    </svg>
    <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 22, letterSpacing: 2.5, color: C.text }}>AI AGENTS WITH PYTHON</div>
    <div style={{ width: 1, height: 26, background: C.line }} />
    <div style={{ fontFamily: MONO, fontSize: 21, color: C.muted }}>
      Module {String(module).padStart(2, "0")} · Lesson {lesson}
    </div>
    {chapter ? (
      <div style={{ marginLeft: "auto", fontFamily: MONO, fontSize: 21, color: C.muted, display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ width: 8, height: 8, borderRadius: 4, background: C.amber }} />
        {chapter}
      </div>
    ) : null}
  </div>
);

/** Bottom bar: lesson progress plus a speaking indicator driven by the narration envelope. */
export const Footer: React.FC<{ envelope: number[]; hz: number; fps: number; total: number }> = ({ envelope, hz, fps, total }) => {
  const frame = useCurrentFrame();
  const i = Math.floor((frame / fps) * hz);
  const level = envelope[Math.min(envelope.length - 1, i)] ?? 0;
  const progress = interpolate(frame, [0, total], [0, 1], { extrapolateRight: "clamp" });
  const bars = [0.55, 0.85, 1, 0.75, 0.5];
  return (
    <>
      <div style={{ position: "absolute", left: 0, bottom: 0, width: W, height: 6, background: C.line }}>
        <div style={{ width: `${progress * 100}%`, height: "100%", background: `linear-gradient(90deg, ${C.teal}, ${C.blue})` }} />
      </div>
      <div style={{ position: "absolute", right: SAFE.x, bottom: 34, display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 5, height: 40 }}>
          {bars.map((b, k) => {
            const wobble = 0.65 + 0.35 * Math.sin(frame / 3 + k * 1.7);
            const h = 6 + 32 * Math.min(1, level * 1.4) * b * wobble;
            return <div key={k} style={{ width: 6, height: h, borderRadius: 3, background: level > 0.05 ? C.teal : C.faint }} />;
          })}
        </div>
        <div style={{ fontFamily: MONO, fontSize: 19, color: C.faint, letterSpacing: 2 }}>INSTRUCTOR</div>
      </div>
    </>
  );
};
