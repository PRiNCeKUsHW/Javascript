import React from "react";
import { Composition, Still } from "remotion";
import { Lesson, LessonData } from "./Lesson";
import { LESSONS } from "./lessons";
import { Thumbnail, ThumbProps, THUMBS } from "./Thumbnail";
import { H, W } from "./theme";

export const RemotionRoot: React.FC = () => (
  <>
    {(LESSONS as unknown as LessonData[]).map((data) => (
      <Composition key={data.id} id={data.id} component={Lesson} durationInFrames={data.durationInFrames} fps={data.fps} width={W} height={H} defaultProps={{ data }} />
    ))}
    {THUMBS.map((t: ThumbProps) => (
      <Still key={t.id} id={t.id} component={Thumbnail} width={1280} height={720} defaultProps={t} />
    ))}
  </>
);
