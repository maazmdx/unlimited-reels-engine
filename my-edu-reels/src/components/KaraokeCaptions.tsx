import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export interface SubtitleWord {
  word: string;
  raw?: string;
  start: number;
  end: number;
}

export interface SubtitleChunk {
  start: number;
  end: number;
  text: string;
  words: SubtitleWord[];
}

export interface SubtitleData {
  words: SubtitleWord[];
  chunks: SubtitleChunk[];
}

interface KaraokeCaptionsProps {
  subtitles?: SubtitleData;
  fallbackText?: string;
}

export const KaraokeCaptions: React.FC<KaraokeCaptionsProps> = ({
  subtitles,
  fallbackText = "Why does time slow down near a black hole?",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Find currently active chunk
  const chunks = subtitles?.chunks || [];
  const activeChunk = chunks.find(
    (c) => currentTime >= c.start && currentTime <= c.end + 0.15
  );

  const displayWords = activeChunk
    ? activeChunk.words
    : fallbackText.split(" ").map((w, idx) => ({
        word: w,
        raw: w,
        start: idx * 0.4,
        end: (idx + 1) * 0.4,
      }));

  const chunkSpring = spring({
    frame: frame % 30,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 180 },
  });

  return (
    <div
      style={{
        position: "absolute",
        left: 64,
        right: 64,
        bottom: 290, // Safe zone: above Instagram UI controls
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 100,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          background: "rgba(11, 15, 25, 0.92)",
          backdropFilter: "blur(14px)",
          border: "2px solid rgba(255, 255, 255, 0.2)",
          boxShadow: "0 20px 40px rgba(0, 0, 0, 0.75), 0 0 35px rgba(0, 240, 255, 0.25)",
          borderRadius: 28,
          padding: "18px 36px",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: "14px",
          maxWidth: 960,
          transform: `scale(${0.96 + chunkSpring * 0.04})`,
        }}
      >
        {displayWords.map((item, index) => {
          const isWordActive =
            currentTime >= item.start && currentTime <= item.end;
          const isPast = currentTime > item.end;

          const wordFrame = Math.max(0, (currentTime - item.start) * fps);
          const wordSpring = spring({
            frame: wordFrame,
            fps,
            config: { damping: 10, mass: 0.5, stiffness: 220 },
          });

          const scale = isWordActive
            ? interpolate(wordSpring, [0, 1], [1, 1.22])
            : 1.0;

          const color = isWordActive
            ? "#FFE600" // Neon yellow active word
            : isPast
            ? "#FFFFFF"
            : "rgba(255, 255, 255, 0.65)";

          const textShadow = isWordActive
            ? "0 0 20px rgba(255, 230, 0, 0.95), 0 0 40px rgba(255, 200, 0, 0.6)"
            : "0 3px 6px rgba(0,0,0,0.9)";

          return (
            <span
              key={`${item.word}-${index}`}
              style={{
                // Universal font stack supporting English, Hindi (Devanagari) and Kannada
                fontFamily:
                  "'Noto Sans Kannada', 'Noto Sans Devanagari', 'Impact', system-ui, -apple-system, sans-serif",
                fontWeight: 900,
                fontSize: 48,
                letterSpacing: "-0.5px",
                color,
                textShadow,
                WebkitTextStroke: isWordActive ? "2px #000000" : "1px #000000",
                display: "inline-block",
                transform: `scale(${scale})`,
                transition: "color 0.1s ease",
              }}
            >
              {item.word}
            </span>
          );
        })}
      </div>
    </div>
  );
};
