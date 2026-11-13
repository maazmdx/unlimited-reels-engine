import React from "react";
import {
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeDinerScene } from "./components/three3d/ThreeDinerScene";
import { ComparisonCard3D } from "./components/three3d/ComparisonCard3D";
import { DialogueSubtitles, DialogueChunk } from "./components/diner/DialogueSubtitles";
import { ViralHook } from "./components/ViralHook";
import { ProgressBar } from "./components/ProgressBar";

export interface ThreeWayTurn {
  index: number;
  speaker: string; // "junior" | "rival" | "bot"
  start: number;
  end: number;
  duration?: number;
  text: string;
  cardTrigger?: boolean | null;
}

export interface ThreeWaySubtitleData {
  chunks: DialogueChunk[];
  turns?: ThreeWayTurn[];
  words?: unknown[];
}

export interface ThreeWayComparisonReelProps {
  [key: string]: unknown;
  subtitles?: ThreeWaySubtitleData;
  audioSrc?: string;
  title?: string;
  cardStartFrame?: number;
  cardEndFrame?: number;
  audioEnvelope?: number[];
}

const DEFAULT_THREEWAY_DATA: ThreeWaySubtitleData = {
  chunks: [
    { start: 0.0, end: 3.0, speaker: "junior", text: "How do I build an AI agent without going broke?" },
    { start: 3.2, end: 6.8, speaker: "rival", text: "You can't. Pay $200 a month for Claude and hire an agency." },
    { start: 7.0, end: 11.5, speaker: "bot", text: "Wrong. Google Antigravity CLI and Gemini 2.5 Flash are 100% free." },
  ],
  turns: [
    { index: 0, speaker: "junior", start: 0.0, end: 3.0, text: "How do I build an AI agent without going broke?" },
    { index: 1, speaker: "rival", start: 3.2, end: 6.8, text: "You can't. Pay $200 a month for Claude and hire an agency." },
    { index: 2, speaker: "bot", start: 7.0, end: 11.5, text: "Wrong. Google Antigravity CLI and Gemini 2.5 Flash are 100% free." },
  ],
};

export const ThreeWayComparisonReel: React.FC<ThreeWayComparisonReelProps> = ({
  subtitles = DEFAULT_THREEWAY_DATA,
  audioSrc = "voice.mp3",
  cardStartFrame,
  cardEndFrame,
  audioEnvelope = [],
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const currentTime = frame / fps;

  const turns = subtitles?.turns || [];
  const chunks = subtitles?.chunks || [];

  // Determine active speaker from timeline turns
  const activeTurn = turns.find(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.15
  );
  const speaker = activeTurn ? activeTurn.speaker.toLowerCase() : "bot";

  // Live audio amplitude for organic mouth lip-syncing
  const currentAmp = audioEnvelope[frame] || 0.0;

  // Card trigger: appears after hook and stays through the key comparison
  const defaultCardStart = cardStartFrame ?? 75; // right after ViralHook fades
  const defaultCardEnd = cardEndFrame ?? Math.floor(durationInFrames * 0.92);

  const isCardVisible = frame >= defaultCardStart && frame <= defaultCardEnd;

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "relative",
        overflow: "hidden",
        backgroundColor: "#0B0F19",
      }}
    >
      {/* 1. Master Dialogue Voice Audio (Broadcast DSP Mastered) */}
      <Audio src={staticFile(audioSrc)} />

      {/* 2. Top Retention Progress Bar */}
      <ProgressBar color="#38BDF8" height={8} />

      {/* 7. REAL 3D Three.js WebGL Scene (Junior Dev, Rival Dev, Antigravity Bot, Desk) */}
      <ThreeDinerScene
        speaker={speaker}
        audioAmplitude={currentAmp}
      />

      {/* 8. Viral Hook Overlay (Frames 0 to 75) */}
      <ViralHook
        headline="THE $200/MO AI MISTAKE"
        subheadline="Why devs are dumping Claude for this $0 Google CLI"
        tag="⚠️ STOP WASTING MONEY"
        durationFrames={75}
      />

      {/* 9. Floating 3D Comparison Card (Claude vs Antigravity) */}
      <ComparisonCard3D
        isVisible={isCardVisible}
        title="Tool Comparison • The Real Numbers"
      />

      {/* 10. Non-Blinking Lower-Third Subtitles (Serif Gold Typography) */}
      <DialogueSubtitles
        chunks={chunks}
        activeSpeaker={speaker}
        styleMode="serif_gold"
      />

      {/* 11. Cinematic Radial Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          background:
            "radial-gradient(circle at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%)",
          pointerEvents: "none",
          zIndex: 90,
        }}
      />
    </div>
  );
};
