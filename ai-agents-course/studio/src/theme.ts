// Course design system: "Agent Console". See COURSE_DESIGN_SYSTEM.md before changing anything here.
export const W = 1920;
export const H = 1080;

// "Paper" light theme (from Module 2's remake on): warm off-white page, dark ink, deeper accents for contrast
export const C = {
  ink: "#F7F4EC", // page
  ink2: "#EFEBE0",
  surface: "#FFFFFF",
  surface2: "#F4F1E8",
  line: "#DDD6C6",
  text: "#1E2330",
  muted: "#555D6E",
  faint: "#8C93A1",
  teal: "#0B8A68", // primary: the agent / success / "correct"
  amber: "#B86E00", // attention: highlights, warnings, numbers
  blue: "#2B66D1", // information, data flow
  violet: "#7347C9", // the model / LLM
  coral: "#CC3348", // errors, wrong answers
  code: "#FFFEFA", // code + terminal panels
  codeHead: "#F3EFE4",
  codeText: "#2A2F3A",
  shadow: "rgba(60,48,20,0.10)",
};

/** "#RRGGBB" + alpha -> rgba(), so tints follow the theme. */
export const alpha = (hex: string, a: number) =>
  `rgba(${parseInt(hex.slice(1, 3), 16)},${parseInt(hex.slice(3, 5), 16)},${parseInt(hex.slice(5, 7), 16)},${a})`;

export type Tone = "teal" | "amber" | "blue" | "violet" | "coral" | "muted";
export const tone = (t?: string) => (C as Record<string, string>)[t ?? "teal"] ?? C.teal;

export const FONT = "Inter, 'Inter Display', system-ui, sans-serif";
export const MONO = "'JetBrains Mono', 'DejaVu Sans Mono', monospace";

export const SAFE = { x: 96, top: 132, bottom: 950 }; // content box; header above, footer below
export const CONTENT_W = W - SAFE.x * 2;

// syntax colours (classes produced by tools/build_lesson.py)
export const SYNTAX: Record<string, string> = {
  kw: "#A626A4",
  con: "#986801",
  str: "#3E8E3A",
  num: "#986801",
  com: "#8E929B",
  fn: "#2F6FE0",
  cls: "#B35C00",
  bi: "#0F7FA6",
  dec: "#D1453B",
  op: "#3B4252",
  pun: "#5A6070",
  "": "#2A2F3A",
};
