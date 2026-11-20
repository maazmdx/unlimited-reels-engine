import React from "react";
import { useCurrentFrame } from "remotion";

export interface CozyDiner3DProps {
  children?: React.ReactNode;
}

/**
 * CozyDiner3D:
 * - Reference-accurate 3D low-poly diner environment (matching reel_DeIwE1-sxVr.mp4).
 * - Classic black-and-white checkered floor (flat-shaded low-poly tiles).
 * - Deep red ribbed diner booth on the left, clean white pedestal table in the center.
 * - Detailed low-poly props: 2 coffee mugs, cake slice on plate, salt/pepper shakers, ketchup squirt bottle, smartphone.
 * - Warm green-cone pendant lamp casting a warm golden pool light (pointLight + soft glow cone).
 * - Large back window with night city skyline, glowing skyscraper window dots, and retro "OPEN 24H" neon sign.
 * - Under 3,000 triangles total, zero shadow maps, flatShading: true everywhere, CPU-render friendly.
 */
export const CozyDiner3D: React.FC<CozyDiner3DProps> = ({ children }) => {
  const frame = useCurrentFrame();

  // Subtle deterministic flicker/hum on neon sign (continuous sine, 0 random)
  const neonGlow = 0.88 + 0.12 * Math.sin(frame * 0.12);
  const lampSway = Math.sin(frame * 0.03) * 0.015;

  return (
    <group name="CozyDiner3D">
      {/* 1. AMBIENT & SCENE LIGHTING (Bright Warm Cozy Diner) */}
      <hemisphereLight
        args={["#E2E8F0", "#78350F", 1.25]}
      />
      <directionalLight
        position={[2.5, 4.5, 4]}
        intensity={0.9}
        color="#FEF3C7"
      />
      <directionalLight
        position={[-3.5, 3.0, 2]}
        intensity={0.45}
        color="#FDE68A"
      />

      {/* 2. OVERHEAD VINTAGE PENDANT LAMP & WARM POOL LIGHT */}
      <group position={[0, 1.35, 0]} rotation={[0, 0, lampSway]}>
        {/* Hanging wire */}
        <mesh position={[0, 0.7, 0]}>
          <cylinderGeometry args={[0.012, 0.012, 1.4, 6]} />
          <meshStandardMaterial color="#1E293B" flatShading roughness={0.6} />
        </mesh>
        {/* Green cone shade */}
        <mesh position={[0, -0.05, 0]} rotation={[Math.PI, 0, 0]}>
          <coneGeometry args={[0.42, 0.32, 12, 1, true]} />
          <meshStandardMaterial
            color="#15803D"
            flatShading
            roughness={0.4}
            metalness={0.1}
          />
        </mesh>
        {/* Gold brass top cap */}
        <mesh position={[0, 0.12, 0]}>
          <cylinderGeometry args={[0.07, 0.11, 0.08, 10]} />
          <meshStandardMaterial color="#D97706" flatShading metalness={0.6} roughness={0.3} />
        </mesh>
        {/* Glowing bulb */}
        <mesh position={[0, -0.12, 0]}>
          <sphereGeometry args={[0.09, 8, 8]} />
          <meshStandardMaterial
            color="#FEF08A"
            emissive="#FDE047"
            emissiveIntensity={1.8}
            toneMapped={false}
          />
        </mesh>
        {/* Warm Golden Pool Point Light */}
        <pointLight
          position={[0, -0.25, 0]}
          color="#FDE047"
          intensity={2.6}
          distance={6.2}
          decay={1.6}
        />
        {/* Soft volumetric light pool cone */}
        <mesh position={[0, -1.0, 0]}>
          <coneGeometry args={[1.15, 1.8, 14, 1, true]} />
          <meshBasicMaterial
            color="#FEF08A"
            transparent
            opacity={0.065}
            depthWrite={false}
          />
        </mesh>
      </group>

      {/* 3. CHECKERED DINER FLOOR (8 x 7 alternating tiles) */}
      <group position={[0, -1.5, 0]}>
        {[-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5].map((x, xi) =>
          [-3, -2, -1, 0, 1, 2, 3].map((z, zi) => {
            const isWhite = (xi + zi) % 2 === 0;
            return (
              <mesh key={`tile-${xi}-${zi}`} position={[x * 0.72, 0, z * 0.72]}>
                <boxGeometry args={[0.71, 0.04, 0.71]} />
                <meshStandardMaterial
                  color={isWhite ? "#F8FAFC" : "#18181B"}
                  flatShading
                  roughness={0.65}
                  metalness={0.05}
                />
              </mesh>
            );
          })
        )}
      </group>

      {/* 4. DEEP RED RIBBED DINER BOOTH (Left Seating) */}
      <group position={[-1.75, -0.65, -0.1]}>
        {/* Wood base / box */}
        <mesh position={[0, -0.5, 0]}>
          <boxGeometry args={[1.0, 0.65, 1.8]} />
          <meshStandardMaterial color="#451A03" flatShading roughness={0.8} />
        </mesh>
        {/* Seat cushion */}
        <mesh position={[0.08, -0.12, 0]}>
          <boxGeometry args={[0.85, 0.16, 1.76]} />
          <meshStandardMaterial color="#B91C1C" flatShading roughness={0.6} />
        </mesh>
        {/* Backrest structure */}
        <mesh position={[-0.38, 0.52, 0]}>
          <boxGeometry args={[0.22, 1.15, 1.8]} />
          <meshStandardMaterial color="#7F1D1D" flatShading roughness={0.7} />
        </mesh>
        {/* 5 Vertical ribbed cushion rolls */}
        {[-0.68, -0.34, 0, 0.34, 0.68].map((zPos, idx) => (
          <mesh key={`rib-${idx}`} position={[-0.26, 0.52, zPos]}>
            <cylinderGeometry args={[0.09, 0.09, 1.05, 7]} />
            <meshStandardMaterial
              color={idx % 2 === 0 ? "#DC2626" : "#B91C1C"}
              flatShading
              roughness={0.55}
            />
          </mesh>
        ))}
        {/* Chrome edge piping */}
        <mesh position={[-0.38, 1.12, 0]}>
          <boxGeometry args={[0.24, 0.04, 1.84]} />
          <meshStandardMaterial color="#E2E8F0" metalness={0.7} roughness={0.3} flatShading />
        </mesh>
      </group>

      {/* 5. CENTER PEDESTAL DINER TABLE */}
      <group position={[0, -0.55, 0]}>
        {/* White tabletop with chrome beveled rim */}
        <mesh position={[0, 0, 0]}>
          <cylinderGeometry args={[0.88, 0.88, 0.08, 22]} />
          <meshStandardMaterial color="#FFFFFF" flatShading roughness={0.35} metalness={0.05} />
        </mesh>
        <mesh position={[0, -0.02, 0]}>
          <cylinderGeometry args={[0.91, 0.91, 0.05, 22]} />
          <meshStandardMaterial color="#CBD5E1" metalness={0.8} roughness={0.2} flatShading />
        </mesh>
        {/* Central chrome pedestal pillar */}
        <mesh position={[0, -0.45, 0]}>
          <cylinderGeometry args={[0.075, 0.09, 0.85, 10]} />
          <meshStandardMaterial color="#94A3B8" metalness={0.75} roughness={0.25} flatShading />
        </mesh>
        {/* Heavy floor disc base */}
        <mesh position={[0, -0.88, 0]}>
          <cylinderGeometry args={[0.42, 0.45, 0.06, 16]} />
          <meshStandardMaterial color="#64748B" metalness={0.7} roughness={0.3} flatShading />
        </mesh>

        {/* ======================================================== */}
        {/* TABLE PROPS (ON TOP OF TABLE y = +0.06)                 */}
        {/* ======================================================== */}

        {/* Coffee Mug 1 (Left, White ceramic) */}
        <group position={[-0.42, 0.14, 0.18]}>
          <mesh>
            <cylinderGeometry args={[0.08, 0.07, 0.16, 10]} />
            <meshStandardMaterial color="#F8FAFC" flatShading roughness={0.4} />
          </mesh>
          {/* Coffee inside */}
          <mesh position={[0, 0.07, 0]}>
            <cylinderGeometry args={[0.07, 0.07, 0.02, 8]} />
            <meshStandardMaterial color="#3E2723" roughness={0.9} flatShading />
          </mesh>
          {/* Handle */}
          <mesh position={[-0.09, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
            <torusGeometry args={[0.045, 0.015, 6, 8, Math.PI]} />
            <meshStandardMaterial color="#F8FAFC" flatShading roughness={0.4} />
          </mesh>
        </group>

        {/* Coffee Mug 2 (Right, Diner Teal) */}
        <group position={[0.44, 0.14, -0.14]}>
          <mesh>
            <cylinderGeometry args={[0.08, 0.07, 0.16, 10]} />
            <meshStandardMaterial color="#0284C7" flatShading roughness={0.4} />
          </mesh>
          <mesh position={[0, 0.07, 0]}>
            <cylinderGeometry args={[0.07, 0.07, 0.02, 8]} />
            <meshStandardMaterial color="#3E2723" roughness={0.9} flatShading />
          </mesh>
          <mesh position={[0.09, 0, 0]} rotation={[0, 0, -Math.PI / 2]}>
            <torusGeometry args={[0.045, 0.015, 6, 8, Math.PI]} />
            <meshStandardMaterial color="#0284C7" flatShading roughness={0.4} />
          </mesh>
        </group>

        {/* Strawberry Shortcake slice on plate */}
        <group position={[-0.12, 0.08, 0.22]}>
          {/* Small plate */}
          <mesh position={[0, 0, 0]}>
            <cylinderGeometry args={[0.22, 0.2, 0.03, 12]} />
            <meshStandardMaterial color="#F1F5F9" flatShading roughness={0.3} />
          </mesh>
          {/* Cake wedge */}
          <mesh position={[0, 0.07, 0]} rotation={[0, 0.5, 0]}>
            <coneGeometry args={[0.13, 0.12, 3]} />
            <meshStandardMaterial color="#FFFBEB" flatShading roughness={0.7} />
          </mesh>
          {/* Red strawberry topping */}
          <mesh position={[0, 0.14, 0]}>
            <dodecahedronGeometry args={[0.04, 0]} />
            <meshStandardMaterial color="#E11D48" flatShading roughness={0.5} />
          </mesh>
        </group>

        {/* Salt & Pepper Shakers */}
        <group position={[0.16, 0.12, -0.26]}>
          {/* Salt */}
          <mesh position={[-0.07, 0, 0]}>
            <cylinderGeometry args={[0.04, 0.045, 0.13, 7]} />
            <meshStandardMaterial color="#E2E8F0" flatShading roughness={0.5} />
          </mesh>
          <mesh position={[-0.07, 0.08, 0]}>
            <cylinderGeometry args={[0.035, 0.038, 0.03, 7]} />
            <meshStandardMaterial color="#94A3B8" metalness={0.7} roughness={0.3} flatShading />
          </mesh>
          {/* Pepper */}
          <mesh position={[0.07, 0, 0]}>
            <cylinderGeometry args={[0.04, 0.045, 0.13, 7]} />
            <meshStandardMaterial color="#334155" flatShading roughness={0.6} />
          </mesh>
          <mesh position={[0.07, 0.08, 0]}>
            <cylinderGeometry args={[0.035, 0.038, 0.03, 7]} />
            <meshStandardMaterial color="#94A3B8" metalness={0.7} roughness={0.3} flatShading />
          </mesh>
        </group>

        {/* Ketchup Squirt Bottle */}
        <group position={[0.3, 0.16, -0.28]}>
          <mesh>
            <cylinderGeometry args={[0.05, 0.055, 0.22, 8]} />
            <meshStandardMaterial color="#DC2626" flatShading roughness={0.5} />
          </mesh>
          {/* Cone squirt cap */}
          <mesh position={[0, 0.14, 0]}>
            <coneGeometry args={[0.045, 0.09, 8]} />
            <meshStandardMaterial color="#FFFFFF" flatShading roughness={0.4} />
          </mesh>
        </group>

        {/* Smartphone on table */}
        <group position={[-0.32, 0.05, -0.15]} rotation={[-Math.PI / 2, 0, 0.35]}>
          <mesh>
            <boxGeometry args={[0.12, 0.22, 0.015]} />
            <meshStandardMaterial color="#0F172A" flatShading roughness={0.4} metalness={0.3} />
          </mesh>
          <mesh position={[0, 0, 0.009]}>
            <planeGeometry args={[0.1, 0.19]} />
            <meshStandardMaterial
              color="#38BDF8"
              emissive="#0284C7"
              emissiveIntensity={0.6}
              toneMapped={false}
            />
          </mesh>
        </group>
      </group>

      {/* 6. BACK WALL & LARGE NIGHT SKYLINE WINDOW (Warm Cream-Beige & Indigo Twilight) */}
      <group position={[0, 0.8, -3.2]}>
        {/* Upper wall panels (warm cream-beige for high character contrast) */}
        <mesh position={[-2.4, 0.45, 0]}>
          <boxGeometry args={[1.6, 2.7, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>
        <mesh position={[2.4, 0.45, 0]}>
          <boxGeometry args={[1.6, 2.7, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>
        <mesh position={[0, 1.45, 0]}>
          <boxGeometry args={[3.2, 0.7, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>

        {/* Lower dark wood wainscoting */}
        <mesh position={[-2.4, -1.25, 0.02]}>
          <boxGeometry args={[1.6, 1.1, 0.22]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        <mesh position={[2.4, -1.25, 0.02]}>
          <boxGeometry args={[1.6, 1.1, 0.22]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        <mesh position={[0, -1.45, 0]}>
          <boxGeometry args={[3.2, 0.7, 0.2]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        {/* Dark wood chair rail moulding */}
        <mesh position={[0, -0.7, 0.12]}>
          <boxGeometry args={[6.4, 0.06, 0.06]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.6} />
        </mesh>

        {/* Big window frame (Dark mahogany wood) */}
        <mesh position={[0, 0, 0.05]}>
          <boxGeometry args={[3.2, 2.2, 0.1]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.8} />
        </mesh>
        {/* Window glass pane */}
        <mesh position={[0, 0, 0.08]}>
          <planeGeometry args={[3.0, 2.0]} />
          <meshStandardMaterial
            color="#3B4C7A"
            transparent
            opacity={0.22}
            roughness={0.1}
            metalness={0.2}
          />
        </mesh>
        {/* Central wooden divider cross */}
        <mesh position={[0, 0, 0.1]}>
          <boxGeometry args={[0.06, 2.0, 0.06]} />
          <meshStandardMaterial color="#292524" flatShading />
        </mesh>
        <mesh position={[0, 0, 0.1]}>
          <boxGeometry args={[3.0, 0.06, 0.06]} />
          <meshStandardMaterial color="#292524" flatShading />
        </mesh>

        {/* BRIGHT INDIGO TWILIGHT SKYLINE OUTSIDE WINDOW (z = -1.2 behind window) */}
        <group position={[0, -0.3, -1.2]}>
          {/* Brighter indigo twilight sky background */}
          <mesh position={[0, 0.6, -0.5]}>
            <planeGeometry args={[6.5, 4.2]} />
            <meshBasicMaterial color="#3B4C7A" />
          </mesh>

          {/* Low-poly Skyscraper Silhouettes in deep slate/indigo */}
          <mesh position={[-1.6, 0.2, -0.1]}>
            <boxGeometry args={[0.65, 1.8, 0.2]} />
            <meshStandardMaterial color="#1E293B" flatShading roughness={0.85} />
          </mesh>
          <mesh position={[-0.9, 0.5, -0.2]}>
            <boxGeometry args={[0.7, 2.3, 0.2]} />
            <meshStandardMaterial color="#0F172A" flatShading roughness={0.85} />
          </mesh>
          <mesh position={[0, 0.1, -0.3]}>
            <boxGeometry args={[0.8, 1.6, 0.2]} />
            <meshStandardMaterial color="#1E293B" flatShading roughness={0.85} />
          </mesh>
          <mesh position={[0.85, 0.6, -0.15]}>
            <boxGeometry args={[0.65, 2.5, 0.2]} />
            <meshStandardMaterial color="#0F172A" flatShading roughness={0.85} />
          </mesh>
          <mesh position={[1.5, 0.3, -0.2]}>
            <boxGeometry args={[0.55, 1.9, 0.2]} />
            <meshStandardMaterial color="#1E293B" flatShading roughness={0.85} />
          </mesh>

          {/* Abundant warm glowing apartment windows */}
          {[
            [-1.5, 0.6], [-1.7, 0.4], [-1.55, 0.2], [-1.65, 0.8],
            [-0.8, 0.9], [-1.0, 0.7], [-0.85, 0.4], [-0.95, 0.1], [-0.75, 1.2],
            [-0.1, 0.5], [0.1, 0.3], [0.0, 0.1], [0.15, 0.7],
            [0.8, 1.1], [0.95, 0.8], [0.75, 0.5], [0.9, 0.2], [0.85, 1.4],
            [1.45, 0.6], [1.55, 0.4], [1.4, 0.9],
          ].map(([wx, wy], wIdx) => (
            <mesh key={`win-${wIdx}`} position={[wx, wy, 0.05]}>
              <boxGeometry args={[0.05, 0.05, 0.02]} />
              <meshBasicMaterial
                color={wIdx % 3 === 0 ? "#FEF08A" : wIdx % 3 === 1 ? "#FCD34D" : "#F59E0B"}
              />
            </mesh>
          ))}

          {/* Retro Neon Sign Left: "LAUNDRY" / "MOTEL" Cyan & Pink */}
          <group position={[-1.3, 0.4, 0.15]}>
            <mesh>
              <boxGeometry args={[0.6, 0.22, 0.03]} />
              <meshStandardMaterial color="#0F172A" flatShading roughness={0.8} />
            </mesh>
            <mesh position={[0, 0.03, 0.02]}>
              <boxGeometry args={[0.48, 0.05, 0.02]} />
              <meshStandardMaterial
                color="#EC4899"
                emissive="#F43F5E"
                emissiveIntensity={1.8 * neonGlow}
                toneMapped={false}
              />
            </mesh>
            <mesh position={[0, -0.04, 0.02]}>
              <boxGeometry args={[0.38, 0.04, 0.02]} />
              <meshStandardMaterial
                color="#38BDF8"
                emissive="#06B6D4"
                emissiveIntensity={1.6 * neonGlow}
                toneMapped={false}
              />
            </mesh>
          </group>

          {/* Retro Cozy Neon Sign Right: "OPEN 24H" */}
          <group position={[0.7, 0.25, 0.2]}>
            {/* Neon back backing */}
            <mesh>
              <boxGeometry args={[0.85, 0.38, 0.04]} />
              <meshStandardMaterial color="#090D16" flatShading roughness={0.8} />
            </mesh>
            {/* Pink glowing border frame */}
            <mesh position={[0, 0, 0.03]}>
              <boxGeometry args={[0.8, 0.34, 0.02]} />
              <meshBasicMaterial color="#EC4899" transparent opacity={0.35} />
            </mesh>
            {/* Cyan "OPEN" glowing bar */}
            <mesh position={[0, 0.06, 0.04]}>
              <boxGeometry args={[0.55, 0.08, 0.02]} />
              <meshStandardMaterial
                color="#38BDF8"
                emissive="#00F0FF"
                emissiveIntensity={2.0 * neonGlow}
                toneMapped={false}
              />
            </mesh>
            {/* Amber "24H" glowing bar */}
            <mesh position={[0, -0.06, 0.04]}>
              <boxGeometry args={[0.42, 0.07, 0.02]} />
              <meshStandardMaterial
                color="#FDE047"
                emissive="#EAB308"
                emissiveIntensity={1.8 * neonGlow}
                toneMapped={false}
              />
            </mesh>
          </group>
        </group>
      </group>

      {/* 7. NESTED CHARACTERS / EXTRAS */}
      {children}
    </group>
  );
};
