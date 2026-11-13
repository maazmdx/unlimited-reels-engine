import React from "react";
import {
  Sequence,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { DinerBackground } from "./components/diner/DinerBackground";
import { HumanAvatar } from "./components/diner/HumanAvatar";
import { AntigravityBot } from "./components/diner/AntigravityBot";
import { DesktopExplainerCard } from "./components/diner/DesktopExplainerCard";
import { DialogueSubtitles, DialogueChunk } from "./components/diner/DialogueSubtitles";
import { ProgressBar } from "./components/ProgressBar";

export interface DialogueTurn {
  index: number;
  speaker: string;
  start: number;
  end: number;
  duration?: number;
  text: string;
  cardTrigger?: boolean | null;
}

export interface DialogueSubtitleData {
  chunks: DialogueChunk[];
  turns?: DialogueTurn[];
  words?: unknown[];
}

export interface DinerAgentReelProps {
  [key: string]: unknown;
  subtitles?: DialogueSubtitleData;
  audioSrc?: string;
  title?: string;
  cardStartFrame?: number;
  cardEndFrame?: number;
}

const DEFAULT_DIALOGUE_DATA: DialogueSubtitleData = {
  chunks: [
    {
      start: 0.0,
      end: 2.8,
      speaker: "human",
      text: "Antigravity, my girlfriend's dad asked what I make.",
    },
    {
      start: 3.0,
      end: 4.8,
      speaker: "bot",
      text: "What did you say?",
    },
    {
      start: 5.0,
      end: 6.8,
      speaker: "human",
      text: "I said depends.",
    },
    {
      start: 7.0,
      end: 8.4,
      speaker: "bot",
      text: "On what?",
    },
    {
      start: 8.6,
      end: 11.2,
      speaker: "human",
      text: "On him not asking again.",
    },
  ],
  turns: [
    { index: 0, speaker: "human", start: 0.0, end: 2.8, text: "Antigravity, my girlfriend's dad asked what I make." },
    { index: 1, speaker: "bot", start: 3.0, end: 4.8, text: "What did you say?" },
    { index: 2, speaker: "human", start: 5.0, end: 6.8, text: "I said depends." },
    { index: 3, speaker: "bot", start: 7.0, end: 8.4, text: "On what?" },
    { index: 4, speaker: "human", start: 8.6, end: 11.2, text: "On him not asking again." },
  ],
};

export const DinerAgentReel: React.FC<DinerAgentReelProps> = ({
  subtitles = DEFAULT_DIALOGUE_DATA,
  audioSrc = "voice.mp3",
  cardStartFrame,
  cardEndFrame,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const currentTime = frame / fps;

  const turns = subtitles.turns || [];
  const chunks = subtitles.chunks || [];

  // Determine active speaker from timeline turns
  const activeTurn = turns.find(
    (t) => currentTime >= t.start && currentTime <= t.end + 0.1
  );
  const activeSpeaker = activeTurn ? activeTurn.speaker.toLowerCase() : null;

  const isHumanSpeaking = activeSpeaker === "human";
  const isBotSpeaking =
    activeSpeaker === "bot" ||
    activeSpeaker === "gemini" ||
    activeSpeaker === "antigravity";

  // Calculate card trigger frame: either explicit prop or triggered by turns or halfway through video
  const defaultCardStart = cardStartFrame ?? Math.floor(durationInFrames * 0.32);
  const defaultCardEnd = cardEndFrame ?? Math.floor(durationInFrames * 0.85);

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
      {/* 1. Master Dialogue Voice Audio */}
      <Audio src={staticFile(audioSrc)} />

      {/* 2. Ambient Lofi Background Music (Looping at subtle volume) */}
      <Audio src={staticFile("sfx/lofi_bg.mp3")} volume={0.14} loop />

      {/* 3. Sound Effects: Whoosh when explainer card pops in */}
      {defaultCardStart > 0 && (
        <Sequence from={defaultCardStart} durationInFrames={35}>
          <Audio src={staticFile("sfx/whoosh.mp3")} volume={0.45} />
        </Sequence>
      )}

      {/* 4. Sound Effects: Chime when key takeaway hits */}
      {defaultCardStart + 60 < durationInFrames && (
        <Sequence from={defaultCardStart + 60} durationInFrames={40}>
          <Audio src={staticFile("sfx/chime.mp3")} volume={0.35} />
        </Sequence>
      )}

      {/* 5. Top Progress Bar for Audience Retention */}
      <ProgressBar color="#38BDF8" height={8} />

      {/* 6. Diner Background Environment (Booth, Table Lamp, Rainy Window, Checker Floor) */}
      <DinerBackground lampIntensity={1.0} />

      {/* 7. Left Character: Human Avatar in Hoodie */}
      <HumanAvatar isSpeaking={isHumanSpeaking} />

      {/* 8. Right Character: Antigravity Spherical OLED Robot */}
      <AntigravityBot isSpeaking={isBotSpeaking} />

      {/* 9. Floating Desktop Explainer Card (macOS styled) */}
      <DesktopExplainerCard
        isVisible={isCardVisible}
        title="Google Antigravity • your 90-day path"
        badge="100% free"
      />

      {/* 10. Synchronized Dialogue Subtitles with Active Speaker Badges */}
      <DialogueSubtitles chunks={chunks} activeSpeaker={activeSpeaker} />
    </div>
  );
};
