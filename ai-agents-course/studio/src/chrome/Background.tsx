import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C } from "../theme";

export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = Math.sin(frame / 600) * 60;
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(147,160,186,0.16) 1.5px, transparent 1.5px)",
          backgroundSize: "36px 36px",
          backgroundPosition: `${(frame * 0.05) % 36}px 0px`,
          maskImage: "linear-gradient(180deg, rgba(0,0,0,0.9), rgba(0,0,0,0.35))",
        }}
      />
      <AbsoluteFill style={{ background: `radial-gradient(900px 600px at ${1500 + drift}px 160px, rgba(46,230,168,0.10), transparent 70%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(800px 600px at ${260 - drift}px 1000px, rgba(108,168,255,0.08), transparent 70%)` }} />
    </AbsoluteFill>
  );
};
