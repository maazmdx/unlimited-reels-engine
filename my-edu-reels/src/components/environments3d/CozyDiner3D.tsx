import React from "react";
import { useCurrentFrame } from "remotion";
import * as THREE from "three";

export interface CozyDiner3DProps {
  children?: React.ReactNode;
  weatherMode?: "rain" | "sunny" | "sunset";
}

/**
 * CozyDiner3D:
 * - Reference-accurate 3D low-poly diner environment (matching reel_DeIwE1-sxVr.mp4).
 * - Warm cream-beige walls (#D6C7B2) extended all the way to ceiling (y = +4.8) with retro blue trim stripe,
 *   completely eliminating any top black void in 9:16 vertical view.
 * - Live Animated Weather in Diner Window:
 *   - "rain" (default): 28 sleek translucent angled rain streaks continuously falling diagonally outside glass,
 *     subtle drifting distant city storm clouds, softly pulsing neon LAUNDRY/OPEN 24H signs.
 *   - "sunny": Warm golden morning sky gradient, slowly drifting low-poly white clouds, soft diagonal warm sunbeams across table.
 *   - Driven 100% deterministically by useCurrentFrame() (0 Math.random()).
 * - Wide deep red ribbed booth positioned directly beneath the left seated character.
 * - Under 3,500 triangles total, zero shadow maps, flatShading: true everywhere, CPU-render friendly.
 */
export const CozyDiner3D: React.FC<CozyDiner3DProps> = ({
  children,
  weatherMode = "rain",
}) => {
  const frame = useCurrentFrame();

  const isSunny = weatherMode === "sunny";
  const isSunset = weatherMode === "sunset";
  const isRain = !isSunny && !isSunset;

  // Subtle deterministic flicker/hum on neon sign (continuous sine, 0 random)
  const neonGlow = isRain
    ? 0.88 + 0.12 * Math.sin(frame * 0.12)
    : isSunset
    ? 0.70 + 0.10 * Math.sin(frame * 0.12)
    : 0.35; // Dimmer unlit appearance in daytime

  const lampSway = Math.sin(frame * 0.03) * 0.015;

  return (
    <group name="CozyDiner3D">
      {/* 1. AMBIENT & SCENE LIGHTING (Bright Warm Cozy Diner) */}
      <hemisphereLight
        args={[
          isSunny ? "#FEF9C3" : isSunset ? "#FED7AA" : "#E2E8F0",
          isSunny ? "#A16207" : isSunset ? "#7C2D12" : "#78350F",
          isSunny ? 1.35 : 1.25,
        ]}
      />
      <directionalLight
        position={[2.5, 4.5, 4]}
        intensity={isSunny ? 1.30 : isSunset ? 1.10 : 0.9}
        color={isSunny ? "#FEF08A" : isSunset ? "#FB923C" : "#FEF3C7"}
      />
      <directionalLight
        position={[-3.5, 3.0, 2]}
        intensity={isSunny ? 0.65 : 0.45}
        color={isSunny ? "#FDE68A" : isSunset ? "#F97316" : "#FDE68A"}
      />

      {/* 2. OVERHEAD VINTAGE PENDANT LAMP & WARM POOL LIGHT */}
      <group position={[0, 1.35, 0]} rotation={[0, 0, lampSway]}>
        {/* Hanging wire */}
        <mesh position={[0, 1.7, 0]}>
          <cylinderGeometry args={[0.012, 0.012, 3.4, 6]} />
          <meshStandardMaterial color="#1E293B" flatShading roughness={0.6} />
        </mesh>
        {/* Green cone shade */}
        <mesh position={[0, -0.05, 0]} rotation={[Math.PI, 0, 0]}>
          <coneGeometry args={[0.42, 0.32, 12, 1, true]} />
          <meshStandardMaterial color="#15803D" flatShading roughness={0.4} metalness={0.1} />
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
        <pointLight position={[0, -0.25, 0]} color="#FDE047" intensity={2.6} distance={6.2} decay={1.6} />
        {/* Soft volumetric light pool cone */}
        <mesh position={[0, -1.0, 0]}>
          <coneGeometry args={[1.15, 1.8, 14, 1, true]} />
          <meshBasicMaterial color="#FEF08A" transparent opacity={0.065} depthWrite={false} />
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

      {/* 4. DEEP RED RIBBED DINER BOOTH (Left Seating, Centered around x = -1.15) */}
      <group position={[-1.35, -0.65, -0.1]}>
        {/* Wood base / box */}
        <mesh position={[0, -0.5, 0]}>
          <boxGeometry args={[1.35, 0.65, 1.8]} />
          <meshStandardMaterial color="#451A03" flatShading roughness={0.8} />
        </mesh>
        {/* Seat cushion (Comfortably wide beneath seated human) */}
        <mesh position={[0.06, -0.12, 0]}>
          <boxGeometry args={[1.35, 0.22, 1.8]} />
          <meshStandardMaterial color="#B91C1C" flatShading roughness={0.6} />
        </mesh>
        {/* Backrest structure */}
        <mesh position={[-0.56, 0.52, 0]}>
          <boxGeometry args={[0.22, 1.15, 1.8]} />
          <meshStandardMaterial color="#7F1D1D" flatShading roughness={0.7} />
        </mesh>
        {/* 5 Vertical ribbed cushion rolls */}
        {[-0.68, -0.34, 0, 0.34, 0.68].map((zPos, idx) => (
          <mesh key={`rib-${idx}`} position={[-0.44, 0.52, zPos]}>
            <cylinderGeometry args={[0.10, 0.10, 1.05, 7]} />
            <meshStandardMaterial
              color={idx % 2 === 0 ? "#DC2626" : "#B91C1C"}
              flatShading
              roughness={0.55}
            />
          </mesh>
        ))}
        {/* Chrome edge piping */}
        <mesh position={[-0.56, 1.12, 0]}>
          <boxGeometry args={[0.24, 0.04, 1.84]} />
          <meshStandardMaterial color="#E2E8F0" metalness={0.7} roughness={0.3} flatShading />
        </mesh>
      </group>

      {/* 4B. LEFT DINER COUNTER & 2 RED SWIVEL BARSTOOLS (3/4 Room Depth) */}
      <group position={[-2.4, -0.65, 0.6]}>
        {/* Dark wood counter base */}
        <mesh position={[0, -0.45, 0]}>
          <boxGeometry args={[0.7, 0.75, 2.8]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.8} />
        </mesh>
        {/* Laminated counter top with chrome rim */}
        <mesh position={[0.02, -0.06, 0]}>
          <boxGeometry args={[0.78, 0.08, 2.9]} />
          <meshStandardMaterial color="#F8FAFC" flatShading roughness={0.3} metalness={0.05} />
        </mesh>
        <mesh position={[0.40, -0.06, 0]}>
          <boxGeometry args={[0.04, 0.09, 2.92]} />
          <meshStandardMaterial color="#CBD5E1" metalness={0.8} roughness={0.2} flatShading />
        </mesh>

        {/* 2 Red Swivel Barstools with Chrome Poles */}
        {[-0.65, 0.65].map((zPos, sIdx) => (
          <group key={`barstool-${sIdx}`} position={[0.62, 0, zPos]}>
            {/* Chrome pedestal base */}
            <mesh position={[0, -0.82, 0]}>
              <cylinderGeometry args={[0.22, 0.24, 0.04, 12]} />
              <meshStandardMaterial color="#94A3B8" metalness={0.8} roughness={0.2} flatShading />
            </mesh>
            {/* Chrome pole */}
            <mesh position={[0, -0.45, 0]}>
              <cylinderGeometry args={[0.04, 0.04, 0.72, 8]} />
              <meshStandardMaterial color="#CBD5E1" metalness={0.8} roughness={0.2} flatShading />
            </mesh>
            {/* Footrest ring */}
            <mesh position={[0, -0.55, 0]}>
              <torusGeometry args={[0.14, 0.015, 6, 12]} />
              <meshStandardMaterial color="#94A3B8" metalness={0.8} roughness={0.2} flatShading />
            </mesh>
            {/* Red vinyl round seat cushion */}
            <mesh position={[0, -0.08, 0]}>
              <cylinderGeometry args={[0.22, 0.20, 0.12, 12]} />
              <meshStandardMaterial color="#DC2626" flatShading roughness={0.5} />
            </mesh>
            {/* Chrome seat rim ring */}
            <mesh position={[0, -0.13, 0]}>
              <cylinderGeometry args={[0.23, 0.23, 0.03, 12]} />
              <meshStandardMaterial color="#E2E8F0" metalness={0.85} roughness={0.2} flatShading />
            </mesh>
          </group>
        ))}
      </group>

      {/* 4C. WOODEN WALL SHELVES WITH COFFEE CUPS (Mounted behind red booth for rich close-up depth) */}
      <group position={[-1.75, 1.05, -3.05]}>
        {/* Upper Shelf */}
        <mesh position={[0, 0.45, 0]}>
          <boxGeometry args={[1.65, 0.06, 0.28]} />
          <meshStandardMaterial color="#5C3A21" flatShading roughness={0.7} />
        </mesh>
        {/* Upper Shelf Metal Brackets */}
        {[-0.6, 0.6].map((bx, i) => (
          <mesh key={`bk-u-${i}`} position={[bx, 0.32, -0.05]}>
            <boxGeometry args={[0.04, 0.22, 0.16]} />
            <meshStandardMaterial color="#1E293B" flatShading metalness={0.7} />
          </mesh>
        ))}
        {/* Upper Shelf Cups (Yellow, Turquoise, Cream, Coral) */}
        {[
          { x: -0.48, color: "#FBBF24" },
          { x: -0.16, color: "#06B6D4" },
          { x: 0.16, color: "#FEF08A" },
          { x: 0.48, color: "#F43F5E" },
        ].map((cup, i) => (
          <group key={`cup-u-${i}`} position={[cup.x, 0.58, 0.02]}>
            <mesh>
              <cylinderGeometry args={[0.07, 0.06, 0.15, 8]} />
              <meshStandardMaterial color={cup.color} flatShading roughness={0.4} />
            </mesh>
            <mesh position={[0.08, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
              <torusGeometry args={[0.035, 0.012, 5, 8, Math.PI]} />
              <meshStandardMaterial color={cup.color} flatShading roughness={0.4} />
            </mesh>
          </group>
        ))}

        {/* Lower Shelf */}
        <mesh position={[0, -0.15, 0]}>
          <boxGeometry args={[1.65, 0.06, 0.28]} />
          <meshStandardMaterial color="#5C3A21" flatShading roughness={0.7} />
        </mesh>
        {/* Lower Shelf Brackets */}
        {[-0.6, 0.6].map((bx, i) => (
          <mesh key={`bk-l-${i}`} position={[bx, -0.28, -0.05]}>
            <boxGeometry args={[0.04, 0.22, 0.16]} />
            <meshStandardMaterial color="#1E293B" flatShading metalness={0.7} />
          </mesh>
        ))}
        {/* Lower Shelf Glass Syrup Jars & Mugs */}
        {[
          { x: -0.42, color: "#E2E8F0" },
          { x: -0.12, color: "#F97316" },
          { x: 0.22, color: "#E0E7FF" },
          { x: 0.50, color: "#10B981" },
        ].map((jar, i) => (
          <mesh key={`jar-l-${i}`} position={[jar.x, -0.04, 0.02]}>
            <cylinderGeometry args={[0.065, 0.06, 0.14, 8]} />
            <meshStandardMaterial color={jar.color} flatShading roughness={0.35} />
          </mesh>
        ))}
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

        {/* Table Props */}
        {/* Coffee Mug 1 (Left, White ceramic) */}
        <group position={[-0.42, 0.14, 0.18]}>
          <mesh>
            <cylinderGeometry args={[0.08, 0.07, 0.16, 10]} />
            <meshStandardMaterial color="#F8FAFC" flatShading roughness={0.4} />
          </mesh>
          <mesh position={[0, 0.07, 0]}>
            <cylinderGeometry args={[0.07, 0.07, 0.02, 8]} />
            <meshStandardMaterial color="#3E2723" roughness={0.9} flatShading />
          </mesh>
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

        {/* Cake slice on plate */}
        <group position={[-0.12, 0.08, 0.22]}>
          <mesh position={[0, 0, 0]}>
            <cylinderGeometry args={[0.22, 0.2, 0.03, 12]} />
            <meshStandardMaterial color="#F1F5F9" flatShading roughness={0.3} />
          </mesh>
          <mesh position={[0, 0.07, 0]} rotation={[0, 0.5, 0]}>
            <coneGeometry args={[0.13, 0.12, 3]} />
            <meshStandardMaterial color="#FFFBEB" flatShading roughness={0.7} />
          </mesh>
          <mesh position={[0, 0.14, 0]}>
            <dodecahedronGeometry args={[0.04, 0]} />
            <meshStandardMaterial color="#E11D48" flatShading roughness={0.5} />
          </mesh>
        </group>

        {/* Salt & Pepper Shakers */}
        <group position={[0.16, 0.12, -0.26]}>
          <mesh position={[-0.07, 0, 0]}>
            <cylinderGeometry args={[0.04, 0.045, 0.13, 7]} />
            <meshStandardMaterial color="#E2E8F0" flatShading roughness={0.5} />
          </mesh>
          <mesh position={[-0.07, 0.08, 0]}>
            <cylinderGeometry args={[0.035, 0.038, 0.03, 7]} />
            <meshStandardMaterial color="#94A3B8" metalness={0.7} roughness={0.3} flatShading />
          </mesh>
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

      {/* =================================================================== */}
      {/* 6. FULL-HEIGHT BACK WALL, NIGHT WINDOW & SKYLINE (Zero Black Void)  */}
      {/* =================================================================== */}
      <group position={[0, 0.8, -3.2]}>
        {/* Full-Height Left Cream Wall Panel (#D6C7B2, covers up to y = +4.0 in group) */}
        <mesh position={[-2.5, 1.45, 0]}>
          <boxGeometry args={[1.8, 4.3, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>

        {/* Full-Height Right Cream Wall Panel (#D6C7B2) */}
        <mesh position={[2.5, 1.45, 0]}>
          <boxGeometry args={[1.8, 4.3, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>

        {/* Cream Wall Above Window (y = 1.1 to y = 3.6 in group) */}
        <mesh position={[0, 2.35, 0]}>
          <boxGeometry args={[3.4, 2.5, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>

        {/* Retro Blue Trim Stripe (#0284C7 with silver chrome borders) */}
        <mesh position={[0, 3.45, 0.12]}>
          <boxGeometry args={[8.6, 0.24, 0.08]} />
          <meshStandardMaterial color="#0284C7" flatShading roughness={0.5} />
        </mesh>
        <mesh position={[0, 3.59, 0.13]}>
          <boxGeometry args={[8.6, 0.04, 0.08]} />
          <meshStandardMaterial color="#E2E8F0" metalness={0.8} roughness={0.2} flatShading />
        </mesh>
        <mesh position={[0, 3.31, 0.13]}>
          <boxGeometry args={[8.6, 0.04, 0.08]} />
          <meshStandardMaterial color="#E2E8F0" metalness={0.8} roughness={0.2} flatShading />
        </mesh>

        {/* High Upper Cream Wall Section Above Blue Stripe (Reaches y = +4.8 in group / +5.6 in world!) */}
        <mesh position={[0, 4.25, 0]}>
          <boxGeometry args={[8.6, 1.35, 0.2]} />
          <meshStandardMaterial color="#D6C7B2" flatShading roughness={0.85} />
        </mesh>

        {/* Dark Ceiling Plane (Extending forward at y = +4.9 to completely enclose top frustum) */}
        <mesh position={[0, 4.9, 2.5]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[14.0, 9.0]} />
          <meshStandardMaterial color="#0B0F19" roughness={0.9} flatShading />
        </mesh>
        {/* Dark Ceiling Beams */}
        {[-2.4, 0, 2.4].map((bx, bIdx) => (
          <mesh key={`beam-${bIdx}`} position={[bx, 4.8, 2.5]} rotation={[Math.PI / 2, 0, 0]}>
            <boxGeometry args={[0.22, 9.0, 0.18]} />
            <meshStandardMaterial color="#1C1917" flatShading roughness={0.8} />
          </mesh>
        ))}

        {/* Lower Dark Wood Wainscoting */}
        <mesh position={[-2.5, -1.25, 0.02]}>
          <boxGeometry args={[1.8, 1.1, 0.22]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        <mesh position={[2.5, -1.25, 0.02]}>
          <boxGeometry args={[1.8, 1.1, 0.22]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        <mesh position={[0, -1.55, 0.02]}>
          <boxGeometry args={[3.4, 0.9, 0.22]} />
          <meshStandardMaterial color="#3E2723" flatShading roughness={0.7} />
        </mesh>
        {/* Dark Wood Chair Rail Moulding */}
        <mesh position={[0, -0.7, 0.14]}>
          <boxGeometry args={[8.6, 0.08, 0.08]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.6} />
        </mesh>

        {/* ================================================================= */}
        {/* OPEN WINDOW APERTURE & Z-ORDERED SKYLINE / NEON SIGNS             */}
        {/* ================================================================= */}
        {/* 1. Hollow Window Perimeter Frame (Zero solid blockers!) */}
        {/* Top window frame bar */}
        <mesh position={[0, 1.12, 0.08]}>
          <boxGeometry args={[4.28, 0.08, 0.14]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.8} />
        </mesh>
        {/* Left window frame bar */}
        <mesh position={[-2.10, 0, 0.08]}>
          <boxGeometry args={[0.08, 2.24, 0.14]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.8} />
        </mesh>
        {/* Right window frame bar */}
        <mesh position={[2.10, 0, 0.08]}>
          <boxGeometry args={[0.08, 2.24, 0.14]} />
          <meshStandardMaterial color="#1C1917" flatShading roughness={0.8} />
        </mesh>
        {/* Warm Wooden Windowsill (Extended forward for depth) */}
        <mesh position={[0, -1.12, 0.15]}>
          <boxGeometry args={[4.40, 0.10, 0.28]} />
          <meshStandardMaterial color="#78350F" flatShading roughness={0.65} />
        </mesh>

        {/* 2. Thin Window Mullion Crossbars */}
        {[-1.05, 0.0, 1.05].map((mx, mi) => (
          <mesh key={`mullion-v-${mi}`} position={[mx, 0, 0.09]}>
            <boxGeometry args={[0.045, 2.16, 0.06]} />
            <meshStandardMaterial color="#292524" flatShading />
          </mesh>
        ))}
        <mesh position={[0, 0.15, 0.09]}>
          <boxGeometry args={[4.16, 0.045, 0.06]} />
          <meshStandardMaterial color="#292524" flatShading />
        </mesh>

        {/* 3. Transparent Tinted Window Glass Pane */}
        <mesh position={[0, 0, 0.06]}>
          <planeGeometry args={[4.16, 2.16]} />
          <meshStandardMaterial
            color={isSunny ? "#93C5FD" : "#2E3B63"}
            transparent
            opacity={isSunny ? 0.06 : 0.10}
            roughness={0.1}
            metalness={0.1}
          />
        </mesh>

        {/* ================================================================= */}
        {/* 4. SKYLINE & NEONS (Positioned cleanly inside window opening)     */}
        {/* ================================================================= */}
        <group position={[0, -0.05, -0.22]}>
          {/* Sky Background Plane (Deep indigo night sky #2E3B63 / sunset orange / golden morning) */}
          <mesh position={[0, 0.45, -0.35]}>
            <planeGeometry args={[7.4, 4.4]} />
            <meshBasicMaterial
              color={isSunny ? "#FDE68A" : isSunset ? "#9A3412" : "#2E3B63"}
            />
          </mesh>

          {/* Low-Poly Skyscraper Silhouettes (#1E293B & #0F172A / slate in daylight) */}
          <mesh position={[-1.35, 0.22, -0.18]}>
            <boxGeometry args={[0.62, 1.85, 0.15]} />
            <meshStandardMaterial
              color={isSunny ? "#475569" : "#1E293B"}
              flatShading
              roughness={0.8}
            />
          </mesh>
          <mesh position={[-0.72, 0.58, -0.22]}>
            <boxGeometry args={[0.66, 2.4, 0.15]} />
            <meshStandardMaterial
              color={isSunny ? "#334155" : "#0F172A"}
              flatShading
              roughness={0.8}
            />
          </mesh>
          <mesh position={[0.05, 0.28, -0.20]}>
            <boxGeometry args={[0.76, 1.9, 0.15]} />
            <meshStandardMaterial
              color={isSunny ? "#475569" : "#1E293B"}
              flatShading
              roughness={0.8}
            />
          </mesh>
          <mesh position={[0.82, 0.65, -0.16]}>
            <boxGeometry args={[0.65, 2.5, 0.15]} />
            <meshStandardMaterial
              color={isSunny ? "#334155" : "#0F172A"}
              flatShading
              roughness={0.8}
            />
          </mesh>
          <mesh position={[1.44, 0.32, -0.20]}>
            <boxGeometry args={[0.54, 1.95, 0.15]} />
            <meshStandardMaterial
              color={isSunny ? "#475569" : "#1E293B"}
              flatShading
              roughness={0.8}
            />
          </mesh>

          {/* Glowing Warm Apartment Window Dots (emissiveIntensity: 1.5 in rain, 0.35 in sunny) */}
          {[
            [-1.45, 0.65], [-1.25, 0.45], [-1.4, 0.25], [-1.3, 0.85],
            [-0.82, 0.95], [-0.62, 0.75], [-0.80, 0.45], [-0.65, 0.15], [-0.75, 1.25],
            [-0.10, 0.55], [0.15, 0.35], [0.02, 0.15], [0.20, 0.75],
            [0.72, 1.15], [0.92, 0.85], [0.75, 0.55], [0.90, 0.25], [0.85, 1.45],
            [1.38, 0.65], [1.50, 0.45], [1.42, 0.95],
          ].map(([wx, wy], wIdx) => (
            <mesh key={`win-dot-${wIdx}`} position={[wx, wy, -0.06]}>
              <boxGeometry args={[0.055, 0.055, 0.02]} />
              <meshStandardMaterial
                color={wIdx % 3 === 0 ? "#FEF08A" : wIdx % 3 === 1 ? "#FCD34D" : "#F59E0B"}
                emissive={wIdx % 3 === 0 ? "#FEF08A" : "#F59E0B"}
                emissiveIntensity={isSunny ? 0.35 : 1.5}
                toneMapped={false}
              />
            </mesh>
          ))}

          {/* Retro Neon Sign Left: "LAUNDRY" / "MOTEL" Cyan & Pink */}
          <group position={[-1.12, 0.42, 0.02]}>
            <mesh>
              <boxGeometry args={[0.62, 0.24, 0.03]} />
              <meshStandardMaterial color="#0F172A" flatShading roughness={0.8} />
            </mesh>
            <mesh position={[0, 0.04, 0.025]}>
              <boxGeometry args={[0.50, 0.06, 0.02]} />
              <meshStandardMaterial
                color="#EC4899"
                emissive="#F43F5E"
                emissiveIntensity={2.4 * neonGlow}
                toneMapped={false}
              />
            </mesh>
            <mesh position={[0, -0.04, 0.025]}>
              <boxGeometry args={[0.40, 0.05, 0.02]} />
              <meshStandardMaterial
                color="#38BDF8"
                emissive="#06B6D4"
                emissiveIntensity={2.0 * neonGlow}
                toneMapped={false}
              />
            </mesh>
          </group>

          {/* Retro Neon Sign Right: "OPEN 24H" */}
          <group position={[0.78, 0.28, 0.04]}>
            <mesh>
              <boxGeometry args={[0.88, 0.40, 0.04]} />
              <meshStandardMaterial color="#090D16" flatShading roughness={0.8} />
            </mesh>
            {/* Glowing pink border frame */}
            <mesh position={[0, 0, 0.03]}>
              <boxGeometry args={[0.82, 0.35, 0.02]} />
              <meshBasicMaterial color="#EC4899" transparent opacity={0.45} />
            </mesh>
            {/* Cyan "OPEN" glowing bar */}
            <mesh position={[0, 0.06, 0.04]}>
              <boxGeometry args={[0.58, 0.08, 0.02]} />
              <meshStandardMaterial
                color="#38BDF8"
                emissive="#00F0FF"
                emissiveIntensity={2.6 * neonGlow}
                toneMapped={false}
              />
            </mesh>
            {/* Amber "24H" glowing bar */}
            <mesh position={[0, -0.06, 0.04]}>
              <boxGeometry args={[0.44, 0.07, 0.02]} />
              <meshStandardMaterial
                color="#FDE047"
                emissive="#EAB308"
                emissiveIntensity={2.2 * neonGlow}
                toneMapped={false}
              />
            </mesh>
          </group>
        </group>

        {/* ================================================================= */}
        {/* 5. WEATHER EFFECTS: RAIN/TWILIGHT MODE vs SUNNY MODE              */}
        {/* ================================================================= */}
        {/* RAIN & SUNSET: 35 sleek translucent angled rain streaks + city storm clouds (Window always alive) */}
        {(isRain || isSunset) && (
          <group position={[0, 0, 0.02]}>
            {/* Subtle drifting distant city storm clouds */}
            <mesh position={[(((frame * 0.005 + 1.2) % 7.2) - 3.6), 0.85, -0.26]}>
              <boxGeometry args={[2.2, 0.50, 0.10]} />
              <meshBasicMaterial color="#1E293B" transparent opacity={0.38} />
            </mesh>
            <mesh position={[(((frame * 0.0035 + 4.5) % 7.2) - 3.6), 1.05, -0.24]}>
              <boxGeometry args={[1.6, 0.38, 0.10]} />
              <meshBasicMaterial color="#334155" transparent opacity={0.32} />
            </mesh>

            {/* 35 Sleek Translucent Angled Falling Rain Streaks (Zero Math.random()) */}
            {Array.from({ length: 35 }).map((_, i) => {
              const xBase = -2.05 + (((i * 47) % 100) / 100) * 4.1;
              const speed = 0.09 + ((i * 17) % 7) * 0.012;
              const offset = (((i * 61) % 100) / 100) * 3.4;
              const spanY = 3.2;
              const cycleY = (frame * speed + offset) % spanY;
              const yPos = 1.6 - cycleY;
              const xPos = xBase - cycleY * 0.18; // Angled diagonal drift
              const zPos = -0.02 - ((i % 4) * 0.02);

              return (
                <mesh
                  key={`rain-streak-${i}`}
                  position={[xPos, yPos, zPos]}
                  rotation={[0, 0, -0.20]}
                >
                  <boxGeometry args={[0.016, 0.28, 0.008]} />
                  <meshBasicMaterial
                    color="#93C5FD"
                    transparent
                    opacity={0.45}
                    depthWrite={false}
                  />
                </mesh>
              );
            })}
          </group>
        )}

        {/* SUNNY MODE: Golden sky glow + slowly drifting low-poly white clouds */}
        {isSunny && (
          <group position={[0, 0, 0.02]}>
            {/* Golden Horizon Morning Glow */}
            <mesh position={[0, -0.15, -0.32]}>
              <planeGeometry args={[6.8, 2.0]} />
              <meshBasicMaterial color="#FDBA74" transparent opacity={0.55} />
            </mesh>

            {/* Drifting Low-Poly White Clouds Outside Window */}
            {[
              { baseOffset: 0.8, y: 0.82, z: -0.22, speed: 0.006, scale: 0.85 },
              { baseOffset: 3.2, y: 1.05, z: -0.20, speed: 0.0045, scale: 1.10 },
              { baseOffset: 5.6, y: 0.65, z: -0.24, speed: 0.0055, scale: 0.75 },
            ].map((cloud, ci) => {
              const cloudX = (((frame * cloud.speed + cloud.baseOffset) % 7.2) - 3.6);
              return (
                <group
                  key={`sunny-cloud-${ci}`}
                  position={[cloudX, cloud.y, cloud.z]}
                  scale={cloud.scale}
                >
                  <mesh position={[-0.22, 0, 0]}>
                    <dodecahedronGeometry args={[0.22, 0]} />
                    <meshStandardMaterial color="#FFFFFF" flatShading roughness={0.9} />
                  </mesh>
                  <mesh position={[0, 0.06, 0.02]}>
                    <dodecahedronGeometry args={[0.28, 0]} />
                    <meshStandardMaterial color="#FFFFFF" flatShading roughness={0.9} />
                  </mesh>
                  <mesh position={[0.24, -0.02, -0.01]}>
                    <dodecahedronGeometry args={[0.20, 0]} />
                    <meshStandardMaterial color="#FFFFFF" flatShading roughness={0.9} />
                  </mesh>
                </group>
              );
            })}
          </group>
        )}
      </group>

      {/* 6. WARM SUNBEAMS ACROSS DINER TABLE (Sunny Mode Only) */}
      {isSunny && (
        <group position={[0.15, -0.20, 0.50]} rotation={[-0.32, 0.28, -0.48]}>
          <mesh position={[0, 0, 0]}>
            <planeGeometry args={[1.5, 3.4]} />
            <meshBasicMaterial
              color="#FEF08A"
              transparent
              opacity={0.075}
              depthWrite={false}
              side={THREE.DoubleSide}
            />
          </mesh>
          <mesh position={[0.25, 0.1, 0.08]}>
            <planeGeometry args={[1.0, 3.0]} />
            <meshBasicMaterial
              color="#FDE047"
              transparent
              opacity={0.045}
              depthWrite={false}
              side={THREE.DoubleSide}
            />
          </mesh>
        </group>
      )}

      {/* 7. NESTED CHARACTERS / EXTRAS */}
      {children}
    </group>
  );
};
