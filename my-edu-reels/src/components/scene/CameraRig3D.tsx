import React, { useLayoutEffect } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { TimelineTurn } from "../ui/CinematicSubtitles";

export type CameraShotType = "wide" | "closeup_left" | "closeup_right";

export interface CameraRig3DProps {
  activeTurn?: TimelineTurn | null;
  turns?: TimelineTurn[];
  isProofCardActive?: boolean;
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
    position: [0.0, 0.55, 7.8],
    target: [0.0, 0.22, 0.0],
    fov: 46,
  },
  closeup_left: {
    position: [-0.85, 0.48, 3.8],
    target: [-1.15, 0.36, 0.0],
    fov: 38,
  },
  closeup_right: {
    position: [0.85, 0.52, 3.4],
    target: [1.05, 0.45, 0.05],
    fov: 38,
  },
};

/**
 * Calculates deterministic camera parameters for the current frame.
 * Strictly locks cuts to activeTurn.character_id, but HOLDS previous shot during inter-turn pauses:
 * - Turn 0 OR isProofCardActive -> "wide"
 * - activeTurn.character_id === leftCharId -> "closeup_left"
 * - activeTurn.character_id === rightCharId -> "closeup_right"
 * - Inter-turn pauses (activeTurn === null): holds most recent completed turn shot (ZERO flash-cuts to wide!)
 */
export function getCameraRigParams(
  frame: number,
  activeTurn?: TimelineTurn | null,
  turns?: TimelineTurn[],
  isProofCardActive: boolean = false,
  leftCharId: string = "junior_dev",
  rightCharId: string = "claude",
  forcedShot?: CameraShotType
): { shot: CameraShotType; position: [number, number, number]; target: [number, number, number]; fov: number } {
  // 1. Determine active shot strictly from turn character_id with smooth inter-turn hold
  let shot: CameraShotType = "wide";

  if (forcedShot) {
    shot = forcedShot;
  } else if (isProofCardActive) {
    // Shot A: Establishing two-shot forced during Proof Card
    shot = "wide";
  } else if (activeTurn) {
    if (activeTurn.turn_index === 0) {
      shot = "wide";
    } else if (activeTurn.character_id === leftCharId) {
      shot = "closeup_left";
    } else if (activeTurn.character_id === rightCharId) {
      shot = "closeup_right";
    } else {
      shot = "wide";
    }
  } else {
    // Inter-turn pause or pre/post dialogue:
    // DO NOT snap back to "wide" between dialogue turns!
    // Hold the most recent completed turn's shot until the next turn begins.
    const firstTurn = turns && turns.length > 0 ? turns[0] : null;
    if (firstTurn && frame < firstTurn.start_frame) {
      shot = "wide";
    } else {
      const lastActiveTurn =
        turns && turns.length > 0
          ? [...turns].filter((t) => t.end_frame <= frame).pop()
          : null;

      if (lastActiveTurn) {
        if (lastActiveTurn.turn_index === 0) {
          shot = "wide";
        } else if (lastActiveTurn.character_id === leftCharId) {
          shot = "closeup_left";
        } else if (lastActiveTurn.character_id === rightCharId) {
          shot = "closeup_right";
        } else {
          shot = "wide";
        }
      } else {
        shot = "wide";
      }
    }
  }

  const base = SHOT_COORDINATES[shot];

  // 2. Subtle deterministic camera push-in over the active turn duration (3-5% zoom)
  let pushInZ = 0;
  if (activeTurn && activeTurn.end_frame > activeTurn.start_frame) {
    const turnProgress = interpolate(
      frame,
      [activeTurn.start_frame, activeTurn.end_frame],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    pushInZ = turnProgress * 0.14;
  } else if (!activeTurn && turns && turns.length > 0) {
    // During inter-turn pause, hold the completed turn's maximum push-in to prevent zoom pops
    const lastActiveTurn = [...turns].filter((t) => t.end_frame <= frame).pop();
    if (lastActiveTurn && lastActiveTurn.turn_index !== 0) {
      pushInZ = 0.14;
    }
  }

  // 3. Subtle organic camera breathe (deterministic sine, zero random)
  const breathY = Math.sin(frame * 0.03) * 0.012;
  const breathX = Math.cos(frame * 0.02) * 0.008;

  const position: [number, number, number] = [
    base.position[0] + breathX,
    base.position[1] + breathY,
    base.position[2] - pushInZ,
  ];

  return {
    shot,
    position,
    target: base.target,
    fov: base.fov,
  };
}

/**
 * CameraRig3D:
 * - Mounted inside <ThreeCanvas> to control the active perspective camera.
 * - Executes crisp editorial cuts strictly locked to activeTurn.character_id.
 * - Holds speaker close-up during brief inter-turn pauses (0 flash-cuts).
 * - Automatically forces Wide on Turn 0 and when proof card is active.
 * - Deterministic push-in over turn duration with zero jitter.
 */
export const CameraRig3D: React.FC<CameraRig3DProps> = ({
  activeTurn,
  turns,
  isProofCardActive = false,
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
    forcedShot
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
