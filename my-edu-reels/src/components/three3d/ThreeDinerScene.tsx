import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame } from "remotion";

export interface ThreeDinerSceneProps {
  speaker: string; // "junior" | "rival" | "bot"
  audioAmplitude: number; // 0.0 to 1.0
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
            position={[xOffset, -0.14, 0.81]}
            scale={[1, barScaleY, 1]}
          >
            <capsuleGeometry args={[0.026, 0.09, 4, 8]} />
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
      <mesh position={[0, -0.32, 0.62]} scale={[1, mouthOpen * 8, 1]}>
        <boxGeometry args={[0.22, 0.05, 0.06]} />
        <meshStandardMaterial color="#4A1D1D" roughness={0.4} />
      </mesh>
      <mesh position={[0, -0.3, 0.63]}>
        <boxGeometry args={[0.16, 0.018, 0.025]} />
        <meshStandardMaterial color="#FFFFFF" roughness={0.3} />
      </mesh>
    </group>
  );
};

/**
 * 3D Low-Poly Senior / Rival Developer
 * Curly hair facets, dark acetate glasses, goatee, and dark green jacket
 */
const RivalDev3D: React.FC<{
  isSpeaking: boolean;
  amplitude: number;
  frame: number;
}> = ({ isSpeaking, amplitude, frame }) => {
  const headNod = isSpeaking ? Math.sin(frame * 0.16) * 0.04 : Math.sin(frame * 0.035) * 0.015;
  const mouthOpen = isSpeaking ? Math.max(0.08, amplitude * 0.42) : 0.04;

  return (
    <group position={[0.0, -0.62, -0.1]} rotation={[0.04 + headNod, 0.0, 0]}>
      {/* 1. Collared Dark Pine Jacket */}
      <mesh position={[0, -1.3, 0]}>
        <boxGeometry args={[1.6, 1.2, 0.9]} />
        <meshStandardMaterial color="#1B4332" roughness={0.7} flatShading />
      </mesh>

      {/* 2. Neck */}
      <mesh position={[0, -0.58, 0.04]}>
        <cylinderGeometry args={[0.22, 0.26, 0.32, 8]} />
        <meshStandardMaterial color="#8D5B4C" roughness={0.7} flatShading />
      </mesh>

      {/* 3. Faceted Head */}
      <mesh position={[0, -0.14, 0.08]}>
        <dodecahedronGeometry args={[0.64, 1]} />
        <meshStandardMaterial color="#9F6856" roughness={0.65} flatShading />
      </mesh>

      {/* 4. Curly Faceted Hair Clumps */}
      {[
        [-0.3, 0.42, 0.08],
        [0.0, 0.46, 0.12],
        [0.3, 0.42, 0.08],
        [-0.42, 0.24, 0.0],
        [0.42, 0.24, 0.0],
        [0.0, 0.38, -0.26],
      ].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]}>
          <dodecahedronGeometry args={[0.26, 0]} />
          <meshStandardMaterial color="#2B1810" roughness={0.8} flatShading />
        </mesh>
      ))}

      {/* 5. Acetate Glasses Frames */}
      <group position={[0, -0.05, 0.65]}>
        <mesh position={[-0.2, 0, 0]}>
          <boxGeometry args={[0.22, 0.15, 0.03]} />
          <meshStandardMaterial color="#1E293B" roughness={0.3} />
        </mesh>
        <mesh position={[-0.2, 0, 0.015]}>
          <planeGeometry args={[0.18, 0.11]} />
          <meshStandardMaterial color="#38BDF8" roughness={0.1} transparent opacity={0.35} />
        </mesh>
        <mesh position={[0.2, 0, 0]}>
          <boxGeometry args={[0.22, 0.15, 0.03]} />
          <meshStandardMaterial color="#1E293B" roughness={0.3} />
        </mesh>
        <mesh position={[0.2, 0, 0.015]}>
          <planeGeometry args={[0.18, 0.11]} />
          <meshStandardMaterial color="#38BDF8" roughness={0.1} transparent opacity={0.35} />
        </mesh>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.09, 0.025, 0.02]} />
          <meshStandardMaterial color="#1E293B" roughness={0.3} />
        </mesh>
      </group>

      {/* 6. Goatee Beard */}
      <mesh position={[0, -0.38, 0.56]}>
        <dodecahedronGeometry args={[0.18, 0]} />
        <meshStandardMaterial color="#2B1810" roughness={0.85} flatShading />
      </mesh>

      {/* 7. Audio-Reactive Mouth */}
      <mesh position={[0, -0.3, 0.62]} scale={[1, mouthOpen * 8, 1]}>
        <boxGeometry args={[0.2, 0.05, 0.05]} />
        <meshStandardMaterial color="#4A1D1D" roughness={0.4} />
      </mesh>
    </group>
  );
};

/**
 * 3D Tech Cafe Desk, Props & Warm Background Wall
 */
const CafeEnvironment3D: React.FC = () => {
  return (
    <group position={[0, -1.9, 1.1]}>
      {/* 1. Cozy Background Cafe Wall & Window */}
      <mesh position={[0, 2.2, -4.5]}>
        <planeGeometry args={[14, 8]} />
        <meshStandardMaterial color="#1B2333" roughness={0.9} />
      </mesh>
      {/* Warm Ambient Window Pane */}
      <mesh position={[0, 2.8, -4.4]}>
        <planeGeometry args={[6.5, 4.2]} />
        <meshStandardMaterial
          color="#FEF3C7"
          emissive="#FDE68A"
          emissiveIntensity={0.25}
          roughness={0.8}
        />
      </mesh>

      {/* 2. Solid Wood Table with Chamfered Edge */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[6.5, 0.24, 2.6]} />
        <meshStandardMaterial color="#5C3317" roughness={0.5} metalness={0.1} />
      </mesh>

      {/* 3. Developer Laptop */}
      <group position={[-0.85, 0.18, 0.3]} rotation={[0, 0.18, 0]}>
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.8, 0.035, 0.55]} />
          <meshStandardMaterial color="#334155" metalness={0.8} roughness={0.25} />
        </mesh>
        <group position={[0, 0.02, -0.26]} rotation={[-0.32, 0, 0]}>
          <mesh position={[0, 0.26, 0]}>
            <boxGeometry args={[0.8, 0.52, 0.025]} />
            <meshStandardMaterial color="#1E293B" metalness={0.8} roughness={0.3} />
          </mesh>
          <mesh position={[0, 0.26, 0.016]}>
            <planeGeometry args={[0.74, 0.46]} />
            <meshStandardMaterial
              color="#0284C7"
              emissive="#38BDF8"
              emissiveIntensity={0.85}
            />
          </mesh>
        </group>
      </group>

      {/* 4. Ceramic Espresso Cup & Saucer */}
      <group position={[0.22, 0.14, 0.55]}>
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.2, 0.16, 0.025, 16]} />
          <meshStandardMaterial color="#F8FAFC" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.1, 0]}>
          <cylinderGeometry args={[0.13, 0.09, 0.16, 16]} />
          <meshStandardMaterial color="#F8FAFC" roughness={0.2} />
        </mesh>
        <mesh position={[0, 0.16, 0]}>
          <circleGeometry args={[0.11, 16]} />
          <meshStandardMaterial color="#2E1B10" roughness={0.1} />
        </mesh>
      </group>

      {/* 5. Smartphone */}
      <group position={[1.05, 0.14, 0.38]} rotation={[0, -0.2, 0]}>
        <mesh>
          <boxGeometry args={[0.22, 0.018, 0.45]} />
          <meshStandardMaterial color="#0F172A" metalness={0.9} roughness={0.1} />
        </mesh>
      </group>
    </group>
  );
};

export const ThreeDinerScene: React.FC<ThreeDinerSceneProps> = ({
  speaker = "bot",
  audioAmplitude = 0.0,
}) => {
  const frame = useCurrentFrame();

  const isJuniorSpeaking = speaker === "junior" || speaker === "human";
  const isRivalSpeaking = speaker === "rival" || speaker === "senior";
  const isBotSpeaking = speaker === "bot" || speaker === "gemini" || speaker === "antigravity";

  // Gentle camera drift
  const camX = Math.sin(frame * 0.02) * 0.05;
  const camY = Math.cos(frame * 0.025) * 0.03;

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
          position: [camX, 0.2 + camY, 8.2],
          fov: 46,
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

        {/* Character 1: Junior Dev */}
        <JuniorDev3D
          isSpeaking={isJuniorSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />

        {/* Character 2: Rival Senior Dev */}
        <RivalDev3D
          isSpeaking={isRivalSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />

        {/* Character 3: Google Antigravity Bot */}
        <AntigravityBot3D
          isSpeaking={isBotSpeaking}
          amplitude={audioAmplitude}
          frame={frame}
        />
      </ThreeCanvas>
    </div>
  );
};
