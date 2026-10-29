import React from "react";
import { C, MONO } from "../theme";

/** Inline markup used in every text field: `code` and **emphasis**. */
export const Rich: React.FC<{ text: string; accent?: string }> = ({ text, accent = C.amber }) => {
  const parts: React.ReactNode[] = [];
  const re = /`([^`]+)`|\*\*([^*]+)\*\*/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let i = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[1] !== undefined)
      parts.push(
        <span
          key={i++}
          style={{
            fontFamily: MONO,
            fontSize: "0.86em",
            color: "#BFF5DF",
            background: "rgba(46,230,168,0.10)",
            border: "1px solid rgba(46,230,168,0.22)",
            borderRadius: 8,
            padding: "0.04em 0.28em",
          }}
        >
          {m[1]}
        </span>,
      );
    else
      parts.push(
        <span key={i++} style={{ color: accent, fontWeight: 700 }}>
          {m[2]}
        </span>,
      );
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return <>{parts}</>;
};
