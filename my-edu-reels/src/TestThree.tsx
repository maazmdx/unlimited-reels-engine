import React from "react";
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame } from "remotion";

export const TestThree: React.FC = () => {
  const frame = useCurrentFrame();
  const rot = (frame / 30) * Math.PI * 2;

  return (
    <div style={{ width: 1080, height: 1920, backgroundColor: "#0B0F19" }}>
      <ThreeCanvas width={1080} height={1920}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} />
        <mesh rotation={[rot * 0.5, rot, 0]}>
          <dodecahedronGeometry args={[2.5, 0]} />
          <meshStandardMaterial color="#E26D38" roughness={0.3} metalness={0.2} flatShading />
        </mesh>
      </ThreeCanvas>
    </div>
  );
};
