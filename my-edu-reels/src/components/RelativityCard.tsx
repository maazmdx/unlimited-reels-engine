import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const RelativityCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring from frame 230
  const sceneFrame = Math.max(0, frame - 230);
  const cardSpring = spring({
    frame: sceneFrame,
    fps,
    config: { damping: 12, mass: 0.7, stiffness: 140 },
  });

  const ctaPulse = 1.0 + Math.sin((sceneFrame / fps) * 5) * 0.04;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        transform: `scale(${cardSpring})`,
        opacity: interpolate(sceneFrame, [0, 15], [0, 1], {
          extrapolateRight: "clamp",
        }),
      }}
    >
      {/* Category Pill */}
      <div
        style={{
          background: "linear-gradient(90deg, #7000FF, #00F0FF)",
          padding: "10px 28px",
          borderRadius: 999,
          boxShadow: "0 0 24px rgba(112, 0, 255, 0.6)",
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
          EINSTEIN'S LEGACY
        </span>
      </div>

      {/* Main Header */}
      <h2
        style={{
          fontFamily: "system-ui, sans-serif",
          fontWeight: 900,
          fontSize: 66,
          textAlign: "center",
          color: "#FFFFFF",
          margin: "0 0 32px 0",
          textShadow: "0 0 30px rgba(0, 240, 255, 0.4)",
        }}
      >
        The Fabric of Spacetime
      </h2>

      {/* Glassmorphism Einstein Formula Card */}
      <div
        style={{
          background: "rgba(18, 24, 38, 0.88)",
          backdropFilter: "blur(20px)",
          border: "2px solid rgba(0, 240, 255, 0.4)",
          borderRadius: 36,
          padding: "44px 40px",
          width: "100%",
          maxWidth: 900,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          boxShadow:
            "0 30px 60px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 240, 255, 0.2)",
        }}
      >
        <span
          style={{
            fontFamily: "system-ui, sans-serif",
            fontWeight: 800,
            fontSize: 22,
            letterSpacing: "2px",
            color: "#94A3B8",
            textTransform: "uppercase",
            marginBottom: 16,
          }}
        >
          Einstein Field Equation
        </span>

        {/* Elegant Math Formula Display */}
        <div
          style={{
            background: "rgba(0, 0, 0, 0.5)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderRadius: 24,
            padding: "24px 36px",
            margin: "12px 0 24px 0",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span
            style={{
              fontFamily: "'Times New Roman', Times, serif",
              fontStyle: "italic",
              fontWeight: 700,
              fontSize: 54,
              color: "#00F0FF",
              letterSpacing: "4px",
              textShadow: "0 0 20px rgba(0, 240, 255, 0.8)",
            }}
          >
            G<sub>μν</sub> + Λg<sub>μν</sub> ={" "}
            <span style={{ fontSize: 62 }}>(</span>
            8πG / c<sup>4</sup>
            <span style={{ fontSize: 62 }}>)</span> T<sub>μν</sub>
          </span>
        </div>

        {/* Famous Principle Quote */}
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: 30,
            fontWeight: 700,
            textAlign: "center",
            color: "#E2E8F0",
            lineHeight: 1.4,
            margin: "12px 0 24px 0",
          }}
        >
          "Matter tells spacetime how to curve.{" "}
          <br />
          Spacetime tells matter how to move."
        </p>

        {/* Mind-Blowing Stat Banner */}
        <div
          style={{
            background: "linear-gradient(90deg, rgba(255, 230, 0, 0.15), rgba(255, 85, 0, 0.2))",
            border: "2px solid #FFE600",
            borderRadius: 20,
            padding: "16px 32px",
            display: "flex",
            alignItems: "center",
            gap: "16px",
            boxShadow: "0 0 25px rgba(255, 230, 0, 0.3)",
          }}
        >
          <span style={{ fontSize: 36 }}>⚡</span>
          <span
            style={{
              fontFamily: "system-ui, sans-serif",
              fontWeight: 900,
              fontSize: 28,
              color: "#FFE600",
              letterSpacing: "1px",
              textTransform: "uppercase",
            }}
          >
            1 Hour Here = 7 Years on Earth!
          </span>
        </div>
      </div>

      {/* Interactive CTA Banner */}
      <div
        style={{
          marginTop: 36,
          background: "linear-gradient(90deg, #00F0FF, #7000FF)",
          borderRadius: 999,
          padding: "18px 48px",
          display: "flex",
          alignItems: "center",
          gap: "18px",
          boxShadow: "0 10px 30px rgba(0, 240, 255, 0.4)",
          transform: `scale(${ctaPulse})`,
        }}
      >
        <span
          style={{
            fontFamily: "system-ui, sans-serif",
            fontWeight: 900,
            fontSize: 28,
            color: "#FFFFFF",
            letterSpacing: "1.5px",
            textTransform: "uppercase",
          }}
        >
          Follow for More Cosmic Mysteries
        </span>
        <span style={{ fontSize: 32 }}>🚀</span>
      </div>
    </div>
  );
};
