import React, { useLayoutEffect } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { TimelineTurn } from "../ui/CinematicSubtitles";

export type CameraShotType = "wide" | "closeup_left" | "closeup_right";

export interface CameraRig3DProps {
  activeTurn?: TimelineTurn | null;
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
 * Strictly locks cuts to activeTurn.character_id:
 * - Turn 0 OR isProofCardActive -> "wide"
 * - activeTurn.character_id === leftCharId -> "closeup_left"
 * - activeTurn.character_id === rightCharId -> "closeup_right"
 */
export function getCameraRigParams(
  frame: number,
  activeTurn?: TimelineTurn | null,
  isProofCardActive: boolean = false,
  leftCharId: string = "junior_dev",
  rightCharId: string = "claude",
  forcedShot?: CameraShotType
): { shot: CameraShotType; position: [number, number, number]; target: [number, number, number]; fov: number } {
  // 1. Determine active shot strictly from turn character_id
  let shot: CameraShotType = "wide";

  if (forcedShot) {
    shot = forcedShot;
  } else if (isProofCardActive || !activeTurn || activeTurn.turn_index === 0) {
    // Shot A: Establishing two-shot (Turn 0 establishing shot or forced during Proof Card)
    shot = "wide";
  } else if (activeTurn.character_id === leftCharId) {
    // Shot B: Seated human close-up (framed comfortably above table)
    shot = "closeup_left";
  } else if (activeTurn.character_id === rightCharId) {
    // Shot C: AI Orb close-up (framed with halo, antenna, and backdrop)
    shot = "closeup_right";
  } else {
    shot = "wide";
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
 * - Automatically forces Wide on Turn 0 and when proof card is active.
 * - Deterministic push-in over turn duration with zero jitter.
 */
export const CameraRig3D: React.FC<CameraRig3DProps> = ({
  activeTurn,
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
