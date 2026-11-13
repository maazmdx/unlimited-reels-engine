import React from "react";
import { useCurrentFrame, spring, useVideoConfig } from "remotion";

interface ComparisonCard3DProps {
  isVisible: boolean;
  title?: string;
}

export const ComparisonCard3D: React.FC<ComparisonCard3DProps> = ({
  isVisible,
  title = "Tool Comparison • The Real Numbers",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth entrance pop
  const cardFrame = Math.max(0, frame - 70);
  const scale = spring({
    frame: cardFrame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  const floatY = Math.sin(frame / 20) * 4;

  if (!isVisible || scale < 0.01) return null;

  const comparisonRows = [
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

  return (
    <div
      style={{
        position: "absolute",
        left: 130,
        top: 240 + floatY,
        width: 820,
        height: 620,
        backgroundColor: "rgba(12, 17, 29, 0.96)",
        backdropFilter: "blur(20px)",
        borderRadius: 24,
        border: "1px solid rgba(255, 255, 255, 0.14)",
        boxShadow: "0 25px 60px -15px rgba(0, 0, 0, 0.9), 0 0 40px rgba(56, 189, 248, 0.25)",
        overflow: "hidden",
        transform: `scale(${scale})`,
        transformOrigin: "center center",
        zIndex: 45,
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* ======================================================== */}
      {/* 1. MACOS TITLE BAR                                       */}
      {/* ======================================================== */}
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
          $0 VERIFIED
        </div>
      </div>

      {/* ======================================================== */}
      {/* 2. SIDE-BY-SIDE HEADERS                                  */}
      {/* ======================================================== */}
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
          Anthropic Claude
        </div>
        <div style={{ color: "#38BDF8", fontSize: 16, fontWeight: 800, textAlign: "center" }}>
          Google Antigravity
        </div>
      </div>

      {/* ======================================================== */}
      {/* 3. COMPARISON ROWS                                       */}
      {/* ======================================================== */}
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

      {/* ======================================================== */}
      {/* 4. FOOTER VERDICT BAR                                    */}
      {/* ======================================================== */}
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
          Winner: <strong style={{ color: "#38BDF8" }}>Google Antigravity & Gemini 2.5</strong> (100% Free Local Setup)
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
          Run `agy` Free
        </div>
      </div>
    </div>
  );
};
