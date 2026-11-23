import React from "react";
import { useCurrentFrame } from "remotion";

export interface IndianLivingRoom3DProps {
  children?: React.ReactNode;
}

/**
 * IndianLivingRoom3D:
 * - Reference-accurate 3D low-poly Indian middle-class living room diorama.
 * - Auto-selected for "ai_vs_dad" and dad clash reels.
 * - Key features:
 *   1. Spinning ceiling fan (3 blades at frame * 0.18 rad/frame).
 *   2. Warm tubelight fixture with nostalgic #FEF9C3 glow.
 *   3. L-shaped sofa with muted cushions seating the character.
 *   4. Low-poly TV console with blinking 5G Wi-Fi router (green & cyan LEDs).
 *   5. Framed retro posters and decorative wall calendar.
 * - Under 3,000 triangles total, flatShading: true, CPU SwiftShader friendly.
 */
export const IndianLivingRoom3D: React.FC<IndianLivingRoom3DProps> = ({ children }) => {
  const frame = useCurrentFrame();

  // Deterministic Wi-Fi router LED blink
  const isWifiGreen = frame % 20 < 12;
  const isWifiCyan = frame % 14 < 7;

  // Ceiling fan continuous rotation
  const fanRotationY = frame * 0.18;

  return (
    <group name="IndianLivingRoom3D">
      {/* 1. SCENE LIGHTING: WARM INDIAN HOME TUBELIGHT ATMOSPHERE */}
      <hemisphereLight
        args={["#FEF9C3", "#78350F", 1.25]}
      />
      <directionalLight
        position={[2, 4, 3]}
        intensity={0.85}
        color="#FEF3C7"
      />
      <directionalLight
        position={[-2.5, 3, 2]}
        intensity={0.55}
        color="#FDE68A"
      />

      {/* Warm Tubelight Pool Light */}
      <pointLight
        position={[0, 2.1, -1.5]}
        intensity={2.8}
        distance={7.0}
        decay={1.6}
        color="#FEF08A"
      />

      {/* 2. ROOM ENCLOSURE (Warm Cream Walls & Ceramic Floor) */}
      {/* Back Wall */}
      <mesh position={[0, 1.2, -2.2]}>
        <planeGeometry args={[10, 8]} />
        <meshStandardMaterial color="#FDF6E2" flatShading roughness={0.85} />
      </mesh>
      {/* Left Wall */}
      <mesh position={[-4.5, 1.2, 0]} rotation={[0, Math.PI / 2, 0]}>
        <planeGeometry args={[10, 8]} />
        <meshStandardMaterial color="#F7ECCF" flatShading roughness={0.85} />
      </mesh>
      {/* Floor (Off-white tiled ceramic with subtle grid seams) */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#EDE5D8" flatShading roughness={0.65} />
      </mesh>

      {/* 3. WARM TUBELIGHT FIXTURE (Back Wall) */}
      <group position={[0, 2.2, -2.15]}>
        {/* Metal Mounting Backplate */}
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[2.2, 0.08, 0.04]} />
          <meshStandardMaterial color="#94A3B8" flatShading roughness={0.4} metalness={0.5} />
        </mesh>
        {/* Glowing Glass Tube */}
        <mesh position={[0, -0.02, 0.03]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.035, 0.035, 2.0, 10]} />
          <meshStandardMaterial
            color="#FEF9C3"
            emissive="#FEF08A"
            emissiveIntensity={2.4}
            roughness={0.2}
            toneMapped={false}
          />
        </mesh>
      </group>

      {/* 4. SPINNING CEILING FAN */}
      <group position={[0, 2.7, 0]}>
        {/* Downrod from ceiling */}
        <mesh position={[0, 0.35, 0]}>
          <cylinderGeometry args={[0.025, 0.025, 0.7, 8]} />
          <meshStandardMaterial color="#475569" flatShading roughness={0.5} />
        </mesh>
        {/* Fan Motor Cup */}
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.18, 0.16, 0.14, 12]} />
          <meshStandardMaterial color="#64748B" flatShading roughness={0.4} metalness={0.3} />
        </mesh>
        {/* Rotating Blades Assembly */}
        <group rotation={[0, fanRotationY, 0]}>
          {[0, (2 * Math.PI) / 3, (4 * Math.PI) / 3].map((angle, idx) => (
            <group key={`blade-${idx}`} rotation={[0, angle, 0]}>
              {/* Blade arm */}
              <mesh position={[0.22, 0, 0]}>
                <boxGeometry args={[0.18, 0.015, 0.05]} />
                <meshStandardMaterial color="#334155" flatShading />
              </mesh>
              {/* Aerodynamic blade */}
              <mesh position={[0.62, 0.01, 0]} rotation={[0.08, 0, 0]}>
                <boxGeometry args={[0.65, 0.012, 0.14]} />
                <meshStandardMaterial color="#475569" flatShading roughness={0.5} />
              </mesh>
            </group>
          ))}
        </group>
      </group>

      {/* 5. L-SHAPED SOFA (Under Left Seated Character) */}
      <group position={[-1.15, -0.55, 0]}>
        {/* Main Seating Base */}
        <mesh position={[0, -0.45, 0.2]}>
          <boxGeometry args={[1.5, 0.35, 1.2]} />
          <meshStandardMaterial color="#78350F" flatShading roughness={0.8} />
        </mesh>
        {/* Sofa Backrest */}
        <mesh position={[0, 0.15, -0.35]}>
          <boxGeometry args={[1.5, 0.85, 0.3]} />
          <meshStandardMaterial color="#92400E" flatShading roughness={0.75} />
        </mesh>
        {/* Left Armrest */}
        <mesh position={[-0.8, -0.1, 0.2]}>
          <boxGeometry args={[0.24, 0.55, 1.2]} />
          <meshStandardMaterial color="#78350F" flatShading roughness={0.8} />
        </mesh>
        {/* Soft Seat Cushion (Warm Maroon / Rust Brown) */}
        <mesh position={[0, -0.22, 0.25]}>
          <boxGeometry args={[1.35, 0.18, 0.95]} />
          <meshStandardMaterial color="#B45309" flatShading roughness={0.7} />
        </mesh>
        {/* Corner Throw Cushion */}
        <mesh position={[-0.55, 0.05, -0.1]} rotation={[0.2, 0.3, -0.15]}>
          <boxGeometry args={[0.35, 0.35, 0.15]} />
          <meshStandardMaterial color="#F59E0B" flatShading roughness={0.6} />
        </mesh>
      </group>

      {/* 6. TV CONSOLE & BLINKING 5G WI-FI ROUTER (Right Side) */}
      <group position={[1.3, -0.75, -0.4]}>
        {/* Wooden TV Console Unit */}
        <mesh position={[0, -0.25, 0]}>
          <boxGeometry args={[1.2, 0.65, 0.65]} />
          <meshStandardMaterial color="#451A03" flatShading roughness={0.75} />
        </mesh>
        {/* Console Shelf Compartment */}
        <mesh position={[0, -0.15, 0.33]}>
          <boxGeometry args={[1.05, 0.25, 0.05]} />
          <meshStandardMaterial color="#291205" flatShading roughness={0.9} />
        </mesh>

        {/* 5G Wi-Fi Router */}
        <group position={[-0.2, 0.12, 0]}>
          {/* Router Body */}
          <mesh position={[0, 0, 0]}>
            <boxGeometry args={[0.34, 0.05, 0.24]} />
            <meshStandardMaterial color="#0F172A" flatShading roughness={0.4} metalness={0.2} />
          </mesh>
          {/* Dual 5G Antennas */}
          <mesh position={[-0.12, 0.15, -0.09]} rotation={[0.15, 0, -0.2]}>
            <cylinderGeometry args={[0.008, 0.008, 0.28, 6]} />
            <meshStandardMaterial color="#1E293B" flatShading />
          </mesh>
          <mesh position={[0.12, 0.15, -0.09]} rotation={[0.15, 0, 0.2]}>
            <cylinderGeometry args={[0.008, 0.008, 0.28, 6]} />
            <meshStandardMaterial color="#1E293B" flatShading />
          </mesh>
          {/* Blinking 5G Power / Internet LEDs */}
          <mesh position={[-0.08, 0.027, 0.10]}>
            <sphereGeometry args={[0.012, 6, 6]} />
            <meshStandardMaterial
              color={isWifiGreen ? "#22C55E" : "#14532D"}
              emissive={isWifiGreen ? "#4ADE80" : "#000000"}
              emissiveIntensity={isWifiGreen ? 2.5 : 0}
              toneMapped={false}
            />
          </mesh>
          <mesh position={[-0.02, 0.027, 0.10]}>
            <sphereGeometry args={[0.012, 6, 6]} />
            <meshStandardMaterial
              color={isWifiCyan ? "#06B6D4" : "#164E63"}
              emissive={isWifiCyan ? "#22D3EE" : "#000000"}
              emissiveIntensity={isWifiCyan ? 2.5 : 0}
              toneMapped={false}
            />
          </mesh>
          <mesh position={[0.04, 0.027, 0.10]}>
            <sphereGeometry args={[0.012, 6, 6]} />
            <meshStandardMaterial
              color="#22C55E"
              emissive="#4ADE80"
              emissiveIntensity={1.8}
              toneMapped={false}
            />
          </mesh>
        </group>

        {/* Small Potted Indoor Money Plant on Console */}
        <group position={[0.35, 0.15, 0]}>
          <mesh position={[0, 0, 0]}>
            <cylinderGeometry args={[0.08, 0.06, 0.14, 8]} />
            <meshStandardMaterial color="#B45309" flatShading roughness={0.7} />
          </mesh>
          <mesh position={[0, 0.12, 0]}>
            <dodecahedronGeometry args={[0.11, 0]} />
            <meshStandardMaterial color="#15803D" flatShading roughness={0.8} />
          </mesh>
        </group>
      </group>

      {/* 7. WALL DECOR: SUBTLE FRAMED ART & TRADITIONAL WALL CLOCK */}
      {/* Left: Framed Scenery Landscape Art */}
      <group position={[-1.2, 1.15, -2.15]}>
        {/* Dark Teak Frame */}
        <mesh>
          <boxGeometry args={[0.75, 1.05, 0.03]} />
          <meshStandardMaterial color="#2A1810" flatShading roughness={0.6} />
        </mesh>
        {/* Warm Canvas Background */}
        <mesh position={[0, 0, 0.02]}>
          <planeGeometry args={[0.65, 0.95]} />
          <meshStandardMaterial color="#E8E0D5" flatShading roughness={0.8} />
        </mesh>
        {/* Subtle Sun Accent */}
        <mesh position={[0.12, 0.18, 0.025]}>
          <circleGeometry args={[0.09, 16]} />
          <meshStandardMaterial color="#F59E0B" flatShading roughness={0.6} />
        </mesh>
        {/* Distant Mountain Ridge */}
        <mesh position={[0, -0.15, 0.025]}>
          <planeGeometry args={[0.65, 0.35]} />
          <meshStandardMaterial color="#64748B" flatShading roughness={0.8} />
        </mesh>
      </group>

      {/* Right: Traditional Round Indian Wall Clock */}
      <group position={[1.0, 1.35, -2.15]}>
        {/* Wooden Clock Bezel */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.34, 0.34, 0.04, 24]} />
          <meshStandardMaterial color="#451A03" flatShading roughness={0.6} />
        </mesh>
        {/* Off-White Clock Face */}
        <mesh position={[0, 0, 0.022]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.29, 0.29, 0.005, 24]} />
          <meshStandardMaterial color="#FFFBEB" flatShading roughness={0.5} />
        </mesh>
        {/* Hour Hand (Points to 10) */}
        <mesh position={[-0.04, 0.05, 0.028]} rotation={[0, 0, 0.65]}>
          <boxGeometry args={[0.018, 0.13, 0.006]} />
          <meshStandardMaterial color="#1E293B" flatShading />
        </mesh>
        {/* Minute Hand (Points to 2) */}
        <mesh position={[0.05, 0.07, 0.028]} rotation={[0, 0, -0.55]}>
          <boxGeometry args={[0.014, 0.18, 0.006]} />
          <meshStandardMaterial color="#1E293B" flatShading />
        </mesh>
        {/* Center Brass Pivot Pin */}
        <mesh position={[0, 0, 0.03]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.02, 0.02, 0.01, 12]} />
          <meshStandardMaterial color="#B45309" metalness={0.4} roughness={0.3} />
        </mesh>
      </group>

      {/* Children elements (LowPolyHumanRig & LowPolyAIOrbRig) */}
      {children}
    </group>
  );
};
export default IndianLivingRoom3D;
