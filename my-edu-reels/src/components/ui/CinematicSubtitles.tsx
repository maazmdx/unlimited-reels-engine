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
  speakerAccentColor?: string;
  speakerDisplayName?: string;
  isAI?: boolean;
}

/**
 * CinematicSubtitles:
 * - Strictly enforces 1080x1420 Instagram safe zone (top: 220px, bottom: 280px).
 * - Upper-middle (top: 280px) during normal dialogue shots (clears face and table).
 * - Lower-safe (bottom: 320px) whenever DynamicProofCard is active (0 collision with card or bottom UI).
 * - High-contrast typography: 2-5 words per chunk with word-level highlight.
 * - Zero CSS transition, zero Math.random(), zero modulo spring resets.
 */
export const CinematicSubtitles: React.FC<CinematicSubtitlesProps> = ({
  activeTurn,
  isProofCardActive = false,
  speakerAccentColor = "#38BDF8",
  speakerDisplayName,
  isAI = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  if (!activeTurn || !activeTurn.text) return null;

  const words = activeTurn.words || [];

  // Group words into bite-sized chunks of 3-5 words
  const CHUNK_SIZE = 4;
  let activeChunkWords: TimelineWord[] = [];
  let activeWordIndexInChunk = -1;

  if (words.length > 0) {
    const activeWordIdx = words.findIndex(
      (w) => currentTime >= w.start_sec && currentTime <= w.end_sec + 0.1
    );

    const safeWordIdx = activeWordIdx >= 0 ? activeWordIdx : 0;
    const chunkStartIdx = Math.floor(safeWordIdx / CHUNK_SIZE) * CHUNK_SIZE;
    activeChunkWords = words.slice(chunkStartIdx, chunkStartIdx + CHUNK_SIZE);
    activeWordIndexInChunk = safeWordIdx - chunkStartIdx;
  }

  // Positioning: top: 280px for normal shots; bottom: 320px when proof card is active
  const positionStyle: React.CSSProperties = isProofCardActive
    ? {
        position: "absolute",
        bottom: 320,
        left: 60,
        right: 60,
      }
    : {
        position: "absolute",
        top: 280,
        left: 60,
        right: 60,
      };

  const displayName =
    speakerDisplayName ||
    (activeTurn.character_id === "junior_dev"
      ? "JUNIOR DEV"
      : activeTurn.character_id === "dad"
      ? "DAD"
      : activeTurn.character_id.toUpperCase().replace("_", " "));

  const highlightColor = isAI ? speakerAccentColor || "#FCD34D" : "#38BDF8";

  return (
    <div
      style={{
        ...positionStyle,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 10,
        zIndex: 85,
        pointerEvents: "none",
        textAlign: "center",
      }}
    >
      {/* 1. Optional Speaker Label Badge */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          padding: "5px 14px",
          borderRadius: 12,
          backgroundColor: "rgba(10, 15, 29, 0.88)",
          border: `1px solid ${highlightColor}66`,
          boxShadow: `0 4px 12px rgba(0, 0, 0, 0.8), 0 0 10px ${highlightColor}33`,
        }}
      >
        <span
          style={{
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: "0.8px",
            color: highlightColor,
            textTransform: "uppercase",
            fontFamily: "system-ui, -apple-system, sans-serif",
          }}
        >
          {displayName}
        </span>
      </div>

      {/* 2. Main Chunk Subtitle Text */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: "8px 12px",
          maxWidth: 960,
          backgroundColor: "rgba(8, 12, 22, 0.82)",
          backdropFilter: "blur(12px)",
          borderRadius: 20,
          padding: "14px 28px",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          boxShadow: "0 16px 36px rgba(0, 0, 0, 0.75)",
        }}
      >
        {activeChunkWords.length > 0 ? (
          activeChunkWords.map((w, idx) => {
            const isActive = idx === activeWordIndexInChunk;
            return (
              <span
                key={`${w.word}-${idx}`}
                style={{
                  fontFamily:
                    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                  fontSize: 42,
                  fontWeight: 900,
                  letterSpacing: "-0.5px",
                  lineHeight: 1.25,
                  color: isActive ? highlightColor : "#FFFFFF",
                  textShadow: isActive
                    ? `0 0 20px ${highlightColor}AA, 0 4px 12px rgba(0,0,0,0.95)`
                    : "0 4px 12px rgba(0,0,0,0.95), 0 2px 4px rgba(0,0,0,0.9)",
                  transform: isActive ? "scale(1.06)" : "scale(1.0)",
                  display: "inline-block",
                }}
              >
                {w.word}
              </span>
            );
          })
        ) : (
          <span
            style={{
              fontFamily:
                "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
              fontSize: 38,
              fontWeight: 800,
              color: "#FFFFFF",
              textShadow: "0 4px 12px rgba(0,0,0,0.95)",
            }}
          >
            {activeTurn.text}
          </span>
        )}
      </div>
    </div>
  );
};
