import React from "react";
import { useCurrentFrame, spring, useVideoConfig } from "remotion";

interface DesktopExplainerCardProps {
  isVisible: boolean;
  title?: string;
  badge?: string;
}

export const DesktopExplainerCard: React.FC<DesktopExplainerCardProps> = ({
  isVisible,
  title = "Google Antigravity • your 90-day path",
  badge = "most are free",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance pop-in (deterministic without modulo reset)
  const scale = spring({
    frame: isVisible ? Math.min(frame, 30) : 0,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Floating gentle bob
  const floatY = Math.sin(frame / 20) * 6;

  if (!isVisible) return null;

  const steps = [
    { num: "01", name: "Google Antigravity CLI", desc: "Local autonomous multi-agent dev tool", done: true },
    { num: "02", name: "Gemini 2.5 Flash API", desc: "1M token context & multimodal reasoning", done: true },
    { num: "03", name: "Remotion React Video", desc: "Local 1080x1920 60fps render pipeline", done: true },
    { num: "04", name: "Neural Multi-TTS", desc: "Edge-TTS zero-cost voice & synced subtitles", done: true },
    { num: "05", name: "Deploy Real Agent", desc: "Automate phone orders for a local business", done: false },
  ];

  return (
    <div
      style={{
        position: "absolute",
        left: 170,
        top: 340 + floatY,
        width: 740,
        height: 740,
        backgroundColor: "rgba(13, 19, 31, 0.94)",
        backdropFilter: "blur(16px)",
        borderRadius: 24,
        border: "1px solid rgba(255, 255, 255, 0.14)",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.85), 0 0 40px rgba(14, 165, 233, 0.22)",
        overflow: "hidden",
        transform: `scale(${scale})`,
        transformOrigin: "center center",
        zIndex: 40,
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* ======================================================== */}
      {/* 1. MACOS STYLE TITLE BAR                                 */}
      {/* ======================================================== */}
      <div
        style={{
          height: 60,
          backgroundColor: "#161F30",
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingLeft: 24,
          paddingRight: 24,
        }}
      >
        {/* macOS Traffic Lights */}
        <div style={{ display: "flex", gap: 10 }}>
          <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#EF4444" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#F59E0B" }} />
          <div style={{ width: 14, height: 14, borderRadius: "50%", backgroundColor: "#10B981" }} />
        </div>

        {/* Title */}
        <div
          style={{
            color: "#E2E8F0",
            fontSize: 20,
            fontWeight: 600,
            display: "flex",
            alignItems: "center",
            gap: 10,
          }}
        >
          <span style={{ color: "#38BDF8" }}>✦</span>
          <span>{title}</span>
        </div>

        {/* Top Right Mini Badge */}
        <div
          style={{
            backgroundColor: "rgba(56, 189, 248, 0.15)",
            color: "#38BDF8",
            fontSize: 14,
            fontWeight: 700,
            padding: "4px 12px",
            borderRadius: 12,
            border: "1px solid rgba(56, 189, 248, 0.3)",
          }}
        >
          $0 TOOLCHAIN
        </div>
      </div>

      {/* ======================================================== */}
      {/* 2. CARD HEADER SECTION                                   */}
      {/* ======================================================== */}
      <div style={{ padding: "18px 24px 10px 24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <h2
            style={{
              margin: 0,
              color: "#FFFFFF",
              fontSize: 34,
              fontWeight: 800,
              letterSpacing: "-0.02em",
            }}
          >
            5 things.
          </h2>
          <div
            style={{
              backgroundColor: "#FACC15",
              color: "#713F12",
              fontSize: 15,
              fontWeight: 800,
              padding: "4px 14px",
              borderRadius: 20,
              textTransform: "lowercase",
            }}
          >
            {badge}
          </div>
        </div>
        <p
          style={{
            margin: "6px 0 0 0",
            color: "#94A3B8",
            fontSize: 16,
            fontWeight: 500,
          }}
        >
          One hour a day for 90 days to master autonomous AI engineering.
        </p>
      </div>

      {/* ======================================================== */}
      {/* 3. STEPS ROADMAP ACCORDION CARDS                         */}
      {/* ======================================================== */}
      <div style={{ padding: "0 24px", display: "flex", flexDirection: "column", gap: 8 }}>
        {steps.map((s, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              backgroundColor: s.done ? "rgba(30, 41, 59, 0.7)" : "rgba(30, 41, 59, 0.4)",
              borderRadius: 12,
              padding: "10px 16px",
              border: s.done
                ? "1px solid rgba(56, 189, 248, 0.35)"
                : "1px solid rgba(255, 255, 255, 0.05)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  backgroundColor: s.done ? "#0284C7" : "#334155",
                  color: "#FFFFFF",
                  fontSize: 14,
                  fontWeight: 800,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {s.done ? "✓" : s.num}
              </div>
              <div>
                <div style={{ color: "#F8FAFC", fontSize: 17, fontWeight: 700 }}>
                  {s.name}
                </div>
                <div style={{ color: "#94A3B8", fontSize: 13, marginTop: 1 }}>
                  {s.desc}
                </div>
              </div>
            </div>

            <div
              style={{
                fontSize: 12,
                fontWeight: 700,
                color: s.done ? "#38BDF8" : "#E2E8F0",
                backgroundColor: s.done ? "rgba(56, 189, 248, 0.12)" : "rgba(255, 255, 255, 0.08)",
                padding: "4px 10px",
                borderRadius: 8,
              }}
            >
              {s.done ? "READY" : "BUILD"}
            </div>
          </div>
        ))}
      </div>

      {/* ======================================================== */}
      {/* 4. FOOTER ACTION BAR                                     */}
      {/* ======================================================== */}
      <div
        style={{
          marginTop: 14,
          padding: "12px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#111827",
          borderTop: "1px solid rgba(255, 255, 255, 0.06)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ color: "#38BDF8", fontSize: 20, fontWeight: 800 }}>
            80%
          </div>
          <div
            style={{
              width: 180,
              height: 8,
              backgroundColor: "#1E293B",
              borderRadius: 6,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: "80%",
                height: "100%",
                background: "linear-gradient(90deg, #0284C7, #38BDF8)",
              }}
            />
          </div>
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <div
            style={{
              background: "linear-gradient(135deg, #0284C7 0%, #2563EB 100%)",
              color: "#FFFFFF",
              fontSize: 15,
              fontWeight: 700,
              padding: "8px 20px",
              borderRadius: 10,
              boxShadow: "0 4px 14px rgba(2, 132, 199, 0.4)",
            }}
          >
            Start Building
          </div>
        </div>
      </div>
    </div>
  );
};
