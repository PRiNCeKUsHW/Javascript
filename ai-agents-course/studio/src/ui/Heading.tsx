import React from "react";
import { useCurrentFrame } from "remotion";
import { C, FONT } from "../theme";
import { appear } from "./anim";
import { Rich } from "./Rich";

export const Heading: React.FC<{ text?: string; eyebrow?: string; size?: number }> = ({ text, eyebrow, size = 60 }) => {
  const frame = useCurrentFrame();
  if (!text) return null;
  const a = appear(frame, 4, 22);
  return (
    <div style={{ opacity: a, transform: `translateY(${(1 - a) * 18}px)`, marginBottom: 36 }}>
      {eyebrow ? (
        <div
          style={{
            fontFamily: FONT,
            fontSize: 24,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: "uppercase",
            color: C.teal,
            marginBottom: 12,
          }}
        >
          {eyebrow}
        </div>
      ) : null}
      <div style={{ fontFamily: FONT, fontSize: size, fontWeight: 800, color: C.text, letterSpacing: -1, lineHeight: 1.1 }}>
        <Rich text={text} />
      </div>
    </div>
  );
};
