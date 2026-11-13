import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export interface ViralHookProps {
  headline?: string;
  subheadline?: string;
  tag?: string;
  durationFrames?: number;
}

export const ViralHook: React.FC<ViralHookProps> = ({
  headline = "THE $200/MO AI MISTAKE",
  subheadline = "Why devs are deleting Claude for this $0 Google CLI",
  tag = "⚠️ UNPOPULAR OPINION",
  durationFrames = 75,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (frame > durationFrames) {
    return null;
  }

  // Punch-in spring animation
  const punch = spring({
    frame,
    fps,
    config: {
      damping: 14,
      mass: 0.6,
      stiffness: 180,
    },
  });

  // Scale from 1.25 down to 1.0, then fade out at end
  const scale = interpolate(punch, [0, 1], [1.25, 1.0]);
  const opacity = interpolate(
    frame,
    [0, 10, durationFrames - 15, durationFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 240,
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 100,
        pointerEvents: "none",
        padding: "0 64px",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      {/* Alert Tag Badge */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          backgroundColor: "#EF4444",
          color: "#FFFFFF",
          padding: "8px 24px",
          borderRadius: 30,
          fontSize: 20,
          fontWeight: 900,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          boxShadow: "0 0 30px rgba(239, 68, 68, 0.7), 0 4px 12px rgba(0,0,0,0.5)",
          marginBottom: 16,
        }}
      >
        <span>{tag}</span>
      </div>

      {/* Main Hook Headline */}
      <div
        style={{
          backgroundColor: "rgba(11, 15, 25, 0.92)",
          border: "2px solid rgba(239, 68, 68, 0.8)",
          borderRadius: 24,
          padding: "24px 36px",
          textAlign: "center",
          boxShadow: "0 20px 50px rgba(0,0,0,0.8), 0 0 40px rgba(239, 68, 68, 0.3)",
          backdropFilter: "blur(20px)",
          maxWidth: 920,
        }}
      >
        <h1
          style={{
            fontSize: 54,
            fontWeight: 900,
            color: "#FFFFFF",
            margin: "0 0 12px 0",
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            textTransform: "uppercase",
            textShadow: "0 4px 16px rgba(0,0,0,0.8)",
          }}
        >
          {headline}
        </h1>
        <p
          style={{
            fontSize: 26,
            color: "#CBD5E1",
            margin: 0,
            fontWeight: 600,
            lineHeight: 1.35,
          }}
        >
          {subheadline}
        </p>
      </div>
    </div>
  );
};
