import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";

export interface ComparisonRow {
  feature: string;
  claude: string;
  claudeGood?: boolean;
  antigravity: string;
  antiGood?: boolean;
}

export interface ComparisonCard3DProps {
  isVisible?: boolean;
  startFrame?: number;
  endFrame?: number;
  title?: string;
  leftHeader?: string;
  rightHeader?: string;
  badge?: string;
  winner?: string;
  buttonText?: string;
  rows?: ComparisonRow[];
}

const DEFAULT_COMPARISON_ROWS: ComparisonRow[] = [
  {
    feature: "Cost / Month",
    claude: "$200+ / mo",
    claudeGood: false,
    antigravity: "$0 Free Tier",
    antiGood: true,
  },
  {
    feature: "Context Window",
    claude: "200,000 tokens",
    claudeGood: false,
    antigravity: "1,000,000 tokens",
    antiGood: true,
  },
  {
    feature: "Multi-Agent Autonomy",
    claude: "Single chat / Manual",
    claudeGood: false,
    antigravity: "Antigravity CLI (agy)",
    antiGood: true,
  },
  {
    feature: "Local Video Render",
    claude: "Not supported",
    claudeGood: false,
    antigravity: "Unlimited 9:16 Reels ($0)",
    antiGood: true,
  },
];

export const ComparisonCard3D: React.FC<ComparisonCard3DProps> = ({
  isVisible = true,
  startFrame = 75,
  endFrame = 900,
  title = "Tool Comparison • The Real Numbers",
  leftHeader = "Anthropic Claude",
  rightHeader = "Google Antigravity",
  badge = "$0 VERIFIED",
  winner = "Google Antigravity & Gemini 2.5 (100% Free Local Setup)",
  buttonText = "Run `agy` Free",
  rows,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // If outside time bounds or marked invisible, unmount cleanly
  if (!isVisible || frame < startFrame || frame > endFrame + 15) {
    return null;
  }

  // Smooth entrance pop starting exactly at startFrame
  const cardAge = Math.max(0, frame - startFrame);
  const entrance = spring({
    frame: cardAge,
    fps,
    config: { damping: 15, stiffness: 130 },
  });

  const scale = interpolate(entrance, [0, 1], [0.88, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Smooth entrance and exit opacity curve
  const entranceOpacity = interpolate(cardAge, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const exitOpacity = interpolate(frame, [endFrame - 15, endFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const overallOpacity = entranceOpacity * exitOpacity;

  if (overallOpacity <= 0.001) {
    return null;
  }

  // Sub-pixel floating motion
  const floatY = Math.sin(frame / 22) * 3.5;
  const comparisonRows = rows && rows.length > 0 ? rows : DEFAULT_COMPARISON_ROWS;

  return (
    <div
      style={{
        position: "absolute",
        left: 130,
        top: 240,
        width: 820,
        height: 620,
        backgroundColor: "rgba(11, 17, 30, 0.98)",
        borderRadius: 24,
        border: "1px solid rgba(255, 255, 255, 0.14)",
        boxShadow: "0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(56, 189, 248, 0.25)",
        overflow: "hidden",
        opacity: overallOpacity,
        transform: `translate3d(0, ${floatY}px, 0) scale(${scale})`,
        transformOrigin: "center center",
        zIndex: 50,
        fontFamily: "system-ui, -apple-system, sans-serif",
        backfaceVisibility: "hidden",
        WebkitFontSmoothing: "antialiased",
      }}
    >
      {/* 1. Window Header */}
      <div
        style={{
          height: 54,
          backgroundColor: "#161F30",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingLeft: 22,
          paddingRight: 22,
        }}
      >
        <div style={{ display: "flex", gap: 9 }}>
          <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#EF4444" }} />
          <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
          <div style={{ width: 13, height: 13, borderRadius: "50%", backgroundColor: "#10B981" }} />
        </div>

        <div style={{ color: "#E2E8F0", fontSize: 18, fontWeight: 700, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "#38BDF8" }}>✦</span>
          <span>{title}</span>
        </div>

        <div
          style={{
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            color: "#10B981",
            fontSize: 13,
            fontWeight: 800,
            padding: "4px 12px",
            borderRadius: 12,
            border: "1px solid rgba(16, 185, 129, 0.3)",
          }}
        >
          {badge}
        </div>
      </div>

      {/* 2. Side-By-Side Headers */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1.2fr 1fr 1.3fr",
          padding: "16px 24px 12px 24px",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          backgroundColor: "rgba(15, 23, 42, 0.6)",
        }}
      >
        <div style={{ color: "#94A3B8", fontSize: 15, fontWeight: 700, textTransform: "uppercase" }}>
          Feature
        </div>
        <div style={{ color: "#F87171", fontSize: 16, fontWeight: 800, textAlign: "center" }}>
          {leftHeader}
        </div>
        <div style={{ color: "#38BDF8", fontSize: 16, fontWeight: 800, textAlign: "center" }}>
          {rightHeader}
        </div>
      </div>

      {/* 3. Comparison Rows */}
      <div style={{ padding: "8px 24px", display: "flex", flexDirection: "column", gap: 10 }}>
        {comparisonRows.map((row, idx) => (
          <div
            key={idx}
            style={{
              display: "grid",
              gridTemplateColumns: "1.2fr 1fr 1.3fr",
              alignItems: "center",
              padding: "12px 14px",
              backgroundColor: idx % 2 === 0 ? "rgba(30, 41, 59, 0.4)" : "rgba(30, 41, 59, 0.2)",
              borderRadius: 12,
              border: "1px solid rgba(255, 255, 255, 0.04)",
            }}
          >
            <div style={{ color: "#F8FAFC", fontSize: 16, fontWeight: 600 }}>
              {row.feature}
            </div>

            <div style={{ textAlign: "center" }}>
              <span
                style={{
                  display: "inline-block",
                  padding: "4px 10px",
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 700,
                  backgroundColor: row.claudeGood ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)",
                  color: row.claudeGood ? "#34D399" : "#F87171",
                  border: row.claudeGood ? "1px solid rgba(16, 185, 129, 0.3)" : "1px solid rgba(239, 68, 68, 0.3)",
                }}
              >
                {row.claude}
              </span>
            </div>

            <div style={{ textAlign: "center" }}>
              <span
                style={{
                  display: "inline-block",
                  padding: "4px 12px",
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: 800,
                  backgroundColor: "rgba(56, 189, 248, 0.2)",
                  color: "#38BDF8",
                  border: "1px solid rgba(56, 189, 248, 0.4)",
                  boxShadow: "0 0 12px rgba(56, 189, 248, 0.2)",
                }}
              >
                {row.antigravity}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* 4. Footer Verdict Bar */}
      <div
        style={{
          marginTop: 10,
          padding: "14px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#0B1120",
          borderTop: "1px solid rgba(255, 255, 255, 0.08)",
        }}
      >
        <div style={{ color: "#94A3B8", fontSize: 15, fontWeight: 500 }}>
          {winner}
        </div>

        <div
          style={{
            background: "linear-gradient(135deg, #0284C7 0%, #2563EB 100%)",
            color: "#FFFFFF",
            fontSize: 14,
            fontWeight: 800,
            padding: "8px 18px",
            borderRadius: 10,
            boxShadow: "0 4px 12px rgba(2, 132, 199, 0.4)",
          }}
        >
          {buttonText}
        </div>
      </div>
    </div>
  );
};
