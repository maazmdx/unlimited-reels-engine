import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface CameraCue {
  startFrame: number;
  endFrame: number;
  zoomLevel: number; // 1.0 (wide), 1.22 (medium), 1.40 (punch close-up)
  targetX: number; // 540 (center), 270 (left human), 810 (right bot)
  targetY?: number; // default ~820 (character eye/face level)
  shake?: boolean;
  isPunch?: boolean;
}

export interface CameraDirectorProps {
  children: React.ReactNode;
  activeSpeaker?: string;
  cameraCues?: CameraCue[];
  currentTurnIndex?: number;
}

export const CameraDirector: React.FC<CameraDirectorProps> = ({
  children,
  cameraCues = [],
}) => {
  const frame = useCurrentFrame();

  // Find active camera cue for this frame
  const currentCue = cameraCues.find(
    (c) => frame >= c.startFrame && frame <= c.endFrame
  );

  let currentScale = 1.0;
  let currentOriginX = 540;
  let currentOriginY = 860;
  let isShaking = false;

  if (currentCue) {
    const transitionFrames = currentCue.isPunch ? 5 : 12;

    // Smooth ease-in zoom at cue start and ease-out at cue end
    const progressIn = interpolate(
      frame,
      [currentCue.startFrame, currentCue.startFrame + transitionFrames],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const progressOut = interpolate(
      frame,
      [currentCue.endFrame - transitionFrames, currentCue.endFrame],
      [1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    const zoomBlend = Math.min(progressIn, progressOut);

    currentScale = interpolate(zoomBlend, [0, 1], [1.0, currentCue.zoomLevel]);
    currentOriginX = interpolate(zoomBlend, [0, 1], [540, currentCue.targetX]);
    currentOriginY = interpolate(
      zoomBlend,
      [0, 1],
      [860, currentCue.targetY ?? 820]
    );

    isShaking = !!currentCue.shake && frame - currentCue.startFrame < 14;
  } else {
    // Subtle organic breathing push when in wide shot
    const breath = Math.sin(frame / 20) * 0.015;
    currentScale = 1.0 + breath;
    currentOriginX = 540;
    currentOriginY = 860;
  }

  // Handheld camera organic micro-drift (mimicking cinematic steadycam)
  const driftX = Math.sin(frame / 28) * 3;
  const driftY = Math.cos(frame / 32) * 2;

  // Impact camera shake (decaying exponentially)
  let shakeOffset = 0;
  if (isShaking && currentCue) {
    const shakeAge = frame - currentCue.startFrame;
    const decay = Math.max(0, 1 - shakeAge / 14);
    shakeOffset = Math.sin(frame * 1.6) * 12 * decay;
  }

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "relative",
        overflow: "hidden",
        transform: `scale(${currentScale}) translate(${driftX + shakeOffset}px, ${driftY}px)`,
        transformOrigin: `${currentOriginX}px ${currentOriginY}px`,
      }}
    >
      {children}
    </div>
  );
};
