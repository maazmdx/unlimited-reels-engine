import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { CozyDiner3D } from "./components/environments3d/CozyDiner3D";
import { LowPolyHumanRig } from "./components/characters3d/LowPolyHumanRig";
import { LowPolyAIOrbRig } from "./components/characters3d/LowPolyAIOrbRig";
import { DynamicProofCard } from "./components/ui/DynamicProofCard";

/**
 * DinerSceneShowcase:
 * - Verification scene for the 3D Cozy Diner environment (reel_DeIwE1-sxVr.mp4).
 * - Checkered floor, deep red booth, white pedestal table with 2 mugs, cake, salt/pepper, ketchup, phone.
 * - Junior Dev seated in booth on the left, Claude AI orb floating on the right across the table.
 * - Upper-third DynamicProofCard displayed cleanly at top: 220px, clearing characters below.
 */
export const DinerSceneShowcase: React.FC = () => {
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
      {/* Upper-Third Dynamic Proof Card (Strictly clears characters below) */}
      <DynamicProofCard
        startFrame={0}
        durationFrames={120}
        cardData={{
          title: "API Boilerplate Benchmark",
          badge: "340x SPEEDUP",
          type: "benchmark",
          items: [
            { label: "Junior Manual Coding", value: "6h 40m", badge: "FATIGUED", isPositive: false },
            { label: "Claude + Antigravity Loop", value: "48s", badge: "AUTONOMOUS", isPositive: true },
            { label: "Cost & Token Spend", value: "$0.00", badge: "100% PASSING", isPositive: true },
          ],
          highlight: "Zero hallucination with deterministic test gates.",
        }}
      />

      {/* 3D Scene Canvas */}
      <ThreeCanvas
        width={1080}
        height={1920}
        camera={{ position: [0, -0.12, 5.4], fov: 42, near: 0.1, far: 100 }}
        style={{ width: 1080, height: 1920 }}
      >
        <CozyDiner3D>
          {/* Junior Dev seated in the red booth (Left) */}
          <LowPolyHumanRig
            characterId="junior_dev"
            isSpeaking={true}
            mouthOpen={0.70}
            emotion="smug"
            position={[-1.28, -0.38, -0.1]}
            rotation={[0.04, 0.28, 0]}
            scale={1.12}
          />

          {/* Claude AI Orb floating across the table (Right) */}
          <LowPolyAIOrbRig
            characterId="claude"
            isSpeaking={false}
            mouthOpen={0.0}
            emotion="neutral"
            position={[1.28, 0.15, -0.1]}
            rotation={[0.02, -0.22, 0]}
            scale={1.05}
          />
        </CozyDiner3D>
      </ThreeCanvas>
    </div>
  );
};
