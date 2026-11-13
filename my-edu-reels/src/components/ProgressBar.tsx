import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

export const ProgressBar: React.FC<{ color?: string; height?: number }> = ({
  color = "#00F0FF",
  height = 6,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames - 1], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 24,
        left: 32,
        right: 32,
        height: height,
        backgroundColor: "rgba(255, 255, 255, 0.12)",
        borderRadius: 3,
        overflow: "hidden",
        zIndex: 200,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          background: `linear-gradient(90deg, #6366F1, ${color}, #FFE600)`,
          boxShadow: `0 0 12px ${color}`,
          borderRadius: 3,
        }}
      />
    </div>
  );
};
