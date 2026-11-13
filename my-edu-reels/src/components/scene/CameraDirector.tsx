import React from "react";
import { useCurrentFrame } from "remotion";

export interface CameraCue {
  startFrame: number;
  endFrame: number;
  zoomLevel: number; // 1.0 (wide), 1.25 (medium), 1.4 (punch close-up)
  targetX: number; // 540 (center), 270 (left speaker), 810 (right speaker)
  targetY?: number; // default ~900
  shake?: boolean;
}

export interface CameraDirectorProps {
  children: React.ReactNode;
  activeSpeaker?: string;
  cameraCues?: CameraCue[];
  currentTurnIndex?: number;
}

export const CameraDirector: React.FC<CameraDirectorProps> = ({
  children,
  activeSpeaker = "bot",
  cameraCues = [],
  currentTurnIndex = 0,
}) => {
  const frame = useCurrentFrame();

  // Find active camera cue for this frame
  const currentCue = cameraCues.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame
  );

  // Default target based on active speaker if no specific cue is active
  let targetScale = 1.0;
  let targetOriginX = 540;
  let targetOriginY = 960;
  let isShaking = false;

  if (currentCue) {
    targetScale = currentCue.zoomLevel;
    targetOriginX = currentCue.targetX;
    targetOriginY = currentCue.targetY ?? 960;
    isShaking = !!currentCue.shake;
  } else {
    // Subtle rhythmic dialogue push-in on turn changes
    const turnPhase = (frame % 90) / 90;
    targetScale = 1.0 + Math.sin(turnPhase * Math.PI) * 0.04;
    targetOriginX = 540;
    targetOriginY = 960;
  }

  // Camera impact shake
  const shakeX = isShaking ? Math.sin(frame * 1.8) * 8 : 0;
  const shakeY = isShaking ? Math.cos(frame * 2.2) * 6 : 0;

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "relative",
        overflow: "hidden",
        transform: `scale(${targetScale}) translate(${shakeX}px, ${shakeY}px)`,
        transformOrigin: `${targetOriginX}px ${targetOriginY}px`,
        transition: "transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)",
      }}
    >
      {children}
    </div>
  );
};
