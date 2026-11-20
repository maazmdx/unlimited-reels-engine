import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { SunsetDesk3D } from "./components/environments3d/SunsetDesk3D";
import { LowPolyHumanRig } from "./components/characters3d/LowPolyHumanRig";
import { LowPolyAIOrbRig } from "./components/characters3d/LowPolyAIOrbRig";
import { DynamicProofCard } from "./components/ui/DynamicProofCard";
import { NotificationToast } from "./components/ui/NotificationToast";

/**
 * DeskSceneShowcase:
 * - Verification scene for the 3D Sunset Desk environment (reel_DfqncqEyWiK.mp4).
 * - Mahogany desk, articulated Pixar-style lamp, books, mug, glowing laptop + sticky note, succulent.
 * - Soft purple-lavender twilight window with floating bokeh orbs.
 * - Junior Dev seated at desk, Gemini AI orb hovering on right.
 * - Top NotificationToast + Upper-Third DynamicProofCard with code proof.
 */
export const DeskSceneShowcase: React.FC = () => {
  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#0A0B1A",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Top iOS/macOS Notification Toast */}
      <NotificationToast
        title="⚡ Gemini 2.5 Flash Loop Active"
        subtitle="3.4x faster synthesis • 0 manual fatigue"
        icon="⚡"
        startFrame={0}
        durationFrames={90}
      />

      {/* Upper-Third Dynamic Proof Card (Code Proof) */}
      <DynamicProofCard
        startFrame={0}
        durationFrames={120}
        cardData={{
          title: "Autonomous Agent Orchestrator",
          badge: "PRODUCTION READY",
          type: "code",
          language: "ts",
          codeSnippet: `const agent = new AntigravitySwarm({\n  model: "gemini-2.5-flash",\n  tools: [codeReview, testRunner],\n  autoFix: true,\n});\nawait agent.executePipeline();`,
          highlight: "340x faster than manual copy-paste loops.",
        }}
      />

      {/* 3D Scene Canvas */}
      <ThreeCanvas
        width={1080}
        height={1920}
        camera={{ position: [0, -0.1, 5.5], fov: 42, near: 0.1, far: 100 }}
        style={{ width: 1080, height: 1920 }}
      >
        <SunsetDesk3D>
          {/* Junior Dev seated at desk (Left-Center) */}
          <LowPolyHumanRig
            characterId="junior_dev"
            isSpeaking={false}
            mouthOpen={0.0}
            emotion="neutral"
            position={[-0.45, -0.36, -0.3]}
            rotation={[0.04, 0.18, 0]}
            scale={1.08}
          />

          {/* Gemini AI Orb hovering on right */}
          <LowPolyAIOrbRig
            characterId="gemini"
            isSpeaking={true}
            mouthOpen={0.65}
            emotion="shocked"
            position={[1.22, 0.22, -0.1]}
            rotation={[0.02, -0.18, 0]}
            scale={1.10}
          />
        </SunsetDesk3D>
      </ThreeCanvas>
    </div>
  );
};
