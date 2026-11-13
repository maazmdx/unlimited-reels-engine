import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const ClockComparison: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring animation
  const sceneSpring = spring({
    frame: Math.max(0, frame - 110),
    fps,
    config: { damping: 14, mass: 0.8, stiffness: 130 },
  });

  // Calculate elapsed frames in Scene 2
  const sceneFrame = Math.max(0, frame - 110);

  // Rotation angles for Deep Space Clock (1.0x speed)
  // Deep space: 1 full rotation of minute hand every 60 frames (2s)
  const deepSpaceAngle = (sceneFrame * 6) % 360;
  const deepSpaceHourAngle = (sceneFrame * 0.5) % 360;

  // Rotation angles for Event Horizon Clock (0.3x speed)
  // Dilated: rotates at only 30% of the normal speed!
  const dilatedAngle = (sceneFrame * 1.8) % 360;
  const dilatedHourAngle = (sceneFrame * 0.15) % 360;

  // Digital clock simulation
  const deepSpaceSeconds = Math.floor(sceneFrame * 0.6);
  const dilatedSeconds = Math.floor(sceneFrame * 0.18);

  const formatClockTime = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `00:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        transform: `scale(${sceneSpring})`,
        opacity: interpolate(sceneFrame, [0, 15], [0, 1], {
          extrapolateRight: "clamp",
        }),
      }}
    >
      {/* Category Pill */}
      <div
        style={{
          background: "linear-gradient(90deg, #6366F1, #00F0FF)",
          padding: "10px 28px",
          borderRadius: 999,
          boxShadow: "0 0 24px rgba(0, 240, 255, 0.5)",
          marginBottom: 20,
        }}
      >
        <span
          style={{
            fontFamily: "system-ui, sans-serif",
            fontWeight: 900,
            fontSize: 24,
            letterSpacing: "3px",
            color: "#FFFFFF",
            textTransform: "uppercase",
          }}
        >
          RELATIVISTIC MEASUREMENT
        </span>
      </div>

      {/* Main Header */}
      <h2
        style={{
          fontFamily: "system-ui, sans-serif",
          fontWeight: 900,
          fontSize: 64,
          textAlign: "center",
          color: "#FFFFFF",
          margin: "0 0 36px 0",
          textShadow: "0 0 30px rgba(0, 240, 255, 0.3)",
        }}
      >
        Twin Clock Paradox
      </h2>

      {/* Side-by-Side Dual Clocks Container */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: "36px",
          width: "100%",
          maxWidth: 960,
        }}
      >
        {/* Left Clock: Deep Space (1.0x Normal Speed) */}
        <div
          style={{
            flex: 1,
            background: "rgba(11, 25, 44, 0.85)",
            backdropFilter: "blur(16px)",
            border: "2px solid #00F0FF",
            borderRadius: 36,
            padding: "36px 20px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow:
              "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 240, 255, 0.25)",
          }}
        >
          <span
            style={{
              fontFamily: "system-ui, sans-serif",
              fontWeight: 900,
              fontSize: 24,
              color: "#00F0FF",
              letterSpacing: "1px",
              marginBottom: 16,
              textTransform: "uppercase",
            }}
          >
            Deep Space
          </span>

          {/* Clock Dial SVG */}
          <div style={{ position: "relative", width: 260, height: 260 }}>
            <svg width="260" height="260" viewBox="0 0 260 260">
              <circle
                cx="130"
                cy="130"
                r="115"
                fill="#0A111E"
                stroke="rgba(0, 240, 255, 0.3)"
                strokeWidth="4"
              />

              {/* Ticks around dial */}
              {[...Array(12)].map((_, i) => (
                <line
                  key={i}
                  x1="130"
                  y1="25"
                  x2="130"
                  y2={i % 3 === 0 ? "35" : "30"}
                  stroke={i % 3 === 0 ? "#00F0FF" : "rgba(255,255,255,0.4)"}
                  strokeWidth={i % 3 === 0 ? "3" : "1.5"}
                  transform={`rotate(${i * 30} 130 130)`}
                />
              ))}

              {/* Hour Hand */}
              <line
                x1="130"
                y1="130"
                x2="130"
                y2="70"
                stroke="#FFFFFF"
                strokeWidth="5"
                strokeLinecap="round"
                transform={`rotate(${deepSpaceHourAngle} 130 130)`}
              />

              {/* Minute Hand (Fast 1.0x) */}
              <line
                x1="130"
                y1="130"
                x2="130"
                y2="42"
                stroke="#00F0FF"
                strokeWidth="4"
                strokeLinecap="round"
                transform={`rotate(${deepSpaceAngle} 130 130)`}
                filter="drop-shadow(0 0 6px #00F0FF)"
              />

              {/* Center Pin */}
              <circle cx="130" cy="130" r="7" fill="#00F0FF" />
            </svg>
          </div>

          {/* Digital Timer */}
          <div
            style={{
              fontFamily: "monospace",
              fontWeight: 900,
              fontSize: 36,
              color: "#FFFFFF",
              marginTop: 18,
              letterSpacing: "2px",
            }}
          >
            {formatClockTime(deepSpaceSeconds)}
          </div>

          {/* Speed Indicator Pill */}
          <div
            style={{
              background: "rgba(0, 240, 255, 0.15)",
              border: "1px solid rgba(0, 240, 255, 0.5)",
              borderRadius: 999,
              padding: "6px 20px",
              marginTop: 14,
            }}
          >
            <span
              style={{
                fontFamily: "system-ui, sans-serif",
                fontWeight: 900,
                fontSize: 20,
                color: "#00F0FF",
              }}
            >
              1.0x Normal Speed
            </span>
          </div>
        </div>

        {/* Right Clock: Event Horizon (0.3x Dilated Speed) */}
        <div
          style={{
            flex: 1,
            background: "rgba(35, 12, 25, 0.85)",
            backdropFilter: "blur(16px)",
            border: "2px solid #FF0055",
            borderRadius: 36,
            padding: "36px 20px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            boxShadow:
              "0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(255, 0, 85, 0.25)",
          }}
        >
          <span
            style={{
              fontFamily: "system-ui, sans-serif",
              fontWeight: 900,
              fontSize: 24,
              color: "#FF3366",
              letterSpacing: "1px",
              marginBottom: 16,
              textTransform: "uppercase",
            }}
          >
            Near Event Horizon
          </span>

          {/* Clock Dial SVG */}
          <div style={{ position: "relative", width: 260, height: 260 }}>
            <svg width="260" height="260" viewBox="0 0 260 260">
              <circle
                cx="130"
                cy="130"
                r="115"
                fill="#1E0A14"
                stroke="rgba(255, 0, 85, 0.3)"
                strokeWidth="4"
              />

              {/* Ticks around dial */}
              {[...Array(12)].map((_, i) => (
                <line
                  key={i}
                  x1="130"
                  y1="25"
                  x2="130"
                  y2={i % 3 === 0 ? "35" : "30"}
                  stroke={i % 3 === 0 ? "#FF0055" : "rgba(255,255,255,0.4)"}
                  strokeWidth={i % 3 === 0 ? "3" : "1.5"}
                  transform={`rotate(${i * 30} 130 130)`}
                />
              ))}

              {/* Hour Hand */}
              <line
                x1="130"
                y1="130"
                x2="130"
                y2="70"
                stroke="#FFFFFF"
                strokeWidth="5"
                strokeLinecap="round"
                transform={`rotate(${dilatedHourAngle} 130 130)`}
              />

              {/* Minute Hand (Slow 0.3x) */}
              <line
                x1="130"
                y1="130"
                x2="130"
                y2="42"
                stroke="#FF3366"
                strokeWidth="4"
                strokeLinecap="round"
                transform={`rotate(${dilatedAngle} 130 130)`}
                filter="drop-shadow(0 0 6px #FF0055)"
              />

              {/* Center Pin */}
              <circle cx="130" cy="130" r="7" fill="#FF0055" />
            </svg>
          </div>

          {/* Digital Timer */}
          <div
            style={{
              fontFamily: "monospace",
              fontWeight: 900,
              fontSize: 36,
              color: "#FFFFFF",
              marginTop: 18,
              letterSpacing: "2px",
            }}
          >
            {formatClockTime(dilatedSeconds)}
          </div>

          {/* Speed Indicator Pill */}
          <div
            style={{
              background: "rgba(255, 0, 85, 0.15)",
              border: "1px solid rgba(255, 0, 85, 0.5)",
              borderRadius: 999,
              padding: "6px 20px",
              marginTop: 14,
            }}
          >
            <span
              style={{
                fontFamily: "system-ui, sans-serif",
                fontWeight: 900,
                fontSize: 20,
                color: "#FF3366",
              }}
            >
              0.3x DILATED TICK
            </span>
          </div>
        </div>
      </div>

      {/* Comparison Bottom Stat Card */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.06)",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          borderRadius: 24,
          padding: "20px 40px",
          marginTop: 36,
          display: "flex",
          alignItems: "center",
          gap: "20px",
        }}
      >
        <div
          style={{
            width: 16,
            height: 16,
            borderRadius: "50%",
            backgroundColor: "#FFE600",
            boxShadow: "0 0 12px #FFE600",
          }}
        />
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: 28,
            fontWeight: 800,
            color: "#FFFFFF",
            margin: 0,
          }}
        >
          To a distant observer, your clock appears almost{" "}
          <span style={{ color: "#FFE600" }}>frozen in time</span>.
        </p>
      </div>
    </div>
  );
};
