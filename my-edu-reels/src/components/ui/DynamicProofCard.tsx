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
  type?: "code" | "benchmark" | "comparison" | "alert" | "proof_card";
  codeSnippet?: string;
  language?: string;
  searchQuery?: string;
  command?: string;
  items?: CardProofItem[];
  rows?: CardProofItem[];
  highlight?: string;
  topicLogoPath?: string;
  logoPath?: string;
  proofImagePath?: string;
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
  logoPath?: string;
  proofImagePath?: string;
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
 * - Sleek dark-mode 2.5D full-screen visual proof cutaway (2.5–4s duration).
 * - Replaces the tiny white macOS terminal box.
 * - Displays the real logoPath + proofImagePath (GitHub card or live site screenshot)
 *   with bold kinetic badge ("100% FREE") and animated highlight callout.
 */
export const DynamicProofCard: React.FC<DynamicProofCardProps> = ({
  cardData,
  startFrame = 90,
  durationFrames = 105, // default 3.5s @ 30fps
  activeStepIndex = 0,
  topicLogoPath,
  logoPath,
  proofImagePath,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!cardData) return null;

  const effectiveLogo = logoPath || topicLogoPath || cardData.logoPath || cardData.topicLogoPath;
  const effectiveProofImage = proofImagePath || cardData.proofImagePath;

  // Enforce 2.5s – 4.0s duration (75 to 120 frames @ 30fps)
  const effectiveStart = cardData.startFrame ?? startFrame;
  const rawDuration =
    durationFrames ??
    (cardData.durationSeconds
      ? Math.round(cardData.durationSeconds * fps)
      : cardData.durationFrames ?? 105);
  const cutawayDuration = Math.min(Math.max(rawDuration, 75), 120);
  const effectiveEnd = effectiveStart + cutawayDuration;

  // Visibility window check
  if (frame < effectiveStart || frame > effectiveEnd) {
    return null;
  }

  const age = frame - effectiveStart;
  const exitAge = effectiveEnd - frame;

  // Spring entrance & exit interpolations
  const entrance = spring({
    frame: Math.min(age, 22),
    fps,
    config: { damping: 14, stiffness: 140, mass: 0.8 },
  });

  const exitOpacity = interpolate(exitAge, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitScale = interpolate(exitAge, [0, 10], [0.95, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = entrance * exitOpacity;
  const scale = interpolate(entrance, [0, 1], [0.88, 1.0]) * exitScale;
  const translateY = interpolate(entrance, [0, 1], [50, 0]);

  // 2.5D subtle camera perspective tilt
  const tiltX = interpolate(entrance, [0, 1], [6, 2]);
  const subtleFloatY = Math.sin(age * 0.08) * 4;

  const isComedy =
    cardData.badge === "FACT CHECK" ||
    cardData.badge === "COMEDY" ||
    cardData.badge === "DAD TECH AUDIT" ||
    /dad/i.test(cardData.title || "") ||
    /dad/i.test(cardData.subtitle || "") ||
    /wifi/i.test(cardData.title || "");

  // Kinetic pulse for the proof badge
  const badgePulse = 1.0 + 0.05 * Math.sin(age * 0.22);

  // Fallback rows if no screenshot proof card
  const rawItems = cardData.rows || cardData.items;
  let items: CardProofItem[] = [];
  if (rawItems && Array.isArray(rawItems) && rawItems.length > 0) {
    items = rawItems.map((it) => {
      if (isComedy && it.value && typeof it.value === "string") {
        return {
          ...it,
          value: it.value
            .replace(/\$50\/mo/gi, "₹999/mo")
            .replace(/\$100 technician/gi, "₹999 router technician")
            .replace(/\$150 ISP/gi, "₹999 ISP"),
        };
      }
      return it;
    });
  } else {
    items = isComedy
      ? [
          { label: "Wi-Fi Bill Audit", value: "Standard ₹999/mo ISP Charge", badge: "AUDIT", isPositive: false },
          { label: "Hardware Reset", value: "Zero Aluminum Foil Required", badge: "FACT", isPositive: true },
          { label: "Final Outcome", value: "Wi-Fi Restored • Monthly Bill: ₹0", badge: "VERIFIED", isPositive: true },
        ]
      : [
          { label: "Execution Environment", value: "Browser WebAssembly / Native", badge: "VERIFIED", isPositive: true },
          { label: "Access & Pricing", value: "Zero Cost / 100% Free", badge: "FREE", isPositive: true },
          { label: "Setup Time", value: "Instant 0s Local Config", badge: "FAST", isPositive: true },
        ];
  }

  const title = cardData.title
    ? cleanTitleTruncation(cardData.title, 34)
    : (isComedy ? "FACT CHECK BREAKDOWN" : "VERIFIED REAL PROOF");
  const subtitle = cardData.subtitle
    ? cleanTitleTruncation(cardData.subtitle, 48)
    : (isComedy ? "Verified Reality Check & Tech Audit" : "Live Execution & Feature Inspection");
  const highlightText =
    cardData.highlight ||
    (isComedy
      ? "⚡ Real Relatable Tech Breakdown • Zero Hidden Fees"
      : "⚡ 100% Free • Verified Zero Local Installation • Instant Access");

  return (
    <div
      style={{
        position: "absolute",
        top: 240,
        left: 60,
        width: 960,
        zIndex: 95,
        opacity,
        transform: `perspective(1200px) rotateX(${tiltX}deg) translateY(${translateY + subtleFloatY}px) scale(${scale})`,
        transformOrigin: "center center",
        pointerEvents: "none",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* 2.5D Glassmorphism Container */}
      <div
        style={{
          background: "linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(10, 15, 28, 0.98) 100%)",
          backdropFilter: "blur(28px)",
          borderRadius: 28,
          border: "2px solid rgba(56, 189, 248, 0.55)",
          boxShadow:
            "0 36px 90px rgba(0, 0, 0, 0.88), 0 0 50px rgba(56, 189, 248, 0.28), inset 0 1px 2px rgba(255, 255, 255, 0.15)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Header Bar */}
        <div
          style={{
            height: 72,
            backgroundColor: "rgba(30, 41, 59, 0.85)",
            borderBottom: "1px solid rgba(56, 189, 248, 0.25)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 28px",
          }}
        >
          {/* Left: Logo & Title */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            {effectiveLogo ? (
              <Img
                src={staticFile(effectiveLogo)}
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  objectFit: "contain",
                  backgroundColor: "#0F172A",
                  padding: 4,
                  border: "1px solid rgba(56, 189, 248, 0.4)",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.5)",
                }}
              />
            ) : (
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  backgroundColor: "#0284C7",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 22,
                }}
              >
                ⚡
              </div>
            )}
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span
                style={{
                  fontSize: 20,
                  fontWeight: 900,
                  color: "#F8FAFC",
                  letterSpacing: "0.5px",
                  textTransform: "uppercase",
                }}
              >
                {title}
              </span>
              <span
                style={{
                  fontSize: 13,
                  fontWeight: 600,
                  color: "#94A3B8",
                  letterSpacing: "0.2px",
                }}
              >
                {subtitle}
              </span>
            </div>
          </div>

          {/* Right: Bold Kinetic Proof Badge (Clean comedy / fact-check header or 100% FREE) */}
          <div
            style={{
              backgroundColor: isComedy ? "#D97706" : "#059669",
              color: "#FFFFFF",
              padding: "8px 20px",
              borderRadius: 9999,
              fontSize: 15,
              fontWeight: 900,
              letterSpacing: "1.0px",
              textTransform: "uppercase",
              boxShadow: isComedy
                ? "0 0 20px rgba(245, 158, 11, 0.7), 0 4px 12px rgba(0, 0, 0, 0.5)"
                : "0 0 20px rgba(16, 185, 129, 0.7), 0 4px 12px rgba(0, 0, 0, 0.5)",
              border: isComedy
                ? "1px solid rgba(251, 191, 36, 0.8)"
                : "1px solid rgba(52, 211, 153, 0.8)",
              transform: `scale(${badgePulse})`,
              transformOrigin: "center",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <span>✓</span>
            <span>{isComedy ? (cardData.badge || "FACT CHECK") : "100% FREE"}</span>
          </div>
        </div>

        {/* Center: Real Visual Proof Display */}
        <div style={{ padding: "24px 28px 16px 28px" }}>
          {effectiveProofImage ? (
            /* Real Screenshot / GitHub OpenGraph Visual Proof Card */
            <div
              style={{
                position: "relative",
                width: "100%",
                height: 380,
                borderRadius: 18,
                overflow: "hidden",
                border: "2px solid rgba(56, 189, 248, 0.35)",
                boxShadow: "0 12px 36px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 0, 0, 0.4)",
                backgroundColor: "#020617",
              }}
            >
              <Img
                src={staticFile(effectiveProofImage)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }}
              />
              {/* Corner Live Proof Badge */}
              <div
                style={{
                  position: "absolute",
                  top: 14,
                  right: 14,
                  backgroundColor: "rgba(15, 23, 42, 0.90)",
                  border: "1px solid rgba(56, 189, 248, 0.6)",
                  padding: "5px 14px",
                  borderRadius: 8,
                  fontSize: 12,
                  fontWeight: 800,
                  color: "#38BDF8",
                  letterSpacing: "0.5px",
                  backdropFilter: "blur(8px)",
                }}
              >
                LIVE VERIFIED PROOF
              </div>
            </div>
          ) : (
            /* High-Contrast Interactive 3-Step Spec Rows */
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {items.slice(0, 3).map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    backgroundColor: "rgba(30, 41, 59, 0.75)",
                    border: "1px solid rgba(56, 189, 248, 0.3)",
                    borderRadius: 14,
                    padding: "16px 22px",
                    boxShadow: "0 4px 14px rgba(0, 0, 0, 0.4)",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div
                      style={{
                        width: 28,
                        height: 28,
                        borderRadius: 8,
                        backgroundColor: "#0284C7",
                        color: "#FFFFFF",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: 14,
                        fontWeight: 900,
                      }}
                    >
                      {idx + 1}
                    </div>
                    <span style={{ fontSize: 16, fontWeight: 700, color: "#E2E8F0" }}>
                      {item.label}
                    </span>
                  </div>
                  <div
                    style={{
                      backgroundColor: "#0F172A",
                      border: "1px solid rgba(56, 189, 248, 0.4)",
                      color: "#38BDF8",
                      padding: "6px 16px",
                      borderRadius: 8,
                      fontSize: 14,
                      fontWeight: 800,
                    }}
                  >
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bottom Animated Highlight Callout Banner */}
        <div
          style={{
            margin: "0 28px 24px 28px",
            padding: "14px 20px",
            borderRadius: 14,
            backgroundColor: "rgba(56, 189, 248, 0.12)",
            border: "1px solid rgba(56, 189, 248, 0.45)",
            boxShadow: "0 4px 20px rgba(56, 189, 248, 0.15)",
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span style={{ fontSize: 18 }}>💡</span>
          <span
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: "#E0F2FE",
              letterSpacing: "0.2px",
            }}
          >
            {highlightText}
          </span>
        </div>
      </div>
    </div>
  );
};
export default DynamicProofCard;
