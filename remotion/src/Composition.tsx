import {
  AbsoluteFill,
  Composition,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type BrandIntroProps = {
  channelName: string;
  tagline: string;
  accent: string;
};

const defaultProps: BrandIntroProps = {
  channelName: "Your Channel",
  tagline: "New videos every week",
  accent: "#22d3ee",
};

const DURATION_IN_FRAMES = 150;

export const BrandIntroComposition = () => {
  return (
    <Composition
      id="BrandIntro"
      component={BrandIntro}
      durationInFrames={DURATION_IN_FRAMES}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={defaultProps}
    />
  );
};

export const BrandIntro: React.FC<BrandIntroProps> = ({
  channelName,
  tagline,
  accent,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Everything fades out over the last second so the loop ends cleanly.
  const outro = interpolate(
    frame,
    [durationInFrames - 30, durationInFrames - 1],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Play mark: springs in, then pulses once.
  const markScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 120 },
  });
  const pulse = interpolate(frame, [48, 56, 64], [1, 1.08, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Wordmark: letters rise in one after another.
  const letters = Array.from(channelName);
  const wordStart = 14;
  const letterStagger = 2;

  // Underline sweeps out beneath the wordmark once the letters have landed.
  const sweepStart = wordStart + letters.length * letterStagger + 4;
  const sweep = interpolate(frame, [sweepStart, sweepStart + 18], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const taglineOpacity = interpolate(
    frame,
    [sweepStart + 12, sweepStart + 30],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    },
  );

  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(circle at 50% 45%, #1c2030 0%, #0a0b10 70%)",
        color: "#ffffff",
        fontFamily: "Inter, system-ui, sans-serif",
        alignItems: "center",
        justifyContent: "center",
        opacity: outro,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 48,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 48 }}>
          <div
            style={{
              width: 220,
              height: 156,
              borderRadius: 40,
              background: accent,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transform: `scale(${markScale * pulse})`,
            }}
          >
            <div
              style={{
                width: 0,
                height: 0,
                borderTop: "32px solid transparent",
                borderBottom: "32px solid transparent",
                borderLeft: "52px solid #0a0b10",
                marginLeft: 14,
              }}
            />
          </div>

          <div style={{ position: "relative", display: "flex" }}>
            {letters.map((letter, i) => {
              const start = wordStart + i * letterStagger;
              const progress = spring({
                frame: frame - start,
                fps,
                config: { damping: 200 },
              });
              return (
                <span
                  key={`${letter}-${i}`}
                  style={{
                    fontSize: 130,
                    fontWeight: 700,
                    letterSpacing: "-0.02em",
                    whiteSpace: "pre",
                    display: "inline-block",
                    opacity: progress,
                    transform: `translateY(${(1 - progress) * 40}px)`,
                  }}
                >
                  {letter}
                </span>
              );
            })}
          </div>
        </div>

        <div
          style={{
            width: 1000,
            height: 6,
            background: accent,
            borderRadius: 3,
            clipPath: `inset(0 ${100 - sweep}% 0 0)`,
          }}
        />

        <div
          style={{
            fontSize: 48,
            fontWeight: 500,
            color: "#c9ced9",
            opacity: taglineOpacity,
            letterSpacing: "0.01em",
          }}
        >
          {tagline}
        </div>
      </div>
    </AbsoluteFill>
  );
};
