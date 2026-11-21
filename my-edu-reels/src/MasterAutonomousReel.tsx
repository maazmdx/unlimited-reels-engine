import React from "react";
import {
  Audio,
  Img,
  interpolate,
  Sequence,
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
import {
  NotificationToast,
  ToastData,
} from "./components/ui/NotificationToast";
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
  toastData?: ToastData | null;
  endCard?: {
    question?: string;
    keyword?: string;
    cta_text?: string;
    subtext?: string;
    has_resource_link?: boolean;
    hasResourceLink?: boolean;
    cta_type?: "dm" | "share" | string;
  } | null;
  hasResourceLink?: boolean;
  has_resource_link?: boolean;
  hookHeadline?: string;
  hookSubheadline?: string;
  hookTag?: string;
  topicLogoPath?: string;
  forcedCameraShot?: CameraShotType;
  ctaKeyword?: string;
  ctaText?: string;
  weather?: "rain" | "sunny" | "sunset" | string;
  weatherMode?: "rain" | "sunny" | "sunset";
  episodeNumber?: number;
  episodeStr?: string;
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
  toastData = null,
  endCard = null,
  hasResourceLink,
  has_resource_link,
  topicLogoPath,
  hookHeadline,
  hookSubheadline,
  hookTag,
  forcedCameraShot,
  ctaKeyword,
  ctaText,
  weather,
  weatherMode,
  episodeNumber,
  episodeStr,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

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
  ): "neutral" | "tired" | "shocked" | "angry" | "smug" | "sarcastic" => {
    if (!rawEmotion) return "neutral";
    const e = rawEmotion.toLowerCase();
    if (e.includes("smug") || e.includes("sarcas") || e.includes("happy")) return "smug";
    if (e.includes("shock") || e.includes("surpris")) return "shocked";
    if (e.includes("angr")) return "angry";
    if (e.includes("tired") || e.includes("sad")) return "tired";
    return "neutral";
  };

  const isAIRoasting =
    isRightSpeaking &&
    (activeTurn?.emotion === "smug" ||
      activeTurn?.emotion === "sarcastic" ||
      activeTurn?.emotion?.toLowerCase().includes("sarcas"));

  const leftEmotion = isLeftSpeaking
    ? mapEmotion(activeTurn?.emotion)
    : isAIRoasting
    ? "shocked"
    : "neutral";

  const rightEmotion = isRightSpeaking
    ? mapEmotion(activeTurn?.emotion)
    : isLeftSpeaking && activeTurn?.emotion === "shocked"
    ? "smug"
    : "neutral";

  const turnFrame = activeTurn ? Math.max(0, frame - activeTurn.start_frame) : 0;

  // Resolve Weather Mode for Diner scene rotation ("rain" | "sunny" | "sunset")
  const resolvedWeather: "rain" | "sunny" | "sunset" =
    weatherMode ||
    (weather === "sunny" || weather === "rain" || weather === "sunset" ? (weather as any) : undefined) ||
    (environment?.toLowerCase().includes("sunny")
      ? "sunny"
      : environment?.toLowerCase().includes("sunset")
      ? "sunset"
      : "rain");

  // 5. Proof Card State & Safe Zone Coordinates (Act 3: Turns 5-7, 16-30s)
  const totalFrames = durationInFrames || activeTimeline.duration_in_frames || 450;
  const startTurnIdx = typeof (cardData as any)?.startTurn === "number" ? (cardData as any).startTurn : 5;
  const endTurnIdx = typeof (cardData as any)?.endTurn === "number" ? (cardData as any).endTurn : 7;

  // Compute cardStartFrame directly from timeline.turns[startTurnIdx].start_frame (Act 3)
  const turn5StartFrame =
    turns && turns.length > startTurnIdx
      ? turns[startTurnIdx].start_frame
      : (turns && turns.length > 3 ? turns[3].start_frame : (cardData?.startFrame ?? cardStartFrame));
  const turn7EndFrame =
    turns && turns.length > endTurnIdx
      ? turns[endTurnIdx].end_frame
      : Math.min(turn5StartFrame + 360, totalFrames - 90);
  const effectiveCardStart = turn5StartFrame;
  const effectiveCardEnd = Math.min(turn7EndFrame, totalFrames - 90);
  const cappedCardDuration = Math.max(30, effectiveCardEnd - effectiveCardStart);
  const isProofCardActive =
    !!cardData && frame >= effectiveCardStart && frame <= effectiveCardEnd;

  // Dynamic Row-by-Row Highlighting: Row 1 on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7
  let activeStepIndex = 0;
  if (turns && turns.length > endTurnIdx) {
    const turn6Start = turns[startTurnIdx + 1]?.start_frame ?? (effectiveCardStart + 120);
    const turn7Start = turns[endTurnIdx]?.start_frame ?? (effectiveCardStart + 240);
    if (frame < turn6Start) {
      activeStepIndex = 0; // Turn 5 (Row 1)
    } else if (frame < turn7Start) {
      activeStepIndex = 1; // Turn 6 (Row 2)
    } else {
      activeStepIndex = 2; // Turn 7 (Row 3)
    }
  } else {
    const cardProgress = (frame - effectiveCardStart) / Math.max(1, cappedCardDuration);
    activeStepIndex = cardProgress < 0.33 ? 0 : cardProgress < 0.66 ? 1 : 2;
  }

  // 6. Animated iOS Notification Toast (Act 4: Turn 9, 3.5s duration)
  const effectiveToastData = toastData || (cardData as any)?.toastData || null;
  const effectiveTopicLogo = topicLogoPath || (cardData as any)?.topicLogoPath || null;
  const turn0EndFrame = turns && turns.length > 0 ? turns[0].end_frame : 90;
  const turn9StartFrame = turns && turns.length > 9 ? turns[9].start_frame : Math.max(0, totalFrames - 240);
  const toastDurationFrames = 105; // 3.5s @ 30fps
  const effectiveToastEnd = turn9StartFrame + toastDurationFrames;
  const isToastActive =
    !!effectiveToastData && frame >= turn9StartFrame && frame <= effectiveToastEnd;

  // 7. Camera Rig Parameters (Persistent, 0 remount)
  const cameraParams = getCameraRigParams(
    frame,
    activeTurn,
    turns,
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

  // Helper to strip emoji ranges that cause □ glyph issues on Linux
  const stripEmojis = (str: string): string =>
    (str || "")
      .replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}]/gu, "")
      .trim();

  // 8. Clean 2.5s Black End-Card (Strictly starts at lastTurnEndFrame + 9)
  const lastTurn = turns && turns.length > 0 ? turns[turns.length - 1] : null;
  const lastTurnEndFrame = lastTurn ? lastTurn.end_frame : Math.max(0, totalFrames - 75);
  const endCardStartFrame = Math.max(0, lastTurnEndFrame + 9);
  const isEndCardActive = frame >= endCardStartFrame;

  const endCardFade = isEndCardActive
    ? interpolate(frame, [endCardStartFrame, endCardStartFrame + 12], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  // Auto-detect CTA keyword from last turn if not explicitly passed
  const resolvedKeyword = (
    ctaKeyword ||
    endCard?.keyword ||
    (turns.length > 0
      ? turns[turns.length - 1].text.match(/comment\s+([A-Z0-9_]+)/i)?.[1]
      : null) ||
    "LINK"
  ).toUpperCase();

  const effectiveHasResourceLink =
    (hasResourceLink !== undefined ? hasResourceLink : null) ??
    (has_resource_link !== undefined ? has_resource_link : null) ??
    (endCard?.hasResourceLink !== undefined ? endCard.hasResourceLink : null) ??
    (endCard?.has_resource_link !== undefined ? endCard.has_resource_link : null) ??
    (endCard?.cta_type !== "share" && Boolean(resolvedKeyword && resolvedKeyword !== "NONE" && resolvedKeyword !== "SHARE"));

  const resolvedEndCardQuestion =
    endCard?.question ||
    (cardData?.title ? `Would you try ${cardData.title}?` : "Would you switch to this setup?");

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

      {/* 1b. Subtle chime SFX when NotificationToast pops in on Turn 9 */}
      {effectiveToastData && (
        <Sequence from={turn9StartFrame} durationInFrames={60}>
          <Audio src={staticFile("sfx/chime.mp3")} volume={0.35} />
        </Sequence>
      )}

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
          turns={turns}
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
              turnFrame={turnFrame}
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
          <CozyDiner3D weatherMode={resolvedWeather}>
            {/* Left Seat: Human Dev in Diner Booth */}
            <LowPolyHumanRig
              characterId={leftCharId}
              isSpeaking={isLeftSpeaking}
              mouthOpen={mouthOpenLeft}
              emotion={leftEmotion}
              turnFrame={turnFrame}
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

        {/* Dedicated Back Rim Light for Right Character (Crisp glowing silhouette for dark bots like Grok) */}
        <pointLight
          position={[1.3, 0.8, -1.2]}
          intensity={2.4}
          color={
            rightCharId === "grok"
              ? "#38BDF8"
              : rightCharId === "gemini"
              ? "#60A5FA"
              : rightCharId === "claude"
              ? "#F59E0B"
              : "#38BDF8"
          }
          distance={5.0}
          decay={1.8}
        />

        {/* Dedicated Front-Right Fill Light for Right Character (Reveals facets against night window) */}
        <pointLight
          position={[1.2, 0.6, 1.6]}
          intensity={1.6}
          color="#F1F5F9"
          distance={5.0}
          decay={1.6}
        />
      </ThreeCanvas>

      {/* 4. Upper-Third Dynamic Proof Card (Act 3: Turns 5-7, step-by-step row highlighting) */}
      {cardData && isProofCardActive && (
        <DynamicProofCard
          cardData={cardData}
          startFrame={effectiveCardStart}
          durationFrames={cappedCardDuration}
          activeStepIndex={activeStepIndex}
          topicLogoPath={effectiveTopicLogo}
        />
      )}

      {/* 4b. 0-3s Opening Hook Pill (Official App/Game Logo + Headline Badge during Turn 0) */}
      {effectiveTopicLogo && frame < Math.min(turn0EndFrame, 95) && (
        <div
          style={{
            position: "absolute",
            top: 150,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 110,
            opacity: interpolate(
              frame,
              [0, 8, Math.min(turn0EndFrame, 95) - 10, Math.min(turn0EndFrame, 95)],
              [0, 1, 1, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
            ),
            transform: `scale(${interpolate(frame, [0, 10], [0.85, 1.0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })})`,
            pointerEvents: "none",
          }}
        >
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 16,
              padding: "10px 24px",
              borderRadius: 9999,
              backgroundColor: "rgba(15, 23, 42, 0.94)",
              border: "2px solid rgba(56, 189, 248, 0.8)",
              boxShadow: "0 12px 36px rgba(0, 0, 0, 0.8), 0 0 24px rgba(56, 189, 248, 0.4)",
              backdropFilter: "blur(12px)",
            }}
          >
            <Img
              src={staticFile(effectiveTopicLogo)}
              style={{
                width: 56,
                height: 56,
                borderRadius: 14,
                objectFit: "contain",
                backgroundColor: "#FFFFFF",
                padding: 4,
                boxShadow: "0 4px 12px rgba(0,0,0,0.4)",
              }}
            />
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 800,
                  letterSpacing: "0.15em",
                  color: "#38BDF8",
                  textTransform: "uppercase",
                }}
              >
                {hookTag || "FEATURED SHOWCASE"}
              </span>
              <span
                style={{
                  fontSize: 22,
                  fontWeight: 900,
                  color: "#F8FAFC",
                  letterSpacing: "-0.2px",
                  lineHeight: 1.2,
                }}
              >
                {hookHeadline || (cardData as any)?.title || "VERIFIED PROOF"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 5. Animated iOS Notification Toast (Act 4: Turn 9, 3.5s duration) */}
      {effectiveToastData && isToastActive && (
        <NotificationToast
          toastData={effectiveToastData}
          startFrame={turn9StartFrame}
          durationFrames={toastDurationFrames}
        />
      )}

      {/* 6. Safe-Zone Subtitles (Upper-Middle top: 280px / Lower-Safe bottom: 320px when card or toast is active) */}
      {!isEndCardActive && (
        <CinematicSubtitles
          activeTurn={activeTurn}
          isProofCardActive={isProofCardActive || isToastActive}
          isCtaActive={false}
          speakerAccentColor={speakerAccentColor}
          speakerDisplayName={speakerDisplayName}
          isAI={isRightSpeaking || activeCharConfig?.type === "ai_orb"}
        />
      )}

      {/* 7. Clean 2.5s Black End-Card (Act 5: Final 75 frames, matching reference reels with zero subtitle overlap) */}
      {isEndCardActive && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "#030712",
            opacity: endCardFade,
            zIndex: 120,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "0 60px",
            textAlign: "center",
            pointerEvents: "none",
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
          }}
        >
          {/* Top Debate Question */}
          <div
            style={{
              fontSize: 42,
              fontWeight: 800,
              color: "#F8FAFC",
              lineHeight: 1.35,
              maxWidth: 900,
              marginBottom: 48,
              letterSpacing: "-0.5px",
              textShadow: "0 4px 20px rgba(0, 0, 0, 0.95)",
            }}
          >
            {stripEmojis(resolvedEndCardQuestion)}
          </div>

          {/* Middle Highlight Auto-DM or Viral Tag/Share Pill */}
          {effectiveHasResourceLink ? (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: "20px 48px",
                borderRadius: 9999,
                backgroundColor: "rgba(15, 23, 42, 0.96)",
                border: "2px solid #38BDF8",
                boxShadow:
                  "0 16px 48px rgba(0, 0, 0, 0.85), 0 0 36px rgba(56, 189, 248, 0.45)",
                marginBottom: 36,
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  backgroundColor: "#38BDF8",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 16,
                  fontWeight: 900,
                  color: "#030712",
                  letterSpacing: "-0.5px",
                }}
              >
                DM
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                <span
                  style={{
                    fontSize: 30,
                    fontWeight: 800,
                    color: "#FFFFFF",
                    textTransform: "uppercase",
                    letterSpacing: "0.02em",
                  }}
                >
                  Comment
                </span>
                <span
                  style={{
                    fontSize: 36,
                    fontWeight: 900,
                    color: "#38BDF8",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    textShadow: "0 0 20px rgba(56, 189, 248, 0.7)",
                  }}
                >
                  {resolvedKeyword}
                </span>
                <span
                  style={{
                    fontSize: 30,
                    fontWeight: 800,
                    color: "#E2E8F0",
                    textTransform: "uppercase",
                    letterSpacing: "0.02em",
                  }}
                >
                  for the link
                </span>
              </div>
            </div>
          ) : (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: "20px 48px",
                borderRadius: 9999,
                backgroundColor: "rgba(15, 23, 42, 0.96)",
                border: "2px solid #F59E0B",
                boxShadow:
                  "0 16px 48px rgba(0, 0, 0, 0.85), 0 0 36px rgba(245, 158, 11, 0.45)",
                marginBottom: 36,
              }}
            >
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  backgroundColor: "#F59E0B",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 18,
                  fontWeight: 900,
                  color: "#030712",
                }}
              >
                🔥
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                <span
                  style={{
                    fontSize: 32,
                    fontWeight: 900,
                    color: "#FCD34D",
                    textTransform: "uppercase",
                    letterSpacing: "0.04em",
                    textShadow: "0 0 20px rgba(245, 158, 11, 0.6)",
                  }}
                >
                  {endCard?.cta_text || ctaText || "TAG THAT DEV BELOW"}
                </span>
              </div>
            </div>
          )}

          {/* Bottom Subtle Follow Prompt */}
          <div
            style={{
              fontSize: 24,
              fontWeight: 700,
              color: "#94A3B8",
              letterSpacing: "0.8px",
              textTransform: "uppercase",
            }}
          >
            {endCard?.subtext ||
              (episodeNumber
                ? `Follow for Ep. ${episodeNumber + 1 < 10 ? "0" : ""}${episodeNumber + 1}`
                : "Follow for Ep. 02")}
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
