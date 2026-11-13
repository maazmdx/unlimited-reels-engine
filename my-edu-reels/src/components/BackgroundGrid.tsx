import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const BackgroundGrid: React.FC<{ theme?: "space" | "cyber" | "meme" }> = ({
  theme = "space",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subtle breathing pulse
  const pulse = Math.sin((frame / fps) * 2) * 0.15 + 0.85;

  const isMeme = theme === "meme";

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: 1080,
        height: 1920,
        backgroundColor: isMeme ? "#0F0B18" : "#0B0F19",
        overflow: "hidden",
        zIndex: 0,
      }}
    >
      {/* Deep Radial Space Glow 1 (Cyan / Violet) */}
      <div
        style={{
          position: "absolute",
          top: "15%",
          left: "50%",
          width: 900,
          height: 900,
          transform: "translate(-50%, -50%)",
          background: isMeme
            ? "radial-gradient(circle, rgba(255, 0, 128, 0.22) 0%, rgba(130, 0, 255, 0.08) 50%, transparent 70%)"
            : "radial-gradient(circle, rgba(0, 240, 255, 0.18) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 70%)",
          filter: "blur(60px)",
          opacity: pulse,
        }}
      />

      {/* Deep Radial Space Glow 2 (Orange / Gold for Accretion Disk warmth) */}
      <div
        style={{
          position: "absolute",
          top: "45%",
          left: "50%",
          width: 750,
          height: 750,
          transform: "translate(-50%, -50%)",
          background: isMeme
            ? "radial-gradient(circle, rgba(255, 230, 0, 0.16) 0%, transparent 60%)"
            : "radial-gradient(circle, rgba(255, 120, 0, 0.15) 0%, rgba(255, 60, 0, 0.05) 50%, transparent 70%)",
          filter: "blur(80px)",
        }}
      />

      {/* Animated Spacetime Coordinate Grid */}
      <svg
        width="1080"
        height="1920"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          opacity: isMeme ? 0.1 : 0.18,
        }}
      >
        <defs>
          <pattern
            id="spacetime-grid"
            width="80"
            height="80"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 80 0 L 0 0 0 80"
              fill="none"
              stroke={isMeme ? "#FF007F" : "#00F0FF"}
              strokeWidth="1.2"
            />
          </pattern>
        </defs>
        <rect width="1080" height="1920" fill="url(#spacetime-grid)" />
      </svg>

      {/* Ambient Floating Dust Particles */}
      {[...Array(16)].map((_, i) => {
        const speed = (i % 4) + 1;
        const initialY = (i * 120) % 1920;
        const y = (initialY - frame * speed * 0.8) % 1920;
        const finalY = y < 0 ? y + 1920 : y;
        const x = (i * 68 + (frame * 0.2 * ((i % 2 === 0) ? 1 : -1))) % 1080;
        const size = (i % 3) + 2;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: finalY,
              left: (x + 1080) % 1080,
              width: size,
              height: size,
              borderRadius: "50%",
              backgroundColor: isMeme ? "#FFE600" : "#67e8f9",
              boxShadow: `0 0 8px ${isMeme ? "#FFE600" : "#00F0FF"}`,
              opacity: 0.35 + ((i % 5) * 0.1),
            }}
          />
        );
      })}
    </div>
  );
};
