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
    code: ["$ python -m toolkit report", "Requests: 10 (8 ok, 2 errors)", "Success rate: 80.0%", "Estimated cost: 0.0498 USD"],
  },
];

export const Thumbnail: React.FC<ThumbProps> = ({ module, lines, accentLine, tagline, code }) => (
  <AbsoluteFill style={{ background: C.ink, overflow: "hidden", fontVariantLigatures: "none" }}>
    <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(147,160,186,0.18) 1.5px, transparent 1.5px)", backgroundSize: "28px 28px" }} />
    <AbsoluteFill style={{ background: "radial-gradient(700px 500px at 1050px 300px, rgba(46,230,168,0.20), transparent 70%)" }} />
    <div style={{ position: "absolute", right: -230, top: -150, opacity: 0.85 }}>
      <AgentLoop size={680} labels={["", "", "", ""]} />
    </div>
    <div style={{ position: "absolute", left: 60, top: 52, display: "flex", alignItems: "center", gap: 16 }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, color: C.ink, background: C.teal, borderRadius: 12, padding: "8px 18px" }}>MODULE {String(module).padStart(2, "0")}</div>
      <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: C.text }}>AI AGENTS WITH PYTHON</div>
    </div>
    <div style={{ position: "absolute", left: 56, top: 140 }}>
      {lines.map((l, i) => (
        <div key={l} style={{ fontFamily: FONT, fontWeight: 800, fontSize: 104, lineHeight: 0.98, letterSpacing: -3.5, color: i === accentLine ? C.teal : C.text }}>
          {l}
        </div>
      ))}
      <div style={{ marginTop: 26, fontFamily: FONT, fontWeight: 700, fontSize: 38, color: C.amber }}>{tagline}</div>
    </div>
    <div style={{ position: "absolute", right: 44, bottom: 44, width: 500, background: "#0E1522", border: `2px solid ${C.line}`, borderRadius: 18, padding: "20px 24px", boxShadow: "0 20px 60px rgba(0,0,0,0.5)" }}>
      {code.map((c, i) => (
        <div key={i} style={{ fontFamily: MONO, fontSize: 23, lineHeight: 1.5, color: i === 0 ? C.teal : "#D5DCEA", whiteSpace: "pre" }}>
          {c}
        </div>
      ))}
    </div>
  </AbsoluteFill>
);
