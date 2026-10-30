// Render still frames for visual QA: one per scene (at 90% of the scene) plus any extra frames given.
// usage: node snapshots.mjs m01-l01 [outDir] [--at=0.5] [--frames=120,900]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [id, outArg] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const at = Number((process.argv.find((a) => a.startsWith("--at=")) ?? "--at=0.9").slice(5));
const extra = (process.argv.find((a) => a.startsWith("--frames=")) ?? "--frames=").slice(9).split(",").filter(Boolean).map(Number);
const out = outArg ?? `../logs/snapshots/${id}`;
fs.mkdirSync(out, { recursive: true });
const data = JSON.parse(fs.readFileSync(`src/data/${id}.json`, "utf8"));
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const cloudBrowser = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const browserExecutable = process.env.REMOTION_BROWSER ?? (fs.existsSync(cloudBrowser) ? cloudBrowser : null);
const composition = await selectComposition({ serveUrl, id, browserExecutable });
const frames = extra.length ? extra : data.scenes.map((s) => s.from + Math.floor(s.duration * at));
for (const [i, frame] of frames.entries()) {
  const file = path.join(out, `${String(i).padStart(2, "0")}-f${frame}.png`);
  await renderStill({ composition, serveUrl, frame, output: file, imageFormat: "png", browserExecutable });
  console.log(file);
}
fs.rmSync(serveUrl, { recursive: true, force: true }); // bundles are ~0.5 GB each: don't leave them in /tmp
