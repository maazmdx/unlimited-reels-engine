import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import { SceneEnvironment } from "./DynamicBackgroundEngine";

export interface EnvironmentPropsProps {
  environment?: SceneEnvironment;
  showCoffeeMug?: boolean;
  showScreen?: boolean;
  screenContent?: "code" | "benchmark" | "terminal" | "none";
}

export const EnvironmentProps: React.FC<EnvironmentPropsProps> = ({
  environment = "diner",
  showCoffeeMug = true,
  showScreen = true,
  screenContent = "code",
}) => {
  const frame = useCurrentFrame();

  // Procedural animated rising steam particles for the coffee mug
  const steamParticles = useMemo(() => {
    return [0, 1, 2, 3, 4, 5].map((i) => ({
      id: i,
      offsetDelay: i * 22,
      baseX: 0,
      driftFactor: (i % 2 === 0 ? 1 : -1) * (1.2 + (i % 3) * 0.4),
    }));
  }, []);

  return (
    <div
      style={{
        position: "absolute",
        width: 1080,
        height: 1920,
        pointerEvents: "none",
        zIndex: 20,
      }}
    >
      <svg
        width="1080"
        height="1920"
        viewBox="0 0 1080 1920"
        style={{ position: "absolute", top: 0, left: 0 }}
      >
        <defs>
          {/* Wood Table Gradient */}
          <linearGradient id="propWoodTable" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3E2723" />
            <stop offset="35%" stopColor="#4E342E" />
            <stop offset="70%" stopColor="#2E1C14" />
            <stop offset="100%" stopColor="#1B0E09" />
          </linearGradient>

          {/* Minimalist Glass/Aluminum Desk Gradient */}
          <linearGradient id="propGlassDesk" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#334155" />
            <stop offset="25%" stopColor="#1E293B" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>

          {/* Glowing Terminal Cyan/Green Gradient */}
          <linearGradient id="propScreenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#0B132B" />
            <stop offset="100%" stopColor="#050811" />
          </linearGradient>

          {/* Coffee Mug Ceramic Gradient */}
          <linearGradient id="propMugGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="40%" stopColor="#0284C7" />
            <stop offset="100%" stopColor="#0369A1" />
          </linearGradient>
        </defs>

        {/* ======================================================== */}
        {/* 1. SEATING & CHAIRS (MIDGROUND BEHIND/BESIDE TABLE)     */}
        {/* ======================================================== */}
        {environment === "modern_office" && (
          <g id="officeChairs">
            {/* Left Ergonomic Mesh Chair */}
            <g transform="translate(140, 720)">
              {/* Headrest */}
              <rect x="70" y="0" width="100" height="45" rx="14" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              {/* Backrest Mesh Spine */}
              <rect x="110" y="45" width="20" height="180" fill="#1E293B" />
              {/* Curved Backrest */}
              <path d="M 50,55 Q 120,40 190,55 L 180,240 Q 120,255 60,240 Z" fill="#1E293B" stroke="#475569" strokeWidth="6" opacity="0.9" />
              {/* Armrests */}
              <rect x="35" y="170" width="30" height="90" rx="10" fill="#334155" />
              <rect x="175" y="170" width="30" height="90" rx="10" fill="#334155" />
            </g>

            {/* Right Ergonomic Mesh Chair */}
            <g transform="translate(700, 720)">
              <rect x="70" y="0" width="100" height="45" rx="14" fill="#0F172A" stroke="#334155" strokeWidth="4" />
              <rect x="110" y="45" width="20" height="180" fill="#1E293B" />
              <path d="M 50,55 Q 120,40 190,55 L 180,240 Q 120,255 60,240 Z" fill="#1E293B" stroke="#475569" strokeWidth="6" opacity="0.9" />
              <rect x="35" y="170" width="30" height="90" rx="10" fill="#334155" />
              <rect x="175" y="170" width="30" height="90" rx="10" fill="#334155" />
            </g>
          </g>
        )}

        {environment === "inside_home" && (
          <g id="homeSofa">
            {/* Cozy Modern Sofa Backrest Cushion */}
            <path
              d="M 120,920 Q 540,880 960,920 L 980,1260 L 100,1260 Z"
              fill="#292524"
              stroke="#44403C"
              strokeWidth="6"
            />
            {/* Cushion tufting seams */}
            <line x1="380" y1="910" x2="380" y2="1260" stroke="#1C1917" strokeWidth="4" />
            <line x1="700" y1="910" x2="700" y2="1260" stroke="#1C1917" strokeWidth="4" />
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. FOREGROUND TABLE / DESK                               */}
        {/* ======================================================== */}
        {/* Diner or Home Wooden Table */}
        {(environment === "diner" || environment === "inside_home") && (
          <g id="woodenTableGroup">
            {/* Table Surface */}
            <polygon
              points="150,1240 930,1240 1010,1470 70,1470"
              fill="url(#propWoodTable)"
              stroke="#5D4037"
              strokeWidth="6"
            />
            {/* Table Front Trim / Edge */}
            <polygon
              points="70,1470 1010,1470 995,1500 85,1500"
              fill="#795548"
              stroke="#8D6E63"
              strokeWidth="3"
            />
            {/* Heavy Center Steel Base Pedestal */}
            <polygon points="500,1500 580,1500 610,1860 470,1860" fill="#1C1917" stroke="#292524" strokeWidth="4" />
          </g>
        )}

        {/* Modern Office Slate & Steel Desk */}
        {environment === "modern_office" && (
          <g id="officeDeskGroup">
            {/* Desk Surface */}
            <polygon
              points="140,1240 940,1240 1020,1470 60,1470"
              fill="url(#propGlassDesk)"
              stroke="#475569"
              strokeWidth="6"
            />
            {/* Desk Chamfered Bevel Rim */}
            <polygon
              points="60,1470 1020,1470 1010,1498 70,1498"
              fill="#0F172A"
              stroke="#38BDF8"
              strokeWidth="2"
            />
            {/* Sleek Minimalist Matte Black Legs */}
            <rect x="120" y="1498" width="22" height="380" fill="#1E293B" />
            <rect x="938" y="1498" width="22" height="380" fill="#1E293B" />
          </g>
        )}

        {/* Outside Balcony Bistro Table */}
        {environment === "outside_home" && (
          <g id="balconyTableGroup">
            <polygon
              points="200,1260 880,1260 940,1460 140,1460"
              fill="#1E293B"
              stroke="#64748B"
              strokeWidth="5"
            />
            <polygon
              points="140,1460 940,1460 930,1485 150,1485"
              fill="#0F172A"
              stroke="#475569"
              strokeWidth="2"
            />
            {/* Bistro Cast Iron Tripod Leg */}
            <rect x="532" y="1485" width="16" height="380" fill="#0F172A" />
            <polygon points="460,1860 620,1860 540,1780" fill="#0F172A" />
          </g>
        )}

        {/* ======================================================== */}
        {/* 3. DYNAMIC SCREEN / LAPTOP DISPLAY                      */}
        {/* ======================================================== */}
        {showScreen && (
          <g id="tableScreen" transform="translate(370, 1140)">
            {/* Screen Stand */}
            <polygon points="150,160 190,160 205,210 135,210" fill="#334155" stroke="#475569" strokeWidth="2" />
            <rect x="110" y="210" width="120" height="12" rx="4" fill="#1E293B" stroke="#475569" strokeWidth="2" />

            {/* Laptop / Monitor Bezel */}
            <rect
              x="0"
              y="0"
              width="340"
              height="170"
              rx="10"
              fill="#0F172A"
              stroke="#38BDF8"
              strokeWidth="4"
              filter="drop-shadow(0 0 15px rgba(56, 189, 248, 0.4))"
            />

            {/* Inner Display Screen */}
            <rect x="10" y="10" width="320" height="150" rx="6" fill="url(#propScreenGrad)" />

            {/* Content: Terminal Code or Benchmark */}
            {screenContent === "code" && (
              <g>
                {/* Code Window Header */}
                <rect x="10" y="10" width="320" height="20" rx="6" fill="#1E293B" />
                <circle cx="24" cy="20" r="4" fill="#EF4444" />
                <circle cx="36" cy="20" r="4" fill="#F59E0B" />
                <circle cx="48" cy="20" r="4" fill="#10B981" />
                <text x="170" y="24" fill="#94A3B8" fontSize="9" fontFamily="monospace" textAnchor="middle">
                  antigravity_pipeline.py
                </text>

                {/* Animated Code Lines */}
                <text x="20" y="48" fill="#38BDF8" fontSize="11" fontFamily="monospace">
                  def execute_reel_agent():
                </text>
                <text x="32" y="66" fill="#A855F7" fontSize="10" fontFamily="monospace">
                  {"rag_topic = scrape_trending()"}
                </text>
                <text x="32" y="84" fill="#34D399" fontSize="10" fontFamily="monospace">
                  {"model = 'gemini-2.5-flash'"}
                </text>
                <text x="32" y="102" fill="#F472B6" fontSize="10" fontFamily="monospace">
                  {"cost = '$0.00' # 100% Free"}
                </text>
                <text x="32" y="120" fill="#FBBF24" fontSize="10" fontFamily="monospace">
                  {"auditor.verify_quality()"}
                </text>
                {/* Blinking Terminal Cursor */}
                <rect
                  x="200"
                  y="110"
                  width="7"
                  height="12"
                  fill="#38BDF8"
                  opacity={frame % 30 < 15 ? 1.0 : 0.0}
                />
              </g>
            )}

            {screenContent === "benchmark" && (
              <g>
                <rect x="10" y="10" width="320" height="20" rx="6" fill="#1E293B" />
                <text x="170" y="24" fill="#FDE047" fontSize="9" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                  SPEED & COST BENCHMARK
                </text>
                {/* Bar 1: Human Dev */}
                <text x="20" y="52" fill="#EF4444" fontSize="9" fontFamily="monospace">HUMAN DEV: 4.5 HRS ($250)</text>
                <rect x="20" y="58" width="280" height="14" rx="4" fill="#450A0A" />
                <rect x="20" y="58" width="270" height="14" rx="4" fill="#DC2626" />

                {/* Bar 2: AI Multi-Agent */}
                <text x="20" y="96" fill="#10B981" fontSize="9" fontFamily="monospace">AI PIPELINE: 2.4 SEC ($0.00)</text>
                <rect x="20" y="102" width="280" height="14" rx="4" fill="#064E3B" />
                <rect x="20" y="102" width="26" height="14" rx="4" fill="#10B981" />

                <text x="170" y="142" fill="#38BDF8" fontSize="10" fontFamily="monospace" fontWeight="bold" textAnchor="middle">
                  AI IS 6750x FASTER
                </text>
              </g>
            )}
          </g>
        )}

        {/* ======================================================== */}
        {/* 4. CERAMIC STEAMING COFFEE MUG                           */}
        {/* ======================================================== */}
        {showCoffeeMug && (
          <g id="steamingCoffeeMug" transform="translate(230, 1260)">
            {/* Procedural Animated Rising Steam */}
            <g opacity="0.6">
              {steamParticles.map((p) => {
                const progress = ((frame + p.offsetDelay) % 75) / 75; // 0.0 to 1.0
                const steamY = -progress * 70;
                const steamX = Math.sin((frame + p.offsetDelay) / 10) * (8 * p.driftFactor);
                const steamOpacity = (1.0 - progress) * (progress > 0.15 ? 0.75 : progress * 5);
                const steamRadius = 7 + progress * 14;

                return (
                  <ellipse
                    key={p.id}
                    cx={35 + steamX}
                    cy={steamY}
                    rx={steamRadius}
                    ry={steamRadius * 0.7}
                    fill="#E2E8F0"
                    opacity={steamOpacity}
                    filter="blur(5px)"
                  />
                );
              })}
            </g>

            {/* Mug Shadow */}
            <ellipse cx="35" cy="52" rx="34" ry="10" fill="rgba(0,0,0,0.4)" />

            {/* Mug Body */}
            <rect
              x="10"
              y="0"
              width="50"
              height="50"
              rx="8"
              fill="url(#propMugGrad)"
              stroke="#0284C7"
              strokeWidth="2.5"
            />
            {/* Mug Handle */}
            <path
              d="M 60,10 C 76,10 76,40 60,40"
              fill="none"
              stroke="#0284C7"
              strokeWidth="6"
              strokeLinecap="round"
            />
            {/* Coffee Liquid Rim */}
            <ellipse cx="35" cy="6" rx="22" ry="7" fill="#3E2723" stroke="#5D4037" strokeWidth="2" />
            {/* AI Chip Logo on Mug */}
            <rect x="27" y="18" width="16" height="16" rx="3" fill="#0C4A6E" />
            <text x="35" y="30" fill="#38BDF8" fontSize="10" fontFamily="monospace" fontWeight="bold" textAnchor="middle">
              AI
            </text>
          </g>
        )}
      </svg>
    </div>
  );
};
