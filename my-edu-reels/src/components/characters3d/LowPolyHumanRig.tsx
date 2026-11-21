import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import * as THREE from "three";

export interface LowPolyHumanRigProps {
  characterId: "junior_dev" | "dad" | string;
  isSpeaking?: boolean;
  mouthOpen?: number; // 0.0 to 1.0
  emotion?: "neutral" | "tired" | "shocked" | "angry" | "smug" | string;
  turnFrame?: number; // Frames since active turn started
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
  turnFrame,
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
  // 1B. 15-FRAME DISBELIEF HEAD-SHAKE ON SHOCKED OR ANGRY ROAST REACTION
  // =========================================================================
  let headShakeY = 0;
  const isRoastReaction = emotion === "shocked" || emotion === "angry";
  const effectiveTurnFrame = turnFrame !== undefined ? turnFrame : (frame % 30);
  if (isRoastReaction && effectiveTurnFrame >= 0 && effectiveTurnFrame <= 15) {
    const decay = 1.0 - effectiveTurnFrame / 15;
    headShakeY = Math.sin(effectiveTurnFrame * 0.65) * 0.14 * decay;
  }

  // =========================================================================
  // 2. DETERMINISTIC EYE BLINK (Every 110 frames ~3.6s, lasts 4 frames)
  // =========================================================================
  const blinkCycle = frame % 110;
  const isBlinking = blinkCycle >= 104 && blinkCycle <= 108;

  // =========================================================================
  // 3. COLOR PALETTE DEFINITION & FLAT-SHADED MATERIALS
  // =========================================================================
  const skinColor = isDad ? "#C58A5B" : "#E0A97A";
  const primaryCloth = isDad ? "#C2410C" : "#1E4E5F"; // Dad Burnt Orange vs Junior Stylized Dark Teal Hoodie (reel_DeIwE1-sxVr.mp4)
  const secondaryCloth = isDad ? "#FEF3C7" : "#133541"; // Dad Cream Collar vs Junior Dark Teal Trim
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

  const toothMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#F8FAFC", // Clean off-white upper tooth bar (reel_DeIwE1-sxVr.mp4)
        roughness: 0.35,
        metalness: 0.05,
        flatShading: true,
      }),
    []
  );

  const innerMouthMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#2A0808", // Dark-brown / maroon mouth recess
        roughness: 0.90,
        flatShading: true,
      }),
    []
  );

  const pantsColor = isDad ? "#334155" : "#1E293B"; // Dad dark charcoal/slate slacks vs Junior Dev dark navy denim
  const pantsMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: pantsColor,
        roughness: 0.8,
        metalness: 0.05,
        flatShading: true,
      }),
    [pantsColor]
  );

  const lipColor = isDad ? "#8A5738" : "#9E6B50";
  const lipMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: lipColor,
        roughness: 0.8,
        metalness: 0.05,
        flatShading: true,
      }),
    [lipColor]
  );

  const boothSeatMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#B91C1C",
        roughness: 0.6,
        metalness: 0.05,
        flatShading: true,
      }),
    []
  );

  // =========================================================================
  // 4. EMOTION DYNAMICS & BODY ACTING POSTURE
  // =========================================================================
  let browL_Y = 0.16;
  let browR_Y = 0.16;
  let browL_RotZ = 0.0;
  let browR_RotZ = 0.0;
  let topEyelidDrop = 0.10; // 0.0 = wide open, 1.0 = fully closed
  let emotionSlumpRotX = 0.0;
  let gazeRotX = 0.0;
  let headOrientRotY = 0.0;

  if (emotion === "tired" || emotion === "sad") {
    browL_Y = 0.12;
    browR_Y = 0.12;
    topEyelidDrop = 0.55; // Cozy half-lidded sleepy expression
    emotionSlumpRotX = 0.12; // Slight forward slump
    gazeRotX = 0.08; // Downward gaze
  } else if (emotion === "shocked") {
    browL_Y = 0.25;
    browR_Y = 0.25;
    browL_RotZ = 0.15;
    browR_RotZ = -0.15;
    topEyelidDrop = 0.0; // Wide open eyes
    emotionSlumpRotX = -0.08; // Sudden upright lean-back
  } else if (emotion === "angry") {
    browL_Y = 0.10;
    browR_Y = 0.10;
    browL_RotZ = -0.26;
    browR_RotZ = 0.26;
    topEyelidDrop = 0.35;
    emotionSlumpRotX = 0.06;
  } else if (emotion === "smug") {
    browL_Y = 0.22;
    browR_Y = 0.13;
    browL_RotZ = 0.16;
    browR_RotZ = -0.05;
    topEyelidDrop = 0.40;
  }

  // Listening posture: when not speaking, angle head toward the AI orb (+0.28 rad)
  if (!isSpeaking) {
    headOrientRotY = 0.28;
  }

  // Blink overrides eyelid position
  const activeTopEyelid = isBlinking ? 1.0 : topEyelidDrop;

  // Mouth articulation: clean low-poly natural lip-sync (matching reel_DeIwE1-sxVr.mp4)
  const isSilent = mouthOpen < 0.08;
  const mouthWidthFlex = isSpeaking
    ? 0.195 + 0.025 * Math.sin(frame * 0.45)
    : 0.18;
  const mouthHeight = isSilent
    ? 0.018
    : THREE.MathUtils.lerp(0.025, 0.13, Math.min(1.0, Math.max(0.0, mouthOpen)));
  const isToothVisible = !isSilent && mouthOpen > 0.15;

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
      <group position={[0, -1.25, 0]} rotation={[emotionSlumpRotX, 0, 0]}>
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
      {/* 1B. SEATED LEGS & BOOTH SEAT CUSHION (Natural Booth Sitting Pose)   */}
      {/* =================================================================== */}
      <group position={[0, -1.82, 0]}>
        {/* Belt & Waist */}
        <mesh position={[0, -0.02, 0.06]} material={darkMat}>
          <boxGeometry args={[0.84, 0.08, 0.52]} />
        </mesh>
        <mesh position={[0, -0.02, 0.33]} material={whiteMat}>
          <boxGeometry args={[0.10, 0.08, 0.03]} />
        </mesh>

        {/* Pelvis / Hips */}
        <mesh position={[0, -0.16, 0.08]} scale={[1.14, 0.55, 0.82]} material={pantsMat}>
          <cylinderGeometry args={[0.40, 0.38, 0.35, 8]} />
        </mesh>

        {/* Left Seated Thigh (Horizontal, extending forward) */}
        <mesh position={[-0.22, -0.32, 0.36]} rotation={[Math.PI / 2 + 0.06, 0, 0]} material={pantsMat}>
          <cylinderGeometry args={[0.16, 0.14, 0.64, 8]} />
        </mesh>
        {/* Left Knee */}
        <mesh position={[-0.22, -0.35, 0.68]} material={pantsMat}>
          <sphereGeometry args={[0.14, 8, 8]} />
        </mesh>
        {/* Left Lower Leg / Shin (Dropping down) */}
        <mesh position={[-0.22, -0.70, 0.68]} material={pantsMat}>
          <cylinderGeometry args={[0.13, 0.11, 0.60, 8]} />
        </mesh>
        {/* Left Sneaker / Shoe */}
        <mesh position={[-0.22, -1.02, 0.74]} material={darkMat}>
          <boxGeometry args={[0.16, 0.12, 0.28]} />
        </mesh>
        <mesh position={[-0.22, -1.07, 0.74]} material={whiteMat}>
          <boxGeometry args={[0.17, 0.03, 0.30]} />
        </mesh>

        {/* Right Seated Thigh (Horizontal, extending forward) */}
        <mesh position={[0.22, -0.32, 0.36]} rotation={[Math.PI / 2 + 0.06, 0, 0]} material={pantsMat}>
          <cylinderGeometry args={[0.16, 0.14, 0.64, 8]} />
        </mesh>
        {/* Right Knee */}
        <mesh position={[0.22, -0.35, 0.68]} material={pantsMat}>
          <sphereGeometry args={[0.14, 8, 8]} />
        </mesh>
        {/* Right Lower Leg / Shin (Dropping down) */}
        <mesh position={[0.22, -0.70, 0.68]} material={pantsMat}>
          <cylinderGeometry args={[0.13, 0.11, 0.60, 8]} />
        </mesh>
        {/* Right Sneaker / Shoe */}
        <mesh position={[0.22, -1.02, 0.74]} material={darkMat}>
          <boxGeometry args={[0.16, 0.12, 0.28]} />
        </mesh>
        <mesh position={[0.22, -1.07, 0.74]} material={whiteMat}>
          <boxGeometry args={[0.17, 0.03, 0.30]} />
        </mesh>

        {/* Red Booth Seat Cushion directly under character hips */}
        <mesh position={[0, -0.42, 0.24]} material={boothSeatMat}>
          <boxGeometry args={[1.15, 0.22, 1.15]} />
        </mesh>
      </group>

      {/* =================================================================== */}
      {/* 2. ARTICULATED ARMS (Booth-Sitting / Desk Pose, Flush-Connected)   */}
      {/* =================================================================== */}
      {/* Left Arm (Flush into torso side, zero floating gap) */}
      <group position={[-0.52, -0.72, 0]} rotation={[0.45, 0.2, -0.2]}>
        {/* Seamless Shoulder Joint Sphere */}
        <mesh position={[0, 0, 0]} material={clothPrimaryMat}>
          <sphereGeometry args={[0.15, 8, 8]} />
        </mesh>
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

      {/* Right Arm (Flush into torso side, zero floating gap) */}
      <group position={[0.52, -0.72, 0]} rotation={[0.45, -0.2, 0.2]}>
        {/* Seamless Shoulder Joint Sphere */}
        <mesh position={[0, 0, 0]} material={clothPrimaryMat}>
          <sphereGeometry args={[0.15, 8, 8]} />
        </mesh>
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
      {/* 3. HEAD & NECK ASSEMBLY (Articulated Nodding & Disbelief Shaking)   */}
      {/* =================================================================== */}
      <group position={[0, -0.05, 0.05]} rotation={[speakNodX + gazeRotX, headShakeY + headOrientRotY, speakHeadTiltZ]}>
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

        {/* Clean Warm Skin-Tone Low-Poly Nose (Zero dark underside block/shadow) */}
        <mesh position={[0, -0.07, 0.63]} rotation={[-0.12, 0, 0]} material={skinMat}>
          <boxGeometry args={[0.075, 0.12, 0.07]} />
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
          // Junior Dev Clean Low-Poly Sculpted Beard Along Bottom Jaw Edge Only (Zero mouth clipping)
          <group>
            {/* Bottom Chin Edge Contour (Well below mouth, zero goatee block) */}
            <mesh position={[0, -0.39, 0.44]} material={hairMat}>
              <boxGeometry args={[0.22, 0.08, 0.16]} />
            </mesh>
            {/* Left Jaw Edge Contour */}
            <mesh position={[-0.22, -0.31, 0.25]} rotation={[0, 0.32, -0.08]} material={hairMat}>
              <boxGeometry args={[0.13, 0.08, 0.28]} />
            </mesh>
            {/* Right Jaw Edge Contour */}
            <mesh position={[0.22, -0.31, 0.25]} rotation={[0, -0.32, 0.08]} material={hairMat}>
              <boxGeometry args={[0.13, 0.08, 0.28]} />
            </mesh>
          </group>
        ) : (
          // Dad Sculpted Curved Mustache (Sits cleanly right above upper lip line)
          <group position={[0, -0.19, 0.63]}>
            <mesh material={darkMat}>
              <boxGeometry args={[0.32, 0.07, 0.06]} />
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
        {/* 9. ARTICULATED NATURAL LIP-SYNC MOUTH & TEETH                     */}
        {/* ================================================================= */}
        <group position={[0, isDad ? -0.27 : -0.24, 0.59]}>
          {isSilent ? (
            /* When silent (mouthOpen < 0.08): clean subtle closed mouth line */
            <mesh position={[0, 0, 0.01]} material={lipMat}>
              <boxGeometry args={[0.18, 0.018, 0.02]} />
            </mesh>
          ) : (
            /* When speaking: lower jaw drops, width flexes with Math.sin, teeth revealed */
            <group>
              {/* Upper Lip Line */}
              <mesh position={[0, mouthHeight * 0.5 + 0.007, 0.01]} material={lipMat}>
                <boxGeometry args={[mouthWidthFlex, 0.014, 0.02]} />
              </mesh>
              {/* Inner Dark Mouth Cavity (Recessed safely behind lips so it never clips forward) */}
              <mesh position={[0, 0, -0.015]} scale={[mouthWidthFlex / 0.20, mouthHeight / 0.05, 1]} material={innerMouthMat}>
                <boxGeometry args={[0.20, 0.05, 0.03]} />
              </mesh>
              {/* Crisp White Upper Tooth Bar */}
              {isToothVisible && (
                <mesh position={[0, mouthHeight * 0.5 - 0.012, 0.018]} material={toothMat}>
                  <boxGeometry args={[mouthWidthFlex * 0.78, 0.024, 0.02]} />
                </mesh>
              )}
              {/* Lower Jaw Line moving with jaw drop */}
              <mesh position={[0, -mouthHeight * 0.5 - 0.007, 0.01]} material={lipMat}>
                <boxGeometry args={[mouthWidthFlex * 0.9, 0.014, 0.02]} />
              </mesh>
            </group>
          )}
        </group>
      </group>
    </group>
  );
};
