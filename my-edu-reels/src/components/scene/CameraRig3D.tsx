import React, { useLayoutEffect } from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { TimelineTurn } from "../ui/CinematicSubtitles";

export type CameraShotType =
  | "wide"
  | "closeup_left"
  | "closeup_right"
  | "ots_left"
  | "ots_right"
  | "dutch_roast"
  | "climax_zoom";

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
  roll?: number; // Dutch tilt roll in radians
}

export const SHOT_COORDINATES: Record<CameraShotType, CameraShotCoords> = {
  wide: {
    position: [1.65, 0.95, 7.2],
    target: [-0.15, 0.15, 0.0],
    fov: 44,
    roll: 0,
  },
  closeup_left: {
    position: [-0.55, 0.52, 3.8],
    target: [-1.20, 0.38, 0.0],
    fov: 39,
    roll: 0,
  },
  closeup_right: {
    position: [0.75, 0.56, 3.5],
    target: [1.10, 0.46, 0.05],
    fov: 39,
    roll: 0,
  },
  ots_left: {
    position: [1.85, 0.72, 3.25],
    target: [-0.45, 0.36, 0.02],
    fov: 42,
    roll: 0,
  },
  ots_right: {
    position: [-1.95, 0.68, 3.35],
    target: [0.40, 0.42, 0.04],
    fov: 42,
    roll: 0,
  },
  dutch_roast: {
    position: [0.68, 0.58, 3.35],
    target: [1.05, 0.45, 0.05],
    fov: 38,
    roll: 0.061, // ~3.5 degree Dutch tilt on savage AI roast turns
  },
  climax_zoom: {
    position: [0.22, 0.50, 3.65],
    target: [0.35, 0.36, 0.04],
    fov: 37,
    roll: 0,
  },
};

/**
 * Calculates deterministic camera parameters for the current frame.
 * Features:
 * 1. 5 rotating shot types by turn mood: Wide Establishing, Tight Close-Up (14% faster punch-in on
 *    shock/question), Over-the-Shoulder (OTS), Dutch-Tilt Roast (3.5 deg roll + 5-frame whip-pan),
 *    and Climax Zoom (Turn 9 notification + 4-frame camera shake).
 * 2. Continuous subtle dolly push-in, slow orbital drift, and handheld breathing micro-motion on every turn.
 * 3. Zero flicker, zero Math.random(), zero modulo spring resets.
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
  roll: number;
} {
  // Helper to resolve 5 dynamic shot types rotated by turn mood
  const resolveShotForTurn = (turn: TimelineTurn, isCardActive: boolean): CameraShotType => {
    if (turn.turn_index === 0 || isCardActive) {
      return "wide";
    }
    if (turn.turn_index === 9) {
      return "climax_zoom";
    }
    const emo = (turn.emotion || "").toLowerCase();
    const isLeft = turn.character_id === leftCharId;
    const isRight = turn.character_id === rightCharId;
    const isSavageRoast =
      isRight &&
      (emo.includes("smug") ||
        emo.includes("sarcas") ||
        emo.includes("roast") ||
        emo.includes("angr") ||
        turn.turn_index === 1 ||
        turn.turn_index === 11);

    // Mid-skit back-and-forth OTS alternation so both characters stay in frame with depth
    if (turn.turn_index === 3 || turn.turn_index === 4 || turn.turn_index === 7 || turn.turn_index === 10) {
      return isLeft ? "ots_left" : "ots_right";
    }
    if (isSavageRoast) {
      return "dutch_roast";
    }
    if (isLeft) {
      return "closeup_left";
    }
    if (isRight) {
      return "closeup_right";
    }
    return "wide";
  };

  // 1. Determine active shot and transition segment
  let currentShot: CameraShotType = "wide";
  let prevShot: CameraShotType = "wide";
  let transitionStartFrame = 0;

  if (forcedShot) {
    currentShot = forcedShot;
    prevShot = forcedShot;
  } else if (!turns || turns.length === 0) {
    if (isProofCardActive) {
      currentShot = "wide";
    } else if (isToastActive) {
      currentShot = "climax_zoom";
    } else if (activeTurn) {
      currentShot = resolveShotForTurn(activeTurn, false);
    } else {
      currentShot = "wide";
    }
    prevShot = currentShot;
  } else {
    const firstTurn = turns[0];
    if (frame < firstTurn.start_frame) {
      currentShot = "wide";
      prevShot = "wide";
    } else {
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
        isProofCardActive || (currentTurn.turn_index >= 5 && currentTurn.turn_index <= 7 && isProofCardActive);
      currentShot = resolveShotForTurn(currentTurn, isCardAtCurrentTurn);
      transitionStartFrame = currentTurn.start_frame;

      if (turnIdx === 0) {
        prevShot = "wide";
      } else {
        const prevTurn = turns[turnIdx - 1];
        const isCardAtPrevTurn =
          prevTurn.turn_index >= 5 && prevTurn.turn_index <= 7 && isProofCardActive;
        prevShot = resolveShotForTurn(prevTurn, isCardAtPrevTurn);
      }
    }
  }

  // Quick 5-frame whip-pan on Dutch-tilt roast turns; 6-frame cubic ease-out otherwise
  const transitionDuration = currentShot === "dutch_roast" ? 5 : 6;

  // 2. Compute cubic ease-out transition progress
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

  // Turn 0 opening slow push-in from z = 7.9 -> 7.2
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

  const baseX = interpolate(transitionT, [0, 1], [prevBase.position[0], targetBase.position[0]]);
  const baseY = interpolate(transitionT, [0, 1], [prevBase.position[1], targetBase.position[1]]);
  let baseZ = interpolate(transitionT, [0, 1], [prevZ, targetZ]);

  const targetLookX = interpolate(transitionT, [0, 1], [prevBase.target[0], targetBase.target[0]]);
  const targetLookY = interpolate(transitionT, [0, 1], [prevBase.target[1], targetBase.target[1]]);
  const targetLookZ = interpolate(transitionT, [0, 1], [prevBase.target[2], targetBase.target[2]]);

  let fov = interpolate(transitionT, [0, 1], [prevBase.fov, targetBase.fov]);
  const roll = interpolate(transitionT, [0, 1], [prevBase.roll ?? 0, targetBase.roll ?? 0]);

  const activeEmotion = (activeTurn?.emotion || "").toLowerCase();
  const isQuestionTurn = Boolean(activeTurn?.text && activeTurn.text.includes("?"));
  const isShockOrQuestion =
    isQuestionTurn || activeEmotion.includes("shock") || activeEmotion.includes("angr");
  const isHookTurn = !!activeTurn && activeTurn.turn_index === 0;
  const isTwistTurn =
    !!activeTurn &&
    (activeTurn.turn_index === 3 ||
      activeTurn.turn_index === 8 ||
      activeTurn.turn_index === 9);
  const isHighEmotionRoast =
    !!activeTurn &&
    (activeEmotion.includes("roast") ||
      activeEmotion.includes("smug") ||
      activeEmotion.includes("sarcas") ||
      isShockOrQuestion);

  // Punch-in snap: 14% faster on Tight Close-Up shock/question turns (10 frames vs 12 frames)
  if ((isHookTurn || isTwistTurn || isHighEmotionRoast) && activeTurn) {
    const punchFrames =
      (currentShot === "closeup_left" || currentShot === "closeup_right") && isShockOrQuestion
        ? 10
        : 12;
    const roastAge = Math.max(0, frame - activeTurn.start_frame);
    if (roastAge <= punchFrames) {
      const easePunch = interpolate(roastAge, [0, punchFrames], [0, 1], {
        easing: Easing.out(Easing.cubic),
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      fov += interpolate(easePunch, [0, 1], [-7.0, 0]);
    }
  }

  // 3. Continuous subtle dolly push-in on EVERY turn > 0 (14% faster on shock/question close-ups)
  if (!isTurn0) {
    const pushDepth = isShockOrQuestion ? 0.16 * 1.14 : 0.16;
    let pushInZ = 0;
    if (activeTurn && activeTurn.end_frame > activeTurn.start_frame && activeTurn.turn_index > 0) {
      const turnProgress = interpolate(
        frame,
        [activeTurn.start_frame + transitionDuration, activeTurn.end_frame],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );
      pushInZ = turnProgress * pushDepth;
    } else if (!activeTurn && turns && turns.length > 0) {
      const lastActiveTurn = [...turns].filter((t) => t.end_frame <= frame).pop();
      if (lastActiveTurn && lastActiveTurn.turn_index > 0) {
        pushInZ = pushDepth;
      }
    }
    baseZ -= pushInZ;
  }

  // 4. Continuous Orbital Drift + Organic Handheld Breathing Micro-Motion (never frozen tripod)
  const orbitX = Math.sin(frame * 0.025) * 0.12 + Math.sin(frame * 0.053) * 0.022;
  const orbitY = Math.cos(frame * 0.02) * 0.032 + Math.cos(frame * 0.047) * 0.014;
  const breathZ = Math.sin(frame * 0.037) * 0.024;

  // 5. Notification Reaction Tilt & 4-Frame Climax Shake on Turn 9
  let toastTiltY = 0;
  let toastTiltX = 0;
  let toastTargetShiftY = 0;

  const turn9 = turns?.find((t) => t.turn_index === 9);
  if (turn9) {
    const toastStart = turn9.start_frame;
    const toastDuration = 105;
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

      toastTiltY = toastWeight * -0.09;
      toastTargetShiftY = toastWeight * -0.05;
      const isLeftSpeaker = turn9.character_id === leftCharId;
      toastTiltX = toastWeight * (isLeftSpeaker ? 0.06 : -0.06);
    }
  } else if (isToastActive) {
    toastTiltY = -0.09;
    toastTargetShiftY = -0.05;
    toastTiltX = currentShot === "closeup_left" ? 0.06 : -0.06;
  }

  // Subtle 4-frame camera shake on Turn 9 Climax Zoom / notification pop-in
  let toastShakeX = 0;
  let toastShakeY = 0;
  if (turn9) {
    const toastAge = frame - turn9.start_frame;
    if (toastAge >= 0 && toastAge <= 4) {
      const decay = (4 - toastAge) / 4;
      toastShakeX = Math.sin(toastAge * 4.5) * 0.04 * decay;
      toastShakeY = Math.cos(toastAge * 5.0) * 0.03 * decay;
    }
  } else if (isToastActive) {
    toastShakeX = Math.sin(frame * 0.8) * 0.01;
  }

  // Subtle 4-frame impact tremor on non-Turn-9 speaker cuts
  let shakeX = 0;
  let shakeY = 0;
  if (activeTurn && activeTurn.turn_index !== 9) {
    const turnAge = Math.max(0, frame - activeTurn.start_frame);
    if (turnAge <= 4) {
      const shakeDecay = (4 - turnAge) / 4;
      shakeX = Math.sin(turnAge * 3.5) * 0.022 * shakeDecay;
      shakeY = Math.cos(turnAge * 4.2) * 0.015 * shakeDecay;
    }
  }

  const position: [number, number, number] = [
    baseX + orbitX + toastTiltX + shakeX + toastShakeX,
    baseY + orbitY + toastTiltY + shakeY + toastShakeY,
    baseZ + breathZ,
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
    roll,
  };
}

/**
 * CameraRig3D:
 * - Mounted inside <ThreeCanvas> to control the active perspective camera.
 * - Supports 5 dynamic shot types with smooth cubic/whip-pan transitions, Dutch roll, and Climax Zoom.
 * - Continuous orbital drift, dolly push-in, and handheld breathing micro-motion.
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
      if (params.roll !== 0) {
        camera.rotateZ(params.roll);
      }
      if ((camera as THREE.PerspectiveCamera).fov !== params.fov) {
        (camera as THREE.PerspectiveCamera).fov = params.fov;
        camera.updateProjectionMatrix();
      }
    }
  }, [camera, params]);

  return null;
};
