import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface NotificationToastProps {
  title: string;
  subtitle?: string;
  icon?: string;
  startFrame?: number;
  durationFrames?: number;
}

/**
 * NotificationToast:
 * - Compact iOS/macOS frosted top notification banner.
 * - Positioned at top: 140px, safe from Instagram notch / upper controls.
 * - Auto-dismisses within 2.5s - 3.5s max.
 * - Zero flicker: 0 Math.random(), 0 CSS transition, 0 frame % N spring resets.
 */
export const NotificationToast: React.FC<NotificationToastProps> = ({
  title,
  subtitle,
  icon = "⚡",
  startFrame = 40,
  durationFrames = 90, // 3.0s @ 30fps
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cappedDuration = Math.min(Math.max(durationFrames, 60), 105);
  const endFrame = startFrame + cappedDuration;

  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  const age = frame - startFrame;
  const exitAge = endFrame - frame;

  const entrance = spring({
    frame: Math.min(age, 20),
    fps,
    config: { damping: 14, stiffness: 180, mass: 0.6 },
  });

  const exitOpacity = interpolate(exitAge, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitSlide = interpolate(exitAge, [0, 10], [-25, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = entrance * exitOpacity;
  const translateY = interpolate(entrance, [0, 1], [-50, 0]) + exitSlide;

  return (
    <div
      style={{
        position: "absolute",
        top: 130,
        left: "50%",
        transform: `translateX(-50%) translateY(${translateY}px)`,
        opacity,
        zIndex: 95,
        pointerEvents: "none",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          padding: "12px 24px",
          borderRadius: 30,
          background: "rgba(15, 23, 42, 0.90)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(255, 255, 255, 0.2)",
          boxShadow:
            "0 12px 32px rgba(0, 0, 0, 0.6), 0 0 24px rgba(56, 189, 248, 0.3)",
          minWidth: 320,
        }}
      >
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: "50%",
            backgroundColor: "rgba(56, 189, 248, 0.2)",
            border: "1px solid rgba(56, 189, 248, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 20,
          }}
        >
          {icon}
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span style={{ fontSize: 16, fontWeight: 800, color: "#F8FAFC" }}>
            {title}
          </span>
          {subtitle && (
            <span style={{ fontSize: 13, fontWeight: 500, color: "#94A3B8" }}>
              {subtitle}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
