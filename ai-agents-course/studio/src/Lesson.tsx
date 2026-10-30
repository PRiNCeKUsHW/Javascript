import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import { Background } from "./chrome/Background";
import { Footer, Header } from "./chrome/Chrome";
import { loadFonts } from "./fonts";
import { SceneBase } from "./ui/anim";
import { SceneFrame } from "./scenes/SceneFrame";
import { TitleScene } from "./scenes/TitleScene";
import { SectionScene } from "./scenes/SectionScene";
import { BulletsScene } from "./scenes/BulletsScene";
import { CardsScene } from "./scenes/CardsScene";
import { CodeScene } from "./scenes/CodeScene";
import { TerminalScene } from "./scenes/TerminalScene";
import { DiagramScene } from "./scenes/DiagramScene";
import { CompareScene } from "./scenes/CompareScene";
import { CalloutScene } from "./scenes/CalloutScene";
import { QuizScene } from "./scenes/QuizScene";
import { LinksScene } from "./scenes/LinksScene";
import { RunScene } from "./scenes/RunScene";

loadFonts();

export type LessonData = {
  id: string;
  module: number;
  lesson: number;
  moduleTitle: string;
  title: string;
  fps: number;
  durationInFrames: number;
  audio: string;
  envelope: number[];
  envelopeHz: number;
  chapters: { t: number; title: string }[];
  scenes: SceneBase[];
};

const SCENES: Record<string, React.FC<{ scene: SceneBase }>> = {
  title: TitleScene,
  section: SectionScene,
  bullets: BulletsScene,
  objectives: BulletsScene,
  recap: BulletsScene,
  steps: BulletsScene,
  cards: CardsScene,
  code: CodeScene,
  terminal: TerminalScene,
  diagram: DiagramScene,
  compare: CompareScene,
  callout: CalloutScene,
  quiz: QuizScene,
  links: LinksScene,
  run: RunScene,
};


export const Lesson: React.FC<{ data: LessonData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const t = frame / data.fps;
  const chapter = [...data.chapters].reverse().find((c) => c.t <= t + 0.01)?.title;
  return (
    <AbsoluteFill style={{ fontVariantLigatures: "none", fontFeatureSettings: '"liga" 0, "calt" 0' }}>
      <Background />
      {data.scenes.map((scene, i) => {
        const Comp = SCENES[scene.type];
        if (!Comp) throw new Error(`unknown scene type ${scene.type}`);
        return (
          <Sequence key={i} from={scene.from} durationInFrames={scene.duration} premountFor={0}>
            <SceneFrame duration={scene.duration} pad>
              <Comp scene={scene} />
            </SceneFrame>
          </Sequence>
        );
      })}
      <Header module={data.module} lesson={data.lesson} chapter={chapter} />
      <Footer envelope={data.envelope} hz={data.envelopeHz} fps={data.fps} total={data.durationInFrames} />
      <Audio src={staticFile(data.audio)} />
    </AbsoluteFill>
  );
};
