import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SAFE, W } from "../theme";

/** Fades/lifts every scene in and out so cuts never flash. */
export const SceneFrame: React.FC<{ duration: number; children: React.ReactNode; pad?: boolean }> = ({ duration, children, pad = true }) => {
  const frame = useCurrentFrame();
  const inT = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const outT = interpolate(frame, [duration - 14, duration], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: pad ? SAFE.x : 0,
        top: pad ? SAFE.top : 0,
        width: pad ? W - SAFE.x * 2 : W,
        height: pad ? SAFE.bottom - SAFE.top : "100%",
        opacity: Math.min(inT, outT),
        transform: `translateY(${(1 - inT) * 14}px)`,
      }}
    >
      {children}
    </div>
  );
};
