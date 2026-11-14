import React from "react";
import {
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeDinerScene, ThreeDinerTurn } from "./components/three3d/ThreeDinerScene";
import { ComparisonCard3D, ComparisonRow } from "./components/three3d/ComparisonCard3D";
import { DialogueSubtitles, DialogueChunk } from "./components/diner/DialogueSubtitles";
import { ViralHook } from "./components/ViralHook";
import { ProgressBar } from "./components/ProgressBar";

export interface ThreeWayTurn {
  index: number;
  speaker: string; // "junior" | "rival" | "dad" | "bot" | "claude"
  start: number;
  end: number;
  duration?: number;
  text: string;
  cardTrigger?: boolean | null;
  emotion?: string;
  zoomLevel?: number;
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
  hookHeadline?: string;
  hookSubheadline?: string;
  hookTag?: string;
  explainerTitle?: string;
  comparisonRows?: ComparisonRow[];
  leftHeader?: string;
  rightHeader?: string;
  badge?: string;
  winner?: string;
  buttonText?: string;
  cardStartFrame?: number;
  cardEndFrame?: number;
  audioEnvelope?: number[];
  enableSFX?: boolean;
  bgMusicVolume?: number;
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
  hookHeadline = "THE $200/MO AI MISTAKE",
  hookSubheadline = "Why devs are dumping paid wrappers for this $0 Google CLI",
  hookTag = "⚠️ STOP WASTING MONEY",
  explainerTitle = "Tool Comparison • The Real Numbers",
  comparisonRows,
  leftHeader = "Anthropic Claude",
  rightHeader = "Google Antigravity",
  badge = "$0 VERIFIED",
  winner = "Winner: Google Antigravity & Gemini 2.5 (100% Free Local Setup)",
  buttonText = "Run `agy` Free",
  cardStartFrame,
  cardEndFrame,
  audioEnvelope = [],
  enableSFX = true,
  bgMusicVolume = 0.10,
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
  const hasDad = turns.some((t) => t.speaker.toLowerCase().includes("dad"));

  // Live audio amplitude for organic mouth lip-syncing
  const currentAmp = audioEnvelope[frame] || 0.0;

  // Impact camera shake on brutal roasts or dad outbursts
  const isRoasting =
    (activeTurn?.speaker === "bot" &&
      (activeTurn?.emotion === "smug" ||
        activeTurn?.text.includes("Wrong") ||
        activeTurn?.text.includes("zero") ||
        activeTurn?.text.includes("wasted"))) ||
    (activeTurn?.speaker === "dad" && activeTurn?.emotion === "angry");

  const roastTurnStartFrame = activeTurn ? Math.floor(activeTurn.start * fps) : 0;
  const isShaking = isRoasting && frame >= roastTurnStartFrame && frame <= roastTurnStartFrame + 14;

  // Card trigger: appears after hook and stays through the key comparison
  const defaultCardStart = cardStartFrame ?? 75; // right after ViralHook fades
  const defaultCardEnd = cardEndFrame ?? Math.floor(durationInFrames * 0.92);
  const isCardVisible = frame >= defaultCardStart && frame <= defaultCardEnd;

  // Climax punchline frame for sub-bass impact SFX
  const climaxTurn = turns.find(
    (t) =>
      (t.speaker === "bot" &&
        (t.text.includes("free") ||
          t.text.includes("Wrong") ||
          t.text.includes("zero") ||
          t.text.includes("numbers"))) ||
      (t.speaker === "dad" && (t.text.includes("bill") || t.text.includes("slap")))
  );
  const climaxFrame = climaxTurn ? Math.floor(climaxTurn.start * fps) : Math.floor(durationInFrames * 0.45);

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

      {/* 2. Ambient Background Lofi Music */}
      <Audio src={staticFile("sfx/lofi_bg.mp3")} volume={bgMusicVolume} loop />

      {/* 3. Layered Sound Effects (SFX) */}
      {enableSFX && (
        <>
          {/* Opening Hook Whoosh */}
          <Sequence from={0} durationInFrames={30}>
            <Audio src={staticFile("sfx/whoosh.mp3")} volume={0.45} />
          </Sequence>

          {/* Card Pop Entrance */}
          <Sequence from={defaultCardStart} durationInFrames={30}>
            <Audio src={staticFile("sfx/pop.mp3")} volume={0.65} />
          </Sequence>

          {/* Savage Roast / Punchline Bass Impact */}
          <Sequence from={climaxFrame} durationInFrames={45}>
            <Audio src={staticFile("sfx/impact.mp3")} volume={0.75} />
          </Sequence>
        </>
      )}

      {/* 4. Top Retention Progress Bar */}
      <ProgressBar color="#38BDF8" height={8} />

      {/* 5. 3D Three.js WebGL Scene with Smooth Spring Interpolated Camera */}
      <ThreeDinerScene
        speaker={speaker}
        audioAmplitude={currentAmp}
        shake={isShaking}
        turns={turns as ThreeDinerTurn[]}
        hasDad={hasDad}
      />

      {/* 6. Viral Hook Overlay (Frames 0 to 75, Anti-Flicker) */}
      <ViralHook
        headline={hookHeadline}
        subheadline={hookSubheadline}
        tag={hookTag}
        durationFrames={75}
      />

      {/* 7. Floating 3D Comparison Card (Anti-Flicker Spring Entrance & Exit) */}
      <ComparisonCard3D
        isVisible={isCardVisible}
        startFrame={defaultCardStart}
        endFrame={defaultCardEnd}
        title={explainerTitle}
        leftHeader={leftHeader}
        rightHeader={rightHeader}
        badge={badge}
        winner={winner}
        buttonText={buttonText}
        rows={comparisonRows}
      />

      {/* 8. Non-Blinking Lower-Third Subtitles (Multi-Character Badges) */}
      <DialogueSubtitles
        chunks={chunks}
        activeSpeaker={speaker}
        styleMode="serif_gold"
      />

      {/* 9. Cinematic Radial Vignette */}
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
