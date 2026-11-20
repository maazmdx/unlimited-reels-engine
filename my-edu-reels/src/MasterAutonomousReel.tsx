import React from "react";
import {
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  spring,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { CozyDiner3D } from "./components/environments3d/CozyDiner3D";
import { SunsetDesk3D } from "./components/environments3d/SunsetDesk3D";
import { LowPolyHumanRig } from "./components/characters3d/LowPolyHumanRig";
import { LowPolyAIOrbRig } from "./components/characters3d/LowPolyAIOrbRig";
import {
  CameraRig3D,
  CameraShotType,
  getCameraRigParams,
} from "./components/scene/CameraRig3D";
import {
  CinematicSubtitles,
  TimelineTurn,
} from "./components/ui/CinematicSubtitles";
import {
  DynamicProofCard,
  DynamicCardData,
} from "./components/ui/DynamicProofCard";
import { ProgressBar } from "./components/ProgressBar";
import charactersConfigJson from "./config/characters.json";
import defaultTimelineJson from "../public/timeline.json";

export interface TimelineData {
  total_duration_sec: number;
  duration_in_frames: number;
  fps: number;
  turns: TimelineTurn[];
  mouth_envelopes: Record<string, number[]>;
}

export interface CharacterItemConfig {
  id: string;
  type?: string;
  name?: string;
  emotion?: string;
  isSpeaking?: boolean;
}

export interface MasterAutonomousReelProps {
  [key: string]: unknown;
  scenePreset?: "diner" | "desk";
  environment?: string;
  timeline?: TimelineData;
  subtitles?: {
    turns?: TimelineTurn[];
    chunks?: Array<{ start: number; end: number; speaker: string; text: string }>;
  };
  audioSrc?: string;
  characters?: Array<CharacterItemConfig | string>;
  cast?: {
    left?: "junior_dev" | "dad";
    right?: "claude" | "gemini" | "grok" | "antigravity_bot";
  };
  leftCharacterId?: "junior_dev" | "dad";
  rightCharacterId?: "claude" | "gemini" | "grok" | "antigravity_bot";
  cardData?: DynamicCardData | null;
  cardStartFrame?: number;
  cardEndFrame?: number;
  hookHeadline?: string;
  hookSubheadline?: string;
  hookTag?: string;
  forcedCameraShot?: CameraShotType;
  ctaKeyword?: string;
  ctaText?: string;
}

type CharacterRegistry = Record<
  string,
  {
    id: string;
    display_name: string;
    badge_label: string;
    type: "human" | "ai_orb";
    palette?: Record<string, string>;
  }
>;

const CHAR_CONFIGS = charactersConfigJson as unknown as CharacterRegistry;
const DEFAULT_TIMELINE = defaultTimelineJson as unknown as TimelineData;

export const MasterAutonomousReel: React.FC<MasterAutonomousReelProps> = ({
  scenePreset,
  environment = "diner",
  timeline,
  subtitles,
  audioSrc = "voice.mp3",
  characters,
  cast,
  leftCharacterId,
  rightCharacterId,
  cardData = null,
  cardStartFrame = 430,
  forcedCameraShot,
  ctaKeyword,
  ctaText,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Resolve timeline and turns
  const activeTimeline: TimelineData = timeline || DEFAULT_TIMELINE;
  const turns: TimelineTurn[] =
    activeTimeline.turns && activeTimeline.turns.length > 0
      ? activeTimeline.turns
      : (subtitles?.turns as TimelineTurn[]) || [];

  // Determine active turn for current frame
  const activeTurn = turns.find(
    (t) => frame >= t.start_frame && frame <= t.end_frame
  );

  // 2. Resolve Environment (Diner vs Sunset Desk)
  const isDeskPreset =
    scenePreset === "desk" ||
    environment.toLowerCase().includes("desk") ||
    environment.toLowerCase().includes("sunset") ||
    environment.toLowerCase().includes("home");

  // 3. Resolve Cast (Left Human + Right AI Orb)
  let leftCharId: "junior_dev" | "dad" =
    leftCharacterId || cast?.left || "junior_dev";
  let rightCharId: "claude" | "gemini" | "grok" | "antigravity_bot" =
    rightCharacterId || cast?.right || "claude";

  // Auto-detect from characters array or turns if not explicitly set in cast
  if (!leftCharacterId && !cast?.left && characters && characters.length > 0) {
    const charNames = characters.map((c) =>
      typeof c === "string" ? c.toLowerCase() : (c.id || c.name || "").toLowerCase()
    );
    if (charNames.some((n) => n.includes("dad"))) {
      leftCharId = "dad";
    }
  }

  if (!rightCharacterId && !cast?.right && characters && characters.length > 0) {
    const charNames = characters.map((c) =>
      typeof c === "string" ? c.toLowerCase() : (c.id || c.name || "").toLowerCase()
    );
    if (charNames.some((n) => n.includes("gemini"))) {
      rightCharId = "gemini";
    } else if (charNames.some((n) => n.includes("grok"))) {
      rightCharId = "grok";
    } else if (charNames.some((n) => n.includes("antigravity"))) {
      rightCharId = "antigravity_bot";
    } else if (charNames.some((n) => n.includes("claude"))) {
      rightCharId = "claude";
    }
  }

  // 4. Resolve Speaker State & Mouth Envelopes (30fps RMS Envelope from timeline)
  // Strictly lock speaking to active turn character
  const isLeftSpeaking = !!activeTurn && activeTurn.character_id === leftCharId;
  const isRightSpeaking = !!activeTurn && activeTurn.character_id === rightCharId;

  const mouthOpenLeft = isLeftSpeaking
    ? (activeTimeline.mouth_envelopes?.[leftCharId]?.[frame] ?? 0)
    : 0;
  const mouthOpenRight = isRightSpeaking
    ? (activeTimeline.mouth_envelopes?.[rightCharId]?.[frame] ?? 0)
    : 0;

  // Emotion mapping
  const mapEmotion = (
    rawEmotion?: string
  ): "neutral" | "tired" | "shocked" | "angry" | "smug" => {
    if (!rawEmotion) return "neutral";
    const e = rawEmotion.toLowerCase();
    if (e.includes("smug") || e.includes("happy")) return "smug";
    if (e.includes("shock") || e.includes("surpris")) return "shocked";
    if (e.includes("angr")) return "angry";
    if (e.includes("tired") || e.includes("sad")) return "tired";
    return "neutral";
  };

  const leftEmotion = isLeftSpeaking
    ? mapEmotion(activeTurn?.emotion)
    : isRightSpeaking && activeTurn?.emotion === "smug"
    ? "tired"
    : "neutral";

  const rightEmotion = isRightSpeaking
    ? mapEmotion(activeTurn?.emotion)
    : isLeftSpeaking && activeTurn?.emotion === "shocked"
    ? "smug"
    : "neutral";

  // 5. Proof Card State & Safe Zone Coordinates
  const effectiveCardStart = cardData?.startFrame ?? cardStartFrame;
  const cardDuration = cardData?.durationSeconds
    ? Math.round(cardData.durationSeconds * fps)
    : 120;
  const cappedCardDuration = Math.min(Math.max(cardDuration, 90), 150);
  const effectiveCardEnd = effectiveCardStart + cappedCardDuration;
  const isProofCardActive =
    !!cardData && frame >= effectiveCardStart && frame <= effectiveCardEnd;

  // 6. Camera Rig Parameters (Persistent, 0 remount)
  const cameraParams = getCameraRigParams(
    frame,
    activeTurn,
    isProofCardActive,
    leftCharId,
    rightCharId,
    forcedCameraShot
  );

  // Active speaker styling for subtitles
  const activeCharConfig = activeTurn
    ? CHAR_CONFIGS[activeTurn.character_id]
    : null;
  const speakerAccentColor =
    (activeCharConfig?.palette as any)?.accent ||
    (isRightSpeaking ? "#F59E0B" : "#38BDF8");
  const speakerDisplayName =
    activeCharConfig?.display_name ||
    activeCharConfig?.badge_label ||
    (activeTurn?.character_id === "junior_dev" ? "Junior Dev" : activeTurn?.character_id);

  // 7. End-Screen Auto-DM CTA Banner (Final 2.5s / 75 frames)
  const totalFrames = durationInFrames || activeTimeline.duration_in_frames || 450;
  const ctaDurationFrames = Math.round(2.5 * fps);
  const ctaStartFrame = Math.max(0, totalFrames - ctaDurationFrames);
  const isCtaActive = frame >= ctaStartFrame;

  // Auto-detect CTA keyword from last turn if not explicitly passed
  const resolvedKeyword = (
    ctaKeyword ||
    (turns.length > 0
      ? turns[turns.length - 1].text.match(/comment\s+([A-Z0-9_]+)/i)?.[1]
      : null) ||
    "LINK"
  ).toUpperCase();

  const ctaSpring = isCtaActive
    ? spring({
        frame: frame - ctaStartFrame,
        fps,
        config: {
          damping: 14,
          mass: 0.8,
          stiffness: 140,
        },
      })
    : 0;

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "relative",
        overflow: "hidden",
        backgroundColor: "#070B14",
      }}
    >
      {/* 1. Master Audio Track */}
      <Audio src={staticFile(audioSrc)} />

      {/* 2. Top Progress Bar */}
      <ProgressBar color="#38BDF8" height={8} />

      {/* 3. Single Persistent Three.js Canvas (Never Remounted, Native DPR 1 for Max Quality) */}
      <ThreeCanvas
        dpr={1}
        width={1080}
        height={1920}
        camera={{
          position: cameraParams.position,
          fov: cameraParams.fov,
          near: 0.1,
          far: 100,
        }}
        style={{
          width: 1080,
          height: 1920,
          position: "absolute",
          top: 0,
          left: 0,
        }}
      >
        {/* Dynamic 3-Camera Cutting Controller */}
        <CameraRig3D
          activeTurn={activeTurn}
          isProofCardActive={isProofCardActive}
          leftCharId={leftCharId}
          rightCharId={rightCharId}
          forcedShot={forcedCameraShot}
        />

        {/* 3D Environment: CozyDiner3D or SunsetDesk3D */}
        {isDeskPreset ? (
          <SunsetDesk3D>
            {/* Left Seat: Human Dev at Wooden Desk */}
            <LowPolyHumanRig
              characterId={leftCharId}
              isSpeaking={isLeftSpeaking}
              mouthOpen={mouthOpenLeft}
              emotion={leftEmotion}
              position={[-1.15, 0.22, 0.0]}
              rotation={[
                0.04 + (isLeftSpeaking ? Math.sin(frame * 0.25) * 0.015 : 0),
                isLeftSpeaking ? 0.20 : 0.28,
                0,
              ]}
              scale={0.65}
            />

            {/* Right Side: AI Orb hovering by Desk */}
            <LowPolyAIOrbRig
              characterId={rightCharId}
              isSpeaking={isRightSpeaking}
              mouthOpen={mouthOpenRight}
              emotion={rightEmotion}
              position={[1.05, 0.45, 0.05]}
              rotation={[0.02, isRightSpeaking ? -0.16 : -0.25, 0]}
              scale={0.46}
            />
          </SunsetDesk3D>
        ) : (
          <CozyDiner3D>
            {/* Left Seat: Human Dev in Diner Booth */}
            <LowPolyHumanRig
              characterId={leftCharId}
              isSpeaking={isLeftSpeaking}
              mouthOpen={mouthOpenLeft}
              emotion={leftEmotion}
              position={[-1.15, 0.22, 0.0]}
              rotation={[
                0.04 + (isLeftSpeaking ? Math.sin(frame * 0.25) * 0.015 : 0),
                isLeftSpeaking ? 0.20 : 0.28,
                0,
              ]}
              scale={0.65}
            />

            {/* Right Side: AI Orb Floating Across Diner Table */}
            <LowPolyAIOrbRig
              characterId={rightCharId}
              isSpeaking={isRightSpeaking}
              mouthOpen={mouthOpenRight}
              emotion={rightEmotion}
              position={[1.05, 0.45, 0.05]}
              rotation={[0.02, isRightSpeaking ? -0.16 : -0.25, 0]}
              scale={0.46}
            />
          </CozyDiner3D>
        )}
      </ThreeCanvas>

      {/* 4. Upper-Third Dynamic Proof Card (Capped 3.0-5.0s, clears characters below) */}
      {cardData && (
        <DynamicProofCard
          cardData={cardData}
          startFrame={effectiveCardStart}
          durationFrames={cappedCardDuration}
        />
      )}

      {/* 5. Safe-Zone Subtitles (Upper-Middle top: 280px / Lower-Safe bottom: 320px when card active) */}
      <CinematicSubtitles
        activeTurn={activeTurn}
        isProofCardActive={isProofCardActive}
        speakerAccentColor={speakerAccentColor}
        speakerDisplayName={speakerDisplayName}
        isAI={isRightSpeaking || activeCharConfig?.type === "ai_orb"}
      />

      {/* 6. End-Screen Auto-DM CTA Banner (Pulsing-free deterministic spring pill) */}
      {isCtaActive && (
        <div
          style={{
            position: "absolute",
            bottom: 340,
            left: "50%",
            transform: `translateX(-50%) translateY(${(1 - ctaSpring) * 36}px) scale(${0.88 + 0.12 * ctaSpring})`,
            opacity: Math.min(1, ctaSpring * 1.6),
            zIndex: 110,
            display: "flex",
            alignItems: "center",
            gap: 16,
            padding: "16px 36px",
            borderRadius: 9999,
            backgroundColor: "rgba(10, 15, 29, 0.94)",
            border: "2px solid rgba(56, 189, 248, 0.75)",
            boxShadow:
              "0 12px 36px rgba(0, 0, 0, 0.65), 0 0 24px rgba(56, 189, 248, 0.35)",
            backdropFilter: "blur(16px)",
            pointerEvents: "none",
          }}
        >
          <span style={{ fontSize: 34, lineHeight: 1 }}>💬</span>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
            <span
              style={{
                fontFamily: "Inter, -apple-system, system-ui, sans-serif",
                fontSize: 28,
                fontWeight: 800,
                color: "#FFFFFF",
                letterSpacing: "0.02em",
                textTransform: "uppercase",
              }}
            >
              Comment
            </span>
            <span
              style={{
                fontFamily: "Inter, -apple-system, system-ui, sans-serif",
                fontSize: 32,
                fontWeight: 900,
                color: "#38BDF8",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
                textShadow: "0 0 16px rgba(56, 189, 248, 0.6)",
              }}
            >
              {resolvedKeyword}
            </span>
            <span
              style={{
                fontFamily: "Inter, -apple-system, system-ui, sans-serif",
                fontSize: 28,
                fontWeight: 800,
                color: "#E2E8F0",
                letterSpacing: "0.02em",
              }}
            >
              for the link
            </span>
          </div>
        </div>
      )}

      {/* 7. Subtle Cinematic Edge Vignette */}
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
