import React from "react";
import { useCurrentFrame } from "remotion";

export const MangaSpeedLines: React.FC<{
  color?: string;
  intensity?: number;
  centerX?: number;
  centerY?: number;
}> = ({
  color = "#FFFFFF",
  intensity = 1.0,
  centerX = 540,
  centerY = 960,
}) => {
  const frame = useCurrentFrame();

  // Shift lines every frame to simulate high-speed anime action
  const lineCount = 36;
  const seed = (frame * 3) % 17;

  return (
    <svg
      width="1080"
      height="1920"
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        pointerEvents: "none",
        zIndex: 2,
        opacity: 0.22 * intensity,
      }}
    >
      <defs>
        <radialGradient id="speedFade" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="transparent" />
          <stop offset="35%" stopColor="transparent" />
          <stop offset="100%" stopColor={color} />
        </radialGradient>
      </defs>

      {[...Array(lineCount)].map((_, i) => {
        const angle = ((i * (360 / lineCount) + (seed * 7)) * Math.PI) / 180;
        const innerRadius = 380 + ((i * 37 + seed * 19) % 140);
        const outerRadius = 1400;

        const x1 = centerX + Math.cos(angle) * innerRadius;
        const y1 = centerY + Math.sin(angle) * innerRadius;
        const x2 = centerX + Math.cos(angle) * outerRadius;
        const y2 = centerY + Math.sin(angle) * outerRadius;

        const strokeW = 2 + ((i + seed) % 6);

        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="url(#speedFade)"
            strokeWidth={strokeW}
            strokeLinecap="round"
          />
        );
      })}
    </svg>
  );
};
