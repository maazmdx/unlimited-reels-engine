import React from "react";
import { useCurrentFrame } from "remotion";

export const TechCafeScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Gentle light flicker / pulse
  const lampGlow = 0.95 + Math.sin(frame / 10) * 0.05;

  return (
    <div
      style={{
        position: "absolute",
        width: 1080,
        height: 1920,
        overflow: "hidden",
        backgroundColor: "#090D16",
      }}
    >
      <svg width="1080" height="1920" viewBox="0 0 1080 1920">
        <defs>
          {/* Sunset Twilight Window Gradient */}
          <linearGradient id="twilightSky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2E1B4E" />
            <stop offset="45%" stopColor="#6D28D9" />
            <stop offset="75%" stopColor="#D97706" />
            <stop offset="100%" stopColor="#F59E0B" />
          </linearGradient>

          {/* Wooden Tabletop Gradient */}
          <linearGradient id="cafeTable" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3F271D" />
            <stop offset="40%" stopColor="#543628" />
            <stop offset="100%" stopColor="#24160F" />
          </linearGradient>

          {/* Table Lamp Warm Ambient Radial Light */}
          <radialGradient id="deskLampLight" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255, 200, 100, 0.45)" />
            <stop offset="40%" stopColor="rgba(255, 170, 60, 0.20)" />
            <stop offset="80%" stopColor="rgba(255, 140, 30, 0.05)" />
            <stop offset="100%" stopColor="rgba(0, 0, 0, 0)" />
          </radialGradient>
        </defs>

        {/* ======================================================== */}
        {/* 1. LARGE CAFE WINDOW & DISTANT SKYLINE                   */}
        {/* ======================================================== */}
        {/* Window Pane */}
        <rect x="80" y="160" width="920" height="920" rx="20" fill="url(#twilightSky)" stroke="#1E293B" strokeWidth="12" />

        {/* Distant City Silhouette / Buildings */}
        <polygon points="120,860 180,720 220,720 220,860" fill="#1C1032" opacity="0.85" />
        <polygon points="260,860 310,680 370,680 370,860" fill="#150B27" opacity="0.9" />
        <polygon points="420,860 480,750 540,750 540,860" fill="#1C1032" opacity="0.8" />
        <polygon points="600,860 670,640 730,640 730,860" fill="#120921" opacity="0.95" />
        <polygon points="780,860 840,710 900,710 900,860" fill="#1C1032" opacity="0.85" />

        {/* City Window Bokeh Light Dots */}
        {[
          { cx: 160, cy: 750, r: 4 },
          { cx: 200, cy: 790, r: 3 },
          { cx: 330, cy: 710, r: 5 },
          { cx: 350, cy: 760, r: 4 },
          { cx: 650, cy: 680, r: 5 },
          { cx: 700, cy: 720, r: 4 },
          { cx: 820, cy: 740, r: 3 },
          { cx: 870, cy: 780, r: 4 },
        ].map((pt, i) => (
          <circle key={i} cx={pt.cx} cy={pt.cy} r={pt.r} fill="#FDE047" opacity="0.75" />
        ))}

        {/* Window Mullion Grid Bar */}
        <line x1="540" y1="160" x2="540" y2="1080" stroke="#1E293B" strokeWidth="8" />

        {/* ======================================================== */}
        {/* 2. CAFE BOOTH BENCH SEATING                              */}
        {/* ======================================================== */}
        {/* Green/Teal Padded Backrest */}
        <path
          d="M 60,780 C 60,680 120,650 200,650 L 880,650 C 960,650 1020,680 1020,780 L 1020,1320 L 60,1320 Z"
          fill="#0F241C"
          stroke="#06120E"
          strokeWidth="6"
        />
        {/* Quilted Seams */}
        {[720, 800, 880, 960, 1040, 1120, 1200].map((y, i) => (
          <line key={i} x1="70" y1={y} x2="1010" y2={y} stroke="#071711" strokeWidth="4" />
        ))}

        {/* ======================================================== */}
        {/* 3. CHECKERBOARD FLOOR (PERSPECTIVE)                      */}
        {/* ======================================================== */}
        <polygon points="0,1380 1080,1380 1080,1920 0,1920" fill="#0F172A" />
        {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
          const isWhite = col % 2 === 0;
          const x1 = (col * 1080) / 8;
          const x2 = ((col + 1) * 1080) / 8;
          return (
            <polygon
              key={`f1-${col}`}
              points={`${x1},1380 ${x2},1380 ${x2 + 20},1580 ${x1 - 20},1580`}
              fill={isWhite ? "#E2E8F0" : "#1E293B"}
              opacity={isWhite ? 0.75 : 0.95}
            />
          );
        })}
        {[0, 1, 2, 3, 4, 5, 6, 7].map((col) => {
          const isWhite = (col + 1) % 2 === 0;
          const x1 = (col * 1080) / 8 - 20;
          const x2 = ((col + 1) * 1080) / 8 + 20;
          return (
            <polygon
              key={`f2-${col}`}
              points={`${x1},1580 ${x2},1580 ${x2 + 50},1920 ${x1 - 50},1920`}
              fill={isWhite ? "#F8FAFC" : "#0F172A"}
              opacity={isWhite ? 0.85 : 1.0}
            />
          );
        })}

        {/* ======================================================== */}
        {/* 4. LARGE WOODEN TABLETOP                                 */}
        {/* ======================================================== */}
        <polygon points="100,1260 980,1260 1050,1480 30,1480" fill="url(#cafeTable)" stroke="#684232" strokeWidth="6" />
        <polygon points="30,1480 1050,1480 1040,1515 40,1515" fill="#845540" stroke="#9C6B55" strokeWidth="2" />

        {/* Table Lamp Warm Ambient Glow Halo */}
        <ellipse cx="540" cy="1260" rx={450 * lampGlow} ry={250 * lampGlow} fill="url(#deskLampLight)" />

        {/* ======================================================== */}
        {/* 5. TABLE PROPS (LAPTOP, COFFEE CUP, SMARTPHONE, BOOK)    */}
        {/* ======================================================== */}
        {/* Low-Poly Laptop (Left Center) */}
        <g id="tableLaptop">
          {/* Base Keyboard */}
          <polygon points="260,1320 400,1320 420,1370 240,1370" fill="#334155" stroke="#1E293B" strokeWidth="2" />
          {/* Screen (Angled Up) */}
          <polygon points="260,1320 400,1320 395,1230 265,1230" fill="#0F172A" stroke="#475569" strokeWidth="2" />
          <polygon points="268,1315 392,1315 388,1238 272,1238" fill="#38BDF8" opacity="0.85" />
          {/* Sticky Note on Laptop Lid */}
          <polygon points="360,1235 390,1235 390,1265 360,1265" fill="#FDE047" />
          <text x="365" y="1255" fontSize="8" fill="#854D0E" fontFamily="sans-serif" fontWeight="bold">agy</text>
        </g>

        {/* Low-Poly White Coffee Cup on Saucer */}
        <g id="coffeeCup">
          <ellipse cx="480" cy="1360" rx="26" ry="10" fill="#F1F5F9" stroke="#CBD5E1" strokeWidth="2" />
          <polygon points="462,1340 498,1340 494,1360 466,1360" fill="#FFFFFF" stroke="#E2E8F0" strokeWidth="2" />
          <ellipse cx="480" cy="1340" rx="18" ry="6" fill="#78350F" />
        </g>

        {/* Low-Poly Smartphone (Flat on table) */}
        <polygon points="560,1350 610,1340 625,1375 575,1385" fill="#18181B" stroke="#3F3F46" strokeWidth="2" />
        <polygon points="564,1352 606,1344 619,1372 577,1380" fill="#0284C7" opacity="0.6" />

        {/* 3D Book with Red Bookmark */}
        <polygon points="680,1340 780,1330 800,1370 700,1380" fill="#3B82F6" stroke="#1D4ED8" strokeWidth="2" />
        <polygon points="700,1380 800,1370 798,1382 698,1392" fill="#F8FAFC" stroke="#E2E8F0" strokeWidth="1.5" />
        {/* Red Bookmark Ribbon */}
        <polygon points="740,1372 748,1371 750,1398 742,1399" fill="#EF4444" />

        {/* Low-Poly Desk Lamp */}
        <ellipse cx="540" cy="1310" rx="36" ry="14" fill="#1F2937" stroke="#374151" strokeWidth="3" />
        <rect x="535" y="1230" width="10" height="80" fill="#374151" rx="2" />
        <polygon points="510,1230 570,1230 560,1160 520,1160" fill="#F59E0B" filter="drop-shadow(0 0 20px #F59E0B)" />
      </svg>
    </div>
  );
};
