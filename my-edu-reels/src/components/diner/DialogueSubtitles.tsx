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
    const prevChunk = [...chunks]
      .reverse()
      .find((c) => currentTime > c.end && currentTime - c.end < 0.6);
    if (prevChunk) {
      activeChunk = prevChunk;
      activeWordIndex = (prevChunk.words?.length || 1) - 1;
    }
  }

  if (!activeChunk) {
    return null;
  }

  const speaker = (activeChunk.speaker || activeSpeaker || "bot").toLowerCase();
  const isHuman = speaker === "human" || speaker === "junior" || speaker === "dev";
  const isRival = speaker === "rival" || speaker === "senior";
  const isDad = speaker === "dad" || speaker === "father" || speaker === "uncle";
  const isClaude = speaker === "claude";
  const isGrok = speaker === "grok";

  // Dynamic speaker badge styling
  let badgeLabel = "Google Antigravity";
  let badgeColor = "#38BDF8";
  let badgeBg = "rgba(56, 189, 248, 0.15)";
  let badgeBorder = "rgba(56, 189, 248, 0.5)";

  if (isDad) {
    badgeLabel = "Dad (Unbeatable Logic)";
    badgeColor = "#F97316"; // Bright Orange
    badgeBg = "rgba(249, 115, 22, 0.20)";
    badgeBorder = "rgba(249, 115, 22, 0.6)";
  } else if (isHuman) {
    badgeLabel = "Junior Dev";
    badgeColor = "#34D399";
    badgeBg = "rgba(52, 211, 153, 0.15)";
    badgeBorder = "rgba(52, 211, 153, 0.5)";
  } else if (isRival) {
    badgeLabel = "Senior Dev";
    badgeColor = "#F59E0B";
    badgeBg = "rgba(245, 158, 11, 0.15)";
    badgeBorder = "rgba(245, 158, 11, 0.5)";
  } else if (isClaude) {
    badgeLabel = "Anthropic Claude";
    badgeColor = "#D97706";
    badgeBg = "rgba(217, 119, 6, 0.15)";
    badgeBorder = "rgba(217, 119, 6, 0.5)";
  } else if (isGrok) {
    badgeLabel = "xAI Grok";
    badgeColor = "#E2E8F0";
    badgeBg = "rgba(226, 232, 240, 0.15)";
    badgeBorder = "rgba(226, 232, 240, 0.5)";
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
        zIndex: 100,
        pointerEvents: "none",
        padding: "0 48px",
        transform: "translate3d(0, 0, 0)",
        backfaceVisibility: "hidden",
        WebkitFontSmoothing: "antialiased",
      }}
    >
      {/* Speaker Identifier Badge */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          backgroundColor: badgeBg,
          color: badgeColor,
          border: `1.5px solid ${badgeBorder}`,
          borderRadius: 20,
          padding: "6px 18px",
          fontSize: 16,
          fontWeight: 800,
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          marginBottom: 12,
          boxShadow: `0 4px 16px ${badgeBg}`,
        }}
      >
        <span style={{ fontSize: 14 }}>●</span>
        <span>{badgeLabel}</span>
      </div>

      {/* Main Subtitle Box (Anti-Flicker Solid Translucency) */}
      <div
        style={{
          backgroundColor: "rgba(11, 15, 25, 0.94)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: 20,
          padding: "16px 28px",
          maxWidth: 960,
          textAlign: "center",
          boxShadow: "0 16px 40px rgba(0,0,0,0.8)",
          backfaceVisibility: "hidden",
        }}
      >
        {words.length > 0 ? (
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: "8px 12px",
              fontFamily:
                styleMode === "serif_gold"
                  ? "Georgia, 'Times New Roman', serif"
                  : "system-ui, -apple-system, sans-serif",
            }}
          >
            {words.map((w, idx) => {
              const isActive = idx === activeWordIndex;
              const isPast = idx < activeWordIndex;
              return (
                <span
                  key={idx}
                  style={{
                    fontSize: 32,
                    fontWeight: 700,
                    lineHeight: 1.3,
                    color: isActive
                      ? "#FFDF00"
                      : isPast
                      ? "#F8FAFC"
                      : "rgba(248, 250, 252, 0.65)",
                    textShadow: isActive
                      ? "0 0 16px rgba(255, 223, 0, 0.8), 0 2px 8px rgba(0,0,0,0.9)"
                      : "0 2px 6px rgba(0,0,0,0.8)",
                    transform: isActive ? "scale(1.08)" : "scale(1.0)",
                    display: "inline-block",
                    transition: "transform 0.05s ease-out",
                  }}
                >
                  {w.word}
                </span>
              );
            })}
          </div>
        ) : (
          <span
            style={{
              fontSize: 32,
              fontWeight: 700,
              color: "#F8FAFC",
              lineHeight: 1.3,
              fontFamily:
                styleMode === "serif_gold"
                  ? "Georgia, 'Times New Roman', serif"
                  : "system-ui, -apple-system, sans-serif",
              textShadow: "0 2px 8px rgba(0,0,0,0.9)",
            }}
          >
            {activeChunk.text}
          </span>
        )}
      </div>
    </div>
  );
};
