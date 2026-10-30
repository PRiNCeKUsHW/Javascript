// Render several lesson compositions from ONE bundle, then delete the bundle.
// (`npx remotion render` bundles once per call and each bundle copies public/, ~0.5 GB.)
// usage: node render.mjs <outDir> m04-l01 m04-l02 ...   -> <outDir>/lesson-01.mp4 ...
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import fs from "node:fs";
import path from "node:path";

const [outDir, ...ids] = process.argv.slice(2);
const cloudBrowser = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell";
const browserExecutable = process.env.REMOTION_BROWSER ?? (fs.existsSync(cloudBrowser) ? cloudBrowser : null);
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
try {
  for (const id of ids) {
    const out = path.join(outDir, `lesson-${id.slice(-2)}.mp4`);
    const partial = out.replace(/\.mp4$/, ".partial.mp4");
    const start = Date.now();
    const composition = await selectComposition({ serveUrl, id, browserExecutable });
    await renderMedia({
      composition, serveUrl, codec: "h264", crf: 18, audioCodec: "aac", audioBitrate: "192k",
      imageFormat: "jpeg", outputLocation: partial, overwrite: true, browserExecutable,
      concurrency: Number(process.env.REMOTION_CONCURRENCY ?? 4),
    });
    fs.renameSync(partial, out);
    console.log(`lesson ${Number(id.slice(-2))}: rendered in ${((Date.now() - start) / 60000).toFixed(1)} min -> ${out}`);
  }
} finally {
  fs.rmSync(serveUrl, { recursive: true, force: true });
}
