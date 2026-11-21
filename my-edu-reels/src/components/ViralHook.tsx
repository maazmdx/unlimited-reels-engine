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

  // If frame has completely passed the duration window, unmount cleanly
  if (frame >= durationFrames) {
    return null;
  }

  // Punch-in spring animation with crisp physics damping
  const punch = spring({
    frame,
    fps,
    config: {
      damping: 15,
      mass: 0.65,
      stiffness: 175,
    },
  });

  // Scale from 1.20 down to 1.0
  const scale = interpolate(punch, [0, 1], [1.20, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Smooth flicker-free opacity curve: 0 -> 1 over 8 frames, holds, then 1 -> 0 over last 12 frames
  const opacity = interpolate(
    frame,
    [0, 8, durationFrames - 12, durationFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 230,
        left: 0,
        right: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 100,
        pointerEvents: "none",
        padding: "0 64px",
        opacity,
        transform: `translate3d(0, 0, 0) scale(${scale})`,
        transformOrigin: "center center",
        backfaceVisibility: "hidden",
        WebkitFontSmoothing: "antialiased",
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
          backfaceVisibility: "hidden",
        }}
      >
        <span>{tag}</span>
      </div>

      {/* Main Hook Headline Card (Anti-Flicker Solid Translucency) */}
      <div
        style={{
          backgroundColor: "rgba(11, 15, 25, 0.96)",
          border: "2px solid rgba(239, 68, 68, 0.8)",
          borderRadius: 24,
          padding: "24px 36px",
          textAlign: "center",
          boxShadow: "0 20px 50px rgba(0,0,0,0.8), 0 0 40px rgba(239, 68, 68, 0.3)",
          maxWidth: 920,
          backfaceVisibility: "hidden",
        }}
      >
        <h1
          style={{
            fontSize: headline && headline.length > 32 ? (headline.length > 45 ? 38 : 44) : 52,
            fontWeight: 900,
            color: "#FFFFFF",
            margin: "0 0 12px 0",
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            textTransform: "uppercase",
            textShadow: "0 4px 16px rgba(0,0,0,0.8)",
            wordBreak: "break-word",
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
