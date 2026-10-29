import { continueRender, delayRender, staticFile } from "remotion";

const FACES: [string, string, string][] = [
  ["Inter", "fonts/Inter-Regular.otf", "400"],
  ["Inter", "fonts/Inter-Medium.otf", "500"],
  ["Inter", "fonts/Inter-SemiBold.otf", "600"],
  ["Inter", "fonts/Inter-Bold.otf", "700"],
  ["Inter", "fonts/Inter-ExtraBold.otf", "800"],
  ["JetBrains Mono", "fonts/JetBrainsMono-Regular.ttf", "400"],
  ["JetBrains Mono", "fonts/JetBrainsMono-Medium.ttf", "500"],
  ["JetBrains Mono", "fonts/JetBrainsMono-Bold.ttf", "700"],
];

let loaded = false;
export const loadFonts = () => {
  if (loaded || typeof document === "undefined") return;
  loaded = true;
  const handle = delayRender("fonts");
  Promise.all(
    FACES.map(([family, file, weight]) => {
      const face = new FontFace(family, `url(${staticFile(file)})`, { weight });
      document.fonts.add(face);
      return face.load();
    }),
  )
    .then(() => continueRender(handle))
    .catch((e) => {
      console.error(e);
      continueRender(handle);
    });
};
