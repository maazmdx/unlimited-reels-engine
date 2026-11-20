import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { LowPolyHumanRig } from "./components/characters3d/LowPolyHumanRig";
import { LowPolyAIOrbRig } from "./components/characters3d/LowPolyAIOrbRig";

export interface CharacterShowcase3DProps {
  mode?: "humans" | "bots" | "all";
}

/**
 * CharacterShowcase3D: Turntable studio preview composition showcasing
 * the reference-accurate flat-shaded low-poly 3D Three.js rigs
 * for Junior Dev, Dad, Claude, Gemini, and Grok.
 */
export const CharacterShowcase3D: React.FC<CharacterShowcase3DProps> = ({
  mode = "humans",
}) => {
  const isBots = mode === "bots";
  const isAll = mode === "all";

  // Dynamic Camera Staging: Camera backed up for wider 3-bot layout
  const cameraConfig = isBots
    ? { position: [0, 0.15, 8.2] as [number, number, number], fov: 45, near: 0.1, far: 100 }
    : isAll
    ? { position: [0, 0.10, 8.8] as [number, number, number], fov: 45, near: 0.1, far: 100 }
    : { position: [0, -0.25, 5.8] as [number, number, number], fov: 42, near: 0.1, far: 100 };

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#070B14",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Studio Header Overlay */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 60,
          right: 60,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 10,
          pointerEvents: "none",
        }}
      >
        <div>
          <div
            style={{
              fontFamily: "system-ui, -apple-system, sans-serif",
              fontSize: 16,
              fontWeight: 800,
              letterSpacing: "0.2em",
              color: "#38BDF8",
              textTransform: "uppercase",
              marginBottom: 4,
            }}
          >
            3D Low-Poly Character Rig Workshop
          </div>
          <h1
            style={{
              fontFamily: "system-ui, -apple-system, sans-serif",
              fontSize: 38,
              fontWeight: 900,
              color: "#F8FAFC",
              margin: 0,
            }}
          >
            {mode === "humans"
              ? "Human Cast: Junior Dev & Indian Dad"
              : mode === "bots"
              ? "AI Fleet: Claude, Gemini & Grok"
              : "Full Ensemble: Humans & AI Orbs"}
          </h1>
        </div>
        <div
          style={{
            backgroundColor: "rgba(56, 189, 248, 0.12)",
            border: "1px solid rgba(56, 189, 248, 0.3)",
            padding: "8px 18px",
            borderRadius: 20,
            color: "#38BDF8",
            fontSize: 14,
            fontWeight: 700,
          }}
        >
          {mode === "humans"
            ? "Faceted Human Rig"
            : mode === "bots"
            ? "7-Bar Equalizer Orbs"
            : "Complete Cast (5 Rigs)"}
        </div>
      </div>

      <ThreeCanvas
        width={1080}
        height={1920}
        camera={cameraConfig}
        style={{ width: 1080, height: 1920 }}
      >
        {/* Warm 3-Point Studio Lighting */}
        <ambientLight intensity={0.85} color="#1E293B" />
        <directionalLight position={[3.0, 4.5, 4.0]} intensity={2.6} color="#FFF7ED" />
        <directionalLight position={[-3.5, 2.5, 3.0]} intensity={1.3} color="#93C5FD" />
        <directionalLight position={[0, 4.0, -3.0]} intensity={1.8} color="#F59E0B" />

        {mode === "humans" ? (
          // ===============================================================
          // HUMANS SHOWCASE: Junior Dev vs Indian Dad at Diner Table
          // ===============================================================
          <group position={[0, 0, 0]}>
            {/* Junior Developer (Left, Smug Talking, Clean Eyes, 8-Puff Hair, Jaw Beard) */}
            <LowPolyHumanRig
              characterId="junior_dev"
              isSpeaking={true}
              mouthOpen={0.72}
              emotion="smug"
              position={[-1.25, -0.45, 0.2]}
              rotation={[0.04, 0.24, 0]}
              scale={1.18}
            />

            {/* Indian Dad (Right, Shocked Listening, Clean Mustache & Round Glasses) */}
            <LowPolyHumanRig
              characterId="dad"
              isSpeaking={false}
              mouthOpen={0.0}
              emotion="shocked"
              position={[1.25, -0.45, 0.2]}
              rotation={[0.04, -0.24, 0]}
              scale={1.18}
            />

            {/* Low-Poly Diner Table with Mahogany Top & Chrome Trim */}
            <group position={[0, -1.5, 0.9]}>
              <mesh position={[0, 0, 0]}>
                <boxGeometry args={[4.4, 0.14, 1.4]} />
                <meshStandardMaterial color="#3B1C10" roughness={0.3} metalness={0.1} />
              </mesh>
              <mesh position={[0, 0, 0.71]}>
                <boxGeometry args={[4.42, 0.16, 0.04]} />
                <meshStandardMaterial color="#E2E8F0" roughness={0.1} metalness={0.9} />
              </mesh>
            </group>
          </group>
        ) : mode === "bots" ? (
          // ===============================================================
          // BOTS SHOWCASE: Claude, Gemini & Grok Spread at x = -2.4, 0, +2.4
          // ===============================================================
          <group position={[0, 0, 0]}>
            {/* Claude AI (Left, Terracotta, Amber 7-Bar Equalizer, x = -2.4) */}
            <LowPolyAIOrbRig
              characterId="claude"
              isSpeaking={true}
              mouthOpen={0.75}
              emotion="smug"
              position={[-2.4, 0.05, 0.0]}
              rotation={[0.04, 0.20, 0]}
              scale={1.05}
            />

            {/* Gemini AI (Center, Pearlescent White, Cyan Equalizer + Gold Orb, x = 0) */}
            <LowPolyAIOrbRig
              characterId="gemini"
              isSpeaking={true}
              mouthOpen={0.50}
              emotion="neutral"
              position={[0.0, 0.25, 0.30]}
              rotation={[0.02, 0.0, 0]}
              scale={1.15}
            />

            {/* Grok AI (Right, Stealth Charcoal, Crimson 7-Bar Equalizer, x = +2.4) */}
            <LowPolyAIOrbRig
              characterId="grok"
              isSpeaking={false}
              mouthOpen={0.0}
              emotion="angry"
              position={[2.4, 0.05, 0.0]}
              rotation={[0.04, -0.20, 0]}
              scale={1.05}
            />
          </group>
        ) : (
          // ===============================================================
          // ALL SHOWCASE: Junior Dev, Dad, Claude, Gemini & Grok Side-by-Side
          // ===============================================================
          <group position={[0, 0, 0]}>
            <LowPolyHumanRig
              characterId="junior_dev"
              isSpeaking={true}
              mouthOpen={0.65}
              emotion="smug"
              position={[-2.4, -0.65, 0.0]}
              rotation={[0.04, 0.30, 0]}
              scale={0.95}
            />
            <LowPolyAIOrbRig
              characterId="claude"
              isSpeaking={false}
              mouthOpen={0.0}
              emotion="neutral"
              position={[-1.2, 0.25, 0.1]}
              rotation={[0.02, 0.15, 0]}
              scale={0.85}
            />
            <LowPolyAIOrbRig
              characterId="gemini"
              isSpeaking={true}
              mouthOpen={0.70}
              emotion="shocked"
              position={[0.0, 0.40, 0.25]}
              rotation={[0.0, 0.0, 0]}
              scale={0.95}
            />
            <LowPolyAIOrbRig
              characterId="grok"
              isSpeaking={false}
              mouthOpen={0.0}
              emotion="angry"
              position={[1.2, 0.25, 0.1]}
              rotation={[0.02, -0.15, 0]}
              scale={0.85}
            />
            <LowPolyHumanRig
              characterId="dad"
              isSpeaking={false}
              mouthOpen={0.0}
              emotion="tired"
              position={[2.4, -0.65, 0.0]}
              rotation={[0.04, -0.30, 0]}
              scale={0.95}
            />
          </group>
        )}
      </ThreeCanvas>
    </div>
  );
};
