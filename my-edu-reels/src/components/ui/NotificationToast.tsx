import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface ToastData {
  app_name?: string;
  sender?: string;
  message?: string;
  title?: string;
  subtitle?: string;
  icon?: string;
  time?: string;
}

export interface NotificationToastProps {
  toastData?: ToastData | null;
  title?: string;
  subtitle?: string;
  icon?: string;
  startFrame?: number;
  durationFrames?: number;
}

/**
 * NotificationToast:
 * - Animated iOS-style glassmorphism notification banner sliding in on Turn 9.
 * - Upper-third safe zone positioning (top: 220px, width: 860px).
 * - Zero overlap with subtitles (subtitles move to bottom: 320px).
 * - Auto-dismisses after 3.5 seconds (105 frames).
 */
export const NotificationToast: React.FC<NotificationToastProps> = ({
  toastData,
  title,
  subtitle,
  icon,
  startFrame = 40,
  durationFrames = 105, // 3.5s @ 30fps
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Resolve fields from toastData or fallback props
  const appName = (toastData?.app_name || "MESSAGES").toUpperCase();
  const senderName = toastData?.sender || title || "ALERT";
  const messageBody = toastData?.message || subtitle || "";
  const iconEmoji = toastData?.icon || icon || "💬";
  const timeStr = toastData?.time || "now";

  const cappedDuration = Math.min(Math.max(durationFrames, 60), 120);
  const endFrame = startFrame + cappedDuration;

  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  const age = frame - startFrame;
  const exitAge = endFrame - frame;

  const entrance = spring({
    frame: Math.min(age, 22),
    fps,
    config: { damping: 15, stiffness: 160, mass: 0.7 },
  });

  const exitOpacity = interpolate(exitAge, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exitSlide = interpolate(exitAge, [0, 12], [-25, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const opacity = entrance * exitOpacity;
  const translateY = interpolate(entrance, [0, 1], [-60, 0]) + exitSlide;
  const scale = interpolate(entrance, [0, 1], [0.92, 1.0]);

  return (
    <div
      style={{
        position: "absolute",
        top: 220,
        left: "50%",
        transform: `translateX(-50%) translateY(${translateY}px) scale(${scale})`,
        opacity,
        zIndex: 90,
        pointerEvents: "none",
        width: 860,
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 10,
          padding: "18px 24px",
          borderRadius: 24,
          background: "rgba(15, 23, 42, 0.94)",
          backdropFilter: "blur(24px)",
          border: "1.5px solid rgba(255, 255, 255, 0.22)",
          boxShadow:
            "0 24px 64px rgba(0, 0, 0, 0.75), 0 0 32px rgba(56, 189, 248, 0.35)",
        }}
      >
        {/* App Header Row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            borderBottom: "1px solid rgba(255, 255, 255, 0.10)",
            paddingBottom: 8,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 20 }}>{iconEmoji}</span>
            <span
              style={{
                fontSize: 13,
                fontWeight: 800,
                color: "#38BDF8",
                letterSpacing: "0.8px",
              }}
            >
              {appName}
            </span>
          </div>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#64748B" }}>
            {timeStr}
          </span>
        </div>

        {/* Sender & Message Content */}
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span
            style={{
              fontSize: 20,
              fontWeight: 800,
              color: "#FFFFFF",
              letterSpacing: "-0.2px",
            }}
          >
            {senderName}
          </span>
          {messageBody && (
            <span
              style={{
                fontSize: 18,
                fontWeight: 500,
                color: "#E2E8F0",
                lineHeight: 1.4,
              }}
            >
              {messageBody}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
