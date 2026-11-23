import React, { useLayoutEffect } from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { TimelineTurn } from "../ui/CinematicSubtitles";

export type CameraShotType = "wide" | "closeup_left" | "closeup_right";

export interface CameraRig3DProps {
  activeTurn?: TimelineTurn | null;
  turns?: TimelineTurn[];
  isProofCardActive?: boolean;
  isToastActive?: boolean;
  leftCharId?: string;
  rightCharId?: string;
  forcedShot?: CameraShotType;
}

export interface CameraShotCoords {
  position: [number, number, number];
  target: [number, number, number];
  fov: number;
}

export const SHOT_COORDINATES: Record<CameraShotType, CameraShotCoords> = {
  wide: {
    position: [1.65, 0.95, 7.2],
    target: [-0.15, 0.15, 0.0],
    fov: 44,
  },
  closeup_left: {
    position: [-0.55, 0.52, 3.8],
    target: [-1.20, 0.38, 0.0],
    fov: 39,
  },
  closeup_right: {
    position: [0.75, 0.56, 3.5],
    target: [1.10, 0.46, 0.05],
    fov: 39,
  },
};

/**
 * Calculates deterministic camera parameters for the current frame.
 * Features:
 * 1. Smooth 10-frame cubic ease-out transitions (Easing.out(Easing.cubic)) between shots
 *    (wide, closeup_left, closeup_right) instead of hard teleports.
 * 2. Turn 0 opening slow push-in from z = 8.4 -> 7.6.
 * 3. Continuous volumetric micro-orbit drift (Math.sin on X, Math.cos on Y).
 * 4. Notification reaction tilt on Turn 9 for balanced rule-of-thirds composition.
 * 5. Zero flicker, zero Math.random(), zero modulo spring resets.
 */
export function getCameraRigParams(
  frame: number,
  activeTurn?: TimelineTurn | null,
  turns?: TimelineTurn[],
  isProofCardActive: boolean = false,
  leftCharId: string = "junior_dev",
  rightCharId: string = "claude",
  forcedShot?: CameraShotType,
  isToastActive?: boolean
): {
  shot: CameraShotType;
  position: [number, number, number];
  target: [number, number, number];
  fov: number;
} {
  // Helper to resolve shot for a given turn
  const resolveShotForTurn = (turn: TimelineTurn, isCardActive: boolean): CameraShotType => {
    if (turn.turn_index === 0 || isCardActive) {
      return "wide";
    }
    if (turn.character_id === leftCharId) {
      return "closeup_left";
    }
    if (turn.character_id === rightCharId) {
      return "closeup_right";
    }
    return "wide";
  };

  // 1. Determine active shot and transition segment
  let currentShot: CameraShotType = "wide";
  let prevShot: CameraShotType = "wide";
  let transitionStartFrame = 0;
  const transitionDuration = 6; // 6-frame cubic ease-out whip-pan transition

  if (forcedShot) {
    currentShot = forcedShot;
    prevShot = forcedShot;
  } else if (!turns || turns.length === 0) {
    if (isProofCardActive) {
      currentShot = "wide";
    } else if (activeTurn) {
      currentShot = resolveShotForTurn(activeTurn, false);
    } else {
      currentShot = "wide";
    }
    prevShot = currentShot;
  } else {
    // Deterministic evaluation across full turn timeline
    const firstTurn = turns[0];
    if (frame < firstTurn.start_frame) {
      currentShot = "wide";
      prevShot = "wide";
    } else {
      // Find the turn currently active or the most recent completed turn
      let turnIdx = 0;
      for (let i = 0; i < turns.length; i++) {
        if (turns[i].start_frame <= frame) {
          turnIdx = i;
        } else {
          break;
        }
      }

      const currentTurn = turns[turnIdx];
      const isCardAtCurrentTurn =
        isProofCardActive || (currentTurn.turn_index >= 5 && currentTurn.turn_index <= 7);
      currentShot = resolveShotForTurn(currentTurn, isCardAtCurrentTurn);
      transitionStartFrame = currentTurn.start_frame;

      // Find the previous distinct shot
      if (turnIdx === 0) {
        prevShot = "wide";
      } else {
        const prevTurn = turns[turnIdx - 1];
        const isCardAtPrevTurn =
          prevTurn.turn_index >= 5 && prevTurn.turn_index <= 7;
        prevShot = resolveShotForTurn(prevTurn, isCardAtPrevTurn);
      }
    }
  }

  // 2. Compute 10-frame cubic ease-out transition progress
  let transitionT = 1.0;
  if (currentShot !== prevShot && frame >= transitionStartFrame) {
    transitionT = interpolate(
      frame,
      [transitionStartFrame, transitionStartFrame + transitionDuration],
      [0, 1],
      {
        easing: Easing.out(Easing.cubic),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      }
    );
  }

  const prevBase = SHOT_COORDINATES[prevShot];
  const targetBase = SHOT_COORDINATES[currentShot];

  // Turn 0 opening slow push-in from z = 8.4 -> 7.6
  const turn0 = turns && turns[0] ? turns[0] : null;
  const turn0End = turn0 ? turn0.end_frame : 120;
  const isTurn0 =
    (activeTurn && activeTurn.turn_index === 0) ||
    (!activeTurn && turn0 && frame <= turn0.end_frame);

  const getBaseZ = (shot: CameraShotType, isPrev: boolean): number => {
    if (shot === "wide") {
      if (isTurn0 && !isPrev) {
        return interpolate(frame, [0, turn0End], [7.9, 7.2], {
          easing: Easing.out(Easing.cubic),
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
      }
      return 7.2;
    }
    return SHOT_COORDINATES[shot].position[2];
  };

  const prevZ = getBaseZ(prevShot, true);
  const targetZ = getBaseZ(currentShot, false);

  // Interpolate base coordinates over the transition
  const baseX = interpolate(transitionT, [0, 1], [prevBase.position[0], targetBase.position[0]]);
  const baseY = interpolate(transitionT, [0, 1], [prevBase.position[1], targetBase.position[1]]);
  let baseZ = interpolate(transitionT, [0, 1], [prevZ, targetZ]);

  const targetLookX = interpolate(transitionT, [0, 1], [prevBase.target[0], targetBase.target[0]]);
  const targetLookY = interpolate(transitionT, [0, 1], [prevBase.target[1], targetBase.target[1]]);
  const targetLookZ = interpolate(transitionT, [0, 1], [prevBase.target[2], targetBase.target[2]]);

  let fov = interpolate(transitionT, [0, 1], [prevBase.fov, targetBase.fov]);

  // Crash zoom (12-18% punch-in snap -7.0 FOV + 12-frame cubic ease) on hook (Turn 0) and roast/twist turns (Turns 3, 8, 9)
  const isHookTurn = !!activeTurn && activeTurn.turn_index === 0;
  const isTwistTurn =
    !!activeTurn &&
    (activeTurn.turn_index === 3 ||
      activeTurn.turn_index === 8 ||
      activeTurn.turn_index === 9);

  const activeEmotion = (activeTurn?.emotion || "").toLowerCase();
  const isSmugRoast =
    !!activeTurn &&
    activeTurn.character_id === rightCharId &&
    (activeEmotion === "smug" || activeEmotion === "sarcastic");

  const isHighEmotionRoast =
    !!activeTurn &&
    (activeEmotion.includes("roast") ||
      activeEmotion.includes("shock") ||
      activeEmotion.includes("angr") ||
      isSmugRoast);

  if ((isHookTurn || isTwistTurn || isHighEmotionRoast) && activeTurn) {
    const roastAge = Math.max(0, frame - activeTurn.start_frame);
    if (roastAge <= 12) {
      const ease12 = interpolate(roastAge, [0, 12], [0, 1], {
        easing: Easing.out(Easing.cubic),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      // Snap in by -7 FOV (~16% crash zoom) and ease back
      const fovSnap = interpolate(ease12, [0, 1], [-7.0, 0]);
      fov += fovSnap;
    }
  }

  // 3. Subtle camera push-in during active speaking turns (for turns > 0)
  if (!isTurn0) {
    let pushInZ = 0;
    if (activeTurn && activeTurn.end_frame > activeTurn.start_frame && activeTurn.turn_index > 0) {
      const turnProgress = interpolate(
        frame,
        [activeTurn.start_frame + transitionDuration, activeTurn.end_frame],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
      pushInZ = turnProgress * 0.12;
    } else if (!activeTurn && turns && turns.length > 0) {
      const lastActiveTurn = [...turns].filter((t) => t.end_frame <= frame).pop();
      if (lastActiveTurn && lastActiveTurn.turn_index > 0) {
        pushInZ = 0.12;
      }
    }
    baseZ -= pushInZ;
  }

  // 4. Subtle Orbital Drift & Handheld Breathing (Blender-grade continuous parallax)
  const orbitX = Math.sin(frame * 0.025) * 0.12;
  const orbitY = Math.cos(frame * 0.02) * 0.03;

  // 5. Notification Reaction Tilt on Turn 9
  let toastTiltY = 0;
  let toastTiltX = 0;
  let toastTargetShiftY = 0;

  const turn9 = turns?.find((t) => t.turn_index === 9);
  if (turn9) {
    const toastStart = turn9.start_frame;
    const toastDuration = 105; // 3.5s @ 30fps
    const toastEnd = toastStart + toastDuration;

    if (frame >= toastStart - 6 && frame <= toastEnd + 15) {
      const toastWeight = interpolate(
        frame,
        [toastStart, toastStart + 12, toastEnd - 12, toastEnd],
        [0, 1, 1, 0],
        {
          easing: Easing.out(Easing.cubic),
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }
      );

      // Downward tilt & subtle rule-of-thirds horizontal framing shift
      toastTiltY = toastWeight * -0.10;
      toastTargetShiftY = toastWeight * -0.06;
      const isLeftSpeaker = turn9.character_id === leftCharId;
      toastTiltX = toastWeight * (isLeftSpeaker ? 0.07 : -0.07);
    }
  } else if (isToastActive) {
    toastTiltY = -0.10;
    toastTargetShiftY = -0.06;
    toastTiltX = currentShot === "closeup_left" ? 0.07 : -0.07;
  }

  // Subtle 6-frame camera shake on bass-thud beats / turn start
  let shakeX = 0;
  let shakeY = 0;
  if (activeTurn) {
    const turnAge = Math.max(0, frame - activeTurn.start_frame);
    if (turnAge <= 6) {
      const shakeDecay = (6 - turnAge) / 6;
      shakeX = Math.sin(turnAge * 3.5) * 0.025 * shakeDecay;
      shakeY = Math.cos(turnAge * 4.2) * 0.018 * shakeDecay;
    }
  }

  // 6-frame notification pop-in screen shake on Turn 9 / Toast alert
  let toastShakeX = 0;
  let toastShakeY = 0;
  if (turn9) {
    const toastAge = frame - turn9.start_frame;
    if (toastAge >= 0 && toastAge <= 8) {
      const decay = (8 - toastAge) / 8;
      toastShakeX = Math.sin(toastAge * 4.5) * 0.035 * decay;
      toastShakeY = Math.cos(toastAge * 5.0) * 0.025 * decay;
    }
  } else if (isToastActive) {
    toastShakeX = Math.sin(frame * 0.8) * 0.01;
  }

  const position: [number, number, number] = [
    baseX + orbitX + toastTiltX + shakeX + toastShakeX,
    baseY + orbitY + toastTiltY + shakeY + toastShakeY,
    baseZ,
  ];

  const target: [number, number, number] = [
    targetLookX + orbitX * 0.15,
    targetLookY + orbitY * 0.15 + toastTargetShiftY,
    targetLookZ,
  ];

  return {
    shot: currentShot,
    position,
    target,
    fov,
  };
}

/**
 * CameraRig3D:
 * - Mounted inside <ThreeCanvas> to control the active perspective camera.
 * - Smooth 10-frame cubic ease-out transitions between shots (zero teleport snaps).
 * - Continuous organic micro-orbital drift & breathing.
 * - Responsive reaction tilt for Notification Toast on Turn 9.
 * - Holds speaker close-up during brief inter-turn pauses (0 flash-cuts).
 * - Deterministic push-in over turn duration with zero jitter.
 */
export const CameraRig3D: React.FC<CameraRig3DProps> = ({
  activeTurn,
  turns,
  isProofCardActive = false,
  isToastActive = false,
  leftCharId = "junior_dev",
  rightCharId = "claude",
  forcedShot,
}) => {
  const frame = useCurrentFrame();
  const { camera } = useThree();

  const params = getCameraRigParams(
    frame,
    activeTurn,
    turns,
    isProofCardActive,
    leftCharId,
    rightCharId,
    forcedShot,
    isToastActive
  );

  useLayoutEffect(() => {
    if (camera) {
      camera.position.set(params.position[0], params.position[1], params.position[2]);
      camera.lookAt(new THREE.Vector3(params.target[0], params.target[1], params.target[2]));
      if ((camera as THREE.PerspectiveCamera).fov !== params.fov) {
        (camera as THREE.PerspectiveCamera).fov = params.fov;
        camera.updateProjectionMatrix();
      }
    }
  }, [camera, params]);

  return null;
};
