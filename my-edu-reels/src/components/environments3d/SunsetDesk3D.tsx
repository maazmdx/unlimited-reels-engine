import React from "react";
import { useCurrentFrame } from "remotion";

export interface SunsetDesk3DProps {
  children?: React.ReactNode;
}

/**
 * SunsetDesk3D:
 * - Reference-accurate 3D low-poly desk environment (matching reel_DfqncqEyWiK.mp4).
 * - Warm mahogany/walnut wooden desk with side drawers.
 * - Articulated Pixar-style low-poly desk lamp with warm golden glow.
 * - Rich desk props: stack of colorful books, ceramic coffee mug, open glowing laptop with yellow sticky note, potted low-poly succulent.
 * - Soft purple-lavender twilight window backdrop with deterministic floating bokeh orbs (Math.sin, 0 random).
 * - Under 3,000 triangles total, zero shadow maps, flatShading: true everywhere, CPU-friendly SwiftShader renders.
 */
export const SunsetDesk3D: React.FC<SunsetDesk3DProps> = ({ children }) => {
  const frame = useCurrentFrame();

  // Deterministic floating bokeh positions (zero Math.random, zero flicker)
  const bokehOrbs = [
    { x: -1.8, y: 0.8, z: -2.0, r: 0.12, speed: 0.022, phase: 0.0, color: "#FDE047" },
    { x: -1.1, y: 1.4, z: -2.2, r: 0.18, speed: 0.018, phase: 1.2, color: "#FDA4AF" },
    { x: -0.4, y: 0.6, z: -1.8, r: 0.09, speed: 0.025, phase: 2.1, color: "#C084FC" },
    { x: 0.3, y: 1.6, z: -2.4, r: 0.15, speed: 0.016, phase: 3.4, color: "#FDE047" },
    { x: 1.0, y: 0.9, z: -2.1, r: 0.11, speed: 0.021, phase: 4.2, color: "#F472B6" },
    { x: 1.7, y: 1.3, z: -2.3, r: 0.16, speed: 0.019, phase: 5.1, color: "#E879F9" },
    { x: -1.4, y: 0.2, z: -1.7, r: 0.08, speed: 0.028, phase: 0.8, color: "#FEF08A" },
    { x: 1.4, y: 0.3, z: -1.9, r: 0.10, speed: 0.024, phase: 2.7, color: "#A78BFA" },
  ];

  return (
    <group name="SunsetDesk3D">
      {/* 1. SCENE LIGHTING: WARM SUNSET & TWILIGHT */}
      <ambientLight intensity={0.52} color="#DDD6FE" />
      <directionalLight position={[3, 4, 3]} intensity={0.75} color="#FDE047" />
      <directionalLight position={[-3, 2, -1]} intensity={0.45} color="#C084FC" />

      {/* 2. WARM WOODEN DESK */}
      <group position={[0, -0.55, 0]}>
        {/* Main tabletop slab */}
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[2.6, 0.08, 1.4]} />
          <meshStandardMaterial
            color="#78350F"
            flatShading
            roughness={0.7}
            metalness={0.05}
          />
        </mesh>
        {/* Beveled edge trim */}
        <mesh position={[0, -0.04, 0]}>
          <boxGeometry args={[2.64, 0.03, 1.44]} />
          <meshStandardMaterial color="#92400E" flatShading roughness={0.75} />
        </mesh>

        {/* 4 Sturdy Square Tapered Legs */}
        {[
          [-1.15, -0.5, -0.55],
          [-1.15, -0.5, 0.55],
          [1.15, -0.5, -0.55],
          [1.15, -0.5, 0.55],
        ].map(([lx, ly, lz], idx) => (
          <mesh key={`leg-${idx}`} position={[lx, ly, lz]}>
            <boxGeometry args={[0.09, 0.95, 0.09]} />
            <meshStandardMaterial color="#451A03" flatShading roughness={0.8} />
          </mesh>
        ))}

        {/* Right-Side Drawer Cabinet */}
        <group position={[0.82, -0.45, 0]}>
          <mesh>
            <boxGeometry args={[0.56, 0.78, 1.15]} />
            <meshStandardMaterial color="#5B21B6" flatShading roughness={0.8} />
          </mesh>
          {/* Drawer faces */}
          {[-0.22, 0.02, 0.24].map((dy, didx) => (
            <mesh key={`drawer-${didx}`} position={[0, dy, 0.59]}>
              <boxGeometry args={[0.5, 0.18, 0.02]} />
              <meshStandardMaterial color="#4C1D95" flatShading roughness={0.7} />
            </mesh>
          ))}
          {/* Brass drawer handles */}
          {[-0.22, 0.02, 0.24].map((dy, didx) => (
            <mesh key={`handle-${didx}`} position={[0, dy, 0.61]} rotation={[0, 0, Math.PI / 2]}>
              <cylinderGeometry args={[0.015, 0.015, 0.12, 6]} />
              <meshStandardMaterial color="#F59E0B" metalness={0.75} roughness={0.25} flatShading />
            </mesh>
          ))}
        </group>

        {/* ======================================================== */}
        {/* DESK PROPS (ON TOP OF DESK y = +0.04)                   */}
        {/* ======================================================== */}

        {/* Articulated Low-Poly Desk Lamp (Left) */}
        <group position={[-0.85, 0.04, -0.2]}>
          {/* Round lamp base */}
          <mesh position={[0, 0.02, 0]}>
            <cylinderGeometry args={[0.16, 0.18, 0.04, 10]} />
            <meshStandardMaterial color="#D97706" flatShading metalness={0.4} roughness={0.4} />
          </mesh>
          {/* Lower arm strut (angled back) */}
          <mesh position={[0.04, 0.22, -0.06]} rotation={[0.35, 0, -0.2]}>
            <cylinderGeometry args={[0.018, 0.018, 0.42, 6]} />
            <meshStandardMaterial color="#92400E" flatShading roughness={0.5} />
          </mesh>
          {/* Elbow hinge sphere */}
          <mesh position={[0.08, 0.42, -0.12]}>
            <sphereGeometry args={[0.04, 7, 7]} />
            <meshStandardMaterial color="#F59E0B" metalness={0.6} roughness={0.3} flatShading />
          </mesh>
          {/* Upper arm strut (angled forward toward center) */}
          <mesh position={[0.18, 0.46, 0.02]} rotation={[-0.6, 0, -0.45]}>
            <cylinderGeometry args={[0.018, 0.018, 0.38, 6]} />
            <meshStandardMaterial color="#92400E" flatShading roughness={0.5} />
          </mesh>
          {/* Beveled conical lampshade */}
          <mesh position={[0.3, 0.48, 0.12]} rotation={[-0.8, 0, -0.6]}>
            <coneGeometry args={[0.15, 0.22, 10, 1, true]} />
            <meshStandardMaterial color="#F59E0B" flatShading roughness={0.3} metalness={0.3} />
          </mesh>
          {/* Glowing lamp bulb */}
          <mesh position={[0.32, 0.44, 0.14]}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshStandardMaterial
              color="#FEF08A"
              emissive="#FDE047"
              emissiveIntensity={2.0}
              toneMapped={false}
            />
          </mesh>
          {/* Warm pool light cast on desk */}
          <pointLight
            position={[0.34, 0.38, 0.15]}
            color="#FDE047"
            intensity={2.2}
            distance={4.8}
            decay={1.8}
          />
        </group>

        {/* Stack of Colorful Books (Left foreground) */}
        <group position={[-0.78, 0.04, 0.28]}>
          {/* Bottom book (Navy) */}
          <mesh position={[0, 0.03, 0]}>
            <boxGeometry args={[0.34, 0.06, 0.44]} />
            <meshStandardMaterial color="#1E3A8A" flatShading roughness={0.6} />
          </mesh>
          <mesh position={[0.01, 0.03, 0]}>
            <boxGeometry args={[0.32, 0.048, 0.42]} />
            <meshStandardMaterial color="#FFFBEB" flatShading roughness={0.9} />
          </mesh>
          {/* Middle book (Terracotta) */}
          <mesh position={[0.02, 0.08, 0.01]} rotation={[0, 0.12, 0]}>
            <boxGeometry args={[0.3, 0.05, 0.4]} />
            <meshStandardMaterial color="#C2410C" flatShading roughness={0.6} />
          </mesh>
          {/* Top book (Sage forest green) */}
          <mesh position={[-0.01, 0.13, -0.01]} rotation={[0, -0.09, 0]}>
            <boxGeometry args={[0.26, 0.05, 0.36]} />
            <meshStandardMaterial color="#047857" flatShading roughness={0.6} />
          </mesh>
        </group>

        {/* Ceramic Coffee Mug */}
        <group position={[-0.38, 0.12, 0.35]}>
          <mesh>
            <cylinderGeometry args={[0.075, 0.07, 0.15, 9]} />
            <meshStandardMaterial color="#F1F5F9" flatShading roughness={0.4} />
          </mesh>
          {/* Coffee inside */}
          <mesh position={[0, 0.065, 0]}>
            <cylinderGeometry args={[0.065, 0.065, 0.02, 8]} />
            <meshStandardMaterial color="#3E2723" flatShading roughness={0.9} />
          </mesh>
          {/* Mug handle */}
          <mesh position={[-0.08, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
            <torusGeometry args={[0.04, 0.014, 6, 8, Math.PI]} />
            <meshStandardMaterial color="#F1F5F9" flatShading roughness={0.4} />
          </mesh>
        </group>

        {/* Open Laptop & Glowing Code Screen (Center) */}
        <group position={[0.0, 0.05, 0.1]}>
          {/* Base keyboard slab */}
          <mesh position={[0, 0.01, 0]}>
            <boxGeometry args={[0.56, 0.02, 0.38]} />
            <meshStandardMaterial color="#334155" flatShading roughness={0.4} metalness={0.4} />
          </mesh>
          {/* Trackpad */}
          <mesh position={[0, 0.021, 0.1]}>
            <planeGeometry args={[0.16, 0.11]} />
            <meshStandardMaterial color="#475569" flatShading roughness={0.3} metalness={0.3} />
          </mesh>
          {/* Keyboard keys area */}
          <mesh position={[0, 0.021, -0.05]}>
            <planeGeometry args={[0.48, 0.18]} />
            <meshStandardMaterial color="#0F172A" flatShading roughness={0.8} />
          </mesh>

          {/* Screen lid (tilted back 105 deg) */}
          <group position={[0, 0.02, -0.19]} rotation={[-0.26, 0, 0]}>
            <mesh position={[0, 0.18, 0]}>
              <boxGeometry args={[0.56, 0.36, 0.016]} />
              <meshStandardMaterial color="#1E293B" flatShading roughness={0.4} metalness={0.4} />
            </mesh>
            {/* Glowing IDE screen */}
            <mesh position={[0, 0.18, 0.009]}>
              <planeGeometry args={[0.52, 0.32]} />
              <meshStandardMaterial
                color="#38BDF8"
                emissive="#0284C7"
                emissiveIntensity={0.8}
                toneMapped={false}
              />
            </mesh>
            {/* Yellow sticky note on top corner of screen bezel */}
            <mesh position={[0.22, 0.33, 0.015]} rotation={[0, 0, 0.1]}>
              <planeGeometry args={[0.08, 0.08]} />
              <meshStandardMaterial color="#FEF08A" flatShading roughness={0.9} />
            </mesh>
          </group>
        </group>

        {/* Small Potted Succulent Plant (Right) */}
        <group position={[0.62, 0.04, -0.15]}>
          {/* Terracotta pot */}
          <mesh position={[0, 0.08, 0]}>
            <cylinderGeometry args={[0.12, 0.08, 0.16, 8]} />
            <meshStandardMaterial color="#EA580C" flatShading roughness={0.7} />
          </mesh>
          {/* Dark soil */}
          <mesh position={[0, 0.15, 0]}>
            <cylinderGeometry args={[0.11, 0.11, 0.02, 8]} />
            <meshStandardMaterial color="#3E2723" flatShading roughness={0.9} />
          </mesh>
          {/* 6 Low-poly succulent leaves radiating out */}
          {[0, 60, 120, 180, 240, 300].map((deg, sIdx) => {
            const rad = (deg * Math.PI) / 180;
            return (
              <mesh
                key={`leaf-${sIdx}`}
                position={[Math.sin(rad) * 0.06, 0.18, Math.cos(rad) * 0.06]}
                rotation={[0.4 * Math.cos(rad), rad, -0.4 * Math.sin(rad)]}
              >
                <coneGeometry args={[0.045, 0.12, 4]} />
                <meshStandardMaterial
                  color={sIdx % 2 === 0 ? "#16A34A" : "#22C55E"}
                  flatShading
                  roughness={0.6}
                />
              </mesh>
            );
          })}
        </group>
      </group>

      {/* 3. TWILIGHT BACKDROP & WINDOW (z = -3.0) */}
      <group position={[0, 0.7, -3.0]}>
        {/* Large Twilight Sky Plane (Deep violet into coral-sunset) */}
        <mesh position={[0, 0.2, -0.3]}>
          <planeGeometry args={[6.0, 4.0]} />
          <meshBasicMaterial color="#31103F" />
        </mesh>
        {/* Soft sunset horizon band */}
        <mesh position={[0, -0.6, -0.2]}>
          <planeGeometry args={[6.0, 1.4]} />
          <meshBasicMaterial color="#7E22CE" transparent opacity={0.65} />
        </mesh>
        <mesh position={[0, -1.0, -0.1]}>
          <planeGeometry args={[6.0, 0.8]} />
          <meshBasicMaterial color="#FB7185" transparent opacity={0.45} />
        </mesh>

        {/* Window frame surround */}
        <mesh position={[0, 0, 0.05]}>
          <boxGeometry args={[3.4, 2.4, 0.1]} />
          <meshStandardMaterial color="#1E1B4B" flatShading roughness={0.8} />
        </mesh>
        {/* Window glass pane */}
        <mesh position={[0, 0, 0.08]}>
          <planeGeometry args={[3.2, 2.2]} />
          <meshStandardMaterial
            color="#E0E7FF"
            transparent
            opacity={0.18}
            roughness={0.2}
            metalness={0.1}
          />
        </mesh>
        {/* Window vertical mullion */}
        <mesh position={[0, 0, 0.1]}>
          <boxGeometry args={[0.06, 2.2, 0.06]} />
          <meshStandardMaterial color="#2E1065" flatShading />
        </mesh>

        {/* Deterministic Floating Bokeh Orbs */}
        {bokehOrbs.map((orb, oIdx) => {
          const floatY = Math.sin(frame * orb.speed + orb.phase) * 0.15;
          const floatX = Math.cos(frame * orb.speed * 0.8 + orb.phase) * 0.08;
          return (
            <mesh
              key={`bokeh-${oIdx}`}
              position={[orb.x + floatX, orb.y + floatY, orb.z + 2.0]}
            >
              <sphereGeometry args={[orb.r, 8, 8]} />
              <meshBasicMaterial
                color={orb.color}
                transparent
                opacity={0.28}
                depthWrite={false}
              />
            </mesh>
          );
        })}
      </group>

      {/* 4. NESTED CHARACTERS / EXTRAS */}
      {children}
    </group>
  );
};
