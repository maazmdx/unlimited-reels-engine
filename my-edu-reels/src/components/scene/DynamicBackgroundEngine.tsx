import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

export type SceneEnvironment = "diner" | "inside_home" | "outside_home" | "modern_office";
export type WeatherType = "raining" | "sunny" | "night_clear" | "overcast";

export interface DynamicBackgroundProps {
  environment?: SceneEnvironment;
  weather?: WeatherType;
  ambientIntensity?: number;
}

export const DynamicBackgroundEngine: React.FC<DynamicBackgroundProps> = ({
  environment = "diner",
  weather = "raining",
  ambientIntensity = 1.0,
}) => {
  const frame = useCurrentFrame();

  // 1. Procedural animated raindrops for rainy windows
  const raindrops = useMemo(() => {
    const drops = [];
    for (let i = 0; i < 55; i++) {
      const x = 90 + ((i * 47) % 900);
      const speed = 14 + (i % 9) * 2.8;
      const length = 24 + (i % 7) * 7;
      const delay = (i * 37) % 600;
      drops.push({ id: i, x, speed, length, delay });
    }
    return drops;
  }, []);

  // 2. Procedural clouds for sunny / outside terrace
  const clouds = useMemo(() => {
    return [
      { id: 1, y: 220, scale: 1.1, baseSpeed: 0.4 },
      { id: 2, y: 340, scale: 0.8, baseSpeed: 0.25 },
      { id: 3, y: 160, scale: 1.3, baseSpeed: 0.5 },
    ];
  }, []);

  // 3. Ambient lighting pulses
  const lampPulse = 0.96 + Math.sin(frame / 14) * 0.04 * ambientIntensity;
  const sunPulse = 0.98 + Math.sin(frame / 20) * 0.02 * ambientIntensity;
  const neonFlicker = frame % 180 === 42 || frame % 180 === 45 ? 0.35 : 1.0;

  return (
    <div
      style={{
        position: "absolute",
        width: 1080,
        height: 1920,
        overflow: "hidden",
        backgroundColor: environment === "outside_home" && weather === "sunny" ? "#1E293B" : "#07090E",
      }}
    >
      <svg
        width="1080"
        height="1920"
        viewBox="0 0 1080 1920"
        style={{ position: "absolute", top: 0, left: 0 }}
      >
        <defs>
          {/* Night Sky Gradient */}
          <linearGradient id="bgNightSky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#04060A" />
            <stop offset="50%" stopColor="#09101E" />
            <stop offset="100%" stopColor="#0E1729" />
          </linearGradient>

          {/* Sunny Sky Gradient */}
          <linearGradient id="bgSunnySky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#1E3A8A" />
            <stop offset="40%" stopColor="#2563EB" />
            <stop offset="70%" stopColor="#60A5FA" />
            <stop offset="100%" stopColor="#93C5FD" />
          </linearGradient>

          {/* Golden Sunset / Warm Sky */}
          <linearGradient id="bgGoldenSky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#31103F" />
            <stop offset="45%" stopColor="#7E22CE" />
            <stop offset="75%" stopColor="#E11D48" />
            <stop offset="100%" stopColor="#FB923C" />
          </linearGradient>

          {/* Window Glass Glare */}
          <linearGradient id="bgGlassGlare" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(255, 255, 255, 0.09)" />
            <stop offset="40%" stopColor="rgba(255, 255, 255, 0.02)" />
            <stop offset="100%" stopColor="rgba(255, 255, 255, 0.0)" />
          </linearGradient>

          {/* Table Lamp Warm Glow */}
          <radialGradient id="bgLampGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 185, 75, 0.45)" />
            <stop offset="40%" stopColor="rgba(255, 150, 45, 0.22)" />
            <stop offset="70%" stopColor="rgba(255, 120, 20, 0.08)" />
            <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
          </radialGradient>

          {/* Office Blue Ambient Glow */}
          <radialGradient id="bgOfficeGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(56, 189, 248, 0.35)" />
            <stop offset="45%" stopColor="rgba(14, 165, 233, 0.15)" />
            <stop offset="80%" stopColor="rgba(3, 105, 161, 0.04)" />
            <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
          </radialGradient>

          {/* Neon Glow Blur Filter */}
          <filter id="bgNeonBlur" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="16" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* BASE SKY & HORIZON                                      */}
        {/* ======================================================== */}
        <rect
          width="1080"
          height="1920"
          fill={weather === "sunny" ? "url(#bgSunnySky)" : "url(#bgNightSky)"}
        />

        {/* ======================================================== */}
        {/* OUTSIDE CITY SKYLINE / MOUNTAINS                        */}
        {/* ======================================================== */}
        {/* Far background silhouettes */}
        <g opacity={weather === "sunny" ? "0.45" : "0.7"}>
          {/* Skyscraper silhouettes */}
          <rect x="80" y="440" width="110" height="620" fill="#0A0F1D" />
          <rect x="210" y="380" width="140" height="680" fill="#0C1427" />
          <rect x="370" y="490" width="90" height="570" fill="#080D1A" />
          <rect x="480" y="340" width="150" height="720" fill="#0D162B" />
          <rect x="650" y="420" width="120" height="640" fill="#0B1324" />
          <rect x="790" y="360" width="130" height="700" fill="#0E182F" />
          <rect x="940" y="460" width="100" height="600" fill="#090E1C" />

          {/* Building Window Dots (Night) */}
          {weather !== "sunny" && (
            <g fill="#FDE047" opacity="0.45">
              {[0, 1, 2, 3, 4, 5, 6].map((row) => (
                <React.Fragment key={row}>
                  <rect x="235" y={420 + row * 45} width="6" height="10" />
                  <rect x="270" y={420 + row * 45} width="6" height="10" />
                  <rect x="310" y={420 + row * 45} width="6" height="10" />
                  <rect x="510" y={380 + row * 50} width="8" height="12" />
                  <rect x="550" y={380 + row * 50} width="8" height="12" />
                  <rect x="590" y={380 + row * 50} width="8" height="12" />
                  <rect x="820" y={410 + row * 48} width="7" height="11" />
                  <rect x="860" y={410 + row * 48} width="7" height="11" />
                </React.Fragment>
              ))}
            </g>
          )}

          {/* Building Antenna with Blinking Red Lights */}
          <line x1="555" y1="340" x2="555" y2="280" stroke="#334155" strokeWidth="4" />
          <circle
            cx="555"
            cy="280"
            r="5"
            fill="#EF4444"
            opacity={frame % 60 < 30 ? 0.9 : 0.2}
          />

          <line x1="855" y1="360" x2="855" y2="310" stroke="#334155" strokeWidth="3" />
          <circle
            cx="855"
            cy="310"
            r="4"
            fill="#EF4444"
            opacity={frame % 50 < 25 ? 0.9 : 0.2}
          />
        </g>

        {/* ======================================================== */}
        {/* WEATHER ENGINE: RAIN OR SUNNY DRIFTING CLOUDS           */}
        {/* ======================================================== */}
        {weather === "sunny" && (
          <g>
            {/* Drifting Clouds */}
            {clouds.map((c) => {
              const xPos = ((frame * c.baseSpeed * 1.5) % 1400) - 300;
              return (
                <g
                  key={c.id}
                  transform={`translate(${xPos}, ${c.y}) scale(${c.scale})`}
                  opacity="0.65"
                >
                  <path
                    d="M 60,60 A 30,30 0 0,1 110,40 A 45,45 0 0,1 180,50 A 35,35 0 0,1 230,75 A 25,25 0 0,1 220,105 L 50,105 A 25,25 0 0,1 60,60 Z"
                    fill="#FFFFFF"
                  />
                </g>
              );
            })}

            {/* Radiant Sun Lens Flare */}
            <circle
              cx="860"
              cy="210"
              r={90 * sunPulse}
              fill="#FDE047"
              opacity="0.3"
              filter="blur(25px)"
            />
            <circle
              cx="860"
              cy="210"
              r="48"
              fill="#FEF08A"
              opacity="0.85"
            />
          </g>
        )}

        {/* ======================================================== */}
        {/* DISTANT CYBER NEON SIGNS (DINER & OFFICE)               */}
        {/* ======================================================== */}
        {(environment === "diner" || environment === "modern_office") && (
          <g opacity={0.8 * neonFlicker} filter="url(#bgNeonBlur)">
            {/* GEMINI 24/7 Neon Sign */}
            <rect
              x="160"
              y="280"
              width="210"
              height="80"
              rx="10"
              fill="none"
              stroke="#FF2A85"
              strokeWidth="4"
            />
            <text
              x="265"
              y="330"
              fill="#FF4DA6"
              fontSize="28"
              fontFamily="Arial, sans-serif"
              fontWeight="bold"
              textAnchor="middle"
              letterSpacing="3"
            >
              GEMINI 24/7
            </text>

            {/* ANTIGRAVITY Neon Sign */}
            <rect
              x="710"
              y="260"
              width="220"
              height="80"
              rx="10"
              fill="none"
              stroke="#00F0FF"
              strokeWidth="4"
            />
            <text
              x="820"
              y="310"
              fill="#38BDF8"
              fontSize="24"
              fontFamily="Arial, sans-serif"
              fontWeight="bold"
              textAnchor="middle"
              letterSpacing="2"
            >
              ANTIGRAVITY
            </text>
          </g>
        )}

        {/* ======================================================== */}
        {/* ENVIRONMENT FOREGROUND ARCHITECTURE                    */}
        {/* ======================================================== */}
        {/* 1. DINER ARCHITECTURE */}
        {environment === "diner" && (
          <g id="dinerInterior">
            {/* Large Diner Window Frame */}
            <rect
              x="90"
              y="180"
              width="900"
              height="900"
              rx="20"
              fill="none"
              stroke="#1E293B"
              strokeWidth="16"
            />
            <line x1="540" y1="180" x2="540" y2="1080" stroke="#1E293B" strokeWidth="12" />
            <line x1="90" y1="630" x2="990" y2="630" stroke="#1E293B" strokeWidth="8" />

            {/* Window Glass Glare */}
            <polygon points="90,180 500,180 320,1080 90,1080" fill="url(#bgGlassGlare)" />

            {/* Animated Raindrops on Diner Window */}
            {weather === "raining" && (
              <g stroke="#60A5FA" strokeWidth="2.5" strokeLinecap="round" opacity="0.6">
                {raindrops.map((d) => {
                  const yPos = 190 + ((frame * d.speed + d.delay) % 870);
                  return (
                    <line
                      key={d.id}
                      x1={d.x}
                      y1={yPos}
                      x2={d.x + 4}
                      y2={yPos + d.length}
                    />
                  );
                })}
              </g>
            )}

            {/* Classic Red Leather Booth (Left Side) */}
            <path
              d="M 50,780 C 50,700 90,660 170,660 L 410,660 C 440,660 470,680 470,740 L 470,1300 L 50,1300 Z"
              fill="#831818"
              stroke="#450A0A"
              strokeWidth="8"
            />
            {[740, 820, 900, 980, 1060, 1140, 1220].map((y, i) => (
              <line
                key={i}
                x1="60"
                y1={y}
                x2="460"
                y2={y}
                stroke="#370707"
                strokeWidth="5"
                strokeDasharray="12,4"
              />
            ))}

            {/* Classic Red Leather Booth (Right Side) */}
            <path
              d="M 1030,780 C 1030,700 990,660 910,660 L 670,660 C 640,660 610,680 610,740 L 610,1300 L 1030,1300 Z"
              fill="#831818"
              stroke="#450A0A"
              strokeWidth="8"
            />
            {[740, 820, 900, 980, 1060, 1140, 1220].map((y, i) => (
              <line
                key={i}
                x1="620"
                y1={y}
                x2="1020"
                y2={y}
                stroke="#370707"
                strokeWidth="5"
                strokeDasharray="12,4"
              />
            ))}

            {/* Checkerboard Perspective Floor */}
            <polygon points="0,1360 1080,1360 1080,1920 0,1920" fill="#0F172A" />
            {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
              const isWhite = col % 2 === 0;
              const x1 = (col * 1080) / 8;
              const x2 = ((col + 1) * 1080) / 8;
              return (
                <polygon
                  key={`tile-${col}`}
                  points={`${x1},1360 ${x2},1360 ${x2 + 25},1620 ${x1 - 25},1620`}
                  fill={isWhite ? "#E2E8F0" : "#1E293B"}
                  opacity={isWhite ? 0.75 : 0.95}
                />
              );
            })}
            {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
              const isWhite = (col + 1) % 2 === 0;
              const x1 = (col * 1080) / 8 - 25;
              const x2 = ((col + 1) * 1080) / 8 + 25;
              return (
                <polygon
                  key={`tile2-${col}`}
                  points={`${x1},1620 ${x2},1620 ${x2 + 50},1920 ${x1 - 50},1920`}
                  fill={isWhite ? "#F8FAFC" : "#0F172A"}
                  opacity={isWhite ? 0.85 : 1.0}
                />
              );
            })}
          </g>
        )}

        {/* 2. INSIDE HOME ARCHITECTURE */}
        {environment === "inside_home" && (
          <g id="homeInterior">
            {/* Wooden Floor Planks */}
            <polygon points="0,1320 1080,1320 1080,1920 0,1920" fill="#2E1C14" />
            {[1380, 1450, 1530, 1620, 1720, 1830].map((y, i) => (
              <line key={i} x1="0" y1={y} x2="1080" y2={y} stroke="#1A0F0A" strokeWidth="4" />
            ))}

            {/* Contemporary Balcony Glass French Doors */}
            <rect x="120" y="200" width="840" height="920" fill="none" stroke="#334155" strokeWidth="14" />
            <line x1="540" y1="200" x2="540" y2="1120" stroke="#334155" strokeWidth="12" />

            {/* Indoor Bookshelf (Left Wall) */}
            <rect x="20" y="380" width="90" height="880" fill="#1C1917" stroke="#44403C" strokeWidth="4" />
            {[480, 600, 720, 840, 960, 1080].map((shelfY, i) => (
              <g key={i}>
                <line x1="20" y1={shelfY} x2="110" y2={shelfY} stroke="#78716C" strokeWidth="6" />
                {/* Book Spines */}
                <rect x="26" y={shelfY - 70} width="16" height="70" fill="#0284C7" />
                <rect x="44" y={shelfY - 80} width="20" height="80" fill="#DC2626" />
                <rect x="66" y={shelfY - 65} width="14" height="65" fill="#EAB308" />
                <rect x="82" y={shelfY - 75} width="18" height="75" fill="#16A34A" />
              </g>
            ))}

            {/* Cozy Hanging Plant on the Right */}
            <path d="M 980,180 L 980,320" stroke="#57534E" strokeWidth="3" />
            <polygon points="960,320 1000,320 990,360 970,360" fill="#78350F" />
            <ellipse cx="980" cy="330" rx="35" ry="20" fill="#15803D" opacity="0.9" />
            <ellipse cx="965" cy="345" rx="20" ry="30" fill="#16A34A" opacity="0.85" />
            <ellipse cx="995" cy="350" rx="22" ry="32" fill="#22C55E" opacity="0.85" />

            {/* Warm Living Room Ambient Glow */}
            <ellipse
              cx="540"
              cy="1260"
              rx={520 * lampPulse}
              ry={280 * lampPulse}
              fill="url(#bgLampGlow)"
            />
          </g>
        )}

        {/* 3. MODERN OFFICE ARCHITECTURE */}
        {environment === "modern_office" && (
          <g id="officeInterior">
            {/* Sleek Slate Office Carpet */}
            <polygon points="0,1320 1080,1320 1080,1920 0,1920" fill="#1E293B" />
            {[0, 1, 2, 3, 4, 5].map((idx) => (
              <line
                key={idx}
                x1={idx * 216}
                y1="1320"
                x2={idx * 216}
                y2="1920"
                stroke="#0F172A"
                strokeWidth="2"
              />
            ))}

            {/* Glass Conference Partition (Frosted Hexagonal Matrix) */}
            <rect x="80" y="200" width="920" height="920" fill="none" stroke="#475569" strokeWidth="12" />
            <line x1="540" y1="200" x2="540" y2="1120" stroke="#475569" strokeWidth="8" />

            {/* Server Rack Status Lights in Corner */}
            <rect x="30" y="440" width="60" height="780" rx="8" fill="#0B0F17" stroke="#1E293B" strokeWidth="3" />
            {[480, 530, 580, 630, 680, 730, 780, 830, 880, 930].map((ledY, i) => (
              <g key={i}>
                <circle
                  cx="50"
                  cy={ledY}
                  r="4"
                  fill="#10B981"
                  opacity={frame % (20 + (i % 5) * 10) < 15 ? 0.9 : 0.2}
                />
                <circle
                  cx="70"
                  cy={ledY}
                  r="4"
                  fill="#38BDF8"
                  opacity={frame % (15 + (i % 4) * 8) < 10 ? 0.9 : 0.2}
                />
              </g>
            ))}

            {/* Blue Ambient Tech Glow */}
            <ellipse
              cx="540"
              cy="1260"
              rx={540 * lampPulse}
              ry={280 * lampPulse}
              fill="url(#bgOfficeGlow)"
            />
          </g>
        )}

        {/* 4. OUTSIDE HOME / URBAN BALCONY */}
        {environment === "outside_home" && (
          <g id="outsideBalcony">
            {/* Balcony Concrete Deck */}
            <polygon points="0,1320 1080,1320 1080,1920 0,1920" fill="#334155" />
            {/* Glass Railing with Steel Balusters */}
            <rect x="60" y="1040" width="960" height="280" fill="rgba(255, 255, 255, 0.08)" stroke="#64748B" strokeWidth="8" />
            {[140, 260, 380, 500, 620, 740, 860, 980].map((postX, i) => (
              <line key={i} x1={postX} y1="1040" x2={postX} y2="1320" stroke="#94A3B8" strokeWidth="6" />
            ))}
            {/* Handrail Top Bar */}
            <rect x="40" y="1025" width="1000" height="22" rx="6" fill="#CBD5E1" stroke="#64748B" strokeWidth="3" />

            {/* Outdoor Weather Ambient Rain if raining */}
            {weather === "raining" && (
              <g stroke="#93C5FD" strokeWidth="3" strokeLinecap="round" opacity="0.75">
                {raindrops.map((d) => {
                  const yPos = 100 + ((frame * d.speed + d.delay) % 1700);
                  return (
                    <line
                      key={d.id}
                      x1={d.x + 30}
                      y1={yPos}
                      x2={d.x + 36}
                      y2={yPos + d.length * 1.2}
                    />
                  );
                })}
              </g>
            )}
          </g>
        )}
      </svg>
    </div>
  );
};
