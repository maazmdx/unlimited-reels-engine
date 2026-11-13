import React from "react";
import {
  Sequence,
  Audio,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";
import { BackgroundGrid } from "./components/BackgroundGrid";
import { ProgressBar } from "./components/ProgressBar";
import { BlackHoleVisual } from "./components/BlackHoleVisual";
import { ClockComparison } from "./components/ClockComparison";
import { RelativityCard } from "./components/RelativityCard";
import { KaraokeCaptions, SubtitleData } from "./components/KaraokeCaptions";
import { DEFAULT_SUBTITLES } from "./data/defaultSubs";

export interface EduReelProps {
  [key: string]: unknown;
  subtitles?: SubtitleData;
  audioSrc?: string;
  title?: string;
}

export const EduReel: React.FC<EduReelProps> = ({
  subtitles = DEFAULT_SUBTITLES,
  audioSrc = "voice.mp3",
}) => {
  const frame = useCurrentFrame();

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
      {/* Dynamic Audio Track with staticFile */}
      <Audio src={staticFile(audioSrc)} />

      {/* Top Retention Progress Bar */}
      <ProgressBar color="#00F0FF" />

      {/* Background Animated Spacetime Grid & Cosmic Particles */}
      <BackgroundGrid theme="space" />

      {/* 
        100% Guaranteed Instagram Safe Zone Container
        Centered: paddingTop 220, paddingBottom 280, paddingLeft 64, paddingRight 64
        Ensures UI controls (Like, Comment, Share, Audio Name) never clip content.
      */}
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
          justifyContent: "flex-start",
          alignItems: "center",
          zIndex: 10,
        }}
      >
        {/* SCENE 1 (Frames 0 to 110): Hook & Black Hole Accretion Disk */}
        <Sequence from={0} durationInFrames={115}>
          <div
            style={{
              width: "100%",
              opacity: interpolate(frame, [95, 110], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
              transform: `translateY(${interpolate(frame, [95, 110], [0, -30], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })}px)`,
            }}
          >
            <BlackHoleVisual />
          </div>
        </Sequence>

        {/* SCENE 2 (Frames 110 to 230): Side-by-Side Dual Clock Paradox */}
        <Sequence from={110} durationInFrames={125}>
          <div
            style={{
              width: "100%",
              opacity: interpolate(frame, [215, 230], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
              transform: `translateY(${interpolate(frame, [215, 230], [0, -30], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })}px)`,
            }}
          >
            <ClockComparison />
          </div>
        </Sequence>

        {/* SCENE 3 (Frames 230+): Einstein Equation Takeaway & CTA */}
        <Sequence from={230}>
          <div style={{ width: "100%" }}>
            <RelativityCard />
          </div>
        </Sequence>
      </div>

      {/* Synchronized Word-Highlight Karaoke Captions in the Safe Zone */}
      <KaraokeCaptions subtitles={subtitles} />
    </div>
  );
};
