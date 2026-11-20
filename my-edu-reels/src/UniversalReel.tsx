import React from "react";
import {
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";
import { BackgroundGrid } from "./components/BackgroundGrid";
import { ProgressBar } from "./components/ProgressBar";
import { KaraokeCaptions, SubtitleData } from "./components/KaraokeCaptions";
import { DEFAULT_SUBTITLES } from "./data/defaultSubs";

export interface SceneItem {
  title: string;
  tag?: string;
  text: string;
}

export interface UniversalReelProps {
  [key: string]: unknown;
  title?: string;
  tag?: string;
  scenes?: SceneItem[];
  subtitles?: SubtitleData;
  audioSrc?: string;
  accentColor?: string;
}

export const UniversalReel: React.FC<UniversalReelProps> = ({
  title = "Universal Mind Explainer",
  tag = "DID YOU KNOW?",
  scenes = [
    {
      title: "The Initial Paradox",
      tag: "THE HOOK",
      text: "Reality is far stranger than what common sense tells us.",
    },
    {
      title: "The Hidden Mechanism",
      tag: "CORE INSIGHT",
      text: "Deep underneath the surface, fundamental laws bend the rules of everyday physics.",
    },
    {
      title: "The Big Takeaway",
      tag: "MIND = BLOWN",
      text: "Every discovery pushes human knowledge one step further into the unknown.",
    },
  ],
  subtitles = DEFAULT_SUBTITLES,
  audioSrc = "voice.mp3",
  accentColor = "#00F0FF",
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  // Determine active scene based on progress through duration
  const totalScenes = Math.max(scenes.length, 1);
  const framesPerScene = durationInFrames / totalScenes;
  const currentSceneIndex = Math.min(
    Math.floor(frame / framesPerScene),
    totalScenes - 1
  );
  const activeScene = scenes[currentSceneIndex] || scenes[0];

  const sceneProgressFrame = Math.max(0, frame - currentSceneIndex * framesPerScene);
  const sceneSpring = spring({
    frame: sceneProgressFrame,
    fps,
    config: { damping: 13, mass: 0.6, stiffness: 160 },
  });

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#0B0F19",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile(audioSrc)} />
      <ProgressBar color={accentColor} />
      <BackgroundGrid theme="space" />

      {/* Safe Area Container */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          boxSizing: "border-box",
          paddingTop: 220,
          paddingBottom: 280,
          paddingLeft: 64,
          paddingRight: 64,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          zIndex: 10,
        }}
      >
        {/* Dynamic Category Pill */}
        <div
          style={{
            background: `linear-gradient(90deg, #6366F1, ${accentColor})`,
            padding: "10px 30px",
            borderRadius: 999,
            boxShadow: `0 0 24px ${accentColor}`,
            marginBottom: 24,
          }}
        >
          <span
            style={{
              fontFamily: "system-ui, sans-serif",
              fontWeight: 900,
              fontSize: 24,
              letterSpacing: "3px",
              color: "#FFFFFF",
              textTransform: "uppercase",
            }}
          >
            {activeScene.tag || tag}
          </span>
        </div>

        {/* Dynamic Main Title */}
        <h1
          style={{
            fontFamily: "system-ui, sans-serif",
            fontWeight: 900,
            fontSize: 64,
            textAlign: "center",
            color: "#FFFFFF",
            lineHeight: 1.15,
            margin: "0 0 40px 0",
            textShadow: `0 0 30px ${accentColor}`,
            maxWidth: 900,
          }}
        >
          {title}
        </h1>

        {/* Dynamic Active Scene Card */}
        <div
          style={{
            background: "rgba(18, 24, 38, 0.88)",
            backdropFilter: "blur(20px)",
            border: `2px solid ${accentColor}`,
            borderRadius: 36,
            padding: "48px 40px",
            width: "100%",
            maxWidth: 920,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            transform: `scale(${0.94 + sceneSpring * 0.06})`,
            boxShadow: `0 24px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(0, 240, 255, 0.2)`,
          }}
        >
          <span
            style={{
              fontFamily: "system-ui, sans-serif",
              fontWeight: 800,
              fontSize: 26,
              color: accentColor,
              letterSpacing: "1px",
              textTransform: "uppercase",
              marginBottom: 16,
            }}
          >
            Phase {currentSceneIndex + 1} of {totalScenes}: {activeScene.title}
          </span>

          <p
            style={{
              fontFamily: "system-ui, sans-serif",
              fontSize: 36,
              fontWeight: 700,
              textAlign: "center",
              color: "#F8FAFC",
              lineHeight: 1.4,
              margin: "12px 0 24px 0",
            }}
          >
            {activeScene.text}
          </p>

          {/* Scene indicator dots */}
          <div style={{ display: "flex", gap: "12px", marginTop: 12 }}>
            {scenes.map((_, idx) => (
              <div
                key={idx}
                style={{
                  width: idx === currentSceneIndex ? 36 : 14,
                  height: 14,
                  borderRadius: 7,
                  backgroundColor:
                    idx === currentSceneIndex
                      ? accentColor
                      : "rgba(255, 255, 255, 0.2)",
                  boxShadow:
                    idx === currentSceneIndex
                      ? `0 0 10px ${accentColor}`
                      : "none",
                }}
              />
            ))}
          </div>
        </div>
      </div>

      <KaraokeCaptions subtitles={subtitles} />
    </div>
  );
};
