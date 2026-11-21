import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export interface CardProofItem {
  label: string;
  value: string;
  badge?: string;
  status?: string;
  isPositive?: boolean;
}

export interface DynamicCardData {
  title?: string;
  subtitle?: string;
  badge?: string;
  type?: "code" | "benchmark" | "comparison" | "alert";
  codeSnippet?: string;
  language?: string;
  searchQuery?: string;
  command?: string;
  items?: CardProofItem[];
  rows?: CardProofItem[];
  highlight?: string;
  topicLogoPath?: string;
  durationSeconds?: number;
  startFrame?: number;
  durationFrames?: number;
}

export interface DynamicProofCardProps {
  cardData?: DynamicCardData | null;
  startFrame?: number;
  durationFrames?: number;
  activeStepIndex?: number;
  topicLogoPath?: string;
}

/**
 * Highlights key power words / numbers ($19.99, 60 FPS, 100%, FREE, ZERO, etc.)
 * with bold glowing pills (#FEF08A / #DBEAFE).
 */
function renderHighlightedValue(value: string, isCurrent: boolean) {
  const powerWordRegex = /(\$?\d+[\d,.]*(?:\s*(?:FPS|DOWNLOADS?|K|M|B|X|%|ms|s|GB|TB))?|\bFREE\b|\bZERO\b|\bNATIVE\b|\bINSTANT\b|\bOFFICIAL\b|\bVERIFIED\b|100%|\$\d+(?:\.\d{2})?)/gi;

  const parts = value.split(powerWordRegex);
  if (parts.length <= 1) {
    return value;
  }

  return parts.map((part, i) => {
    if (!part) return null;
    const isPowerMatch = part.match(powerWordRegex);
    if (isPowerMatch) {
      return (
        <span
          key={i}
          style={{
            backgroundColor: isCurrent ? "#FEF08A" : "#DBEAFE",
            color: isCurrent ? "#854D0E" : "#1E40AF",
            padding: "2px 8px",
            borderRadius: 6,
            fontWeight: 900,
            boxShadow: isCurrent
              ? "0 0 10px rgba(254, 240, 138, 0.7)"
              : "0 0 8px rgba(219, 234, 254, 0.6)",
            border: isCurrent
              ? "1px solid rgba(250, 204, 21, 0.8)"
              : "1px solid rgba(147, 197, 253, 0.7)",
            display: "inline-block",
            margin: "0 2px",
          }}
        >
          {part}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

function cleanTitleTruncation(text: string, maxChars: number = 32): string {
  if (!text) return "";
  const trimmed = text.trim();
  if (trimmed.length <= maxChars) return trimmed;
  const lastSpace = trimmed.lastIndexOf(" ", maxChars);
  return lastSpace > 10 ? trimmed.slice(0, lastSpace) : trimmed.slice(0, maxChars);
}

/**
 * DynamicProofCard:
 * - High-contrast light-mode frosted browser card (#F8FAFC with dark #0F172A text).
 * - Upper-third positioning (top: 220px, maxHeight: 500px, width: 920px), perfectly clearing seated characters.
 * - Dynamic Step-by-Step highlighting: highlights Row 1 on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7.
 * - Pops cleanly against dark diner and desk backgrounds.
 * - Renders ONLY dynamic topic-specific cardData passed from HookMaster / SceneDirector.
 */
export const DynamicProofCard: React.FC<DynamicProofCardProps> = ({
  cardData,
  startFrame = 90,
  durationFrames = 360, // default ~12.0s @ 30fps for 3-turn interactive proof
  activeStepIndex,
  topicLogoPath,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!cardData) return null;

  const effectiveLogo = topicLogoPath || cardData.topicLogoPath;

  // Strict duration capping: allow interactive multi-step proof up to 14.0s (420 frames @ 30fps)
  const effectiveStart = cardData.startFrame ?? startFrame;
  const requestedDuration =
    durationFrames ??
    (cardData.durationSeconds
      ? Math.round(cardData.durationSeconds * fps)
      : cardData.durationFrames ?? 360);
  const cappedDuration = Math.min(Math.max(requestedDuration, 60), 420);
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

  // Extract topic-specific rows/items
  const rawItems = cardData.rows || cardData.items;
  let items: CardProofItem[] = [];

  if (rawItems && Array.isArray(rawItems) && rawItems.length > 0) {
    items = rawItems;
  } else {
    // If cardData has direct custom key/value pairs (e.g. point_1, engine, etc.), normalize them
    const ignoredKeys = new Set([
      "title",
      "subtitle",
      "badge",
      "type",
      "codeSnippet",
      "language",
      "items",
      "rows",
      "highlight",
      "durationSeconds",
      "startFrame",
      "durationFrames",
    ]);
    const customEntries = Object.entries(cardData).filter(([k]) => !ignoredKeys.has(k));
    if (customEntries.length > 0) {
      items = customEntries.slice(0, 3).map(([k, v]) => ({
        label: k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        value: String(v),
        badge: "VERIFIED",
        status: "VERIFIED",
        isPositive: true,
      }));
    }
  }

  const title = cardData.title
    ? cleanTitleTruncation(cardData.title, 34)
    : (cardData.subtitle ? `${cleanTitleTruncation(cardData.subtitle, 26)} Specs` : "Verified Tech Specs");
  const badge = cardData.badge || "VERIFIED PROOF";
  const type = cardData.type || (cardData.codeSnippet ? "code" : "comparison");

  // Deterministic Typing & Click Search Bar (Turn 5 Typing, Turns 6-7 Click + Verified Pill)
  const cleanSearchTitle = cleanTitleTruncation(cardData.title || "", 30);
  const rawSearchText =
    cardData.searchQuery ||
    cardData.command ||
    (cleanSearchTitle
      ? `verify --inspect "${cleanSearchTitle}"`
      : "benchmark --live --official");

  const typingAge = Math.max(0, age - 8);
  const typingDuration = 36;
  const typingProgress = interpolate(typingAge, [0, typingDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const typedLength =
    activeStepIndex === 0
      ? Math.floor(typingProgress * rawSearchText.length)
      : rawSearchText.length;
  const displayedSearchText = rawSearchText.slice(0, typedLength);
  const isTypingDone = activeStepIndex !== 0 || typingProgress >= 1.0;
  const showBlinkingCursor = !isTypingDone && (Math.floor(frame / 6) % 2 === 0);

  const isTurn6Or7 = (activeStepIndex ?? 0) >= 1;
  const searchPillLabel = isTurn6Or7 ? "✓ Verified" : "Active";
  const searchPillBg = isTurn6Or7 ? "#16A34A" : "#0284C7";
  const searchPillShadow = isTurn6Or7
    ? "0 2px 10px rgba(22, 163, 74, 0.4)"
    : "0 2px 8px rgba(2, 132, 199, 0.35)";

  return (
    <div
      style={{
        position: "absolute",
        top: 220,
        left: 80,
        width: 920,
        maxHeight: 500,
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
          background: "rgba(248, 250, 252, 0.96)",
          backdropFilter: "blur(24px)",
          borderRadius: 22,
          border: "2px solid rgba(255, 255, 255, 0.95)",
          boxShadow:
            "0 28px 70px rgba(0, 0, 0, 0.7), 0 0 40px rgba(56, 189, 248, 0.3), inset 0 1px 2px rgba(255, 255, 255, 1)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Window Titlebar */}
        <div
          style={{
            height: 52,
            backgroundColor: "rgba(241, 245, 249, 0.98)",
            borderBottom: "1px solid rgba(203, 213, 225, 0.8)",
            display: "flex",
            alignItems: "center",
            padding: "0 20px",
            justifyContent: "space-between",
          }}
        >
          {/* macOS Traffic Lights */}
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#EF4444" }} />
            <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
            <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#10B981" }} />
            <span
              style={{
                marginLeft: 14,
                fontSize: 14,
                fontWeight: 700,
                color: "#64748B",
                letterSpacing: "0.2px",
              }}
            >
              {cardData.language ? `proof.${cardData.language}` : "proof.verified"}
            </span>
          </div>

          {/* Window Center Title with optional Topic Logo */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              fontSize: 16,
              fontWeight: 800,
              color: "#0F172A",
              letterSpacing: "0.4px",
              textTransform: "uppercase",
            }}
          >
            {effectiveLogo && (
              <Img
                src={staticFile(effectiveLogo)}
                style={{
                  width: 26,
                  height: 26,
                  borderRadius: 6,
                  objectFit: "contain",
                  backgroundColor: "#FFFFFF",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
                  border: "1px solid rgba(203, 213, 225, 0.8)",
                  padding: 2,
                }}
              />
            )}
            <span>{title}</span>
          </div>

          {/* Badge Pill */}
          <div
            style={{
              backgroundColor: "#0284C7",
              color: "#FFFFFF",
              padding: "5px 14px",
              borderRadius: 12,
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.8px",
              boxShadow: "0 2px 8px rgba(2, 132, 199, 0.35)",
            }}
          >
            {badge}
          </div>
        </div>

        {/* Interactive Search / Command Action Bar (Turn 5 Typing -> Turn 6-7 Click + Pill Toggle) */}
        <div
          style={{
            position: "relative",
            margin: "12px 24px 0 24px",
            padding: "8px 16px",
            backgroundColor: "rgba(241, 245, 249, 0.95)",
            border: isTurn6Or7 ? "1.5px solid rgba(22, 163, 74, 0.6)" : "1.5px solid rgba(203, 213, 225, 0.9)",
            borderRadius: 12,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            boxShadow: "inset 0 1px 3px rgba(0,0,0,0.06)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, overflow: "hidden", flex: 1 }}>
            <span style={{ fontSize: 13, color: "#64748B" }}>🔍</span>
            <span
              style={{
                fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
                fontSize: 13,
                fontWeight: 700,
                color: "#0F172A",
                whiteSpace: "nowrap",
                letterSpacing: "-0.2px",
              }}
            >
              {displayedSearchText}
              {showBlinkingCursor && (
                <span style={{ color: "#0284C7", fontWeight: 900 }}>|</span>
              )}
            </span>
          </div>

          {/* Interactive Pill Toggle Button */}
          <div
            style={{
              backgroundColor: searchPillBg,
              color: "#FFFFFF",
              padding: "4px 14px",
              borderRadius: 8,
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.5px",
              textTransform: "uppercase",
              boxShadow: searchPillShadow,
              display: "flex",
              alignItems: "center",
              gap: 4,
              transform:
                activeStepIndex === 1
                  ? `scale(${interpolate(age % 24, [0, 6, 12, 24], [1, 0.92, 1, 1])})`
                  : "scale(1)",
              transformOrigin: "center",
            }}
          >
            <span>{searchPillLabel}</span>
          </div>

          {/* Animated Cursor Click on Turn 6 (activeStepIndex === 1) */}
          {activeStepIndex === 1 && (
            <div
              style={{
                position: "absolute",
                right: 20,
                top: 14,
                transform: `scale(${interpolate(age % 24, [0, 6, 12, 24], [1, 0.85, 1, 1])})`,
                pointerEvents: "none",
                filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.4))",
                zIndex: 10,
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#0F172A" stroke="#FFFFFF" strokeWidth="1.5">
                <path d="M4 3l13 8-7 2-3 7L4 3z" />
              </svg>
            </div>
          )}
        </div>

        {/* Content Body */}
        <div style={{ padding: "16px 24px", color: "#0F172A" }}>
          {cardData.subtitle && (
            <div
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: "#475569",
                marginBottom: 14,
                letterSpacing: "-0.2px",
              }}
            >
              {cardData.subtitle}
            </div>
          )}

          {type === "code" && cardData.codeSnippet ? (
            <div
              style={{
                backgroundColor: "#0F172A",
                borderRadius: 14,
                padding: "16px 20px",
                border: "1px solid rgba(15, 23, 42, 0.9)",
                fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
                fontSize: 17,
                lineHeight: 1.5,
                color: "#F8FAFC",
                whiteSpace: "pre-wrap",
                boxShadow: "inset 0 2px 6px rgba(0,0,0,0.5)",
              }}
            >
              {cardData.codeSnippet}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {items.map((item, idx) => {
                const isStepMode = activeStepIndex !== undefined;
                const isCurrent = isStepMode && idx === activeStepIndex;
                const isPast = isStepMode && idx < activeStepIndex;
                const isFuture = isStepMode && idx > activeStepIndex;
                const isPos = item.isPositive !== false;

                // Step-by-step interactive styling
                let rowBg = isPos ? "rgba(241, 245, 249, 0.95)" : "rgba(254, 242, 242, 0.95)";
                let rowBorder = isPos ? "1px solid rgba(203, 213, 225, 0.9)" : "1px solid rgba(252, 165, 165, 0.8)";
                let rowShadow = "none";
                let rowOpacity = 1.0;
                let badgeBg = isPos ? "#0F172A" : "#DC2626";
                let badgeText = item.badge || item.status || "VERIFIED";

                if (isCurrent) {
                  rowBg = "rgba(240, 249, 255, 0.98)";
                  rowBorder = "2px solid #0284C7";
                  rowShadow = "0 4px 18px rgba(2, 132, 199, 0.25), inset 0 0 12px rgba(56, 189, 248, 0.12)";
                  badgeBg = "#0284C7";
                  badgeText = item.status || "ACTIVE";
                } else if (isPast) {
                  rowBg = "rgba(240, 253, 244, 0.95)";
                  rowBorder = "1px solid rgba(134, 239, 172, 0.85)";
                  badgeBg = "#16A34A";
                  badgeText = "✓ CHECKED";
                } else if (isFuture) {
                  rowBg = "rgba(248, 250, 252, 0.65)";
                  rowBorder = "1px solid rgba(226, 232, 240, 0.6)";
                  rowOpacity = 0.55;
                  badgeBg = "#CBD5E1";
                  badgeText = "PENDING";
                }

                return (
                  <div
                    key={idx}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      backgroundColor: rowBg,
                      border: rowBorder,
                      borderRadius: 14,
                      padding: "10px 18px",
                      boxShadow: rowShadow,
                      opacity: rowOpacity,
                      transform: isCurrent ? "scale(1.015)" : "scale(1.0)",
                      transformOrigin: "center left",
                    }}
                  >
                    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        {isStepMode && (
                          <span
                            style={{
                              fontSize: 12,
                              fontWeight: 800,
                              color: isCurrent ? "#0284C7" : isPast ? "#16A34A" : "#94A3B8",
                              letterSpacing: "0.5px",
                            }}
                          >
                            STEP {idx + 1}
                          </span>
                        )}
                        <span style={{ fontSize: 13, fontWeight: 700, color: "#475569" }}>
                          {item.label}
                        </span>
                      </div>
                      <span
                        style={{
                          fontSize: 20,
                          fontWeight: 800,
                          color: isCurrent ? "#0284C7" : isPast ? "#14532D" : isPos ? "#0F172A" : "#B91C1C",
                          letterSpacing: "-0.5px",
                        }}
                      >
                        {renderHighlightedValue(item.value, isCurrent)}
                      </span>
                    </div>
                    <span
                      style={{
                        padding: "5px 12px",
                        borderRadius: 8,
                        fontSize: 11,
                        fontWeight: 800,
                        backgroundColor: badgeBg,
                        color: isFuture ? "#475569" : "#FFFFFF",
                        letterSpacing: "0.5px",
                        textTransform: "uppercase",
                      }}
                    >
                      {badgeText}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Bottom highlight pill */}
          {cardData.highlight && (
            <div
              style={{
                marginTop: 14,
                padding: "10px 16px",
                backgroundColor: "rgba(224, 242, 254, 0.85)",
                borderRadius: 12,
                border: "1px solid rgba(56, 189, 248, 0.5)",
                display: "flex",
                alignItems: "center",
                gap: 10,
                fontSize: 14,
                fontWeight: 700,
                color: "#0369A1",
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
