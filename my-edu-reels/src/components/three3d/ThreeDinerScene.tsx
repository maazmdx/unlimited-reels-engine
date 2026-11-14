import React, { useMemo } from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, interpolate, spring, useVideoConfig, staticFile } from "remotion";
import * as THREE from "three";

export interface ThreeDinerTurn {
  index: number;
  speaker: string;
  start: number;
  end: number;
  text?: string;
  emotion?: string;
}

export interface ThreeDinerSceneProps {
  speaker: string; // "junior" | "rival" | "dad" | "bot" | "claude" | "grok" | "codex"
  audioAmplitude: number; // 0.0 to 1.0
  cameraTarget?: "wide" | "junior" | "rival" | "dad" | "bot" | "claude" | "grok" | "codex" | "auto";
  shake?: boolean;
  turns?: ThreeDinerTurn[];
  hasDad?: boolean;
  bgImage?: string;
}

// =====================================================================
// 1. Google Antigravity AI Bot (Terracotta Faceted + Gemini Star Logo)
// =====================================================================
const AntigravityBot3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const bobY = Math.sin(frame * 0.06) * 0.06;
  const tiltZ = Math.sin(frame * 0.04) * 0.03;
  const speakAmp = isSpeaking ? amplitude : 0.05;

  const logoTex = useMemo(() => {
    return new THREE.TextureLoader().load(staticFile("logos/logo_antigravity.png"));
  }, []);

  return (
    <group position={[1.4, -0.3 + bobY, 0.3]} rotation={[0.06, -0.32, tiltZ]}>
      {/* Faceted Low-Poly Body */}
      <mesh>
        <dodecahedronGeometry args={[0.88, 1]} />
        <meshStandardMaterial color="#D95A2B" roughness={0.55} metalness={0.12} flatShading />
      </mesh>

      {/* Top Antenna */}
      <mesh position={[0, 1.05, 0]}>
        <cylinderGeometry args={[0.03, 0.04, 0.42, 6]} />
        <meshStandardMaterial color="#8C3518" roughness={0.5} flatShading />
      </mesh>
      <mesh position={[0, 1.32, 0]}>
        <sphereGeometry args={[0.09, 8, 8]} />
        <meshStandardMaterial color="#FFD166" emissive="#FFD166" emissiveIntensity={1.2} />
      </mesh>

      {/* Side Bolt Ears */}
      <mesh position={[-0.92, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.16, 0.22, 0.18, 6]} />
        <meshStandardMaterial color="#A23B18" roughness={0.6} flatShading />
      </mesh>
      <mesh position={[0.92, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.16, 0.22, 0.18, 6]} />
        <meshStandardMaterial color="#A23B18" roughness={0.6} flatShading />
      </mesh>

      {/* Obsidian Faceplate Base */}
      <mesh position={[0, 0.02, 0.76]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 0.06, 24]} />
        <meshStandardMaterial color="#0A0F1A" roughness={0.2} metalness={0.8} />
      </mesh>

      {/* Official Glowing Google Antigravity / Gemini Logo on Face */}
      <mesh position={[0, 0.08, 0.81]}>
        <planeGeometry args={[0.72, 0.72]} />
        <meshBasicMaterial map={logoTex} transparent={true} />
      </mesh>

      {/* Dynamic 5-Bar Equalizer Mouth */}
      {[-0.22, -0.11, 0, 0.11, 0.22].map((xOffset, i) => {
        const mult = [0.7, 1.0, 1.4, 1.0, 0.7][i];
        const barScaleY = Math.max(0.3, speakAmp * 3.4 * mult);
        return (
          <mesh key={i} position={[xOffset, -0.22, 0.81]} scale={[1, barScaleY, 1]}>
            <boxGeometry args={[0.065, 0.10, 0.02]} />
            <meshStandardMaterial color="#38BDF8" emissive="#38BDF8" emissiveIntensity={isSpeaking ? 2.0 : 0.7} />
          </mesh>
        );
      })}

      <pointLight position={[0, 0, 1.0]} color="#38BDF8" intensity={isSpeaking ? 2.5 : 1.2} distance={3.2} />
    </group>
  );
};

// =====================================================================
// 2. Anthropic Claude AI Bot (Warm Terracotta / Amber + Claude Asterisk Logo)
// =====================================================================
const ClaudeBot3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
  position?: [number, number, number];
  rotation?: [number, number, number];
}> = ({ isSpeaking, amplitude, frame, position = [0.0, -0.35, 0.2], rotation = [0.05, 0.0, 0] }) => {
  const bobY = Math.sin(frame * 0.05 + 1) * 0.05;
  const speakAmp = isSpeaking ? amplitude : 0.04;

  const logoTex = useMemo(() => {
    return new THREE.TextureLoader().load(staticFile("logos/logo_claude.png"));
  }, []);

  return (
    <group position={[position[0], position[1] + bobY, position[2]]} rotation={rotation}>
      {/* Warm Terracotta Faceted Low-Poly Body */}
      <mesh>
        <dodecahedronGeometry args={[0.88, 1]} />
        <meshStandardMaterial color="#CC785C" roughness={0.6} metalness={0.15} flatShading />
      </mesh>

      {/* Dual Curved Academic Side Antennas */}
      <mesh position={[-0.45, 0.95, 0]} rotation={[0, 0, 0.25]}>
        <cylinderGeometry args={[0.03, 0.04, 0.35, 6]} />
        <meshStandardMaterial color="#994D33" roughness={0.6} flatShading />
      </mesh>
      <mesh position={[0.45, 0.95, 0]} rotation={[0, 0, -0.25]}>
        <cylinderGeometry args={[0.03, 0.04, 0.35, 6]} />
        <meshStandardMaterial color="#994D33" roughness={0.6} flatShading />
      </mesh>

      {/* Faceplate Base */}
      <mesh position={[0, 0.02, 0.76]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 0.06, 24]} />
        <meshStandardMaterial color="#1C140E" roughness={0.2} metalness={0.7} />
      </mesh>

      {/* Official Glowing Anthropic Claude Asterisk Logo on Face */}
      <mesh position={[0, 0.08, 0.81]}>
        <planeGeometry args={[0.72, 0.72]} />
        <meshBasicMaterial map={logoTex} transparent={true} />
      </mesh>

      {/* Warm Amber Equalizer Mouth */}
      {[-0.18, 0, 0.18].map((xOffset, i) => {
        const mult = [0.8, 1.3, 0.8][i];
        const barScaleY = Math.max(0.3, speakAmp * 3.2 * mult);
        return (
          <mesh key={i} position={[xOffset, -0.22, 0.81]} scale={[1, barScaleY, 1]}>
            <boxGeometry args={[0.09, 0.10, 0.02]} />
            <meshStandardMaterial color="#F59E0B" emissive="#F59E0B" emissiveIntensity={isSpeaking ? 2.0 : 0.6} />
          </mesh>
        );
      })}

      <pointLight position={[0, 0, 1.0]} color="#F59E0B" intensity={isSpeaking ? 2.2 : 0.9} distance={3.0} />
    </group>
  );
};

// =====================================================================
// 3. OpenAI Codex Bot (Obsidian & Emerald Green + OpenAI Rosette Logo)
// =====================================================================
const CodexBot3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const bobY = Math.sin(frame * 0.05 + 2) * 0.05;
  const speakAmp = isSpeaking ? amplitude : 0.04;

  const logoTex = useMemo(() => {
    return new THREE.TextureLoader().load(staticFile("logos/logo_codex.png"));
  }, []);

  return (
    <group position={[0.0, -0.35 + bobY, 0.2]} rotation={[0.05, 0.0, 0]}>
      {/* Obsidian Low-Poly Carbon Chassis */}
      <mesh>
        <icosahedronGeometry args={[0.88, 1]} />
        <meshStandardMaterial color="#0B131E" roughness={0.4} metalness={0.5} flatShading />
      </mesh>

      {/* Emerald Energy Conduits on Shoulders */}
      <mesh position={[-0.75, 0.3, 0]}>
        <boxGeometry args={[0.15, 0.45, 0.25]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={1.2} />
      </mesh>
      <mesh position={[0.75, 0.3, 0]}>
        <boxGeometry args={[0.15, 0.45, 0.25]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={1.2} />
      </mesh>

      {/* Faceplate Base */}
      <mesh position={[0, 0.02, 0.76]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 0.06, 24]} />
        <meshStandardMaterial color="#040A0F" roughness={0.15} metalness={0.9} />
      </mesh>

      {/* Official Glowing OpenAI Codex Rosette Logo on Face */}
      <mesh position={[0, 0.08, 0.81]}>
        <planeGeometry args={[0.72, 0.72]} />
        <meshBasicMaterial map={logoTex} transparent={true} />
      </mesh>

      {/* Neon Emerald Waveform Mouth */}
      {[-0.20, -0.10, 0, 0.10, 0.20].map((xOffset, i) => {
        const mult = [0.7, 1.1, 1.4, 1.1, 0.7][i];
        const barScaleY = Math.max(0.3, speakAmp * 3.4 * mult);
        return (
          <mesh key={i} position={[xOffset, -0.22, 0.81]} scale={[1, barScaleY, 1]}>
            <boxGeometry args={[0.06, 0.09, 0.02]} />
            <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={isSpeaking ? 2.2 : 0.7} />
          </mesh>
        );
      })}

      <pointLight position={[0, 0, 1.0]} color="#10B981" intensity={isSpeaking ? 2.4 : 1.0} distance={3.0} />
    </group>
  );
};

// =====================================================================
// 4. xAI Grok Bot (Sharp Gunmetal Angular + Grok X Logo)
// =====================================================================
const GrokBot3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const bobY = Math.sin(frame * 0.06 + 3) * 0.05;
  const speakAmp = isSpeaking ? amplitude : 0.04;

  const logoTex = useMemo(() => {
    return new THREE.TextureLoader().load(staticFile("logos/logo_grok.png"));
  }, []);

  return (
    <group position={[0.0, -0.35 + bobY, 0.2]} rotation={[0.05, 0.0, 0]}>
      {/* Angular Stealth Chrome/Gunmetal Chassis */}
      <mesh>
        <octahedronGeometry args={[0.90, 1]} />
        <meshStandardMaterial color="#1C1C22" roughness={0.3} metalness={0.7} flatShading />
      </mesh>

      {/* Dual Sharp Cyber Horn Antennas with Red Tips */}
      <mesh position={[-0.48, 0.95, 0]} rotation={[0, 0, 0.35]}>
        <coneGeometry args={[0.07, 0.45, 4]} />
        <meshStandardMaterial color="#EF4444" emissive="#EF4444" emissiveIntensity={1.5} />
      </mesh>
      <mesh position={[0.48, 0.95, 0]} rotation={[0, 0, -0.35]}>
        <coneGeometry args={[0.07, 0.45, 4]} />
        <meshStandardMaterial color="#EF4444" emissive="#EF4444" emissiveIntensity={1.5} />
      </mesh>

      {/* Faceplate Base */}
      <mesh position={[0, 0.02, 0.76]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.56, 0.56, 0.06, 24]} />
        <meshStandardMaterial color="#0A0A0C" roughness={0.1} metalness={0.9} />
      </mesh>

      {/* Official Glowing xAI Grok X Logo on Face */}
      <mesh position={[0, 0.08, 0.81]}>
        <planeGeometry args={[0.72, 0.72]} />
        <meshBasicMaterial map={logoTex} transparent={true} />
      </mesh>

      {/* Stark White Cyber Equalizer Mouth */}
      {[-0.20, -0.10, 0, 0.10, 0.20].map((xOffset, i) => {
        const mult = [0.8, 1.2, 1.5, 1.2, 0.8][i];
        const barScaleY = Math.max(0.3, speakAmp * 3.5 * mult);
        return (
          <mesh key={i} position={[xOffset, -0.22, 0.81]} scale={[1, barScaleY, 1]}>
            <boxGeometry args={[0.065, 0.10, 0.02]} />
            <meshStandardMaterial color="#FFFFFF" emissive="#FFFFFF" emissiveIntensity={isSpeaking ? 2.5 : 0.8} />
          </mesh>
        );
      })}

      <pointLight position={[0, 0, 1.0]} color="#FFFFFF" intensity={isSpeaking ? 2.5 : 1.0} distance={3.0} />
    </group>
  );
};

// =====================================================================
// 5. Low-Poly Junior Developer
// =====================================================================
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
      {/* Hoodie Torso */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.55, 1.2, 0.9]} />
        <meshStandardMaterial color="#1E293B" roughness={0.7} flatShading />
      </mesh>

      {/* Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.22, 0.26, 0.32, 8]} />
        <meshStandardMaterial color="#A3704C" roughness={0.7} flatShading />
      </mesh>

      {/* Faceted Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.64, 1]} />
        <meshStandardMaterial color="#B88258" roughness={0.65} flatShading />
      </mesh>

      {/* Beanie */}
      <mesh position={[0, 0.3, 0.04]}>
        <sphereGeometry args={[0.68, 12, 10, 0, Math.PI * 2, 0, Math.PI / 1.8]} />
        <meshStandardMaterial color="#1E222A" roughness={0.8} flatShading />
      </mesh>

      {/* Eyebrows */}
      <mesh position={[-0.2, 0.07, 0.62]} rotation={[0, 0, eyebrowTilt]}>
        <boxGeometry args={[0.18, 0.06, 0.06]} />
        <meshStandardMaterial color="#0F172A" />
      </mesh>
      <mesh position={[0.2, 0.07, 0.62]} rotation={[0, 0, -eyebrowTilt]}>
        <boxGeometry args={[0.18, 0.06, 0.06]} />
        <meshStandardMaterial color="#0F172A" />
      </mesh>

      {/* Spectacles */}
      <group position={[0, -0.06, 0.62]}>
        <mesh position={[-0.18, 0, 0]}>
          <boxGeometry args={[0.22, 0.14, 0.02]} />
          <meshStandardMaterial color="#0F172A" metalness={0.7} />
        </mesh>
        <mesh position={[0.18, 0, 0]}>
          <boxGeometry args={[0.22, 0.14, 0.02]} />
          <meshStandardMaterial color="#0F172A" metalness={0.7} />
        </mesh>
      </group>

      {/* Mouth */}
      <mesh position={[0, -0.32, 0.62]} scale={[1, mouthOpen * 4, 1]}>
        <boxGeometry args={[0.22, 0.08, 0.06]} />
        <meshStandardMaterial color="#4A1E14" roughness={0.7} />
      </mesh>

      {/* Laptop Model */}
      <group position={[0.1, -0.7, 0.8]} rotation={[0, -0.3, 0]}>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.8, 0.03, 0.55]} />
          <meshStandardMaterial color="#94A3B8" metalness={0.8} roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.28, -0.27]} rotation={[-0.32, 0, 0]}>
          <boxGeometry args={[0.8, 0.55, 0.03]} />
          <meshStandardMaterial color="#0F172A" metalness={0.5} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0.28, -0.25]} rotation={[-0.32, 0, 0]}>
          <planeGeometry args={[0.74, 0.49]} />
          <meshStandardMaterial color="#38BDF8" emissive="#38BDF8" emissiveIntensity={0.6} />
        </mesh>
      </group>
    </group>
  );
};

// =====================================================================
// 6. Low-Poly Indian / Boomer Dad Character
// =====================================================================
const DadCharacter3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const headWag = isSpeaking ? Math.sin(frame * 0.22) * 0.06 : Math.sin(frame * 0.03) * 0.015;
  const mouthOpen = isSpeaking ? Math.max(0.08, amplitude * 0.5) : 0.03;
  const eyebrowDisbelief = isSpeaking ? 0.12 : 0.0;

  return (
    <group position={[0.0, -0.65, 0.2]} rotation={[0.06, headWag, 0]}>
      {/* Burnt Orange Polo Shirt with Beige Collar */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.65, 1.25, 0.95]} />
        <meshStandardMaterial color="#C2410C" roughness={0.75} flatShading />
      </mesh>
      <mesh position={[0, -0.72, 0.46]}>
        <boxGeometry args={[0.42, 0.16, 0.1]} />
        <meshStandardMaterial color="#FEF3C7" roughness={0.6} />
      </mesh>

      {/* Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.24, 0.28, 0.34, 8]} />
        <meshStandardMaterial color="#A3704C" roughness={0.7} flatShading />
      </mesh>

      {/* Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.66, 1]} />
        <meshStandardMaterial color="#B88258" roughness={0.65} flatShading />
      </mesh>

      {/* Side-Parted Hair with Grey Temples */}
      <mesh position={[0, 0.28, 0.02]}>
        <sphereGeometry args={[0.69, 12, 10, 0, Math.PI * 2, 0, Math.PI / 1.7]} />
        <meshStandardMaterial color="#334155" roughness={0.8} flatShading />
      </mesh>
      <mesh position={[-0.52, 0.08, 0.1]}>
        <boxGeometry args={[0.16, 0.24, 0.3]} />
        <meshStandardMaterial color="#94A3B8" roughness={0.7} flatShading />
      </mesh>
      <mesh position={[0.52, 0.08, 0.1]}>
        <boxGeometry args={[0.16, 0.24, 0.3]} />
        <meshStandardMaterial color="#94A3B8" roughness={0.7} flatShading />
      </mesh>

      {/* Spectacles */}
      <group position={[0, -0.06, 0.65]}>
        <mesh position={[-0.2, 0, 0]}>
          <torusGeometry args={[0.14, 0.022, 6, 16]} />
          <meshStandardMaterial color="#0F172A" roughness={0.3} metalness={0.6} />
        </mesh>
        <mesh position={[0.2, 0, 0]}>
          <torusGeometry args={[0.14, 0.022, 6, 16]} />
          <meshStandardMaterial color="#0F172A" roughness={0.3} metalness={0.6} />
        </mesh>
      </group>

      {/* Eyebrows */}
      <mesh position={[-0.2, 0.12 + eyebrowDisbelief, 0.64]} rotation={[0, 0, -0.08]}>
        <boxGeometry args={[0.20, 0.06, 0.06]} />
        <meshStandardMaterial color="#1E293B" roughness={0.9} />
      </mesh>
      <mesh position={[0.2, 0.12 + eyebrowDisbelief, 0.64]} rotation={[0, 0, 0.08]}>
        <boxGeometry args={[0.20, 0.06, 0.06]} />
        <meshStandardMaterial color="#1E293B" roughness={0.9} />
      </mesh>

      {/* Thick Moustache */}
      <mesh position={[0, -0.22, 0.68]}>
        <boxGeometry args={[0.38, 0.10, 0.09]} />
        <meshStandardMaterial color="#0F172A" roughness={0.9} />
      </mesh>

      {/* Mouth */}
      <mesh position={[0, -0.35, 0.62]} scale={[1, mouthOpen * 4, 1]}>
        <boxGeometry args={[0.24, 0.08, 0.06]} />
        <meshStandardMaterial color="#4A1E14" roughness={0.7} />
      </mesh>

      {/* Chai Cup on Table */}
      <group position={[0.35, -0.72, 0.75]}>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.25, 0.22, 0.03, 16]} />
          <meshStandardMaterial color="#FFFFFF" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.14, 0]}>
          <cylinderGeometry args={[0.14, 0.11, 0.25, 16]} />
          <meshStandardMaterial color="#FFFFFF" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.24, 0]}>
          <cylinderGeometry args={[0.13, 0.13, 0.02, 16]} />
          <meshStandardMaterial color="#9A3412" roughness={0.4} />
        </mesh>
      </group>
    </group>
  );
};

// =====================================================================
// 7. Diner Table & 16:9 Scenic Background Projection Screen
// =====================================================================
const CafeEnvironment3D: React.FC<{ bgImage?: string }> = ({
  bgImage = "backgrounds/bg_cyber_diner.jpg",
}) => {
  const bgTexture = useMemo(() => {
    let clean = bgImage;
    if (!clean.startsWith("backgrounds/") && !clean.includes("/")) {
      clean = `backgrounds/${clean}`;
    }
    return new THREE.TextureLoader().load(staticFile(clean));
  }, [bgImage]);

  return (
    <group position={[0, -0.7, 0]}>
      {/* Wooden Table Top */}
      <mesh position={[0, -0.76, 0.6]}>
        <boxGeometry args={[5.2, 0.14, 1.8]} />
        <meshStandardMaterial color="#3B2314" roughness={0.3} metalness={0.2} />
      </mesh>
      {/* Front Chrome Trim */}
      <mesh position={[0, -0.76, 1.51]}>
        <boxGeometry args={[5.22, 0.15, 0.04]} />
        <meshStandardMaterial color="#E2E8F0" metalness={0.9} roughness={0.1} />
      </mesh>
      {/* 16:9 Scenic Environment Billboard Projection */}
      <mesh position={[0, 1.8, -3.2]}>
        <planeGeometry args={[14.2, 8.0]} />
        <meshBasicMaterial map={bgTexture} toneMapped={false} />
      </mesh>
      {/* Contrast Vignette Layer */}
      <mesh position={[0, 1.8, -3.18]}>
        <planeGeometry args={[14.3, 8.1]} />
        <meshBasicMaterial color="#070B14" transparent opacity={0.32} />
      </mesh>
      {/* Top Neon Ambient Light Bar */}
      <mesh position={[0, 2.8, -3.15]}>
        <boxGeometry args={[10, 0.08, 0.04]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" emissiveIntensity={1.8} />
      </mesh>
    </group>
  );
};

// =====================================================================
// Master 3D Scene Controller with Dynamic Roster
// =====================================================================
export const ThreeDinerScene: React.FC<ThreeDinerSceneProps> = ({
  speaker = "junior",
  audioAmplitude = 0.0,
  cameraTarget = "auto",
  shake = false,
  turns = [],
  hasDad = false,
  bgImage = "backgrounds/bg_cyber_diner.jpg",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const spkLower = speaker.toLowerCase();
  const isJuniorSpeaking = spkLower === "junior" || spkLower === "human" || spkLower === "dev";
  const isDadSpeaking = spkLower === "dad" || spkLower === "father" || spkLower === "uncle";
  const isClaudeSpeaking = spkLower === "claude" || spkLower === "anthropic";
  const isGrokSpeaking = spkLower === "grok" || spkLower === "xai";
  const isCodexSpeaking = spkLower === "codex" || spkLower === "chatgpt" || spkLower === "openai";
  const isBotSpeaking = spkLower === "bot" || spkLower === "gemini" || spkLower === "antigravity";

  // Determine dynamic cast layout
  const turnSpeakers = turns.map((t) => t.speaker.toLowerCase());
  const hasClaude = isClaudeSpeaking || turnSpeakers.some((s) => s.includes("claude"));
  const hasGrok = isGrokSpeaking || turnSpeakers.some((s) => s.includes("grok"));
  const hasCodex = isCodexSpeaking || turnSpeakers.some((s) => s.includes("codex"));
  const hasJunior = isJuniorSpeaking || turnSpeakers.some((s) => s.includes("junior") || s.includes("human") || s.includes("dev"));
  const claudeOnLeft = hasClaude && hasGrok && !hasJunior;
  const showDad = (hasDad || isDadSpeaking || turnSpeakers.some((s) => s.includes("dad"))) && !hasClaude && !hasGrok && !hasCodex;

  // Coordinates lookup for each character camera target
  const getCameraCoords = (target: string) => {
    switch (target) {
      case "junior":
        return { x: -0.65, y: -0.12, z: 6.6, fov: 41 };
      case "claude":
        return claudeOnLeft ? { x: -0.65, y: -0.12, z: 6.6, fov: 41 } : { x: 0.0, y: -0.08, z: 6.4, fov: 40 };
      case "dad":
      case "grok":
      case "codex":
      case "rival":
        return { x: 0.0, y: -0.08, z: 6.4, fov: 40 };
      case "bot":
      case "antigravity":
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
  } else if (isClaudeSpeaking) {
    currentTarget = "claude";
  } else if (isGrokSpeaking) {
    currentTarget = "grok";
  } else if (isCodexSpeaking) {
    currentTarget = "codex";
  } else if (isBotSpeaking) {
    currentTarget = "bot";
  }

  const targetCoords = getCameraCoords(currentTarget);

  // Butter-smooth camera transitions using turn progress & spring physics
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
          else if (prevSpk.includes("claude")) prevTarget = "claude";
          else if (prevSpk.includes("grok")) prevTarget = "grok";
          else if (prevSpk.includes("codex")) prevTarget = "codex";
          else if (prevSpk.includes("junior") || prevSpk.includes("human")) prevTarget = "junior";
          else if (prevSpk.includes("bot") || prevSpk.includes("gemini")) prevTarget = "bot";
          else prevTarget = "rival";
        }
        break;
      }
    }
  }

  const prevCoords = getCameraCoords(prevTarget);
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

  const driftX = Math.sin(frame * 0.02) * 0.03;
  const driftY = Math.cos(frame * 0.025) * 0.02;
  const shakeOffset = shake ? Math.sin(frame * 1.5) * 0.07 : 0.0;

  const camX = smoothX + driftX + shakeOffset;
  const camY = smoothY + driftY;
  const camZ = smoothZ;
  const camFov = smoothFov;

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
        <ambientLight intensity={1.2} color="#F1F5F9" />
        <directionalLight position={[4.5, 7.5, 6.0]} intensity={2.4} color="#FFF7ED" />
        <directionalLight position={[-5.0, 4.0, 4.0]} intensity={1.1} color="#94A3B8" />
        <pointLight position={[0, 3.2, -2.5]} intensity={2.6} color="#38BDF8" distance={12} />

        {/* 3D Diner Table Environment with 16:9 Scenic Projection */}
        <CafeEnvironment3D bgImage={bgImage} />

        {/* Left Seat: Junior Dev or Claude (in 3-AI Showdown) */}
        {claudeOnLeft ? (
          <ClaudeBot3D
            isSpeaking={isClaudeSpeaking}
            amplitude={audioAmplitude}
            frame={frame}
            position={[-1.4, -0.35, 0.3]}
            rotation={[0.06, 0.32, 0]}
          />
        ) : (
          <JuniorDev3D
            isSpeaking={isJuniorSpeaking}
            amplitude={audioAmplitude}
            frame={frame}
          />
        )}

        {/* Center Seat: Dynamic Roster (Grok, Claude, Codex, or Dad) */}
        {claudeOnLeft ? (
          <GrokBot3D isSpeaking={isGrokSpeaking} amplitude={audioAmplitude} frame={frame} />
        ) : hasClaude ? (
          <ClaudeBot3D isSpeaking={isClaudeSpeaking} amplitude={audioAmplitude} frame={frame} />
        ) : hasGrok ? (
          <GrokBot3D isSpeaking={isGrokSpeaking} amplitude={audioAmplitude} frame={frame} />
        ) : hasCodex ? (
          <CodexBot3D isSpeaking={isCodexSpeaking} amplitude={audioAmplitude} frame={frame} />
        ) : showDad ? (
          <DadCharacter3D isSpeaking={isDadSpeaking} amplitude={audioAmplitude} frame={frame} />
        ) : (
          <ClaudeBot3D isSpeaking={false} amplitude={audioAmplitude} frame={frame} />
        )}

        {/* Right Seat: Google Antigravity AI Bot (Terracotta + Gemini Star) */}
        <AntigravityBot3D
          isSpeaking={isBotSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />
      </ThreeCanvas>
    </div>
  );
};
