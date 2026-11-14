import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export interface ThreeDinerTurn {
  index: number;
  speaker: string;
  start: number;
  end: number;
  text?: string;
  emotion?: string;
}

export interface ThreeDinerSceneProps {
  speaker: string; // "junior" | "rival" | "dad" | "bot"
  audioAmplitude: number; // 0.0 to 1.0
  cameraTarget?: "wide" | "junior" | "rival" | "dad" | "bot" | "auto";
  shake?: boolean;
  turns?: ThreeDinerTurn[];
  hasDad?: boolean;
}

/**
 * 3D Antigravity Terracotta Bot
 * Spherical faceted body, glowing OLED eyes, antenna, side bolts, and dynamic audio-reactive 5-bar equalizer mouth
 */
const AntigravityBot3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const bobY = Math.sin(frame * 0.06) * 0.06;
  const tiltZ = Math.sin(frame * 0.04) * 0.03;
  const speakAmp = isSpeaking ? amplitude : 0.05;

  return (
    <group position={[1.4, -0.3 + bobY, 0.3]} rotation={[0.06, -0.32, tiltZ]}>
      {/* 1. Terracotta Faceted Spherical Chassis */}
      <mesh>
        <dodecahedronGeometry args={[0.88, 1]} />
        <meshStandardMaterial
          color="#D95A2B"
          roughness={0.55}
          metalness={0.12}
          flatShading
        />
      </mesh>

      {/* 2. Top Antenna */}
      <mesh position={[0, 1.05, 0]}>
        <cylinderGeometry args={[0.03, 0.04, 0.42, 6]} />
        <meshStandardMaterial color="#8C3518" roughness={0.5} flatShading />
      </mesh>
      <mesh position={[0, 1.32, 0]}>
        <sphereGeometry args={[0.09, 8, 8]} />
        <meshStandardMaterial
          color="#FFD166"
          emissive="#FFD166"
          emissiveIntensity={1.0}
        />
      </mesh>

      {/* 3. Side Bolt Ears */}
      <mesh position={[-0.92, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.16, 0.22, 0.18, 6]} />
        <meshStandardMaterial color="#A23B18" roughness={0.6} flatShading />
      </mesh>
      <mesh position={[0.92, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.16, 0.22, 0.18, 6]} />
        <meshStandardMaterial color="#A23B18" roughness={0.6} flatShading />
      </mesh>

      {/* 4. Circular Obsidian OLED Display Faceplate (Facing forward Z) */}
      <mesh position={[0, 0.02, 0.76]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 0.06, 24]} />
        <meshStandardMaterial color="#0A0F1A" roughness={0.2} metalness={0.8} />
      </mesh>

      {/* 5. Glowing Capsule OLED Eyes */}
      <mesh position={[-0.2, 0.16, 0.81]} rotation={[0, 0, Math.PI / 2]}>
        <capsuleGeometry args={[0.065, 0.13, 4, 8]} />
        <meshStandardMaterial
          color="#FFD166"
          emissive="#FFD166"
          emissiveIntensity={1.5}
        />
      </mesh>
      <mesh position={[0.2, 0.16, 0.81]} rotation={[0, 0, Math.PI / 2]}>
        <capsuleGeometry args={[0.065, 0.13, 4, 8]} />
        <meshStandardMaterial
          color="#FFD166"
          emissive="#FFD166"
          emissiveIntensity={1.5}
        />
      </mesh>

      {/* 6. Dynamic 5-Bar Equalizer Mouth (Audio-reactive scale Y) */}
      {[-0.22, -0.11, 0, 0.11, 0.22].map((xOffset, i) => {
        const multiplier = [0.7, 1.0, 1.4, 1.0, 0.7][i];
        const barScaleY = Math.max(0.3, speakAmp * 3.4 * multiplier);

        return (
          <mesh
            key={i}
            position={[xOffset, -0.18, 0.81]}
            scale={[1, barScaleY, 1]}
          >
            <boxGeometry args={[0.065, 0.12, 0.02]} />
            <meshStandardMaterial
              color="#FFD166"
              emissive="#FFD166"
              emissiveIntensity={isSpeaking ? 1.8 : 0.6}
            />
          </mesh>
        );
      })}

      {/* Warm Golden Glow on Desk */}
      <pointLight
        position={[0, 0, 1.0]}
        color="#FFB703"
        intensity={isSpeaking ? 2.5 : 1.2}
        distance={3.2}
      />
    </group>
  );
};

/**
 * 3D Low-Poly Junior Developer
 * Beanie, faceted head, white & dark eyes, responsive eyebrows, audio-reactive mouth, hoodie
 */
const JuniorDev3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const headNod = isSpeaking ? Math.sin(frame * 0.18) * 0.04 : Math.sin(frame * 0.04) * 0.015;
  const mouthOpen = isSpeaking ? Math.max(0.08, amplitude * 0.45) : 0.04;
  const eyebrowTilt = isSpeaking ? -0.14 : 0.0;

  return (
    <group position={[-1.4, -0.65, 0.1]} rotation={[0.05 + headNod, 0.26, 0]}>
      {/* 1. Hoodie Torso & Shoulders */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.55, 1.2, 0.9]} />
        <meshStandardMaterial color="#1E293B" roughness={0.7} flatShading />
      </mesh>
      {/* White Drawstrings */}
      <mesh position={[-0.16, -1.0, 0.5]}>
        <cylinderGeometry args={[0.02, 0.02, 0.42, 6]} />
        <meshStandardMaterial color="#F1F5F9" roughness={0.5} />
      </mesh>
      <mesh position={[0.16, -1.0, 0.5]}>
        <cylinderGeometry args={[0.02, 0.02, 0.42, 6]} />
        <meshStandardMaterial color="#F1F5F9" roughness={0.5} />
      </mesh>

      {/* 2. Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.22, 0.26, 0.32, 8]} />
        <meshStandardMaterial color="#A3704C" roughness={0.7} flatShading />
      </mesh>

      {/* 3. Faceted Low-Poly Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.64, 1]} />
        <meshStandardMaterial color="#B88258" roughness={0.65} flatShading />
      </mesh>

      {/* 4. Knit Folded Beanie */}
      <mesh position={[0, 0.3, 0.04]}>
        <sphereGeometry args={[0.68, 12, 10, 0, Math.PI * 2, 0, Math.PI / 1.8]} />
        <meshStandardMaterial color="#1E222A" roughness={0.8} flatShading />
      </mesh>
      <mesh position={[0, 0.18, 0.06]}>
        <torusGeometry args={[0.64, 0.09, 8, 16]} />
        <meshStandardMaterial color="#111827" roughness={0.9} flatShading />
      </mesh>

      {/* 5. Expressive Floating Eyebrows */}
      <mesh position={[-0.2, 0.07, 0.62]} rotation={[0, 0, eyebrowTilt]}>
        <boxGeometry args={[0.18, 0.06, 0.06]} />
        <meshStandardMaterial color="#0F172A" roughness={0.8} />
      </mesh>
      <mesh position={[0.2, 0.07, 0.62]} rotation={[0, 0, -eyebrowTilt]}>
        <boxGeometry args={[0.18, 0.06, 0.06]} />
        <meshStandardMaterial color="#0F172A" roughness={0.8} />
      </mesh>

      {/* 6. Glossy Eyes */}
      <group position={[-0.18, -0.06, 0.6]}>
        <mesh>
          <sphereGeometry args={[0.07, 12, 12]} />
          <meshStandardMaterial color="#F8FAFC" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0, 0.045]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial color="#0F172A" roughness={0.1} />
        </mesh>
      </group>
      <group position={[0.18, -0.06, 0.6]}>
        <mesh>
          <sphereGeometry args={[0.07, 12, 12]} />
          <meshStandardMaterial color="#F8FAFC" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0, 0.045]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshStandardMaterial color="#0F172A" roughness={0.1} />
        </mesh>
      </group>

      {/* 7. Audio-Reactive Mouth */}
      <mesh position={[0, -0.32, 0.62]} scale={[1, mouthOpen * 4, 1]}>
        <boxGeometry args={[0.22, 0.08, 0.06]} />
        <meshStandardMaterial color="#4A1E14" roughness={0.7} />
      </mesh>

      {/* Laptop Model on Table */}
      <group position={[0.1, -0.7, 0.8]} rotation={[0, -0.3, 0]}>
        {/* Base */}
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.8, 0.03, 0.55]} />
          <meshStandardMaterial color="#94A3B8" metalness={0.8} roughness={0.2} />
        </mesh>
        {/* Screen */}
        <mesh position={[0, 0.28, -0.27]} rotation={[-0.32, 0, 0]}>
          <boxGeometry args={[0.8, 0.55, 0.03]} />
          <meshStandardMaterial color="#0F172A" metalness={0.5} roughness={0.3} />
        </mesh>
        {/* Glowing Code Screen */}
        <mesh position={[0, 0.28, -0.25]} rotation={[-0.32, 0, 0]}>
          <planeGeometry args={[0.74, 0.49]} />
          <meshStandardMaterial
            color="#38BDF8"
            emissive="#38BDF8"
            emissiveIntensity={0.6}
          />
        </mesh>
      </group>
    </group>
  );
};

/**
 * 3D Indian / Boomer Dad Character
 * Spectacles, thick majestic moustache, orange/burnt polo shirt with white collar,
 * expressive head shake, audio-reactive mouth, and steaming chai cup on table!
 */
const DadCharacter3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  // Scolding dad head shake when speaking
  const headWag = isSpeaking
    ? Math.sin(frame * 0.22) * 0.06
    : Math.sin(frame * 0.03) * 0.015;
  const mouthOpen = isSpeaking ? Math.max(0.08, amplitude * 0.5) : 0.03;
  const eyebrowDisbelief = isSpeaking ? 0.12 : 0.0;

  return (
    <group position={[0.0, -0.65, 0.2]} rotation={[0.06, headWag, 0]}>
      {/* 1. Classic Burnt Orange / Polo Shirt with Collar */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.65, 1.25, 0.95]} />
        <meshStandardMaterial color="#C2410C" roughness={0.75} flatShading />
      </mesh>
      {/* Beige Inner Collar */}
      <mesh position={[0, -0.72, 0.46]}>
        <boxGeometry args={[0.42, 0.16, 0.1]} />
        <meshStandardMaterial color="#FEF3C7" roughness={0.6} />
      </mesh>

      {/* 2. Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.24, 0.28, 0.34, 8]} />
        <meshStandardMaterial color="#A3704C" roughness={0.7} flatShading />
      </mesh>

      {/* 3. Faceted Low-Poly Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.66, 1]} />
        <meshStandardMaterial color="#B88258" roughness={0.65} flatShading />
      </mesh>

      {/* 4. Distinguished Side-Parted Hair (Dark with Grey Temples) */}
      <mesh position={[0, 0.28, 0.02]}>
        <sphereGeometry args={[0.69, 12, 10, 0, Math.PI * 2, 0, Math.PI / 1.7]} />
        <meshStandardMaterial color="#334155" roughness={0.8} flatShading />
      </mesh>
      {/* Grey Temple Highlights */}
      <mesh position={[-0.52, 0.08, 0.1]}>
        <boxGeometry args={[0.16, 0.24, 0.3]} />
        <meshStandardMaterial color="#94A3B8" roughness={0.7} flatShading />
      </mesh>
      <mesh position={[0.52, 0.08, 0.1]}>
        <boxGeometry args={[0.16, 0.24, 0.3]} />
        <meshStandardMaterial color="#94A3B8" roughness={0.7} flatShading />
      </mesh>

      {/* 5. Classic Horn-Rim Eyeglasses */}
      <group position={[0, -0.06, 0.65]}>
        {/* Left Frame */}
        <mesh position={[-0.2, 0, 0]}>
          <torusGeometry args={[0.14, 0.022, 6, 16]} />
          <meshStandardMaterial color="#0F172A" roughness={0.3} metalness={0.6} />
        </mesh>
        {/* Right Frame */}
        <mesh position={[0.2, 0, 0]}>
          <torusGeometry args={[0.14, 0.022, 6, 16]} />
          <meshStandardMaterial color="#0F172A" roughness={0.3} metalness={0.6} />
        </mesh>
        {/* Bridge */}
        <mesh position={[0, 0.04, 0]}>
          <boxGeometry args={[0.12, 0.025, 0.02]} />
          <meshStandardMaterial color="#0F172A" roughness={0.3} metalness={0.6} />
        </mesh>
        {/* Eyes behind lenses */}
        <mesh position={[-0.2, 0, -0.05]}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial color="#0F172A" />
        </mesh>
        <mesh position={[0.2, 0, -0.05]}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial color="#0F172A" />
        </mesh>
      </group>

      {/* 6. High-Arching Skeptical Eyebrows */}
      <mesh position={[-0.2, 0.12 + eyebrowDisbelief, 0.64]} rotation={[0, 0, -0.08]}>
        <boxGeometry args={[0.20, 0.06, 0.06]} />
        <meshStandardMaterial color="#1E293B" roughness={0.9} />
      </mesh>
      <mesh position={[0.2, 0.12 + eyebrowDisbelief, 0.64]} rotation={[0, 0, 0.08]}>
        <boxGeometry args={[0.20, 0.06, 0.06]} />
        <meshStandardMaterial color="#1E293B" roughness={0.9} />
      </mesh>

      {/* 7. Majestic Thick Dad Moustache */}
      <mesh position={[0, -0.22, 0.68]}>
        <boxGeometry args={[0.38, 0.10, 0.09]} />
        <meshStandardMaterial color="#0F172A" roughness={0.9} />
      </mesh>

      {/* 8. Audio-Reactive Mouth under moustache */}
      <mesh position={[0, -0.35, 0.62]} scale={[1, mouthOpen * 4, 1]}>
        <boxGeometry args={[0.24, 0.08, 0.06]} />
        <meshStandardMaterial color="#4A1E14" roughness={0.7} />
      </mesh>

      {/* Steaming Chai Cup & Saucer on Table */}
      <group position={[0.35, -0.72, 0.75]}>
        {/* Saucer */}
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.25, 0.22, 0.03, 16]} />
          <meshStandardMaterial color="#FFFFFF" roughness={0.2} />
        </mesh>
        {/* Chai Cup */}
        <mesh position={[0, 0.14, 0]}>
          <cylinderGeometry args={[0.14, 0.11, 0.25, 16]} />
          <meshStandardMaterial color="#FFFFFF" roughness={0.2} />
        </mesh>
        {/* Brown Spiced Chai */}
        <mesh position={[0, 0.24, 0]}>
          <cylinderGeometry args={[0.13, 0.13, 0.02, 16]} />
          <meshStandardMaterial color="#9A3412" roughness={0.4} />
        </mesh>
      </group>
    </group>
  );
};

/**
 * 3D Rival Senior Developer (or Claude/SaaS Defender)
 */
const RivalDev3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const headNod = isSpeaking ? Math.sin(frame * 0.18) * 0.04 : 0;
  const mouthOpen = isSpeaking ? Math.max(0.08, amplitude * 0.45) : 0.04;

  return (
    <group position={[0.0, -0.65, 0.2]} rotation={[0.05 + headNod, -0.1, 0]}>
      {/* 1. Sharp Corporate Blazer */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.6, 1.25, 0.9]} />
        <meshStandardMaterial color="#334155" roughness={0.65} flatShading />
      </mesh>
      {/* Inner Shirt & Tie */}
      <mesh position={[0, -0.85, 0.47]}>
        <boxGeometry args={[0.3, 0.4, 0.06]} />
        <meshStandardMaterial color="#F8FAFC" roughness={0.5} />
      </mesh>
      <mesh position={[0, -1.05, 0.51]}>
        <boxGeometry args={[0.08, 0.45, 0.04]} />
        <meshStandardMaterial color="#EF4444" roughness={0.6} />
      </mesh>

      {/* 2. Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.22, 0.26, 0.32, 8]} />
        <meshStandardMaterial color="#A3704C" roughness={0.7} flatShading />
      </mesh>

      {/* 3. Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.64, 1]} />
        <meshStandardMaterial color="#B88258" roughness={0.65} flatShading />
      </mesh>

      {/* 4. Styled Slick Hair */}
      <mesh position={[0, 0.3, 0.04]}>
        <sphereGeometry args={[0.68, 12, 10, 0, Math.PI * 2, 0, Math.PI / 1.8]} />
        <meshStandardMaterial color="#1E293B" roughness={0.6} flatShading />
      </mesh>

      {/* 5. Eyeglasses */}
      <group position={[0, -0.06, 0.65]}>
        <mesh position={[-0.18, 0, 0]}>
          <boxGeometry args={[0.26, 0.16, 0.02]} />
          <meshStandardMaterial color="#0F172A" metalness={0.8} roughness={0.2} />
        </mesh>
        <mesh position={[0.18, 0, 0]}>
          <boxGeometry args={[0.26, 0.16, 0.02]} />
          <meshStandardMaterial color="#0F172A" metalness={0.8} roughness={0.2} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.1, 0.02, 0.02]} />
          <meshStandardMaterial color="#0F172A" />
        </mesh>
      </group>

      {/* 6. Mouth */}
      <mesh position={[0, -0.32, 0.62]} scale={[1, mouthOpen * 4, 1]}>
        <boxGeometry args={[0.22, 0.08, 0.06]} />
        <meshStandardMaterial color="#4A1E14" roughness={0.7} />
      </mesh>
    </group>
  );
};

/**
 * 3D Diner Table & Environment Props
 */
const CafeEnvironment3D: React.FC = () => {
  return (
    <group position={[0, -0.7, 0]}>
      {/* 1. Polished Diner Counter / Table */}
      <mesh position={[0, -0.76, 0.6]}>
        <boxGeometry args={[5.2, 0.14, 1.8]} />
        <meshStandardMaterial
          color="#3B2314"
          roughness={0.3}
          metalness={0.2}
        />
      </mesh>

      {/* 2. Chrome Table Rim */}
      <mesh position={[0, -0.76, 1.51]}>
        <boxGeometry args={[5.22, 0.15, 0.04]} />
        <meshStandardMaterial color="#E2E8F0" metalness={0.9} roughness={0.1} />
      </mesh>

      {/* 3. Diner Neon Backwall */}
      <mesh position={[0, 1.8, -3.2]}>
        <planeGeometry args={[14, 10]} />
        <meshStandardMaterial color="#0B0F19" roughness={0.8} />
      </mesh>

      {/* 4. Glowing Neon Accent Line */}
      <mesh position={[0, 2.8, -3.15]}>
        <boxGeometry args={[10, 0.08, 0.04]} />
        <meshStandardMaterial
          color="#00F0FF"
          emissive="#00F0FF"
          emissiveIntensity={1.8}
        />
      </mesh>
    </group>
  );
};

export const ThreeDinerScene: React.FC<ThreeDinerSceneProps> = ({
  speaker = "junior",
  audioAmplitude = 0.0,
  cameraTarget = "auto",
  shake = false,
  turns = [],
  hasDad = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const isJuniorSpeaking = speaker === "junior" || speaker === "human" || speaker === "dev";
  const isDadSpeaking = speaker === "dad" || speaker === "father" || speaker === "uncle";
  const isRivalSpeaking = (speaker === "rival" || speaker === "senior" || speaker === "claude") && !isDadSpeaking;
  const isBotSpeaking = speaker === "bot" || speaker === "gemini" || speaker === "antigravity";

  // Coordinates lookup for each character camera target
  const getCameraCoords = (target: string) => {
    switch (target) {
      case "junior":
        return { x: -0.65, y: -0.12, z: 6.6, fov: 41 };
      case "dad":
        return { x: 0.0, y: -0.08, z: 6.4, fov: 40 };
      case "rival":
        return { x: 0.0, y: -0.12, z: 6.6, fov: 41 };
      case "bot":
        return { x: 0.65, y: -0.05, z: 6.3, fov: 39 };
      case "wide":
      default:
        return { x: 0.0, y: 0.20, z: 8.2, fov: 46 };
    }
  };

  // Determine current active target
  let currentTarget = "wide";
  if (cameraTarget !== "auto") {
    currentTarget = cameraTarget;
  } else if (isJuniorSpeaking) {
    currentTarget = "junior";
  } else if (isDadSpeaking) {
    currentTarget = "dad";
  } else if (isRivalSpeaking) {
    currentTarget = "rival";
  } else if (isBotSpeaking) {
    currentTarget = "bot";
  }

  // Butter-smooth camera transitions using turn progress & spring physics
  const targetCoords = getCameraCoords(currentTarget);

  // Find current turn index and when it started
  const currentTime = frame / fps;
  let turnStartFrame = 0;
  let prevTarget = "wide";

  if (turns && turns.length > 0) {
    for (let i = 0; i < turns.length; i++) {
      if (currentTime >= turns[i].start && currentTime <= turns[i].end + 0.15) {
        turnStartFrame = Math.floor(turns[i].start * fps);
        if (i > 0) {
          const prevSpk = turns[i - 1].speaker.toLowerCase();
          if (prevSpk.includes("dad")) prevTarget = "dad";
          else if (prevSpk.includes("junior") || prevSpk.includes("human")) prevTarget = "junior";
          else if (prevSpk.includes("bot") || prevSpk.includes("gemini")) prevTarget = "bot";
          else prevTarget = "rival";
        }
        break;
      }
    }
  }

  const prevCoords = getCameraCoords(prevTarget);

  // Transition progress over 14 frames from turn start
  const framesSinceTurn = Math.max(0, frame - turnStartFrame);
  const transition = spring({
    frame: framesSinceTurn,
    fps,
    config: { damping: 16, stiffness: 130, mass: 0.8 },
  });

  const smoothX = interpolate(transition, [0, 1], [prevCoords.x, targetCoords.x], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const smoothY = interpolate(transition, [0, 1], [prevCoords.y, targetCoords.y], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const smoothZ = interpolate(transition, [0, 1], [prevCoords.z, targetCoords.z], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const smoothFov = interpolate(transition, [0, 1], [prevCoords.fov, targetCoords.fov], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Steadycam organic micro-drift
  const driftX = Math.sin(frame * 0.02) * 0.03;
  const driftY = Math.cos(frame * 0.025) * 0.02;

  // Impact shake on roast punchlines
  const shakeOffset = shake ? Math.sin(frame * 1.5) * 0.07 : 0.0;

  const camX = smoothX + driftX + shakeOffset;
  const camY = smoothY + driftY;
  const camZ = smoothZ;
  const camFov = smoothFov;

  // Decide if we render Dad or Rival in the center seat
  const showDad = hasDad || isDadSpeaking || turns.some((t) => t.speaker.toLowerCase().includes("dad"));

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: "absolute",
        top: 0,
        left: 0,
        pointerEvents: "none",
      }}
    >
      <ThreeCanvas
        width={1080}
        height={1920}
        camera={{
          position: [camX, camY, camZ],
          fov: camFov,
          near: 0.1,
          far: 100,
        }}
      >
        {/* Warm Studio Ambient Light */}
        <ambientLight intensity={1.2} color="#F1F5F9" />

        {/* Directional Sun Key Light */}
        <directionalLight
          position={[4.5, 7.5, 6.0]}
          intensity={2.4}
          color="#FFF7ED"
        />

        {/* Soft Cool Fill Light */}
        <directionalLight
          position={[-5.0, 4.0, 4.0]}
          intensity={1.1}
          color="#94A3B8"
        />

        {/* Back Rim Light */}
        <pointLight
          position={[0, 3.2, -2.5]}
          intensity={2.6}
          color="#38BDF8"
          distance={12}
        />

        {/* 3D Cafe Environment */}
        <CafeEnvironment3D />

        {/* Character 1: Junior Dev (Left) */}
        <JuniorDev3D
          isSpeaking={isJuniorSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />

        {/* Character 2: Either Dad (Unbeatable Logic) or Rival Senior Dev (Center) */}
        {showDad ? (
          <DadCharacter3D
            isSpeaking={isDadSpeaking}
            amplitude={audioAmplitude}
            frame={frame}
          />
        ) : (
          <RivalDev3D
            isSpeaking={isRivalSpeaking}
            amplitude={audioAmplitude}
            frame={frame}
          />
        )}

        {/* Character 3: Google Antigravity Bot (Right) */}
        <AntigravityBot3D
          isSpeaking={isBotSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />
      </ThreeCanvas>
    </div>
  );
};
