import React from "react";
import { useCurrentFrame, useVideoConfig, spring } from "remotion";

export const AnimeBadge: React.FC<{
  kanji?: string;
  label?: string;
  accentColor?: string;
}> = ({
  kanji = "領域展開",
  label = "INFINITY CALCULUS",
  accentColor = "#00F0FF",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const badgeSpring = spring({
    frame,
    fps,
    config: { damping: 10, mass: 0.6, stiffness: 180 },
  });

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "16px",
        background: "rgba(15, 10, 30, 0.85)",
        border: `2px solid ${accentColor}`,
        borderRadius: 999,
        padding: "8px 24px",
        boxShadow: `0 0 25px ${accentColor}66`,
        transform: `scale(${badgeSpring})`,
        marginBottom: 20,
      }}
    >
      {/* Kanji Tag */}
      <span
        style={{
          fontFamily: "'Hiragino Kaku Gothic Pro', 'Meiryo', sans-serif",
          fontWeight: 900,
          fontSize: 28,
          color: "#FFE600",
          textShadow: "0 0 10px rgba(255, 230, 0, 0.8)",
          letterSpacing: "2px",
        }}
      >
        {kanji}
      </span>

      <div
        style={{
          width: 2,
          height: 24,
          backgroundColor: "rgba(255, 255, 255, 0.3)",
        }}
      />

      {/* Western / Romanized Tag */}
      <span
        style={{
          fontFamily: "system-ui, sans-serif",
          fontWeight: 900,
          fontSize: 22,
          color: "#FFFFFF",
          letterSpacing: "2.5px",
          textTransform: "uppercase",
        }}
      >
        {label}
      </span>
    </div>
  );
};
