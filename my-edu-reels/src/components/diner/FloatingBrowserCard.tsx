import React from "react";
import { useCurrentFrame, spring, interpolate, useVideoConfig } from "remotion";

export type CardContentType =
  | "job_posting"
  | "rejection"
  | "aws_bill"
  | "tweet_thread"
  | "vibe_coder"
  | "retention_trap"
  | "comparison";

export interface FloatingBrowserCardProps {
  isVisible?: boolean;
  startFrame?: number;
  endFrame?: number;
  contentType?: CardContentType;
  url?: string;
  badge?: string;
  title?: string;
  data?: Record<string, any>;
}

export const FloatingBrowserCard: React.FC<FloatingBrowserCardProps> = ({
  isVisible = true,
  startFrame = 75,
  endFrame = 900,
  contentType = "job_posting",
  url = "job-boards.greenhouse.io/anthropic/fellowship",
  badge = "REAL JOB BOARD",
  title = "Anthropic • Research Fellow",
  data = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!isVisible || frame < startFrame || frame > endFrame + 15) {
    return null;
  }

  // Smooth entrance spring
  const cardAge = Math.max(0, frame - startFrame);
  const entrance = spring({
    frame: cardAge,
    fps,
    config: { damping: 15, stiffness: 125, mass: 0.8 },
  });

  const scale = interpolate(entrance, [0, 1], [0.86, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Micro-floating bob
  const floatY = Math.sin(frame * 0.04) * 6;

  // Entrance & Exit opacity
  const enterOpacity = interpolate(cardAge, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitOpacity = interpolate(frame, [endFrame - 15, endFrame], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = enterOpacity * exitOpacity;

  return (
    <div
      style={{
        position: "absolute",
        top: 280 + floatY,
        left: 120,
        width: 840,
        backgroundColor: "rgba(15, 23, 42, 0.96)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderRadius: 24,
        border: "1.5px solid rgba(255, 255, 255, 0.16)",
        boxShadow:
          "0 32px 80px rgba(0, 0, 0, 0.90), 0 0 50px rgba(56, 189, 248, 0.20)",
        overflow: "hidden",
        transform: `scale(${scale})`,
        transformOrigin: "center top",
        opacity,
        zIndex: 50,
        fontFamily:
          "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      {/* ======================================================== */}
      {/* 1. macOS Style Browser Title Bar with Traffic Lights     */}
      {/* ======================================================== */}
      <div
        style={{
          height: 64,
          backgroundColor: "#1E293B",
          borderBottom: "1px solid rgba(255, 255, 255, 0.10)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          paddingLeft: 24,
          paddingRight: 24,
        }}
      >
        {/* Traffic Light Buttons */}
        <div style={{ display: "flex", gap: 9 }}>
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: "#EF4444",
              boxShadow: "0 0 8px rgba(239, 68, 68, 0.6)",
            }}
          />
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: "#F59E0B",
              boxShadow: "0 0 8px rgba(245, 158, 11, 0.6)",
            }}
          />
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              backgroundColor: "#10B981",
              boxShadow: "0 0 8px rgba(16, 185, 129, 0.6)",
            }}
          />
        </div>

        {/* macOS Search / URL Pill */}
        <div
          style={{
            backgroundColor: "rgba(15, 23, 42, 0.8)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            borderRadius: 12,
            padding: "6px 20px",
            display: "flex",
            alignItems: "center",
            gap: 10,
            maxWidth: 500,
          }}
        >
          <span style={{ fontSize: 13, color: "#94A3B8" }}>🔒</span>
          <span
            style={{
              fontSize: 15,
              fontWeight: 500,
              color: "#E2E8F0",
              letterSpacing: "0.02em",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {url}
          </span>
        </div>

        {/* Category Pill */}
        <div
          style={{
            backgroundColor: "rgba(56, 189, 248, 0.18)",
            color: "#38BDF8",
            border: "1px solid rgba(56, 189, 248, 0.4)",
            borderRadius: 12,
            padding: "5px 14px",
            fontSize: 13,
            fontWeight: 700,
            letterSpacing: "0.05em",
            textTransform: "uppercase",
          }}
        >
          {badge}
        </div>
      </div>

      {/* ======================================================== */}
      {/* 2. Realistic Comedic Content Body                        */}
      {/* ======================================================== */}
      <div style={{ padding: "28px 32px" }}>
        {contentType === "job_posting" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div>
                <span style={{ color: "#D97706", fontSize: 15, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  {data.company || "Anthropic • San Francisco, CA"}
                </span>
                <h2 style={{ color: "#F8FAFC", fontSize: 30, fontWeight: 800, margin: "6px 0 0 0", lineHeight: 1.2 }}>
                  {data.role || "Research Fellow • Alignment"}
                </h2>
              </div>
              <div
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.18)",
                  border: "1.5px solid #10B981",
                  borderRadius: 16,
                  padding: "10px 18px",
                  textAlign: "right",
                }}
              >
                <div style={{ color: "#10B981", fontSize: 26, fontWeight: 900 }}>
                  {data.salary || "$3,850 / wk"}
                </div>
                <div style={{ color: "#94A3B8", fontSize: 13, fontWeight: 600 }}>($200,200 / yr stipend)</div>
              </div>
            </div>

            {/* Requirement Highlight Box */}
            <div
              style={{
                backgroundColor: "rgba(245, 158, 11, 0.12)",
                border: "1px dashed rgba(245, 158, 11, 0.5)",
                borderRadius: 14,
                padding: "14px 20px",
                marginBottom: 20,
              }}
            >
              <div style={{ color: "#FBBF24", fontSize: 15, fontWeight: 700, marginBottom: 4 }}>
                ⚡ OFFICIAL REQUIREMENT NOTICE:
              </div>
              <div style={{ color: "#F1F5F9", fontSize: 16, fontWeight: 500, lineHeight: 1.4 }}>
                "{data.clause || "Regardless of previous experience in computer science, machine learning, or research."}"
              </div>
            </div>

            {/* Application Checklist */}
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#E2E8F0", fontSize: 16 }}>
                <span style={{ color: "#10B981", fontSize: 20 }}>✓</span>
                <span>Copy research page into AI & pick 1 weekend experiment</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#E2E8F0", fontSize: 16 }}>
                <span style={{ color: "#10B981", fontSize: 20 }}>✓</span>
                <span>Run free Google Colab GPU (Zero hardware dollars)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#F59E0B", fontSize: 16 }}>
                <span style={{ color: "#F59E0B", fontSize: 20 }}>🦉</span>
                <span>Taught an AI to love owls with numbers (Got hired)</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, color: "#EF4444", fontSize: 16 }}>
                <span style={{ color: "#EF4444", fontSize: 20 }}>✕</span>
                <span>Do NOT send standard 2-page PDF resume</span>
              </div>
            </div>
          </div>
        )}

        {contentType === "rejection" && (
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18 }}>
              <div
                style={{
                  width: 46,
                  height: 46,
                  borderRadius: 12,
                  backgroundColor: "rgba(239, 68, 68, 0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 24,
                }}
              >
                📬
              </div>
              <div>
                <div style={{ color: "#94A3B8", fontSize: 14 }}>From: Greenhouse Automated Talent System</div>
                <div style={{ color: "#F8FAFC", fontSize: 20, fontWeight: 700 }}>
                  Update on your application: Candidate #101
                </div>
              </div>
            </div>

            <div
              style={{
                backgroundColor: "rgba(15, 23, 42, 0.7)",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                borderRadius: 16,
                padding: "20px 24px",
                color: "#E2E8F0",
                fontSize: 16,
                lineHeight: 1.6,
                marginBottom: 20,
              }}
            >
              "Dear Candidate, Thank you for completing all <strong>4 technical rounds</strong>. While the team was impressed by your inverted binary tree, we have decided to move forward with another candidate who <strong>never even submitted an application</strong> because he messaged our VP on X at 2:00 AM."
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", color: "#94A3B8", fontSize: 14 }}>
              <span>Total Applicants: 100</span>
              <span style={{ color: "#EF4444", fontWeight: 700 }}>Your Position: 101st</span>
            </div>
          </div>
        )}

        {contentType === "aws_bill" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div>
                <span style={{ color: "#EF4444", fontSize: 14, fontWeight: 700, letterSpacing: "0.08em" }}>
                  ⚠️ AWS CLOUDWATCH CRITICAL ALARM
                </span>
                <h2 style={{ color: "#F8FAFC", fontSize: 28, fontWeight: 800, margin: "6px 0 0 0" }}>
                  Account #9842 • 72-Hour Billing Spike
                </h2>
              </div>
              <div
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.2)",
                  border: "2px solid #EF4444",
                  borderRadius: 16,
                  padding: "10px 20px",
                  textAlign: "right",
                }}
              >
                <div style={{ color: "#EF4444", fontSize: 32, fontWeight: 900 }}>
                  $14,892.41
                </div>
                <div style={{ color: "#FCA5A5", fontSize: 13, fontWeight: 600 }}>Auto-charge in 4 hours</div>
              </div>
            </div>

            {/* Bill Line Items */}
            <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 14, padding: "16px 20px", marginBottom: 16 }}>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", color: "#E2E8F0", fontSize: 15 }}>
                <span>p4d.24xlarge (Left running over weekend)</span>
                <span style={{ fontWeight: 700, color: "#EF4444" }}>$12,410.00</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid rgba(255,255,255,0.06)", color: "#E2E8F0", fontSize: 15 }}>
                <span>Lambda infinite while loop (3.8M invocations)</span>
                <span style={{ fontWeight: 700, color: "#EF4444" }}>$2,482.15</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", color: "#94A3B8", fontSize: 15 }}>
                <span>Your Bank Account Balance</span>
                <span style={{ fontWeight: 700, color: "#10B981" }}>$14.20</span>
              </div>
            </div>

            <div style={{ color: "#F59E0B", fontSize: 14, fontWeight: 600, textAlign: "center" }}>
              Dad's reaction: "Turn off the hall light! You gave $14,000 to Jeff Bezos?!"
            </div>
          </div>
        )}

        {contentType === "vibe_coder" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
              <div>
                <span style={{ color: "#38BDF8", fontSize: 14, fontWeight: 700, letterSpacing: "0.08em" }}>
                  NATURAL HABITAT SPECIMEN #0492
                </span>
                <h2 style={{ color: "#F8FAFC", fontSize: 28, fontWeight: 800, margin: "4px 0 0 0" }}>
                  Homo Promptus • "The Vibe Coder"
                </h2>
              </div>
              <div style={{ backgroundColor: "rgba(56, 189, 248, 0.2)", borderRadius: 12, padding: "8px 16px", color: "#38BDF8", fontWeight: 800 }}>
                CRITICALLY NOCTURNAL
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 18 }}>
              <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 12, padding: "14px 18px" }}>
                <div style={{ color: "#94A3B8", fontSize: 13 }}>HABITAT</div>
                <div style={{ color: "#F1F5F9", fontSize: 16, fontWeight: 700, marginTop: 4 }}>
                  Dark bedroom, IDE blue glow
                </div>
              </div>
              <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 12, padding: "14px 18px" }}>
                <div style={{ color: "#94A3B8", fontSize: 13 }}>DIET</div>
                <div style={{ color: "#F1F5F9", fontSize: 16, fontWeight: 700, marginTop: 4 }}>
                  Cold pizza, caffeine, rate limits
                </div>
              </div>
              <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 12, padding: "14px 18px" }}>
                <div style={{ color: "#94A3B8", fontSize: 13 }}>11:00 PM PROMPT</div>
                <div style={{ color: "#10B981", fontSize: 15, fontWeight: 600, marginTop: 4 }}>
                  "Please kindly refactor this function"
                </div>
              </div>
              <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 12, padding: "14px 18px" }}>
                <div style={{ color: "#94A3B8", fontSize: 13 }}>3:00 AM PROMPT</div>
                <div style={{ color: "#EF4444", fontSize: 16, fontWeight: 800, marginTop: 4 }}>
                  "FIX IT."
                </div>
              </div>
            </div>

            <div style={{ backgroundColor: "rgba(239, 68, 68, 0.15)", border: "1px solid #EF4444", borderRadius: 12, padding: "12px 18px", color: "#FCA5A5", fontSize: 14, fontWeight: 600, textAlign: "center" }}>
              APEX PREDATOR: Tuesday Weekly Token Quota Cap
            </div>
          </div>
        )}

        {contentType === "retention_trap" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div>
                <span style={{ color: "#38BDF8", fontSize: 14, fontWeight: 700, letterSpacing: "0.08em" }}>
                  AUDIENCE RETENTION ANALYTICS
                </span>
                <h2 style={{ color: "#F8FAFC", fontSize: 28, fontWeight: 800, margin: "6px 0 0 0" }}>
                  "80% Left in 3 Seconds"
                </h2>
              </div>
              <div
                style={{
                  backgroundColor: "rgba(16, 185, 129, 0.2)",
                  border: "1.5px solid #10B981",
                  borderRadius: 16,
                  padding: "10px 18px",
                  textAlign: "right",
                }}
              >
                <div style={{ color: "#10B981", fontSize: 24, fontWeight: 900 }}>
                  100% AUTOMATED
                </div>
                <div style={{ color: "#94A3B8", fontSize: 13 }}>Three.js + Edge-TTS</div>
              </div>
            </div>

            <div style={{ backgroundColor: "rgba(15, 23, 42, 0.8)", borderRadius: 14, padding: "18px 22px", marginBottom: 18 }}>
              <div style={{ color: "#94A3B8", fontSize: 14, marginBottom: 8 }}>Tech Stack ($0 Cloud Cost):</div>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <span style={{ backgroundColor: "#1E293B", padding: "6px 14px", borderRadius: 8, color: "#38BDF8", fontWeight: 700, fontSize: 14 }}>Three.js 3D Diner</span>
                <span style={{ backgroundColor: "#1E293B", padding: "6px 14px", borderRadius: 8, color: "#34D399", fontWeight: 700, fontSize: 14 }}>Edge-TTS Neural Voice</span>
                <span style={{ backgroundColor: "#1E293B", padding: "6px 14px", borderRadius: 8, color: "#F59E0B", fontWeight: 700, fontSize: 14 }}>Remotion React Video</span>
                <span style={{ backgroundColor: "#1E293B", padding: "6px 14px", borderRadius: 8, color: "#E2E8F0", fontWeight: 700, fontSize: 14 }}>GitHub Cloud ($0 CI)</span>
              </div>
            </div>

            <div style={{ color: "#38BDF8", fontSize: 16, fontWeight: 700, textAlign: "center" }}>
              ✨ "And you're still watching."
            </div>
          </div>
        )}

        {contentType === "comparison" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
              <div style={{ color: "#F8FAFC", fontSize: 24, fontWeight: 800 }}>
                {title || "Benchmark Showdown"}
              </div>
              <div style={{ backgroundColor: "rgba(56, 189, 248, 0.2)", borderRadius: 12, padding: "6px 14px", color: "#38BDF8", fontSize: 13, fontWeight: 700 }}>
                100% UNBIASED
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", padding: "10px 14px", backgroundColor: "rgba(15, 23, 42, 0.9)", borderRadius: 10, color: "#E2E8F0", fontSize: 14, fontWeight: 600 }}>
                <span>METRIC</span>
                <span style={{ color: "#D97706" }}>CLAUDE</span>
                <span style={{ color: "#38BDF8" }}>ANTIGRAVITY</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", padding: "10px 14px", backgroundColor: "rgba(15, 23, 42, 0.5)", borderRadius: 10, color: "#F1F5F9", fontSize: 14 }}>
                <span>Monthly Cost</span>
                <span style={{ color: "#EF4444", fontWeight: 700 }}>$200 / mo</span>
                <span style={{ color: "#10B981", fontWeight: 700 }}>$0 Free Tier</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", padding: "10px 14px", backgroundColor: "rgba(15, 23, 42, 0.5)", borderRadius: 10, color: "#F1F5F9", fontSize: 14 }}>
                <span>Context Window</span>
                <span style={{ color: "#94A3B8" }}>200k tokens</span>
                <span style={{ color: "#10B981", fontWeight: 700 }}>1,000,000 tokens</span>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", padding: "10px 14px", backgroundColor: "rgba(15, 23, 42, 0.5)", borderRadius: 10, color: "#F1F5F9", fontSize: 14 }}>
                <span>Multi-Agent CLI</span>
                <span style={{ color: "#94A3B8" }}>Single chat</span>
                <span style={{ color: "#10B981", fontWeight: 700 }}>Autonomous `agy`</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
