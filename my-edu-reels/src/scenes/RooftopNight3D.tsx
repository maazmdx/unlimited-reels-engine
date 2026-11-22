import React from "react";
import { useCurrentFrame } from "remotion";

export interface RooftopNight3DProps {
  children?: React.ReactNode;
}

/**
 * RooftopNight3D:
 * - Reference-grade 3D low-poly cyberpunk / rooftop night skyline diorama.
 * - Key features:
 *   1. Night city skyline towers with scattered glowing windows (#38BDF8 & #FDE047).
 *   2. Concrete parapet ledge with metallic safety railings.
 *   3. Bar stools / rooftop deck seating under the characters.
 *   4. Soft moonlight (#93C5FD) + pulsing neon signage glow.
 * - Under 3,200 triangles total, flatShading: true, zero shadow maps, CPU-render friendly.
 */
export const RooftopNight3D: React.FC<RooftopNight3DProps> = ({ children }) => {
  const frame = useCurrentFrame();

  // Deterministic neon sign glow pulsation
  const neonPulse = 0.85 + 0.15 * Math.sin(frame * 0.14);
  const cityWindowBlink = frame % 30 < 15;

  // Skyline tower definitions: [x, y, z, width, height, depth, color]
  const towers = [
    { x: -3.8, y: 1.5, z: -4.5, w: 1.4, h: 4.8, d: 1.4, color: "#0B132B" },
    { x: -2.2, y: 2.2, z: -5.2, w: 1.6, h: 6.2, d: 1.6, color: "#111827" },
    { x: -0.6, y: 1.8, z: -4.8, w: 1.3, h: 5.4, d: 1.3, color: "#0F172A" },
    { x: 1.0, y: 2.6, z: -5.5, w: 1.8, h: 7.0, d: 1.8, color: "#0B132B" },
    { x: 2.8, y: 1.9, z: -4.6, w: 1.5, h: 5.6, d: 1.5, color: "#111827" },
    { x: 4.2, y: 1.3, z: -4.2, w: 1.3, h: 4.4, d: 1.3, color: "#0F172A" },
  ];

  return (
    <group name="RooftopNight3D">
      {/* 1. SCENE LIGHTING: DEEP BLUE MOONLIGHT & NIGHT SKY GLOW */}
      <ambientLight intensity={0.45} color="#1E293B" />
      <directionalLight
        position={[3, 5, 2]}
        intensity={0.95}
        color="#93C5FD"
      />
      <directionalLight
        position={[-3, 3, -1]}
        intensity={0.40}
        color="#38BDF8"
      />

      {/* Pulsing Neon Sign Fill Light */}
      <pointLight
        position={[1.5, 1.2, -1.0]}
        intensity={2.2 * neonPulse}
        distance={6.0}
        decay={1.8}
        color="#EC4899"
      />

      {/* 2. NIGHT SKY & DISTANT MOON */}
      {/* Deep Midnight Blue Backdrop */}
      <mesh position={[0, 2.5, -6.5]}>
        <planeGeometry args={[18, 12]} />
        <meshBasicMaterial color="#050814" />
      </mesh>
      {/* Glowing Full Moon */}
      <group position={[2.5, 4.2, -6.0]}>
        <mesh>
          <sphereGeometry args={[0.65, 12, 12]} />
          <meshBasicMaterial color="#E2E8F0" />
        </mesh>
        <mesh scale={[1.2, 1.2, 1.0]}>
          <sphereGeometry args={[0.7, 8, 8]} />
          <meshBasicMaterial color="#93C5FD" transparent opacity={0.25} depthWrite={false} />
        </mesh>
      </group>

      {/* 3. DISTANT CITY SKYLINE TOWERS WITH GLOWING WINDOWS */}
      {towers.map((t, idx) => (
        <group key={`tower-${idx}`} position={[t.x, t.y, t.z]}>
          {/* Main Skyscraper Block */}
          <mesh>
            <boxGeometry args={[t.w, t.h, t.d]} />
            <meshStandardMaterial color={t.color} flatShading roughness={0.7} />
          </mesh>
          {/* Glowing Window Strips (Alternating Yellow & Cyan) */}
          {[-0.8, -0.2, 0.4, 1.0, 1.6].map((wy, widx) => (
            <mesh
              key={`win-${widx}`}
              position={[0, wy, t.d * 0.5 + 0.02]}
            >
              <boxGeometry args={[t.w * 0.75, 0.12, 0.02]} />
              <meshStandardMaterial
                color={widx % 2 === 0 ? "#FDE047" : "#38BDF8"}
                emissive={widx % 2 === 0 ? "#FDE047" : "#38BDF8"}
                emissiveIntensity={
                  widx % 2 === 0
                    ? 1.8 * (cityWindowBlink ? 1.0 : 0.85)
                    : 1.6 * neonPulse
                }
                toneMapped={false}
              />
            </mesh>
          ))}
          {/* Rooftop Antenna Beacon */}
          <mesh position={[0, t.h * 0.5 + 0.35, 0]}>
            <cylinderGeometry args={[0.02, 0.02, 0.7, 4]} />
            <meshStandardMaterial color="#94A3B8" flatShading />
          </mesh>
          <mesh position={[0, t.h * 0.5 + 0.72, 0]}>
            <sphereGeometry args={[0.04, 6, 6]} />
            <meshStandardMaterial
              color="#EF4444"
              emissive="#EF4444"
              emissiveIntensity={frame % 40 < 20 ? 3.0 : 0.2}
              toneMapped={false}
            />
          </mesh>
        </group>
      ))}

      {/* 4. ROOFTOP DECK FLOOR & CONCRETE PARAPET */}
      {/* Rooftop Concrete Slab */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#1E293B" flatShading roughness={0.8} />
      </mesh>

      {/* Back Parapet Ledge Wall */}
      <group position={[0, -0.65, -1.8]}>
        <mesh>
          <boxGeometry args={[8.0, 1.7, 0.4]} />
          <meshStandardMaterial color="#0F172A" flatShading roughness={0.85} />
        </mesh>
        {/* Parapet Top Capping Stone */}
        <mesh position={[0, 0.87, 0]}>
          <boxGeometry args={[8.1, 0.08, 0.46]} />
          <meshStandardMaterial color="#334155" flatShading roughness={0.7} />
        </mesh>
        {/* Metal Safety Railing on Top of Parapet */}
        <group position={[0, 1.25, 0]}>
          {/* Top Rail Bar */}
          <mesh position={[0, 0.3, 0]}>
            <boxGeometry args={[7.8, 0.04, 0.04]} />
            <meshStandardMaterial color="#64748B" flatShading roughness={0.4} metalness={0.6} />
          </mesh>
          {/* Middle Rail Bar */}
          <mesh position={[0, 0, 0]}>
            <boxGeometry args={[7.8, 0.03, 0.03]} />
            <meshStandardMaterial color="#64748B" flatShading roughness={0.4} metalness={0.6} />
          </mesh>
          {/* Railing Vertical Posts */}
          {[-3.0, -1.5, 0, 1.5, 3.0].map((px, idx) => (
            <mesh key={`post-${idx}`} position={[px, 0.15, 0]}>
              <cylinderGeometry args={[0.02, 0.02, 0.6, 6]} />
              <meshStandardMaterial color="#475569" flatShading metalness={0.5} />
            </mesh>
          ))}
        </group>
      </group>

      {/* 5. VIBRANT PULSING NEON SIGN ON PARAPET */}
      <group position={[0.8, 0.25, -1.58]}>
        {/* Neon Backing Plate */}
        <mesh>
          <boxGeometry args={[1.5, 0.45, 0.04]} />
          <meshStandardMaterial color="#0B0F19" flatShading roughness={0.9} />
        </mesh>
        {/* Neon Tube Letters (Stylized "OPEN 24H" Neon Glow) */}
        <mesh position={[0, 0, 0.03]}>
          <boxGeometry args={[1.35, 0.28, 0.02]} />
          <meshStandardMaterial
            color="#EC4899"
            emissive="#F43F5E"
            emissiveIntensity={2.5 * neonPulse}
            toneMapped={false}
          />
        </mesh>
      </group>

      {/* 6. ROOFTOP BAR STOOL & TABLE (Under Left Seated Character) */}
      <group position={[-1.15, -0.65, 0]}>
        {/* Stool Seat Cushion */}
        <mesh position={[0, -0.32, 0]}>
          <cylinderGeometry args={[0.42, 0.40, 0.18, 12]} />
          <meshStandardMaterial color="#E11D48" flatShading roughness={0.6} />
        </mesh>
        {/* Central Metal Pedestal */}
        <mesh position={[0, -0.72, 0]}>
          <cylinderGeometry args={[0.06, 0.06, 0.65, 8]} />
          <meshStandardMaterial color="#64748B" flatShading metalness={0.7} roughness={0.3} />
        </mesh>
        {/* Stool Heavy Disc Base */}
        <mesh position={[0, -1.02, 0]}>
          <cylinderGeometry args={[0.38, 0.42, 0.08, 12]} />
          <meshStandardMaterial color="#334155" flatShading metalness={0.6} roughness={0.4} />
        </mesh>
      </group>

      {/* Children elements (LowPolyHumanRig & LowPolyAIOrbRig) */}
      {children}
    </group>
  );
};
export default RooftopNight3D;
