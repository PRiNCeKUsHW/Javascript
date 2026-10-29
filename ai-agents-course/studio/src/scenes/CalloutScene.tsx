import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT, MONO, tone } from "../theme";
import { appear, itemProgress, SceneBase } from "../ui/anim";
import { Rich } from "../ui/Rich";

const KINDS: Record<string, { color: string; label: string; icon: string }> = {
  error: { color: "coral", label: "Common error", icon: "!" },
  warn: { color: "amber", label: "Watch out", icon: "!" },
  tip: { color: "teal", label: "Pro tip", icon: "✓" },
  info: { color: "blue", label: "Good to know", icon: "i" },
  challenge: { color: "violet", label: "Extension challenge", icon: "★" },
};

export const CalloutScene: React.FC<{ scene: SceneBase }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const s = scene as SceneBase & { kind?: string; label?: string; title: string; body?: string; error?: string; fix?: string; items?: { text: string }[] };
  const k = KINDS[s.kind ?? "info"];
  const col = tone(k.color);
  const { items, count, current } = itemProgress(s.beats, frame);
  const a = appear(frame, 4, 24);
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div
        style={{
          width: 1520,
          opacity: a,
          transform: `scale(${0.96 + 0.04 * a})`,
          background: C.surface,
          border: `1px solid ${C.line}`,
          borderTop: `6px solid ${col}`,
          borderRadius: 28,
          padding: "52px 64px",
          boxShadow: "0 40px 100px rgba(0,0,0,0.45)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20, marginBottom: 26 }}>
          <div style={{ width: 56, height: 56, borderRadius: 28, background: col, color: C.ink, fontFamily: FONT, fontWeight: 800, fontSize: 32, display: "flex", alignItems: "center", justifyContent: "center" }}>{k.icon}</div>
          <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 3, textTransform: "uppercase", color: col, fontWeight: 700 }}>{s.label ?? k.label}</div>
        </div>
        <div style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: C.text, lineHeight: 1.15, letterSpacing: -1 }}>
          <Rich text={s.title} />
        </div>
        {s.body ? <div style={{ fontFamily: FONT, fontSize: 36, color: C.muted, lineHeight: 1.45, marginTop: 22 }}><Rich text={s.body} /></div> : null}
        {s.error ? (
          <div style={{ marginTop: 30, fontFamily: MONO, fontSize: 28, color: "#FFB3BB", background: "#1A0F16", border: `1px solid ${C.coral}55`, borderRadius: 16, padding: "20px 26px", whiteSpace: "pre-wrap", lineHeight: 1.45 }}>{s.error}</div>
        ) : null}
        {s.fix ? (
          <div style={{ marginTop: 22, opacity: appear(frame, s.beats[s.beats.length - 1].from, 20), fontFamily: FONT, fontSize: 34, color: C.text, display: "flex", gap: 16, lineHeight: 1.4 }}>
            <span style={{ color: C.teal, fontWeight: 800 }}>Fix:</span>
            <span>
              <Rich text={s.fix} />
            </span>
          </div>
        ) : null}
        {s.items?.length ? (
          <div style={{ marginTop: 30, display: "flex", flexDirection: "column", gap: 18 }}>
            {s.items.map((it, i) => (
              <div key={i} style={{ opacity: i < count ? appear(frame, items[i].from, 18) * (i === current ? 1 : 0.7) : 0, display: "flex", gap: 18, fontFamily: FONT, fontSize: 34, color: C.text, lineHeight: 1.35 }}>
                <span style={{ color: col, fontWeight: 800, fontFamily: MONO }}>{String(i + 1).padStart(2, "0")}</span>
                <span>
                  <Rich text={it.text} />
                </span>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
};
