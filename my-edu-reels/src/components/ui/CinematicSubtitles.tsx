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
 * never renders broken placeholder boxes (□), while preserving contractions and apostrophes.
 */
const stripEmojis = (str: string): string => {
  return (str || "")
    .replace(/[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}]/gu, "")
    .replace(/[’‘]/g, "'")
    .replace(/^[^\w']+|[^\w']+$/gu, "")
    .replace(/^_+|_+$/g, "")
    .trim();
};

/**
 * CinematicSubtitles:
 * - High-contrast kinetic typography (fontSize: 58px, fontWeight: 900, 6px stroke, dark shadow).
 * - Permanently locked to lower-middle safe zone (bottom: 340px) above Instagram UI bar.
 * - Active words in electric yellow (#FDE047), resting in pure white (#FFFFFF).
 * - Preserves apostrophes and contractions ("I'm", "doesn't", "you're", "I'll").
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

  // Strict frame-boundary check: render subtitles strictly within this turn's frame range (prevents turn bleed)
  if (frame < activeTurn.start_frame || frame > activeTurn.end_frame) {
    return null;
  }

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

  // Permanently locked in lower-middle safe zone (bottom: 340px, strictly above Instagram 280px UI bar)
  // Never jumps or overlaps top badge pill / robot head during proof cards
  const positionStyle: React.CSSProperties = {
    position: "absolute",
    bottom: 340,
    left: 60,
    right: 60,
    zIndex: 99,
  };

  const activeWordColor = speakerAccentColor || "#F59E0B"; // Warm amber
  const inactiveWordColor = "#FFFFFF"; // Pure white

  return (
    <div
      style={{
        ...positionStyle,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 99,
        pointerEvents: "none",
        textAlign: "center",
      }}
    >
      {/* Floating editorial typography with subtle frosted backdrop and crisp soft drop shadow */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: "8px 14px",
          maxWidth: 960,
          backgroundColor: "rgba(10, 10, 12, 0.72)",
          backdropFilter: "blur(12px)",
          borderRadius: 20,
          padding: "14px 28px",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          boxShadow: "0 12px 32px rgba(0, 0, 0, 0.8)",
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
                    "'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                  fontSize: 54,
                  fontWeight: 800,
                  letterSpacing: "-1px",
                  lineHeight: 1.25,
                  color: isActive ? activeWordColor : inactiveWordColor,
                  WebkitTextStroke: "1px rgba(0, 0, 0, 0.8)",
                  paintOrder: "stroke fill",
                  textShadow: isActive
                    ? "0 4px 16px rgba(245, 158, 11, 0.6), 0 2px 8px rgba(0, 0, 0, 0.9)"
                    : "0 4px 12px rgba(0, 0, 0, 0.9)",
                  transform: isActive ? "scale(1.05)" : "scale(1.0)",
                  display: "inline-block",
                  marginRight: 10,
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
                "'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              fontSize: 54,
              fontWeight: 800,
              letterSpacing: "-1px",
              lineHeight: 1.25,
              color: activeWordColor,
              WebkitTextStroke: "1px rgba(0, 0, 0, 0.8)",
              paintOrder: "stroke fill",
              textShadow:
                "0 4px 16px rgba(245, 158, 11, 0.6), 0 2px 8px rgba(0, 0, 0, 0.9)",
            }}
          >
            {stripEmojis(activeTurn.text)}
          </span>
        )}
      </div>
    </div>
  );
};
