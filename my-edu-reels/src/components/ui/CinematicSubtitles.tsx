import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export interface TimelineWord {
  word: string;
  start_sec: number;
  end_sec: number;
}

export interface TimelineTurn {
  turn_index: number;
  character_id: string;
  text: string;
  emotion?: string;
  start_sec: number;
  end_sec: number;
  start_frame: number;
  end_frame: number;
  duration_sec: number;
  words?: TimelineWord[];
}

export interface CinematicSubtitlesProps {
  activeTurn?: TimelineTurn | null;
  isProofCardActive?: boolean;
  isCtaActive?: boolean;
  speakerAccentColor?: string;
  speakerDisplayName?: string;
  isAI?: boolean;
}

/**
 * Strips non-ASCII emoji characters and symbol ranges so headless Linux/Kaggle
 * never renders broken placeholder boxes (□).
 */
const stripEmojis = (str: string): string => {
  return (str || "")
    .replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}]/gu, "")
    .trim();
};

/**
 * CinematicSubtitles:
 * - Floating editorial typography (fontSize: 52px, fontWeight: 700, soft drop-shadow).
 * - Zero generic black rounded pill box or speaker label badge.
 * - Human in #FFFFFF, AI in #FCD34D (Claude), #7DD3FC (Gemini), #FCA5A5 (Grok).
 * - Strictly enforces 1080x1920 Instagram safe zone (top: 280px / bottom: 320px).
 * - Zero CSS transition, zero Math.random(), zero modulo spring resets.
 */
export const CinematicSubtitles: React.FC<CinematicSubtitlesProps> = ({
  activeTurn,
  isProofCardActive = false,
  isCtaActive = false,
  speakerAccentColor,
  isAI = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Clean exit if no active turn or empty text
  if (!activeTurn || !activeTurn.text || !activeTurn.text.trim()) return null;

  const words = activeTurn.words || [];

  // Group words into bite-sized chunks of 3-4 words for fast editorial reading
  const CHUNK_SIZE = 4;
  let activeChunkWords: TimelineWord[] = [];
  let activeWordIndexInChunk = -1;

  if (words.length > 0) {
    const firstWordStart = words[0].start_sec;
    const lastWordEnd = words[words.length - 1].end_sec;
    if (currentTime < firstWordStart - 0.10 || currentTime > lastWordEnd + 0.18) {
      return null;
    }

    const activeWordIdx = words.findIndex(
      (w) => currentTime >= w.start_sec - 0.05 && currentTime <= w.end_sec + 0.10
    );

    const safeWordIdx = activeWordIdx >= 0 ? activeWordIdx : 0;
    const chunkStartIdx = Math.floor(safeWordIdx / CHUNK_SIZE) * CHUNK_SIZE;
    activeChunkWords = words.slice(chunkStartIdx, chunkStartIdx + CHUNK_SIZE);
    activeWordIndexInChunk = safeWordIdx - chunkStartIdx;

    if (activeChunkWords.length === 0 || activeChunkWords.every((w) => !w.word || !w.word.trim())) {
      return null;
    }
  } else {
    if (currentTime < activeTurn.start_sec || currentTime > activeTurn.end_sec) {
      return null;
    }
  }

  // Positioning: top: 280px for normal shots; bottom: 320px when proof card or toast is active
  const isBottom = isProofCardActive || isCtaActive;
  const positionStyle: React.CSSProperties = isBottom
    ? {
        position: "absolute",
        bottom: 320,
        left: 60,
        right: 60,
        zIndex: 95,
      }
    : {
        position: "absolute",
        top: 280,
        left: 60,
        right: 60,
        zIndex: 95,
      };

  // Color mapping: Human in #FFFFFF, AI in designated color
  const charId = (activeTurn.character_id || "").toLowerCase();
  const isHumanChar = charId === "junior_dev" || charId === "dad" || (!isAI && !charId.includes("claude") && !charId.includes("gemini") && !charId.includes("grok"));

  let primaryColor = "#FFFFFF";
  if (!isHumanChar) {
    if (charId.includes("gemini")) {
      primaryColor = "#7DD3FC";
    } else if (charId.includes("grok")) {
      primaryColor = "#FCA5A5";
    } else {
      primaryColor = speakerAccentColor || "#FCD34D"; // Claude default #FCD34D
    }
  }

  const inactiveColor = isHumanChar
    ? "rgba(255, 255, 255, 0.72)"
    : `${primaryColor}B3`;

  return (
    <div
      style={{
        ...positionStyle,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 95,
        pointerEvents: "none",
        textAlign: "center",
      }}
    >
      {/* Floating editorial typography - Zero black pill box, zero badge */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: "8px 16px",
          maxWidth: 960,
          background: "transparent",
          padding: 0,
          border: "none",
          boxShadow: "none",
        }}
      >
        {activeChunkWords.length > 0 ? (
          activeChunkWords.map((w, idx) => {
            const isActive = idx === activeWordIndexInChunk;
            const displayWord = stripEmojis(w.word);
            if (!displayWord) return null;

            return (
              <span
                key={`${w.word}-${idx}`}
                style={{
                  fontFamily:
                    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                  fontSize: 52,
                  fontWeight: 700,
                  letterSpacing: "-0.5px",
                  lineHeight: 1.25,
                  color: isActive ? primaryColor : inactiveColor,
                  textShadow: isActive
                    ? `0 4px 18px rgba(0, 0, 0, 0.95), 0 0 24px ${primaryColor}88`
                    : "0 4px 18px rgba(0, 0, 0, 0.85)",
                  transform: isActive ? "scale(1.05)" : "scale(1.0)",
                  display: "inline-block",
                }}
              >
                {displayWord}
              </span>
            );
          })
        ) : (
          <span
            style={{
              fontFamily:
                "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              fontSize: 52,
              fontWeight: 700,
              letterSpacing: "-0.5px",
              lineHeight: 1.25,
              color: primaryColor,
              textShadow: `0 4px 18px rgba(0, 0, 0, 0.85), 0 0 16px ${primaryColor}66`,
            }}
          >
            {stripEmojis(activeTurn.text)}
          </span>
        )}
      </div>
    </div>
  );
};
