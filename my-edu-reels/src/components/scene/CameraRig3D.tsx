import React, { useLayoutEffect } from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { TimelineTurn } from "../ui/CinematicSubtitles";

export type CameraShotType = "wide" | "closeup_left" | "closeup_right";

export interface CameraRig3DProps {
  activeTurn?: TimelineTurn | null;
  isProofCardActive?: boolean;
  speakerSide?: "left" | "right" | "wide";
  forcedShot?: CameraShotType;
}

export interface CameraShotCoords {
  position: [number, number, number];
  target: [number, number, number];
  fov: number;
}

export const SHOT_COORDINATES: Record<CameraShotType, CameraShotCoords> = {
  wide: {
    position: [0.0, -0.05, 5.2],
    target: [0.0, -0.1, 0.0],
    fov: 42,
  },
  closeup_left: {
    position: [-1.05, 0.05, 3.2],
    target: [-1.25, 0.05, -0.1],
    fov: 35,
  },
  closeup_right: {
    position: [1.05, 0.18, 3.0],
    target: [1.25, 0.16, -0.1],
    fov: 33,
  },
};

/**
 * Calculates deterministic camera parameters for the current frame.
 */
export function getCameraRigParams(
  frame: number,
  activeTurn?: TimelineTurn | null,
  isProofCardActive: boolean = false,
  speakerSide: "left" | "right" | "wide" = "left",
  forcedShot?: CameraShotType
): { shot: CameraShotType; position: [number, number, number]; target: [number, number, number]; fov: number } {
  // 1. Determine active shot
  let shot: CameraShotType = "wide";

  if (forcedShot) {
    shot = forcedShot;
  } else if (isProofCardActive || !activeTurn || activeTurn.turn_index === 0) {
    // Shot A: Establishing two-shot (used for Turn 0 & forced during Proof Card)
    shot = "wide";
  } else if (speakerSide === "right") {
    // Shot C: AI Orb close-up
    shot = "closeup_right";
  } else {
    // Shot B: Human dev close-up
    shot = "closeup_left";
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
 * - Executes crisp editorial cuts between Wide, Closeup Left, and Closeup Right.
 * - Automatically forces Wide when proof card is active.
 * - Deterministic push-in over turn duration with zero jitter.
 */
export const CameraRig3D: React.FC<CameraRig3DProps> = ({
  activeTurn,
  isProofCardActive = false,
  speakerSide = "left",
  forcedShot,
}) => {
  const frame = useCurrentFrame();
  const { camera } = useThree();

  const params = getCameraRigParams(
    frame,
    activeTurn,
    isProofCardActive,
    speakerSide,
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
