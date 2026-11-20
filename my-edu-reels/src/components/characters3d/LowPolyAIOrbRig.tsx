import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import * as THREE from "three";

export interface LowPolyAIOrbRigProps {
  characterId: "claude" | "gemini" | "grok" | "antigravity_bot" | string;
  isSpeaking?: boolean;
  mouthOpen?: number; // 0.0 to 1.0
  emotion?: "neutral" | "deadpan" | "tired" | "shocked" | "angry" | "smug" | string;
  position?: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
}

/**
 * LowPolyAIOrbRig: Reference-accurate faceted flat-shaded low-poly 3D floating orb
 * for Claude, Gemini, Grok, and Antigravity Bot in the cozy low-poly diorama aesthetic.
 * Features:
 * - Z-squashed orb body (scale=[1.0, 1.0, 0.84]) ensuring max Z <= 0.84
 * - Bezel at z=0.86, glossy screen at z=0.91, glowing eyes & 7-bar mouth at z=0.94 (0% shell poke-through)
 * - Thin horizontal-tilted equatorial halo ring (rotation=[Math.PI * 0.45, 0, 0.14], tube=0.015, radius=1.22)
 * - Character-specific antennas with glowing tips
 * - 0 Math.random(), 0 CSS transition, 0 frame % N spring resets.
 */
export const LowPolyAIOrbRig: React.FC<LowPolyAIOrbRigProps> = ({
  characterId,
  isSpeaking = false,
  mouthOpen = 0.0,
  emotion = "neutral",
  position = [0, 0, 0],
  rotation = [0, 0, 0],
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();

  // Normalize ID
  const rawId = (characterId || "claude").toLowerCase().trim();
  const isClaude = rawId.includes("claude");
  const isGrok = rawId.includes("grok");
  const isGemini = rawId.includes("gemini");
  const isAntigravity = rawId.includes("antigravity") || rawId.includes("bot");

  // =========================================================================
  // 1. DETERMINISTIC HOVER BOB & HALO ROTATION (Zero Modulo Spring Resets)
  // =========================================================================
  const hoverY = Math.sin(frame * 0.08) * 0.055;
  const hoverTiltZ = Math.sin(frame * 0.048) * 0.028;
  const hoverTiltX = Math.sin(frame * 0.062) * 0.018;
  const haloRotY = frame * 0.022;

  // =========================================================================
  // 2. DETERMINISTIC EYE BLINK (Every 110 frames ~3.6s, lasts 4 frames)
  // =========================================================================
  const blinkCycle = frame % 110;
  const isBlinking = blinkCycle >= 104 && blinkCycle <= 108;

  // =========================================================================
  // 3. COLOR PALETTE DEFINITION & FLAT-SHADED MATERIALS
  // =========================================================================
  let shellColor = "#E07A47"; // Warm terracotta for Claude
  let accentColor = "#F59E0B"; // Warm amber
  let eyeGlowColor = "#F59E0B";

  if (isGemini) {
    shellColor = "#E2E8F0"; // Pearlescent blue-white
    accentColor = "#38BDF8"; // Electric cyan
    eyeGlowColor = "#38BDF8";
  } else if (isGrok) {
    shellColor = "#18181B"; // Stealth charcoal
    accentColor = "#EF4444"; // Crimson
    eyeGlowColor = "#EF4444";
  } else if (isAntigravity) {
    shellColor = "#D95A2B"; // Antigravity terracotta
    accentColor = "#38BDF8"; // Electric cyan
    eyeGlowColor = "#38BDF8";
  }

  // Standard flat-shaded low-poly materials (roughness: 0.75, metalness: 0.08, flatShading: true)
  const shellMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: shellColor,
        roughness: 0.75,
        metalness: 0.08,
        flatShading: true,
      }),
    [shellColor]
  );

  const darkBezelMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#0B101B",
        roughness: 0.35,
        metalness: 0.75,
        flatShading: true,
      }),
    []
  );

  // Recessed Glossy Visor Screen with PolygonOffset
  const screenMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#050811",
        roughness: 0.08,
        metalness: 0.90,
        polygonOffset: true,
        polygonOffsetFactor: -1,
        polygonOffsetUnits: -1,
      }),
    []
  );

  const glowMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: accentColor,
        emissive: eyeGlowColor,
        emissiveIntensity: isSpeaking ? 3.0 : 1.8,
        roughness: 0.20,
      }),
    [accentColor, eyeGlowColor, isSpeaking]
  );

  const haloMat = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: accentColor,
        transparent: true,
        opacity: 0.42,
      }),
    [accentColor]
  );

  const goldOrbMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#FFD166",
        emissive: "#FFD166",
        emissiveIntensity: 2.2,
        roughness: 0.20,
      }),
    []
  );

  // =========================================================================
  // 4. EMOTIVE EYE SHAPES (LED Pills on Visor)
  // =========================================================================
  let eyeScaleY = 1.0;
  let eyeScaleX = 1.0;
  let eyeRotZ_L = 0.0;
  let eyeRotZ_R = 0.0;
  let eyePosY = 0.06;

  if (emotion === "deadpan" || emotion === "tired") {
    eyeScaleY = 0.42; // Half-lidded deadpan glance
    eyePosY = 0.04;
  } else if (emotion === "shocked") {
    eyeScaleY = 1.50;
    eyeScaleX = 1.35;
    eyePosY = 0.08;
  } else if (emotion === "angry") {
    eyeScaleY = 0.70;
    eyeRotZ_L = -0.32;
    eyeRotZ_R = 0.32;
    eyePosY = 0.04;
  } else if (emotion === "smug") {
    eyeScaleY = 0.80;
    eyeRotZ_L = 0.22;
    eyeRotZ_R = -0.06;
    eyePosY = 0.06;
  }

  // Blink collapses eyes to a thin horizontal slit
  if (isBlinking) {
    eyeScaleY = 0.08;
  }

  // =========================================================================
  // 5. 7-BAR GLOWING AUDIO EQUALIZER MOUTH
  // =========================================================================
  const barOffsets = [-0.24, -0.16, -0.08, 0.0, 0.08, 0.16, 0.24];
  const barMultipliers = [0.55, 0.85, 1.25, 1.50, 1.25, 0.85, 0.55];

  return (
    <group
      position={[position[0], position[1] + hoverY, position[2]]}
      rotation={[rotation[0] + hoverTiltX, rotation[1], rotation[2] + hoverTiltZ]}
      scale={[scale, scale, scale]}
    >
      {/* =================================================================== */}
      {/* 1. FACETED LOW-POLY ORB CHASSIS (Z-Squashed to max Z = 0.84)        */}
      {/* =================================================================== */}
      <mesh scale={[1.0, 1.0, 0.84]} material={shellMat}>
        <icosahedronGeometry args={[1.0, 1]} />
      </mesh>

      {/* =================================================================== */}
      {/* 2. RECESSED GLOSSY BLACK VISOR (Zero Z-Fighting, 0% Shell Poke)    */}
      {/* =================================================================== */}
      {/* Dark Circular Bezel Ring at z = 0.86 */}
      <mesh position={[0, 0.02, 0.86]} rotation={[Math.PI / 2, 0, 0]} material={darkBezelMat}>
        <cylinderGeometry args={[0.60, 0.60, 0.08, 16]} />
      </mesh>

      {/* Glossy Black Screen Faceplate at z = 0.91 */}
      <mesh position={[0, 0.02, 0.91]} rotation={[Math.PI / 2, 0, 0]} material={screenMat}>
        <cylinderGeometry args={[0.54, 0.54, 0.02, 24]} />
      </mesh>

      {/* =================================================================== */}
      {/* 3. EXPRESSIVE GLOWING LED EYES AT z = 0.94                          */}
      {/* =================================================================== */}
      <group position={[0, 0.02 + eyePosY, 0.94]}>
        {/* Left Eye */}
        <mesh
          position={[-0.18, 0, 0]}
          rotation={[0, 0, eyeRotZ_L]}
          scale={[eyeScaleX, eyeScaleY, 1]}
          material={glowMat}
        >
          <boxGeometry args={[0.15, 0.09, 0.02]} />
        </mesh>

        {/* Right Eye */}
        <mesh
          position={[0.18, 0, 0]}
          rotation={[0, 0, eyeRotZ_R]}
          scale={[eyeScaleX, eyeScaleY, 1]}
          material={glowMat}
        >
          <boxGeometry args={[0.15, 0.09, 0.02]} />
        </mesh>
      </group>

      {/* =================================================================== */}
      {/* 4. 7-BAR GLOWING EQUALIZER MOUTH AT z = 0.94                        */}
      {/* =================================================================== */}
      <group position={[0, -0.22, 0.94]}>
        {barOffsets.map((x, i) => {
          const mult = barMultipliers[i];
          const barHeight =
            isSpeaking && mouthOpen > 0.02
              ? 0.035 +
                mouthOpen *
                  mult *
                  (0.16 + 0.05 * Math.sin(frame * 0.45 + i * 0.85))
              : 0.020;

          return (
            <mesh key={i} position={[x, 0, 0]} material={glowMat}>
              <boxGeometry args={[0.045, barHeight, 0.02]} />
            </mesh>
          );
        })}
      </group>

      {/* =================================================================== */}
      {/* 5. CUTE ANTENNAS (Character Distinct with Glowing Tips)             */}
      {/* =================================================================== */}
      {isClaude && (
        // Claude Dual Academic Swept-Back Antennas
        <group position={[0, 0.92, 0]}>
          {[-0.44, 0.44].map((x, i) => (
            <group key={i} position={[x, 0, 0]} rotation={[0, 0, (i === 0 ? 1 : -1) * 0.28]}>
              <mesh material={shellMat}>
                <cylinderGeometry args={[0.03, 0.04, 0.38, 6]} />
              </mesh>
              <mesh position={[0, 0.22, 0]} material={glowMat}>
                <sphereGeometry args={[0.07, 6, 6]} />
              </mesh>
            </group>
          ))}
        </group>
      )}

      {(isGemini || isAntigravity) && (
        // Gemini / Antigravity Top Antenna with Glowing Plasma Orb + Side Ear Bolts
        <>
          <group position={[0, 1.10, 0]}>
            <mesh material={darkBezelMat}>
              <cylinderGeometry args={[0.035, 0.045, 0.35, 6]} />
            </mesh>
            <mesh position={[0, 0.22, 0]} material={isGemini ? goldOrbMat : glowMat}>
              <sphereGeometry args={[0.10, 8, 8]} />
            </mesh>
          </group>
          {/* Side Bolt Acoustic Ears */}
          {[-1.0, 1.0].map((x, i) => (
            <mesh key={i} position={[x, 0, 0]} rotation={[0, 0, Math.PI / 2]} material={darkBezelMat}>
              <cylinderGeometry args={[0.16, 0.22, 0.16, 6]} />
            </mesh>
          ))}
        </>
      )}

      {isGrok && (
        // Grok Dual Aggressive Crimson Cyber Horns
        <group position={[0, 0.94, 0]}>
          {[-0.46, 0.46].map((x, i) => (
            <group key={i} position={[x, 0, 0]} rotation={[0, 0, (i === 0 ? 1 : -1) * 0.36]}>
              <mesh material={glowMat}>
                <coneGeometry args={[0.08, 0.46, 4]} />
              </mesh>
            </group>
          ))}
        </group>
      )}

      {/* =================================================================== */}
      {/* 6. TRANSLUCENT ORBITING HALO RING (Thin Horizontal-Tilted Ring)     */}
      {/* =================================================================== */}
      <group rotation={[Math.PI * 0.45, 0, 0.14]}>
        <mesh rotation={[0, 0, haloRotY]} material={haloMat}>
          <torusGeometry args={[1.22, 0.015, 6, 32]} />
        </mesh>
      </group>
    </group>
  );
};
