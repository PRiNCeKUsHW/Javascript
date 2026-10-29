import React from "react";
import { AbsoluteFill } from "remotion";
import { C, FONT, MONO } from "./theme";
import { loadFonts } from "./fonts";
import { AgentLoop } from "./ui/AgentLoop";

loadFonts();

export type ThumbProps = { id: string; module: number; lines: string[]; accentLine: number; tagline: string; code: string[] };

// one entry per finished module; rendered with `npx remotion still <id>`
export const THUMBS: ThumbProps[] = [
  {
    id: "thumb-m01",
    module: 1,
    lines: ["PYTHON", "FOR AI", "ENGINEERING"],
    accentLine: 1,
    tagline: "Build a real CLI project from zero",
    code: ["$ python -m toolkit report", "Requests: 10 (8 ok)", "Success rate: 80.0%", "Estimated cost: 0.0498"],
  },
];

export const Thumbnail: React.FC<ThumbProps> = ({ module, lines, accentLine, tagline, code }) => (
  <AbsoluteFill style={{ background: C.ink, overflow: "hidden", fontVariantLigatures: "none" }}>
    <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(147,160,186,0.18) 1.5px, transparent 1.5px)", backgroundSize: "28px 28px" }} />
    <AbsoluteFill style={{ background: "radial-gradient(700px 500px at 1050px 300px, rgba(46,230,168,0.20), transparent 70%)" }} />
    <div style={{ position: "absolute", right: -150, top: 40, opacity: 0.9 }}>
      <AgentLoop size={640} />
    </div>
    <div style={{ position: "absolute", left: 60, top: 52, display: "flex", alignItems: "center", gap: 16 }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, color: C.ink, background: C.teal, borderRadius: 12, padding: "8px 18px" }}>MODULE {String(module).padStart(2, "0")}</div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: C.text }}>AI AGENTS WITH PYTHON</div>
    </div>
    <div style={{ position: "absolute", left: 56, top: 140 }}>
      {lines.map((l, i) => (
        <div key={l} style={{ fontFamily: FONT, fontWeight: 800, fontSize: 118, lineHeight: 0.98, letterSpacing: -4, color: i === accentLine ? C.teal : C.text }}>
          {l}
        </div>
      ))}
      <div style={{ marginTop: 26, fontFamily: FONT, fontWeight: 700, fontSize: 38, color: C.amber }}>{tagline}</div>
    </div>
    <div style={{ position: "absolute", right: 50, bottom: 50, width: 470, background: "#0E1522", border: `2px solid ${C.line}`, borderRadius: 18, padding: "20px 24px", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>
      {code.map((c, i) => (
        <div key={i} style={{ fontFamily: MONO, fontSize: 25, lineHeight: 1.5, color: i === 0 ? C.teal : "#D5DCEA", whiteSpace: "pre" }}>
          {c}
        </div>
      ))}
    </div>
  </AbsoluteFill>
);
