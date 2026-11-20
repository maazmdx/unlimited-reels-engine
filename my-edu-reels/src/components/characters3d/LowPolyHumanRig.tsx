import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import * as THREE from "three";

export interface LowPolyHumanRigProps {
  characterId: "junior_dev" | "dad" | string;
  isSpeaking?: boolean;
  mouthOpen?: number; // 0.0 to 1.0
  emotion?: "neutral" | "tired" | "shocked" | "angry" | "smug" | string;
  position?: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
  flipHorizontal?: boolean;
}

/**
 * LowPolyHumanRig: Reference-accurate faceted flat-shaded low-poly 3D character rig
 * for Junior Developer and Indian Dad in the cozy low-poly diorama aesthetic.
 * Built with MeshStandardMaterial({ flatShading: true, roughness: 0.75, metalness: 0.08 }).
 * Features:
 * - Proper low-poly connecting neck (cylinderGeometry(0.24, 0.28, 0.35, 7))
 * - Tapered natural torso (narrow shoulders, beveled chest)
 * - Clean forward-pulled eyes (zero cheek clipping)
 * - Junior Dev: Clean open eyes (no broken blocky glasses), 8-puff dodecahedron curly hair, sculpted jaw beard
 * - Dad: Blended salt-and-pepper hair (no ear-protruding boxes), sculpted mustache, clean thin circular reading glasses
 * - Zero flicker: 0 Math.random(), 0 CSS transition, 0 frame % N spring resets.
 */
export const LowPolyHumanRig: React.FC<LowPolyHumanRigProps> = ({
  characterId,
  isSpeaking = false,
  mouthOpen = 0.0,
  emotion = "neutral",
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = 1.0,
  flipHorizontal = false,
}) => {
  const frame = useCurrentFrame();
  const isDad = characterId === "dad";

  // =========================================================================
  // 1. DETERMINISTIC BREATHING & SPEAKING NOD (Zero Modulo Spring Resets)
  // =========================================================================
  const breathY = Math.sin(frame * 0.055) * 0.025;
  const breathRotX = Math.sin(frame * 0.055) * 0.012;
  const speakNodX = isSpeaking ? Math.sin(frame * 0.38) * 0.028 : 0;
  const speakHeadTiltZ = isSpeaking ? Math.sin(frame * 0.22) * 0.018 : 0;

  // =========================================================================
  // 2. DETERMINISTIC EYE BLINK (Every 110 frames ~3.6s, lasts 4 frames)
  // =========================================================================
  const blinkCycle = frame % 110;
  const isBlinking = blinkCycle >= 104 && blinkCycle <= 108;

  // =========================================================================
  // 3. COLOR PALETTE DEFINITION & FLAT-SHADED MATERIALS
  // =========================================================================
  const skinColor = isDad ? "#C58A5B" : "#E0A97A";
  const primaryCloth = isDad ? "#C2410C" : "#1E293B"; // Dad Burnt Orange / Amber vs Junior Dark Teal/Navy Hoodie
  const secondaryCloth = isDad ? "#FEF3C7" : "#0F172A"; // Dad Cream Collar vs Junior Dark Trim
  const hairColor = "#1E293B";
  const darkDetailColor = "#0F172A";

  const skinMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: skinColor,
        roughness: 0.75,
        metalness: 0.08,
        flatShading: true,
      }),
    [skinColor]
  );

  const clothPrimaryMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: primaryCloth,
        roughness: 0.75,
        metalness: 0.08,
        flatShading: true,
      }),
    [primaryCloth]
  );

  const clothSecondaryMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: secondaryCloth,
        roughness: 0.75,
        metalness: 0.08,
        flatShading: true,
      }),
    [secondaryCloth]
  );

  const hairMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: hairColor,
        roughness: 0.85,
        metalness: 0.02,
        flatShading: true,
      }),
    []
  );

  const greyHairMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#94A3B8",
        roughness: 0.85,
        metalness: 0.02,
        flatShading: true,
      }),
    []
  );

  const darkMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: darkDetailColor,
        roughness: 0.40,
        metalness: 0.30,
        flatShading: true,
      }),
    [darkDetailColor]
  );

  const whiteMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#FFFFFF",
        roughness: 0.30,
        metalness: 0.05,
        flatShading: true,
      }),
    []
  );

  const innerMouthMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#2A0808",
        roughness: 0.90,
        flatShading: true,
      }),
    []
  );

  // =========================================================================
  // 4. EMOTION DYNAMICS (Angled Eyebrows, Top Eyelids, Mouth Open)
  // =========================================================================
  let browL_Y = 0.16;
  let browR_Y = 0.16;
  let browL_RotZ = 0.0;
  let browR_RotZ = 0.0;
  let topEyelidDrop = 0.10; // 0.0 = wide open, 1.0 = fully closed

  if (emotion === "tired") {
    browL_Y = 0.12;
    browR_Y = 0.12;
    topEyelidDrop = 0.55; // Cozy half-lidded sleepy expression
  } else if (emotion === "shocked") {
    browL_Y = 0.25;
    browR_Y = 0.25;
    browL_RotZ = 0.15;
    browR_RotZ = -0.15;
    topEyelidDrop = 0.0;
  } else if (emotion === "angry") {
    browL_Y = 0.10;
    browR_Y = 0.10;
    browL_RotZ = -0.26;
    browR_RotZ = 0.26;
    topEyelidDrop = 0.35;
  } else if (emotion === "smug") {
    browL_Y = 0.22;
    browR_Y = 0.13;
    browL_RotZ = 0.16;
    browR_RotZ = -0.05;
    topEyelidDrop = 0.40;
  }

  // Blink overrides eyelid position
  const activeTopEyelid = isBlinking ? 1.0 : topEyelidDrop;

  // Mouth articulation: slit when silent, drops open with visible upper teeth
  const effectiveMouthOpen = isSpeaking ? Math.max(0.08, mouthOpen) : 0.02;
  const mouthScaleY = THREE.MathUtils.lerp(0.18, 2.2, effectiveMouthOpen);

  const flipX = flipHorizontal ? -1 : 1;

  // Junior Dev 8-puff dodecahedron hair cluster
  const juniorHairPuffs = [
    { pos: [-0.22, 0.48, 0.38] as [number, number, number], scale: [0.18, 0.16, 0.16] as [number, number, number] },
    { pos: [-0.06, 0.54, 0.42] as [number, number, number], scale: [0.20, 0.18, 0.17] as [number, number, number] },
    { pos: [0.14, 0.52, 0.39] as [number, number, number], scale: [0.19, 0.17, 0.16] as [number, number, number] },
    { pos: [0.28, 0.46, 0.34] as [number, number, number], scale: [0.17, 0.15, 0.15] as [number, number, number] },
    { pos: [-0.20, 0.64, 0.15] as [number, number, number], scale: [0.22, 0.20, 0.19] as [number, number, number] },
    { pos: [0.02, 0.68, 0.18] as [number, number, number], scale: [0.24, 0.22, 0.20] as [number, number, number] },
    { pos: [0.22, 0.62, 0.12] as [number, number, number], scale: [0.21, 0.19, 0.18] as [number, number, number] },
    { pos: [-0.04, 0.62, -0.16] as [number, number, number], scale: [0.23, 0.20, 0.20] as [number, number, number] },
  ];

  return (
    <group
      position={[position[0], position[1] + breathY, position[2]]}
      rotation={[rotation[0] + breathRotX, rotation[1], rotation[2]]}
      scale={[scale * flipX, scale, scale]}
    >
      {/* =================================================================== */}
      {/* 1. SLIMMER, TAPERED NATURAL TORSO & COLLAR                          */}
      {/* =================================================================== */}
      <group position={[0, -1.25, 0]}>
        {/* Tapered Beveled Low-Poly Torso (Narrower shoulders, beveled chest) */}
        <mesh scale={[1.18, 1.0, 0.72]} material={clothPrimaryMat}>
          <cylinderGeometry args={[0.50, 0.44, 1.15, 8]} />
        </mesh>

        {isDad ? (
          // Dad Collared Polo details
          <>
            <mesh position={[0, 0.56, 0.04]} rotation={[Math.PI / 2, 0, 0]} material={clothSecondaryMat}>
              <torusGeometry args={[0.28, 0.08, 6, 12]} />
            </mesh>
            <mesh position={[0, 0.36, 0.19]} material={clothPrimaryMat}>
              <boxGeometry args={[0.14, 0.34, 0.03]} />
            </mesh>
            {/* Polo Buttons */}
            {[-0.08, 0.04, 0.14].map((y, i) => (
              <mesh key={i} position={[0, 0.36 + y, 0.21]} material={clothSecondaryMat}>
                <cylinderGeometry args={[0.016, 0.016, 0.02, 6]} />
              </mesh>
            ))}
          </>
        ) : (
          // Junior Dev Stylized Blocky-Beveled Hoodie details
          <>
            <mesh position={[0, 0.56, 0.04]} rotation={[Math.PI / 2, 0, 0]} material={clothSecondaryMat}>
              <torusGeometry args={[0.28, 0.08, 6, 12]} />
            </mesh>
            {/* Drawstrings */}
            {[-0.08, 0.08].map((x, i) => (
              <mesh key={i} position={[x, 0.26, 0.20]} material={whiteMat}>
                <cylinderGeometry args={[0.010, 0.010, 0.26, 6]} />
              </mesh>
            ))}
          </>
        )}
      </group>

      {/* =================================================================== */}
      {/* 2. ARTICULATED ARMS (Booth-Sitting / Desk Pose)                     */}
      {/* =================================================================== */}
      {/* Left Arm */}
      <group position={[-0.60, -0.72, 0]} rotation={[0.45, 0.2, -0.2]}>
        <mesh position={[0, -0.31, 0]} material={clothPrimaryMat}>
          <boxGeometry args={[0.22, 0.62, 0.22]} />
        </mesh>
        <group position={[0, -0.62, 0]} rotation={[-0.75, 0.1, 0]}>
          <mesh position={[0, -0.27, 0]} material={clothPrimaryMat}>
            <boxGeometry args={[0.18, 0.54, 0.18]} />
          </mesh>
          <mesh position={[0, -0.58, 0]} material={skinMat}>
            <boxGeometry args={[0.15, 0.15, 0.12]} />
          </mesh>
        </group>
      </group>

      {/* Right Arm */}
      <group position={[0.60, -0.72, 0]} rotation={[0.45, -0.2, 0.2]}>
        <mesh position={[0, -0.31, 0]} material={clothPrimaryMat}>
          <boxGeometry args={[0.22, 0.62, 0.22]} />
        </mesh>
        <group position={[0, -0.62, 0]} rotation={[-0.75, -0.1, 0]}>
          <mesh position={[0, -0.27, 0]} material={clothPrimaryMat}>
            <boxGeometry args={[0.18, 0.54, 0.18]} />
          </mesh>
          <mesh position={[0, -0.58, 0]} material={skinMat}>
            <boxGeometry args={[0.15, 0.15, 0.12]} />
          </mesh>
        </group>
      </group>

      {/* =================================================================== */}
      {/* 3. HEAD & NECK ASSEMBLY (Articulated Nodding & Tilting)             */}
      {/* =================================================================== */}
      <group position={[0, -0.05, 0.05]} rotation={[speakNodX, 0, speakHeadTiltZ]}>
        {/* Proper Low-Poly Connecting Neck */}
        <mesh position={[0, -0.42, 0.0]} material={skinMat}>
          <cylinderGeometry args={[0.24, 0.28, 0.35, 7]} />
        </mesh>

        {/* Faceted Low-Poly Skull (IcosahedronGeometry flatShading) */}
        <mesh position={[0, 0, 0]} scale={[1.0, 1.10, 1.02]} material={skinMat}>
          <icosahedronGeometry args={[0.60, 1]} />
        </mesh>

        {/* Sculpted Chin & Jaw */}
        <mesh position={[0, -0.32, 0.46]} material={skinMat}>
          <boxGeometry args={[0.24, 0.13, 0.20]} />
        </mesh>
        <mesh position={[-0.20, -0.26, 0.24]} rotation={[0, 0.28, 0]} material={skinMat}>
          <boxGeometry args={[0.16, 0.13, 0.26]} />
        </mesh>
        <mesh position={[0.20, -0.26, 0.24]} rotation={[0, -0.28, 0]} material={skinMat}>
          <boxGeometry args={[0.16, 0.13, 0.26]} />
        </mesh>

        {/* Sculpted Nose */}
        <mesh position={[0, -0.06, 0.64]} rotation={[0.25, 0, 0]} material={skinMat}>
          <coneGeometry args={[0.065, 0.16, 5]} />
        </mesh>

        {/* Low-Poly Ears */}
        {[-0.58, 0.58].map((x, i) => (
          <mesh key={i} position={[x, -0.06, 0.02]} scale={[0.45, 0.85, 0.65]} material={skinMat}>
            <dodecahedronGeometry args={[0.14, 0]} />
          </mesh>
        ))}

        {/* ================================================================= */}
        {/* 4. HAIR & HEADWEAR                                                */}
        {/* ================================================================= */}
        {isDad ? (
          // Dad Neat Salt-and-Pepper Side-Part Hair (No protruding ear boxes)
          <group position={[0, 0.16, 0]}>
            <mesh material={hairMat}>
              <sphereGeometry args={[0.65, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.58]} />
            </mesh>
            {/* Side-Part Low-Poly Ridge */}
            <mesh position={[-0.10, 0.36, 0.14]} rotation={[0.1, 0, 0.18]} material={hairMat}>
              <boxGeometry args={[0.48, 0.07, 0.38]} />
            </mesh>
            {/* Grey Temple Highlights Blended Flush Onto Head */}
            <mesh position={[-0.54, 0.12, 0.10]} rotation={[0, 0.25, 0]} material={greyHairMat}>
              <boxGeometry args={[0.06, 0.18, 0.26]} />
            </mesh>
            <mesh position={[0.54, 0.12, 0.10]} rotation={[0, -0.25, 0]} material={greyHairMat}>
              <boxGeometry args={[0.06, 0.18, 0.26]} />
            </mesh>
          </group>
        ) : (
          // Junior Dev 8-Puff Dodecahedron Curly / Messy Low-Poly Hair
          <group position={[0, 0.16, 0]}>
            <mesh material={hairMat}>
              <sphereGeometry args={[0.64, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.58]} />
            </mesh>
            {/* Cohesive Overlapping Hair Puffs */}
            {juniorHairPuffs.map((p, i) => (
              <mesh key={i} position={p.pos} scale={p.scale} material={hairMat}>
                <dodecahedronGeometry args={[1, 0]} />
              </mesh>
            ))}
          </group>
        )}

        {/* ================================================================= */}
        {/* 5. JAW BEARD (Junior Dev) vs MUSTACHE (Dad)                       */}
        {/* ================================================================= */}
        {!isDad ? (
          // Junior Dev Clean Low-Poly Sculpted Beard Along the Jaw
          <group>
            {/* Chin Beard */}
            <mesh position={[0, -0.37, 0.46]} material={hairMat}>
              <boxGeometry args={[0.26, 0.14, 0.20]} />
            </mesh>
            {/* Left Jaw Beard */}
            <mesh position={[-0.22, -0.28, 0.25]} rotation={[0, 0.32, -0.08]} material={hairMat}>
              <boxGeometry args={[0.16, 0.14, 0.30]} />
            </mesh>
            {/* Right Jaw Beard */}
            <mesh position={[0.22, -0.28, 0.25]} rotation={[0, -0.32, 0.08]} material={hairMat}>
              <boxGeometry args={[0.16, 0.14, 0.30]} />
            </mesh>
            {/* Subtle Soul Patch / Lip Accent */}
            <mesh position={[0, -0.20, 0.60]} material={hairMat}>
              <boxGeometry args={[0.10, 0.04, 0.04]} />
            </mesh>
          </group>
        ) : (
          // Dad Sculpted Curved Mustache
          <group position={[0, -0.20, 0.63]}>
            <mesh material={darkMat}>
              <boxGeometry args={[0.32, 0.08, 0.07]} />
            </mesh>
            {[-0.15, 0.15].map((x, i) => (
              <mesh key={i} position={[x, -0.02, 0]} rotation={[0, 0, (i === 0 ? 1 : -1) * 0.65]} material={darkMat}>
                <boxGeometry args={[0.09, 0.05, 0.05]} />
              </mesh>
            ))}
          </group>
        )}

        {/* ================================================================= */}
        {/* 6. SPECTACLES (Dad Only: Clean Thin Circular Reading Glasses)     */}
        {/* ================================================================= */}
        {isDad && (
          <group position={[0, -0.02, 0.70]}>
            {[-0.19, 0.19].map((x, i) => (
              <mesh key={i} position={[x, 0, 0]} material={darkMat}>
                <torusGeometry args={[0.11, 0.014, 6, 16]} />
              </mesh>
            ))}
            <mesh position={[0, 0.01, 0]} material={darkMat}>
              <boxGeometry args={[0.14, 0.014, 0.014]} />
            </mesh>
          </group>
        )}

        {/* ================================================================= */}
        {/* 7. EXPRESSIVE EYES (Clean Forward-Pulled Sclera + Pupils + Lid)   */}
        {/* ================================================================= */}
        {[-0.19, 0.19].map((x, i) => (
          <group key={i} position={[x, -0.02, 0.62]}>
            {/* Sclera (White Eye Sphere, pulled forward to eliminate cheek clipping) */}
            <mesh material={whiteMat}>
              <sphereGeometry args={[0.078, 8, 8]} />
            </mesh>
            {/* Pupil */}
            <mesh position={[0, 0, 0.052]} material={darkMat}>
              <sphereGeometry args={[0.038, 6, 6]} />
            </mesh>
            {/* Top Flat-Shaded Eyelid */}
            <mesh position={[0, 0.078 - activeTopEyelid * 0.065, 0.054]} material={skinMat}>
              <boxGeometry args={[0.16, 0.075, 0.04]} />
            </mesh>
          </group>
        ))}

        {/* ================================================================= */}
        {/* 8. ANGLED EYEBROWS                                                */}
        {/* ================================================================= */}
        <mesh position={[-0.19, browL_Y, 0.65]} rotation={[0, 0, browL_RotZ]} material={hairMat}>
          <boxGeometry args={[0.20, 0.045, 0.03]} />
        </mesh>
        <mesh position={[0.19, browR_Y, 0.65]} rotation={[0, 0, browR_RotZ]} material={hairMat}>
          <boxGeometry args={[0.20, 0.045, 0.03]} />
        </mesh>

        {/* ================================================================= */}
        {/* 9. ARTICULATED MOUTH & TEETH CAVITY                               */}
        {/* ================================================================= */}
        <group position={[0, isDad ? -0.30 : -0.25, 0.59]}>
          {/* Inner Cavity */}
          <mesh scale={[1, mouthScaleY, 1]} material={innerMouthMat}>
            <boxGeometry args={[0.18, 0.05, 0.06]} />
          </mesh>
          {/* Visible Upper Teeth */}
          {(isSpeaking || mouthOpen > 0.05) && (
            <mesh position={[0, 0.015, 0.02]} material={whiteMat}>
              <boxGeometry args={[0.14, 0.022, 0.02]} />
            </mesh>
          )}
        </group>
      </group>
    </group>
  );
};
