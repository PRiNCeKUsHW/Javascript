import { Easing, interpolate } from "remotion";

/** 0 -> 1 over `dur` frames starting at `at`, eased out. */
export const appear = (frame: number, at: number, dur = 18) =>
  interpolate(frame, [at, at + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

export type Beat = { from: number; kind: "intro" | "item" | "outro" | "think" | "reveal" };
export type SceneBase = { type: string; from: number; duration: number; beats: Beat[]; [k: string]: unknown };

/** How many item beats have started, and when the latest one began. */
export const itemProgress = (beats: Beat[], frame: number) => {
  const items = beats.filter((b) => b.kind === "item");
  const started = items.filter((b) => frame >= b.from);
  return { items, count: started.length, current: started.length - 1 };
};

export const beatStart = (beats: Beat[], kind: Beat["kind"]) => beats.find((b) => b.kind === kind)?.from ?? 0;
