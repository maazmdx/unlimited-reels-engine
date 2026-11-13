import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";

interface DinerBackgroundProps {
  lampIntensity?: number;
}

export const DinerBackground: React.FC<DinerBackgroundProps> = ({
  lampIntensity = 1.0,
}) => {
  const frame = useCurrentFrame();

  // Procedural animated raindrops on the window
  const raindrops = useMemo(() => {
    const drops = [];
    for (let i = 0; i < 45; i++) {
      const x = 120 + ((i * 47) % 840);
      const speed = 14 + (i % 9) * 2.5;
      const length = 25 + (i % 7) * 6;
      const delay = (i * 31) % 600;
      drops.push({ id: i, x, speed, length, delay });
    }
    return drops;
  }, []);

  // Ambient lamp pulse
  const lampPulse = 0.96 + Math.sin(frame / 12) * 0.04 * lampIntensity;

  return (
    <div
      style={{
        position: "absolute",
        width: 1080,
        height: 1920,
        overflow: "hidden",
        backgroundColor: "#07090E",
      }}
    >
      {/* ======================================================== */}
      {/* 1. NIGHT SKY & RAINY WINDOW BACKGROUND                  */}
      {/* ======================================================== */}
      <svg
        width="1080"
        height="1920"
        viewBox="0 0 1080 1920"
        style={{ position: "absolute", top: 0, left: 0 }}
      >
        <defs>
          {/* Deep midnight ambient gradient */}
          <linearGradient id="nightSky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#04060A" />
            <stop offset="60%" stopColor="#09101E" />
            <stop offset="100%" stopColor="#0D1627" />
          </linearGradient>

          {/* Window Glass Glare */}
          <linearGradient id="glassGlare" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(255, 255, 255, 0.08)" />
            <stop offset="40%" stopColor="rgba(255, 255, 255, 0.02)" />
            <stop offset="100%" stopColor="rgba(255, 255, 255, 0.0)" />
          </linearGradient>

          {/* Table Lamp Warm Glow */}
          <radialGradient id="lampGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 185, 75, 0.45)" />
            <stop offset="35%" stopColor="rgba(255, 150, 45, 0.22)" />
            <stop offset="70%" stopColor="rgba(255, 120, 20, 0.08)" />
            <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
          </radialGradient>

          {/* Red Leather Texture Gradient */}
          <linearGradient id="boothLeather" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4A0808" />
            <stop offset="15%" stopColor="#7B1113" />
            <stop offset="45%" stopColor="#9E181B" />
            <stop offset="75%" stopColor="#7B1113" />
            <stop offset="100%" stopColor="#3E0606" />
          </linearGradient>

          {/* Wood Table Gradient */}
          <linearGradient id="woodTable" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2A1B14" />
            <stop offset="30%" stopColor="#3D271D" />
            <stop offset="70%" stopColor="#211510" />
            <stop offset="100%" stopColor="#120B08" />
          </linearGradient>

          {/* Neon Blue Blur Filter */}
          <filter id="neonBlur" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="18" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Interior Wall Backdrop */}
        <rect width="1080" height="1920" fill="url(#nightSky)" />

        {/* ======================================================== */}
        {/* 2. LARGE DINER WINDOW WITH RAIN & DISTANT NEON SIGNS    */}
        {/* ======================================================== */}
        {/* Window Frame / Recess */}
        <rect
          x="100"
          y="180"
          width="880"
          height="880"
          rx="18"
          fill="#060A12"
          stroke="#1F2937"
          strokeWidth="14"
        />

        {/* Distant Out-Of-Focus Neon Signs Outside Window */}
        <g opacity="0.75" filter="url(#neonBlur)">
          {/* Neon Pink/Magenta Sign (GEMINI 24/7) */}
          <rect
            x="220"
            y="260"
            width="220"
            height="90"
            rx="12"
            fill="none"
            stroke="#FF2A85"
            strokeWidth="5"
          />
          <text
            x="330"
            y="315"
            fill="#FF4DA6"
            fontSize="32"
            fontFamily="Arial, sans-serif"
            fontWeight="bold"
            textAnchor="middle"
            letterSpacing="4"
          >
            GEMINI
          </text>

          {/* Neon Cyan Sign (ANTIGRAVITY) */}
          <rect
            x="600"
            y="360"
            width="280"
            height="85"
            rx="10"
            fill="none"
            stroke="#00E5FF"
            strokeWidth="5"
          />
          <text
            x="740"
            y="415"
            fill="#33FFFF"
            fontSize="28"
            fontFamily="Arial, sans-serif"
            fontWeight="bold"
            textAnchor="middle"
            letterSpacing="3"
          >
            ANTIGRAVITY
          </text>
        </g>

        {/* Rain Streaks on Glass */}
        <g stroke="rgba(200, 225, 255, 0.35)" strokeWidth="2.2" strokeLinecap="round">
          {raindrops.map((drop) => {
            const currentY = 190 + ((frame * drop.speed + drop.delay) % 840);
            return (
              <line
                key={drop.id}
                x1={drop.x}
                y1={currentY}
                x2={drop.x - 3}
                y2={currentY + drop.length}
              />
            );
          })}
        </g>

        {/* Glass Reflection Glare Overlay */}
        <rect
          x="100"
          y="180"
          width="880"
          height="880"
          rx="18"
          fill="url(#glassGlare)"
        />

        {/* Window Sill / Mullion Bar */}
        <line
          x1="540"
          y1="180"
          x2="540"
          y2="1060"
          stroke="#182232"
          strokeWidth="10"
        />

        {/* ======================================================== */}
        {/* 3. RED QUILTED DINER BOOTH (LEFT SIDE)                  */}
        {/* ======================================================== */}
        {/* Backrest Left */}
        <path
          d="M 60,760 C 60,680 100,640 180,640 L 420,640 C 450,640 480,660 480,720 L 480,1280 L 60,1280 Z"
          fill="url(#boothLeather)"
          stroke="#2A0505"
          strokeWidth="8"
        />
        {/* Quilted Ribs / Seams */}
        {[720, 800, 880, 960, 1040, 1120, 1200].map((y, i) => (
          <line
            key={i}
            x1="70"
            y1={y}
            x2="470"
            y2={y}
            stroke="#2F0505"
            strokeWidth="5"
            strokeDasharray="14,4"
          />
        ))}

        {/* ======================================================== */}
        {/* 4. BLACK & WHITE CHECKERBOARD FLOOR (PERSPECTIVE)       */}
        {/* ======================================================== */}
        <g id="checkerboardFloor">
          {/* Base Floor Plane */}
          <polygon
            points="0,1340 1080,1340 1080,1920 0,1920"
            fill="#111622"
          />

          {/* Perspective Checkerboard Tiles */}
          {/* Row 1 (farthest) */}
          {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
            const isWhite = col % 2 === 0;
            const x1 = (col * 1080) / 8;
            const x2 = ((col + 1) * 1080) / 8;
            return (
              <polygon
                key={`r1-${col}`}
                points={`${x1},1340 ${x2},1340 ${x2 + 10},1460 ${x1 - 10},1460`}
                fill={isWhite ? "#DCE1EB" : "#1A202C"}
                opacity={isWhite ? 0.75 : 0.95}
              />
            );
          })}

          {/* Row 2 */}
          {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
            const isWhite = (col + 1) % 2 === 0;
            const x1 = (col * 1080) / 8 - 10;
            const x2 = ((col + 1) * 1080) / 8 + 10;
            return (
              <polygon
                key={`r2-${col}`}
                points={`${x1},1460 ${x2},1460 ${x2 + 25},1630 ${x1 - 25},1630`}
                fill={isWhite ? "#ECEFF5" : "#141A24"}
                opacity={isWhite ? 0.8 : 0.98}
              />
            );
          })}

          {/* Row 3 (foreground) */}
          {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
            const isWhite = col % 2 === 0;
            const x1 = (col * 1080) / 8 - 25;
            const x2 = ((col + 1) * 1080) / 8 + 25;
            return (
              <polygon
                key={`r3-${col}`}
                points={`${x1},1630 ${x2},1630 ${x2 + 45},1920 ${x1 - 45},1920`}
                fill={isWhite ? "#F8FAFC" : "#0D1117"}
                opacity={isWhite ? 0.85 : 1.0}
              />
            );
          })}
        </g>

        {/* ======================================================== */}
        {/* 5. DINER WOOD TABLE IN FOREGROUND                       */}
        {/* ======================================================== */}
        {/* Table Top Surface */}
        <polygon
          points="180,1260 900,1260 970,1460 110,1460"
          fill="url(#woodTable)"
          stroke="#523528"
          strokeWidth="6"
        />

        {/* Polished Table Edge Trim */}
        <polygon
          points="110,1460 970,1460 960,1490 120,1490"
          fill="#784E3D"
          stroke="#94634F"
          strokeWidth="3"
        />

        {/* Ambient Warm Glow from Table Lamp */}
        <ellipse
          cx="540"
          cy="1260"
          rx={420 * lampPulse}
          ry={240 * lampPulse}
          fill="url(#lampGlow)"
        />

        {/* ======================================================== */}
        {/* 6. CYLINDRICAL TABLE LAMP (WARM AMBER VIBE)              */}
        {/* ======================================================== */}
        {/* Lamp Base Plate */}
        <ellipse cx="540" cy="1310" rx="42" ry="16" fill="#1C1F26" stroke="#4B5563" strokeWidth="3" />
        {/* Lamp Stem */}
        <rect x="534" y="1230" width="12" height="80" fill="#2D333F" rx="3" />
        {/* Lamp Shade Cylindrical Body */}
        <rect
          x="510"
          y="1140"
          width="60"
          height="95"
          rx="12"
          fill="#FFAA33"
          stroke="#FFD580"
          strokeWidth="4"
          filter="drop-shadow(0 0 25px rgba(255, 170, 50, 0.8))"
        />
        {/* Lamp Shade Inner Bulb Core */}
        <rect x="522" y="1152" width="36" height="70" rx="8" fill="#FFF2CC" />
      </svg>
    </div>
  );
};
