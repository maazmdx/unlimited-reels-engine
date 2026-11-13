import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export interface DialogueWord {
  word: string;
  raw: string;
  start: number;
  end: number;
  speaker?: string;
}

export interface DialogueChunk {
  start: number;
  end: number;
  text: string;
  speaker: string;
  words?: DialogueWord[];
}

export interface DialogueSubtitlesProps {
  chunks: DialogueChunk[];
  activeSpeaker?: string | null;
  styleMode?: "serif_gold" | "pill_dark";
}

export const DialogueSubtitles: React.FC<DialogueSubtitlesProps> = ({
  chunks = [],
  activeSpeaker = null,
  styleMode = "serif_gold",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Find current or most recent chunk within turn to avoid blinking/flickering
  let activeChunk: DialogueChunk | null = null;
  let activeWordIndex = -1;

  for (let i = 0; i < chunks.length; i++) {
    const c = chunks[i];
    // Extend boundary by 0.35s to prevent blank flash between words
    if (currentTime >= c.start && currentTime <= c.end + 0.35) {
      activeChunk = c;
      if (c.words) {
        activeWordIndex = c.words.findIndex(
          (w) => currentTime >= w.start && currentTime <= w.end + 0.1
        );
      }
      break;
    }
  }

  // If no exact match, find if we're between two close chunks (less than 0.6s gap)
  if (!activeChunk && chunks.length > 0) {
    const prevChunk = [...chunks].reverse().find((c) => currentTime > c.end && currentTime - c.end < 0.6);
    if (prevChunk) {
      activeChunk = prevChunk;
      activeWordIndex = (prevChunk.words?.length || 1) - 1;
    }
  }

  if (!activeChunk) {
    return null;
  }

  const speaker = (activeChunk.speaker || activeSpeaker || "bot").toLowerCase();
  const isHuman = speaker === "human" || speaker === "junior";
  const isRival = speaker === "rival" || speaker === "senior";

  // Speaker badge styling
  let badgeLabel = "Google Antigravity";
  let badgeColor = "#38BDF8";
  let badgeBg = "rgba(56, 189, 248, 0.15)";
  let badgeBorder = "rgba(56, 189, 248, 0.5)";

  if (isHuman) {
    badgeLabel = "Junior Dev";
    badgeColor = "#34D399";
    badgeBg = "rgba(52, 211, 153, 0.15)";
    badgeBorder = "rgba(52, 211, 153, 0.5)";
  } else if (isRival) {
    badgeLabel = "Senior Dev";
    badgeColor = "#F59E0B";
    badgeBg = "rgba(245, 158, 11, 0.15)";
    badgeBorder = "rgba(245, 158, 11, 0.5)";
  }

  const words = activeChunk.words || [];

  return (
    <div
      style={{
        position: "absolute",
        bottom: 180,
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 80,
        pointerEvents: "none",
        padding: "0 54px",
      }}
    >
      {/* Stable Speaker Badge (No blinking between syllables) */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 10,
          backgroundColor: badgeBg,
          border: `1.5px solid ${badgeBorder}`,
          padding: "6px 20px",
          borderRadius: 24,
          marginBottom: 16,
          backdropFilter: "blur(12px)",
          boxShadow: `0 4px 20px rgba(0,0,0,0.5)`,
        }}
      >
        <span
          style={{
            width: 9,
            height: 9,
            borderRadius: "50%",
            backgroundColor: badgeColor,
            boxShadow: `0 0 12px ${badgeColor}`,
          }}
        />
        <span
          style={{
            color: "#FFFFFF",
            fontSize: 16,
            fontWeight: 800,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            fontFamily: "system-ui, -apple-system, sans-serif",
          }}
        >
          {badgeLabel}
        </span>
      </div>

      {/* High-Impact Subtitle Typography (Matches Reference Reels) */}
      <div
        style={{
          textAlign: "center",
          maxWidth: 960,
          lineHeight: 1.35,
          background: "rgba(7, 11, 20, 0.72)",
          padding: "16px 32px",
          borderRadius: 28,
          border: "1px solid rgba(255, 255, 255, 0.12)",
          backdropFilter: "blur(14px)",
          boxShadow: "0 12px 36px rgba(0,0,0,0.65)",
        }}
      >
        {words.length > 0 ? (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: "8px 12px",
            }}
          >
            {words.map((w, wIdx) => {
              const isCurrent = wIdx === activeWordIndex;
              const isPast = wIdx < activeWordIndex;

              return (
                <span
                  key={wIdx}
                  style={{
                    fontSize: 42,
                    fontWeight: 800,
                    fontFamily:
                      styleMode === "serif_gold"
                        ? "Georgia, 'Times New Roman', serif"
                        : "system-ui, -apple-system, sans-serif",
                    color: isCurrent
                      ? "#FDE047" // Golden highlight
                      : isPast
                      ? "#FFFFFF"
                      : "rgba(255, 255, 255, 0.75)",
                    transform: isCurrent ? "scale(1.08)" : "scale(1.0)",
                    display: "inline-block",
                    transition: "transform 0.1s ease, color 0.1s ease",
                    textShadow: isCurrent
                      ? "0 0 20px rgba(253, 224, 71, 0.6), 0 3px 8px rgba(0,0,0,0.9)"
                      : "0 3px 8px rgba(0,0,0,0.9)",
                  }}
                >
                  {w.raw || w.word}
                </span>
              );
            })}
          </div>
        ) : (
          <span
            style={{
              fontSize: 42,
              fontWeight: 800,
              fontFamily: "Georgia, 'Times New Roman', serif",
              color: "#FDE047",
              textShadow: "0 3px 12px rgba(0,0,0,0.9)",
            }}
          >
            {activeChunk.text}
          </span>
        )}
      </div>
    </div>
  );
};
