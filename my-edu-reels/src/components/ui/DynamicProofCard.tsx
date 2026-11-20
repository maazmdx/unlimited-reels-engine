import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface CardProofItem {
  label: string;
  value: string;
  badge?: string;
  isPositive?: boolean;
}

export interface DynamicCardData {
  title?: string;
  subtitle?: string;
  badge?: string;
  type?: "code" | "benchmark" | "comparison" | "alert";
  codeSnippet?: string;
  language?: string;
  items?: CardProofItem[];
  highlight?: string;
  durationSeconds?: number;
  startFrame?: number;
}

export interface DynamicProofCardProps {
  cardData?: DynamicCardData | null;
  startFrame?: number;
  durationFrames?: number;
}

/**
 * DynamicProofCard:
 * - Upper-third positioning (top: 220px, maxHeight: 520px, width: 920px), perfectly clearing seated characters below.
 * - macOS / terminal dark frosted window with traffic lights, title badge, and dynamic code / benchmark proofs.
 * - Strict duration cap: 3.0s - 5.0s max (90 - 150 frames @ 30fps).
 * - Zero flicker: 0 Math.random(), 0 CSS transition, 0 frame % N spring resets.
 */
export const DynamicProofCard: React.FC<DynamicProofCardProps> = ({
  cardData,
  startFrame = 90,
  durationFrames = 120, // default 4.0s @ 30fps
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!cardData) return null;

  // Strict duration capping: clamp duration between 90 and 150 frames (3.0s - 5.0s max)
  const effectiveStart = cardData.startFrame ?? startFrame;
  const requestedDuration = cardData.durationSeconds
    ? Math.round(cardData.durationSeconds * fps)
    : durationFrames;
  const cappedDuration = Math.min(Math.max(requestedDuration, 90), 150);
  const effectiveEnd = effectiveStart + cappedDuration;

  // Card visibility check
  if (frame < effectiveStart || frame > effectiveEnd) {
    return null;
  }

  const age = frame - effectiveStart;
  const exitAge = effectiveEnd - frame;

  // Smooth spring entrance (deterministic, bounded by 30 frames)
  const entrance = spring({
    frame: Math.min(age, 25),
    fps,
    config: { damping: 14, stiffness: 140, mass: 0.8 },
  });

  // Smooth exit fade / slide
  const exitOpacity = interpolate(exitAge, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitSlide = interpolate(exitAge, [0, 12], [-20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = entrance * exitOpacity;
  const translateY = interpolate(entrance, [0, 1], [-40, 0]) + exitSlide;
  const scale = interpolate(entrance, [0, 1], [0.94, 1.0]);

  const title = cardData.title || "Autonomous Multi-Agent Speedup";
  const badge = cardData.badge || "PROVEN ARCHITECTURE";
  const type = cardData.type || (cardData.codeSnippet ? "code" : "benchmark");

  return (
    <div
      style={{
        position: "absolute",
        top: 220,
        left: 80,
        width: 920,
        maxHeight: 520,
        zIndex: 80,
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
        transformOrigin: "center top",
        pointerEvents: "none",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div
        style={{
          background: "rgba(13, 17, 28, 0.94)",
          backdropFilter: "blur(24px)",
          borderRadius: 22,
          border: "1px solid rgba(56, 189, 248, 0.28)",
          boxShadow:
            "0 24px 60px rgba(0, 0, 0, 0.8), 0 0 45px rgba(56, 189, 248, 0.22), inset 0 1px 1px rgba(255, 255, 255, 0.15)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Window Titlebar */}
        <div
          style={{
            height: 48,
            backgroundColor: "rgba(18, 24, 38, 0.98)",
            borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
            display: "flex",
            alignItems: "center",
            padding: "0 18px",
            justifyContent: "space-between",
          }}
        >
          {/* macOS Traffic Lights */}
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#EF4444" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#10B981" }} />
            <span
              style={{
                marginLeft: 14,
                fontSize: 14,
                fontWeight: 600,
                color: "#94A3B8",
                letterSpacing: "0.2px",
              }}
            >
              {cardData.language ? `proof.${cardData.language}` : "proof.tsx"}
            </span>
          </div>

          {/* Window Center Title */}
          <div
            style={{
              fontSize: 15,
              fontWeight: 700,
              color: "#F8FAFC",
              letterSpacing: "0.4px",
              textTransform: "uppercase",
            }}
          >
            {title}
          </div>

          {/* Badge Pill */}
          <div
            style={{
              backgroundColor: "rgba(14, 165, 233, 0.2)",
              border: "1px solid rgba(56, 189, 248, 0.5)",
              color: "#38BDF8",
              padding: "4px 12px",
              borderRadius: 12,
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.8px",
              boxShadow: "0 0 12px rgba(56, 189, 248, 0.35)",
            }}
          >
            {badge}
          </div>
        </div>

        {/* Content Body */}
        <div style={{ padding: "20px 24px", color: "#E2E8F0" }}>
          {type === "code" && cardData.codeSnippet ? (
            <div
              style={{
                backgroundColor: "rgba(6, 9, 16, 0.85)",
                borderRadius: 14,
                padding: "16px 20px",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
                fontSize: 17,
                lineHeight: 1.5,
                color: "#F1F5F9",
                whiteSpace: "pre-wrap",
                boxShadow: "inset 0 2px 6px rgba(0,0,0,0.5)",
              }}
            >
              {cardData.codeSnippet}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {/* Benchmark comparison rows */}
              {(cardData.items || [
                { label: "Junior Manual Loop", value: "6h 40m", badge: "FATIGUED", isPositive: false },
                { label: "Antigravity Multi-Agent", value: "48s", badge: "340x FASTER", isPositive: true },
                { label: "Cost & API Spend", value: "$0.00", badge: "GEMINI FLASH", isPositive: true },
              ]).map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    backgroundColor: item.isPositive
                      ? "rgba(16, 185, 129, 0.12)"
                      : "rgba(239, 68, 68, 0.12)",
                    border: item.isPositive
                      ? "1px solid rgba(16, 185, 129, 0.35)"
                      : "1px solid rgba(239, 68, 68, 0.3)",
                    borderRadius: 14,
                    padding: "12px 20px",
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <span style={{ fontSize: 15, fontWeight: 600, color: "#CBD5E1" }}>
                      {item.label}
                    </span>
                    <span
                      style={{
                        fontSize: 24,
                        fontWeight: 800,
                        color: item.isPositive ? "#34D399" : "#F87171",
                        letterSpacing: "-0.5px",
                      }}
                    >
                      {item.value}
                    </span>
                  </div>
                  {item.badge && (
                    <span
                      style={{
                        padding: "6px 14px",
                        borderRadius: 10,
                        fontSize: 13,
                        fontWeight: 800,
                        backgroundColor: item.isPositive
                          ? "rgba(16, 185, 129, 0.25)"
                          : "rgba(239, 68, 68, 0.25)",
                        color: item.isPositive ? "#6EE7B7" : "#FCA5A5",
                        border: item.isPositive
                          ? "1px solid rgba(52, 211, 153, 0.5)"
                          : "1px solid rgba(248, 113, 113, 0.5)",
                      }}
                    >
                      {item.badge}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Bottom highlight pill */}
          {cardData.highlight && (
            <div
              style={{
                marginTop: 14,
                padding: "10px 16px",
                backgroundColor: "rgba(56, 189, 248, 0.1)",
                borderRadius: 12,
                border: "1px solid rgba(56, 189, 248, 0.25)",
                display: "flex",
                alignItems: "center",
                gap: 10,
                fontSize: 14,
                fontWeight: 600,
                color: "#7DD3FC",
              }}
            >
              <span>⚡</span>
              <span>{cardData.highlight}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
