import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

export type CharacterType =
  | "human_male"
  | "human_female"
  | "antigravity_bot"
  | "gemini_bot"
  | "claude_bot"
  | "grok_bot"
  | "codex_bot";

export type CharacterEmotion = "normal" | "smug" | "angry" | "shocked" | "happy" | "sad";

export interface CharacterConfig {
  id: string;
  type: CharacterType;
  name: string;
  emotion?: CharacterEmotion;
  isSpeaking: boolean;
  scale?: number;
}

export interface DynamicCharacterRosterProps {
  characters: CharacterConfig[];
}

export const DynamicCharacterRoster: React.FC<DynamicCharacterRosterProps> = ({
  characters = [],
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const count = characters.length;

  // Compute horizontal X slots dynamically based on count
  const getSlotX = (index: number) => {
    if (count === 1) return 540;
    if (count === 2) return index === 0 ? 270 : 810;
    if (count === 3) {
      if (index === 0) return 210;
      if (index === 1) return 540;
      return 870;
    }
    // 4 characters
    return 160 + index * 250;
  };

  return (
    <div
      style={{
        position: "absolute",
        width: 1080,
        height: 1920,
        pointerEvents: "none",
        zIndex: 10,
      }}
    >
      {characters.map((char, index) => {
        const slotX = getSlotX(index);
        const isSpeaking = char.isSpeaking;
        const emotion = char.emotion || "normal";
        const charScale = char.scale || (count >= 3 ? 0.88 : 1.0);

        // Natural idle sway / breathing
        const swayY = Math.sin((frame + index * 30) / 18) * 5;
        const headTilt = isSpeaking
          ? Math.sin(frame / 6) * 3
          : Math.sin((frame + index * 20) / 25) * 1.5;

        // Blinking
        const isBlinking = (frame + index * 40) % 110 > 104;

        // Active speaker pop
        const speakerPop = isSpeaking
          ? spring({
              frame: frame % 30,
              fps,
              config: { damping: 14, stiffness: 180 },
            })
          : 0;

        return (
          <div
            key={char.id || index}
            style={{
              position: "absolute",
              left: slotX,
              top: 700 + swayY - (isSpeaking ? 6 : 0),
              transform: `translate(-50%, 0) scale(${charScale * (1 + speakerPop * 0.04)}) rotate(${headTilt}deg)`,
              transformOrigin: "center bottom",
              width: 380,
              height: 640,
              transition: "transform 0.15s ease-out",
            }}
          >
            {/* Speaker Name Tag Indicator */}
            <div
              style={{
                position: "absolute",
                top: 30,
                left: "50%",
                transform: `translateX(-50%) scale(${isSpeaking ? 1.08 : 0.95})`,
                backgroundColor: isSpeaking ? "#0284C7" : "rgba(15, 23, 42, 0.85)",
                border: isSpeaking ? "2px solid #38BDF8" : "1px solid #334155",
                borderRadius: 20,
                padding: "5px 16px",
                color: "#FFFFFF",
                fontSize: 16,
                fontWeight: 700,
                fontFamily: "system-ui, sans-serif",
                letterSpacing: "0.5px",
                boxShadow: isSpeaking ? "0 0 16px rgba(56, 189, 248, 0.6)" : "none",
                whiteSpace: "nowrap",
                zIndex: 5,
              }}
            >
              {char.name.toUpperCase()} {isSpeaking && "🎙️"}
            </div>

            {/* Character Visual SVG */}
            <svg width="380" height="640" viewBox="0 0 380 640">
              <defs>
                {/* Antigravity Bot Sphere Gradient */}
                <radialGradient id={`botGrad-${char.id}`} cx="35%" cy="30%" r="70%">
                  <stop offset="0%" stopColor="#FFA654" />
                  <stop offset="40%" stopColor="#E66A23" />
                  <stop offset="80%" stopColor="#B8420B" />
                  <stop offset="100%" stopColor="#662103" />
                </radialGradient>

                {/* Gemini Bot Deep Cosmic Blue Gradient */}
                <radialGradient id={`geminiGrad-${char.id}`} cx="40%" cy="30%" r="75%">
                  <stop offset="0%" stopColor="#818CF8" />
                  <stop offset="45%" stopColor="#4F46E5" />
                  <stop offset="85%" stopColor="#312E81" />
                  <stop offset="100%" stopColor="#1E1B4B" />
                </radialGradient>

                {/* Claude Bot Anthropic Terracotta Gradient */}
                <radialGradient id={`claudeGrad-${char.id}`} cx="35%" cy="30%" r="70%">
                  <stop offset="0%" stopColor="#FDBA74" />
                  <stop offset="40%" stopColor="#EA580C" />
                  <stop offset="85%" stopColor="#9A3412" />
                  <stop offset="100%" stopColor="#431407" />
                </radialGradient>

                {/* Grok Bot Cyberpunk Neon Green Gradient */}
                <radialGradient id={`grokGrad-${char.id}`} cx="35%" cy="30%" r="70%">
                  <stop offset="0%" stopColor="#4ADE80" />
                  <stop offset="45%" stopColor="#16A34A" />
                  <stop offset="85%" stopColor="#14532D" />
                  <stop offset="100%" stopColor="#052E16" />
                </radialGradient>

                {/* Codex Bot Emerald Matrix Gradient */}
                <radialGradient id={`codexGrad-${char.id}`} cx="35%" cy="30%" r="70%">
                  <stop offset="0%" stopColor="#2DD4BF" />
                  <stop offset="45%" stopColor="#0D9488" />
                  <stop offset="85%" stopColor="#115E59" />
                  <stop offset="100%" stopColor="#042F2E" />
                </radialGradient>

                {/* Human Skin Gradient */}
                <linearGradient id={`skinGrad-${char.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FBD5B5" />
                  <stop offset="100%" stopColor="#E5AC88" />
                </linearGradient>

                {/* Human Male Hoodie Gradient */}
                <linearGradient id={`hoodieMale-${char.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1E3A5F" />
                  <stop offset="100%" stopColor="#0B1728" />
                </linearGradient>

                {/* Human Female Blazer Gradient */}
                <linearGradient id={`blazerFemale-${char.id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#7C2D12" />
                  <stop offset="100%" stopColor="#431407" />
                </linearGradient>
              </defs>

              {/* ======================================================== */}
              {/* 1. HUMAN MALE (Junior Dev / Overconfident Human)        */}
              {/* ======================================================== */}
              {char.type === "human_male" && (
                <g id="humanMaleGroup">
                  {/* Body & Hoodie Torso */}
                  <path
                    d="M 100,560 C 100,420 140,360 190,360 C 240,360 280,420 280,560 Z"
                    fill={`url(#hoodieMale-${char.id})`}
                    stroke="#1E293B"
                    strokeWidth="4"
                  />
                  {/* Hoodie Drawstrings */}
                  <line x1="175" y1="380" x2="175" y2="460" stroke="#E2E8F0" strokeWidth="3" strokeLinecap="round" />
                  <line x1="205" y1="380" x2="205" y2="450" stroke="#E2E8F0" strokeWidth="3" strokeLinecap="round" />

                  {/* Neck */}
                  <rect x="170" y="320" width="40" height="50" rx="8" fill={`url(#skinGrad-${char.id})`} />

                  {/* Head Oval */}
                  <ellipse cx="190" cy="250" rx="72" ry="86" fill={`url(#skinGrad-${char.id})`} />

                  {/* Messy Hair */}
                  <path
                    d="M 115,230 C 110,140 180,120 230,130 C 265,140 275,170 270,220 C 260,195 240,185 220,185 C 190,185 170,205 150,195 C 135,195 125,210 115,230 Z"
                    fill="#1F1610"
                  />

                  {/* Eyebrows (Emotion Dependent) */}
                  {emotion === "angry" ? (
                    <g stroke="#1F1610" strokeWidth="5" strokeLinecap="round">
                      <line x1="140" y1="210" x2="175" y2="225" />
                      <line x1="240" y1="210" x2="205" y2="225" />
                    </g>
                  ) : emotion === "smug" ? (
                    <g stroke="#1F1610" strokeWidth="4" strokeLinecap="round">
                      <line x1="145" y1="215" x2="175" y2="218" />
                      <line x1="205" y1="215" x2="238" y2="205" />
                    </g>
                  ) : (
                    <g stroke="#1F1610" strokeWidth="4" strokeLinecap="round">
                      <line x1="145" y1="215" x2="175" y2="215" />
                      <line x1="205" y1="215" x2="235" y2="215" />
                    </g>
                  )}

                  {/* Eyes */}
                  {isBlinking ? (
                    <g stroke="#1F1610" strokeWidth="3">
                      <line x1="150" y1="235" x2="170" y2="235" />
                      <line x1="210" y1="235" x2="230" y2="235" />
                    </g>
                  ) : (
                    <g>
                      <ellipse cx="160" cy="235" rx="9" ry={emotion === "shocked" ? "12" : "8"} fill="#1F1610" />
                      <circle cx="162" cy="232" r="3" fill="#FFFFFF" />
                      <ellipse cx="220" cy="235" rx="9" ry={emotion === "shocked" ? "12" : "8"} fill="#1F1610" />
                      <circle cx="222" cy="232" r="3" fill="#FFFFFF" />
                    </g>
                  )}

                  {/* Rage / Sweat Drop (if angry or shocked) */}
                  {(emotion === "angry" || emotion === "shocked") && (
                    <path
                      d="M 245,190 C 240,205 255,215 255,205 Z"
                      fill="#38BDF8"
                      stroke="#0284C7"
                      strokeWidth="2"
                    />
                  )}

                  {/* Mouth (Speaking sync) */}
                  {isSpeaking ? (
                    <ellipse
                      cx="190"
                      cy="285"
                      rx="16"
                      ry={interpolate(Math.sin(frame * 0.9), [-1, 1], [4, 16])}
                      fill="#7F1D1D"
                      stroke="#1F1610"
                      strokeWidth="3"
                    />
                  ) : emotion === "smug" ? (
                    <path d="M 175,285 Q 195,295 210,280" fill="none" stroke="#1F1610" strokeWidth="4" strokeLinecap="round" />
                  ) : emotion === "angry" ? (
                    <path d="M 175,290 Q 190,280 205,290" fill="none" stroke="#1F1610" strokeWidth="4" strokeLinecap="round" />
                  ) : (
                    <line x1="178" y1="285" x2="202" y2="285" stroke="#1F1610" strokeWidth="3" strokeLinecap="round" />
                  )}
                </g>
              )}

              {/* ======================================================== */}
              {/* 2. HUMAN FEMALE (Senior Tech Lead / Skeptical Engineer) */}
              {/* ======================================================== */}
              {char.type === "human_female" && (
                <g id="humanFemaleGroup">
                  {/* Blazer Torso */}
                  <path
                    d="M 100,560 C 100,420 140,360 190,360 C 240,360 280,420 280,560 Z"
                    fill={`url(#blazerFemale-${char.id})`}
                    stroke="#292524"
                    strokeWidth="4"
                  />
                  {/* Inner White Shirt Collar */}
                  <polygon points="175,360 190,400 205,360 190,340" fill="#FFFFFF" />

                  {/* Neck */}
                  <rect x="174" y="315" width="32" height="50" rx="6" fill={`url(#skinGrad-${char.id})`} />

                  {/* Head Oval */}
                  <ellipse cx="190" cy="245" rx="68" ry="80" fill={`url(#skinGrad-${char.id})`} />

                  {/* Chic Bob Hair */}
                  <path
                    d="M 112,250 C 110,130 180,115 235,125 C 275,135 272,210 268,260 C 255,270 245,210 240,190 C 210,170 170,175 140,195 C 130,230 120,270 112,250 Z"
                    fill="#31150A"
                  />

                  {/* Modern Sleek Glasses */}
                  <rect x="140" y="222" width="42" height="26" rx="6" fill="none" stroke="#E2E8F0" strokeWidth="3" />
                  <rect x="198" y="222" width="42" height="26" rx="6" fill="none" stroke="#E2E8F0" strokeWidth="3" />
                  <line x1="182" y1="234" x2="198" y2="234" stroke="#E2E8F0" strokeWidth="3" />

                  {/* Eyes behind glasses */}
                  {isBlinking ? (
                    <line x1="150" y1="235" x2="172" y2="235" stroke="#1F1610" strokeWidth="3" />
                  ) : (
                    <g>
                      <circle cx="161" cy="235" r="6" fill="#1F1610" />
                      <circle cx="219" cy="235" r="6" fill="#1F1610" />
                    </g>
                  )}

                  {/* Mouth */}
                  {isSpeaking ? (
                    <ellipse
                      cx="190"
                      cy="285"
                      rx="14"
                      ry={interpolate(Math.sin(frame * 0.9), [-1, 1], [4, 15])}
                      fill="#991B1B"
                      stroke="#1F1610"
                      strokeWidth="2.5"
                    />
                  ) : (
                    <path d="M 178,285 Q 190,288 202,285" fill="none" stroke="#1F1610" strokeWidth="3" strokeLinecap="round" />
                  )}
                </g>
              )}

              {/* ======================================================== */}
              {/* 3. ANTIGRAVITY BOT (Iconic Terracotta AI Assistant)     */}
              {/* ======================================================== */}
              {char.type === "antigravity_bot" && (
                <g id="antigravityBotGroup" transform="translate(15, 0)">
                  {/* Floating Antenna */}
                  <rect x="172" y="90" width="6" height="50" fill="#8C3518" rx="2" />
                  <circle
                    cx="175"
                    cy="85"
                    r="12"
                    fill="#FFD166"
                    filter="drop-shadow(0 0 10px rgba(255, 209, 102, 0.9))"
                  />

                  {/* Side Ear Bolts */}
                  <rect x="45" y="250" width="22" height="40" rx="8" fill="#A23B18" />
                  <rect x="283" y="250" width="22" height="40" rx="8" fill="#A23B18" />

                  {/* Spherical Terracotta Body */}
                  <circle cx="175" cy="270" r="120" fill={`url(#botGrad-${char.id})`} stroke="#7C2D12" strokeWidth="6" />

                  {/* Blue Energy Ring */}
                  <ellipse cx="175" cy="270" rx="130" ry="24" fill="none" stroke="#00F0FF" strokeWidth="4" opacity="0.8" />

                  {/* OLED Black Faceplate Visor */}
                  <rect x="95" y="210" width="160" height="110" rx="28" fill="#0B0F17" stroke="#1E293B" strokeWidth="4" />

                  {/* Glowing Eyes */}
                  {isBlinking ? (
                    <g stroke="#FFD166" strokeWidth="4">
                      <line x1="125" y1="250" x2="155" y2="250" />
                      <line x1="195" y1="250" x2="225" y2="250" />
                    </g>
                  ) : (
                    <g>
                      <rect x="125" y="242" width="30" height="16" rx="8" fill="#FFD166" filter="drop-shadow(0 0 8px #FFD166)" />
                      <rect x="195" y="242" width="30" height="16" rx="8" fill="#FFD166" filter="drop-shadow(0 0 8px #FFD166)" />
                    </g>
                  )}

                  {/* Audio-Reactive Equalizer Mouth */}
                  <g transform="translate(135, 285)">
                    {[0, 1, 2, 3, 4].map((barIdx) => {
                      const h = isSpeaking
                        ? interpolate(
                            Math.sin(frame * 0.8 + barIdx * 1.3),
                            [-1, 1],
                            [4, 20]
                          )
                        : 4;
                      return (
                        <rect
                          key={barIdx}
                          x={barIdx * 18}
                          y={10 - h / 2}
                          width="10"
                          height={h}
                          rx="3"
                          fill="#38BDF8"
                          filter="drop-shadow(0 0 5px #38BDF8)"
                        />
                      );
                    })}
                  </g>
                </g>
              )}

              {/* ======================================================== */}
              {/* 4. GEMINI BOT (Cosmic Blue Prism AI)                    */}
              {/* ======================================================== */}
              {char.type === "gemini_bot" && (
                <g id="geminiBotGroup" transform="translate(15, 0)">
                  {/* Top Cosmic Halo */}
                  <ellipse
                    cx="175"
                    cy="110"
                    rx="60"
                    ry="18"
                    fill="none"
                    stroke="#818CF8"
                    strokeWidth="4"
                    opacity="0.8"
                    filter="drop-shadow(0 0 12px #818CF8)"
                  />

                  {/* Diamond Prism Body */}
                  <polygon
                    points="175,130 295,250 175,390 55,250"
                    fill={`url(#geminiGrad-${char.id})`}
                    stroke="#6366F1"
                    strokeWidth="5"
                  />

                  {/* Core Energy Diamond Visor */}
                  <polygon
                    points="175,200 235,260 175,320 115,260"
                    fill="#0F172A"
                    stroke="#A5B4FC"
                    strokeWidth="3"
                  />

                  {/* Pulsing Core Energy Orb */}
                  <circle
                    cx="175"
                    cy="260"
                    r={isSpeaking ? interpolate(Math.sin(frame * 0.9), [-1, 1], [18, 28]) : 20}
                    fill="#38BDF8"
                    filter="drop-shadow(0 0 16px #38BDF8)"
                  />

                  {/* Gemini Dual Spark Eyes */}
                  <circle cx="160" cy="245" r="5" fill="#FFFFFF" />
                  <circle cx="190" cy="245" r="5" fill="#FFFFFF" />
                </g>
              )}

              {/* ======================================================== */}
              {/* 5. CLAUDE BOT (Anthropic Obsidian & Amber Monolith)     */}
              {/* ======================================================== */}
              {char.type === "claude_bot" && (
                <g id="claudeBotGroup" transform="translate(15, 0)">
                  {/* Monolith Body */}
                  <rect
                    x="85"
                    y="150"
                    width="180"
                    height="250"
                    rx="24"
                    fill={`url(#claudeGrad-${char.id})`}
                    stroke="#C2410C"
                    strokeWidth="5"
                  />
                  {/* Inner Obsidian Faceplate */}
                  <rect x="110" y="180" width="130" height="120" rx="16" fill="#18181B" stroke="#71717A" strokeWidth="3" />

                  {/* Amber Eyes / Visor */}
                  <rect
                    x="130"
                    y="220"
                    width="90"
                    height="20"
                    rx="8"
                    fill="#F59E0B"
                    filter="drop-shadow(0 0 10px #F59E0B)"
                  />
                  {/* Speaking Wave Bar */}
                  {isSpeaking && (
                    <line
                      x1="140"
                      y1="270"
                      x2="210"
                      y2="270"
                      stroke="#FDE68A"
                      strokeWidth={interpolate(Math.sin(frame * 0.8), [-1, 1], [3, 8])}
                      strokeLinecap="round"
                    />
                  )}
                </g>
              )}

              {/* ======================================================== */}
              {/* 6. GROK BOT (Cyberpunk Neon Green Rogue AI)             */}
              {/* ======================================================== */}
              {char.type === "grok_bot" && (
                <g id="grokBotGroup" transform="translate(15, 0)">
                  {/* Angled Cybernetic Horns */}
                  <polygon points="100,160 120,210 90,210" fill="#16A34A" />
                  <polygon points="250,160 230,210 260,210" fill="#16A34A" />

                  {/* Sharp Hexagonal Head */}
                  <polygon
                    points="120,180 230,180 270,260 230,340 120,340 80,260"
                    fill={`url(#grokGrad-${char.id})`}
                    stroke="#22C55E"
                    strokeWidth="5"
                  />

                  {/* Sharp Cybernetic Visor */}
                  <polygon
                    points="110,240 240,240 220,270 130,270"
                    fill="#052E16"
                    stroke="#4ADE80"
                    strokeWidth="3"
                  />

                  {/* Sarcastic Angular LED Eye */}
                  <polygon
                    points="135,248 215,248 195,262 155,262"
                    fill="#4ADE80"
                    filter="drop-shadow(0 0 10px #4ADE80)"
                  />
                </g>
              )}

              {/* ======================================================== */}
              {/* 7. CODEX BOT (Matrix Emerald Wireframe Hacker AI)       */}
              {/* ======================================================== */}
              {char.type === "codex_bot" && (
                <g id="codexBotGroup" transform="translate(15, 0)">
                  {/* Terminal Hacker Cube Chassis */}
                  <rect
                    x="90"
                    y="160"
                    width="170"
                    height="200"
                    rx="18"
                    fill={`url(#codexGrad-${char.id})`}
                    stroke="#14B8A6"
                    strokeWidth="5"
                  />
                  {/* Matrix Binary Screen Face */}
                  <rect x="110" y="190" width="130" height="130" rx="10" fill="#042F2E" />
                  <text x="120" y="225" fill="#2DD4BF" fontSize="14" fontFamily="monospace">
                    {"0101011"}
                  </text>
                  <text x="120" y="250" fill="#5EEAD4" fontSize="16" fontFamily="monospace" fontWeight="bold">
                    {"> CODE_AI"}
                  </text>
                  <text x="120" y="275" fill="#2DD4BF" fontSize="14" fontFamily="monospace">
                    {"1100100"}
                  </text>
                </g>
              )}
            </svg>
          </div>
        );
      })}
    </div>
  );
};
