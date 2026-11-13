import React from "react";
import {
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {
  DynamicBackgroundEngine,
  SceneEnvironment,
  WeatherType,
} from "./components/scene/DynamicBackgroundEngine";
import { EnvironmentProps } from "./components/scene/EnvironmentProps";
import {
  DynamicCharacterRoster,
  CharacterConfig,
} from "./components/scene/DynamicCharacterRoster";
import { CameraDirector, CameraCue } from "./components/scene/CameraDirector";
import { DesktopExplainerCard } from "./components/diner/DesktopExplainerCard";
import { DialogueSubtitles, DialogueChunk } from "./components/diner/DialogueSubtitles";
import { ViralHook } from "./components/ViralHook";
import { ProgressBar } from "./components/ProgressBar";

export interface DialogueTurn {
  index: number;
  speaker: string;
  start: number;
  end: number;
  text: string;
  emotion?: "normal" | "smug" | "angry" | "shocked" | "happy" | "sad";
  cardTrigger?: boolean | null;
  zoomLevel?: number;
}

export interface DialogueSubtitleData {
  chunks: DialogueChunk[];
  turns?: DialogueTurn[];
  words?: unknown[];
}

export interface MasterAutonomousReelProps {
  [key: string]: unknown;
  subtitles?: DialogueSubtitleData;
  audioSrc?: string;
  environment?: SceneEnvironment;
  weather?: WeatherType;
  characters?: CharacterConfig[];
  screenContent?: "code" | "benchmark" | "terminal" | "none";
  hookHeadline?: string;
  hookSubheadline?: string;
  hookTag?: string;
  explainerTitle?: string;
  cardStartFrame?: number;
  cardEndFrame?: number;
  cameraCues?: CameraCue[];
}

const DEFAULT_DIALOGUE_DATA: DialogueSubtitleData = {
  chunks: [
    {
      start: 0.0,
      end: 2.8,
      speaker: "human_male",
      text: "I spent 6 hours manually writing API integration boilerplate today.",
    },
    {
      start: 3.0,
      end: 5.5,
      speaker: "antigravity_bot",
      text: "Congratulations. You wasted $300 of company money on a 2-second command.",
    },
    {
      start: 5.8,
      end: 8.2,
      speaker: "human_male",
      text: "Wait... what? How does Antigravity do that for free?",
    },
    {
      start: 8.5,
      end: 12.0,
      speaker: "antigravity_bot",
      text: "Multi-agent loop with Gemini 2.5 Flash. Zero dollars, zero manual fatigue, 100% test passing.",
    },
  ],
  turns: [
    {
      index: 0,
      speaker: "human_male",
      start: 0.0,
      end: 2.8,
      text: "I spent 6 hours manually writing API integration boilerplate today.",
      emotion: "normal",
      zoomLevel: 1.15,
    },
    {
      index: 1,
      speaker: "antigravity_bot",
      start: 3.0,
      end: 5.5,
      text: "Congratulations. You wasted $300 of company money on a 2-second command.",
      emotion: "smug",
      zoomLevel: 1.35,
    },
    {
      index: 2,
      speaker: "human_male",
      start: 5.8,
      end: 8.2,
      text: "Wait... what? How does Antigravity do that for free?",
      emotion: "shocked",
      zoomLevel: 1.2,
    },
    {
      index: 3,
      speaker: "antigravity_bot",
      start: 8.5,
      end: 12.0,
      text: "Multi-agent loop with Gemini 2.5 Flash. Zero dollars, zero manual fatigue, 100% test passing.",
      emotion: "smug",
      zoomLevel: 1.3,
    },
  ],
};

const DEFAULT_CHARACTERS: CharacterConfig[] = [
  {
    id: "char_human",
    type: "human_male",
    name: "Junior Dev",
    emotion: "normal",
    isSpeaking: false,
  },
  {
    id: "char_ai",
    type: "antigravity_bot",
    name: "Antigravity",
    emotion: "smug",
    isSpeaking: false,
  },
];

export const MasterAutonomousReel: React.FC<MasterAutonomousReelProps> = ({
  subtitles = DEFAULT_DIALOGUE_DATA,
  audioSrc = "voice.mp3",
  environment = "diner",
  weather = "raining",
  characters = DEFAULT_CHARACTERS,
  screenContent = "code",
  hookHeadline = "THE 6-HOUR DEV BLUNDER",
  hookSubheadline = "Why junior devs are getting completely outclassed by $0 AI",
  hookTag = "⚠️ WAKEUPS FOR HUMANS",
  explainerTitle = "Human Blunder vs AI Multi-Agent Speed",
  cardStartFrame,
  cardEndFrame,
  cameraCues,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const currentTime = frame / fps;

  const turns = subtitles?.turns || [];
  const chunks = subtitles?.chunks || [];

  // Determine active speaker from turns
  const activeTurn = turns.find(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.15
  );
  const activeSpeakerName = activeTurn ? activeTurn.speaker.toLowerCase() : "";

  // Dynamic character speaking state & emotion update
  const resolvedCharacters = characters.map((c) => {
    const isThisSpeaker =
      activeSpeakerName.includes(c.type) ||
      activeSpeakerName.includes(c.id) ||
      (activeSpeakerName.includes("human") && c.type.startsWith("human")) ||
      (activeSpeakerName.includes("bot") && c.type.includes("bot")) ||
      activeSpeakerName.includes(c.name.toLowerCase());

    const activeEmotion = isThisSpeaker && activeTurn?.emotion
      ? activeTurn.emotion
      : c.emotion || "normal";

    return {
      ...c,
      isSpeaking: isThisSpeaker,
      emotion: activeEmotion,
    };
  });

  // Dynamic Camera Cues derivation if none provided
  const resolvedCameraCues: CameraCue[] =
    cameraCues ||
    turns.map((t) => {
      const isAI =
        t.speaker.includes("bot") ||
        t.speaker.includes("gemini") ||
        t.speaker.includes("claude") ||
        t.speaker.includes("grok") ||
        t.speaker.includes("codex");
      return {
        startFrame: Math.floor(t.start * fps),
        endFrame: Math.floor(t.end * fps),
        zoomLevel: t.zoomLevel || (isAI ? 1.3 : 1.15),
        targetX: isAI ? 810 : 270,
        shake: t.emotion === "angry" || (isAI && t.emotion === "smug"),
      };
    });

  // Card trigger (defaults to midway through video)
  const defaultCardStart = cardStartFrame ?? 80;
  const defaultCardEnd = cardEndFrame ?? Math.floor(durationInFrames * 0.92);
  const isCardVisible = frame >= defaultCardStart && frame <= defaultCardEnd;

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "relative",
        overflow: "hidden",
        backgroundColor: "#07090E",
      }}
    >
      {/* 1. Master Audio Track */}
      <Audio src={staticFile(audioSrc)} />

      {/* 2. Top Retention Progress Bar */}
      <ProgressBar color="#38BDF8" height={8} />

      {/* 3. Camera Director Wrapper */}
      <CameraDirector
        activeSpeaker={activeSpeakerName}
        cameraCues={resolvedCameraCues}
        currentTurnIndex={activeTurn?.index ?? 0}
      >
        {/* Dynamic Background Engine (Diner / Home / Office / Outside Terrace) */}
        <DynamicBackgroundEngine
          environment={environment}
          weather={weather}
          ambientIntensity={1.0}
        />

        {/* Dynamic Character Roster (1 to 4 characters with emotions and talking sync) */}
        <DynamicCharacterRoster characters={resolvedCharacters} />

        {/* Environment Foreground Props (Table, Seating, Steaming Coffee Mug, Code Screen) */}
        <EnvironmentProps
          environment={environment}
          showCoffeeMug={true}
          showScreen={true}
          screenContent={screenContent}
        />
      </CameraDirector>

      {/* 4. Viral Retention Hook Banner (First 0-3 Seconds) */}
      <ViralHook
        headline={hookHeadline}
        subheadline={hookSubheadline}
        tag={hookTag}
        durationFrames={75}
      />

      {/* 5. Explainer Tech / Benchmark Card */}
      <DesktopExplainerCard
        isVisible={isCardVisible}
        title={explainerTitle}
        badge="AI PROVEN SUPERIOR"
      />

      {/* 6. Dynamic Non-Blinking Subtitles (Gold Serif Lower Third) */}
      <DialogueSubtitles
        chunks={chunks}
        activeSpeaker={activeSpeakerName}
        styleMode="serif_gold"
      />

      {/* 7. Cinematic Radial Vignette */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          background:
            "radial-gradient(circle at 50% 45%, transparent 55%, rgba(0,0,0,0.6) 100%)",
          pointerEvents: "none",
          zIndex: 90,
        }}
      />
    </div>
  );
};
