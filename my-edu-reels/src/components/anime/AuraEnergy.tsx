import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const AuraEnergy: React.FC<{ color?: string }> = ({
  color = "#00F0FF",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const pulse = 1.0 + Math.sin((frame / fps) * 8) * 0.12;
  const rotation = (frame * 1.5) % 360;

  return (
    <div
      style={{
        position: "absolute",
        width: 600,
        height: 600,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        pointerEvents: "none",
        transform: `scale(${pulse})`,
      }}
    >
      {/* Outer Radial Glow */}
      <div
        style={{
          position: "absolute",
          width: 550,
          height: 550,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${color}33 0%, rgba(112, 0, 255, 0.15) 50%, transparent 70%)`,
          filter: "blur(40px)",
        }}
      />

      {/* Rotating Energy Arc SVG */}
      <svg
        width="600"
        height="600"
        viewBox="0 0 600 600"
        style={{
          position: "absolute",
          transform: `rotate(${rotation}deg)`,
        }}
      >
        <defs>
          <linearGradient id="auraGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00F0FF" />
            <stop offset="50%" stopColor="#7000FF" />
            <stop offset="100%" stopColor="#FFE600" />
          </linearGradient>
        </defs>

        <circle
          cx="300"
          cy="300"
          r="220"
          fill="none"
          stroke="url(#auraGrad)"
          strokeWidth="6"
          strokeDasharray="40 30 80 20"
          strokeLinecap="round"
          opacity="0.85"
        />

        <circle
          cx="300"
          cy="300"
          r="180"
          fill="none"
          stroke="#00F0FF"
          strokeWidth="3"
          strokeDasharray="20 40 60 30"
          opacity="0.6"
        />
      </svg>
    </div>
  );
};
