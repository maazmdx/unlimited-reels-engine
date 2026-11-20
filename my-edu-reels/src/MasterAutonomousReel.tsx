import React from "react";
import {
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
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
  cardData?: DynamicCardData | null;
  cardStartFrame?: number;
  cardEndFrame?: number;
  hookHeadline?: string;
  hookSubheadline?: string;
  hookTag?: string;
  forcedCameraShot?: CameraShotType;
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
  cardData = null,
  cardStartFrame = 430,
  forcedCameraShot,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

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
  let leftCharId: "junior_dev" | "dad" = cast?.left || "junior_dev";
  let rightCharId: "claude" | "gemini" | "grok" | "antigravity_bot" =
    cast?.right || "claude";

  // Auto-detect from characters array or turns if not explicitly set in cast
  if (!cast?.left && characters && characters.length > 0) {
    const charNames = characters.map((c) =>
      typeof c === "string" ? c.toLowerCase() : (c.id || c.name || "").toLowerCase()
    );
    if (charNames.some((n) => n.includes("dad"))) {
      leftCharId = "dad";
    }
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
  const isLeftSpeaking = activeTurn?.character_id === leftCharId;
  const isRightSpeaking = activeTurn?.character_id === rightCharId;

  const mouthOpenLeft =
    activeTimeline.mouth_envelopes?.[leftCharId]?.[frame] ?? 0;
  const mouthOpenRight =
    activeTimeline.mouth_envelopes?.[rightCharId]?.[frame] ?? 0;

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

  // Speaker side for camera cutting
  const speakerSide: "left" | "right" | "wide" = isProofCardActive
    ? "wide"
    : isRightSpeaking
    ? "right"
    : isLeftSpeaking
    ? "left"
    : "wide";

  // 6. Camera Rig Parameters (Persistent, 0 remount)
  const cameraParams = getCameraRigParams(
    frame,
    activeTurn,
    isProofCardActive,
    speakerSide,
    forcedCameraShot
  );

  // Active speaker styling for subtitles
  const activeCharConfig = activeTurn
    ? CHAR_CONFIGS[activeTurn.character_id]
    : null;
  const speakerAccentColor =
    (activeCharConfig?.palette as any)?.accent ||
    (isRightSpeaking ? "#F59E0B" : "#38BDF8");
  const speakerDisplayName = activeCharConfig?.badge_label || activeTurn?.character_id;

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

      {/* 3. Single Persistent Three.js Canvas (Never Remounted) */}
      <ThreeCanvas
        dpr={0.75}
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
          speakerSide={speakerSide}
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
              position={[-0.45, -0.36, -0.3]}
              rotation={[
                0.04 + (isLeftSpeaking ? Math.sin(frame * 0.25) * 0.015 : 0),
                isLeftSpeaking ? 0.16 : 0.28,
                0,
              ]}
              scale={1.08}
            />

            {/* Right Side: AI Orb hovering by Desk */}
            <LowPolyAIOrbRig
              characterId={rightCharId}
              isSpeaking={isRightSpeaking}
              mouthOpen={mouthOpenRight}
              emotion={rightEmotion}
              position={[1.22, 0.22, -0.1]}
              rotation={[0.02, isRightSpeaking ? -0.12 : -0.22, 0]}
              scale={1.10}
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
              position={[-1.28, -0.38, -0.1]}
              rotation={[
                0.04 + (isLeftSpeaking ? Math.sin(frame * 0.25) * 0.015 : 0),
                isLeftSpeaking ? 0.22 : 0.32,
                0,
              ]}
              scale={1.12}
            />

            {/* Right Side: AI Orb Floating Across Diner Table */}
            <LowPolyAIOrbRig
              characterId={rightCharId}
              isSpeaking={isRightSpeaking}
              mouthOpen={mouthOpenRight}
              emotion={rightEmotion}
              position={[1.28, 0.15, -0.1]}
              rotation={[0.02, isRightSpeaking ? -0.14 : -0.24, 0]}
              scale={1.05}
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
        isAI={isRightSpeaking}
      />

      {/* 6. Subtle Cinematic Edge Vignette */}
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
