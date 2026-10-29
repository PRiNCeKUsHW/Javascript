// Course design system: "Agent Console". See COURSE_DESIGN_SYSTEM.md before changing anything here.
export const W = 1920;
export const H = 1080;

export const C = {
  ink: "#0A0E17",
  ink2: "#0F1522",
  surface: "#131A29",
  surface2: "#1A2335",
  line: "#28344D",
  text: "#E9EEF8",
  muted: "#93A0BA",
  faint: "#5C6884",
  teal: "#2EE6A8", // primary: the agent / success / "correct"
  amber: "#FFB547", // attention: highlights, warnings, numbers
  blue: "#6CA8FF", // information, data flow
  violet: "#B595FF", // the model / LLM
  coral: "#FF6B7A", // errors, wrong answers
};

export type Tone = "teal" | "amber" | "blue" | "violet" | "coral" | "muted";
export const tone = (t?: string) => (C as Record<string, string>)[t ?? "teal"] ?? C.teal;

export const FONT = "Inter, 'Inter Display', system-ui, sans-serif";
export const MONO = "'JetBrains Mono', 'DejaVu Sans Mono', monospace";

export const SAFE = { x: 96, top: 132, bottom: 950 }; // content box; header above, footer below
export const CONTENT_W = W - SAFE.x * 2;

// syntax colours (classes produced by tools/build_lesson.py)
export const SYNTAX: Record<string, string> = {
  kw: "#C79BFF",
  con: "#FF9E7A",
  str: "#9BE89B",
  num: "#FFB547",
  com: "#6B7896",
  fn: "#6CC4FF",
  cls: "#FFD479",
  bi: "#5FE0C8",
  dec: "#FF9E7A",
  op: "#8FB4FF",
  pun: "#A9B4CC",
  "": "#E9EEF8",
};
