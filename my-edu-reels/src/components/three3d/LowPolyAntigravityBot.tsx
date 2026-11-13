import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface LowPolyAntigravityBotProps {
  isSpeaking: boolean;
  x?: number;
  y?: number;
  scale?: number;
}

export const LowPolyAntigravityBot: React.FC<LowPolyAntigravityBotProps> = ({
  isSpeaking,
  x = 690,
  y = 660,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Floating hover physics with subtle rotation
  const hoverY = Math.sin(frame / 15) * 10;
  const hoverRoll = Math.sin(frame / 20) * 3;

  // Eye blinking
  const isBlinking = frame % 110 > 105;
  const eyeHeight = isBlinking ? 2 : 14;

  // Equalizer waveform mouth pill heights when speaking
  const pill1 = isSpeaking ? interpolate(Math.sin(frame * 0.9), [-1, 1], [4, 18]) : 4;
  const pill2 = isSpeaking ? interpolate(Math.cos(frame * 1.2), [-1, 1], [6, 24]) : 4;
  const pill3 = isSpeaking ? interpolate(Math.sin(frame * 1.5), [-1, 1], [4, 20]) : 4;
  const pill4 = isSpeaking ? interpolate(Math.cos(frame * 0.8), [-1, 1], [6, 22]) : 4;
  const pill5 = isSpeaking ? interpolate(Math.sin(frame * 1.1), [-1, 1], [4, 16]) : 4;

  // Radiating sound wave indicator
  const soundWaveScale = isSpeaking
    ? spring({
        frame: frame % 30,
        fps,
        config: { damping: 14, stiffness: 150 },
      })
    : 0;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y + hoverY,
        width: 340,
        height: 580,
        transform: `scale(${scale}) rotate(${hoverRoll}deg)`,
        transformOrigin: "center center",
        pointerEvents: "none",
        zIndex: 25,
      }}
    >
      <svg width="340" height="580" viewBox="0 0 340 580">
        <defs>
          <filter id="botGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* 1. SPEAKER AUDIO RIPPLE (WHEN BOT SPEAKS)                */}
        {/* ======================================================== */}
        {isSpeaking && (
          <g transform={`translate(170, 30) scale(${soundWaveScale})`} filter="url(#botGlow)">
            <circle cx="0" cy="0" r="22" fill="#FFFFFF" />
            <polygon points="-8,-6 -3,-6 3,-11 3,11 -3,6 -8,6" fill="#D95B18" />
            <path d="M 6,-5 A 7,7 0 0,1 6,5" fill="none" stroke="#0284C7" strokeWidth="2" strokeLinecap="round" />
            <path d="M 10,-9 A 12,12 0 0,1 10,9" fill="none" stroke="#0284C7" strokeWidth="2" strokeLinecap="round" />
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. ANTENNA ON TOP                                        */}
        {/* ======================================================== */}
        <polygon points="166,130 174,130 172,65 168,65" fill="#4B5563" />
        <circle cx="170" cy="58" r="12" fill={isSpeaking ? "#00F0FF" : "#F59E0B"} filter="drop-shadow(0 0 10px #00F0FF)" />

        {/* ======================================================== */}
        {/* 3. 3D FACETED LOW-POLY SPHERE (REFERENCE TERRACOTTA!)    */}
        {/* ======================================================== */}
        {/* Faceted Polygon Outer Shell (Flat Shading) */}
        {/* Top Facets */}
        <polygon points="170,120 120,150 170,180 220,150" fill="#F97316" />
        <polygon points="170,120 220,150 260,180 220,130" fill="#EA580C" />
        <polygon points="170,120 120,150 80,180 120,130" fill="#C2410C" />

        {/* Left Side Facets */}
        <polygon points="80,180 120,150 100,220 50,220" fill="#9A3412" />
        <polygon points="50,220 100,220 90,290 40,280" fill="#7C2D12" />
        <polygon points="40,280 90,290 110,350 60,340" fill="#6C2710" />

        {/* Right Side Facets (Key Light) */}
        <polygon points="220,150 260,180 290,220 240,220" fill="#FB923C" />
        <polygon points="240,220 290,220 300,280 250,290" fill="#F97316" />
        <polygon points="250,290 300,280 280,340 230,350" fill="#EA580C" />

        {/* Bottom Facets */}
        <polygon points="110,350 170,380 230,350 170,340" fill="#9A3412" />
        <polygon points="60,340 110,350 140,395 90,390" fill="#7C2D12" />
        <polygon points="230,350 280,340 250,390 200,395" fill="#C2410C" />

        {/* Side Ear Pegs */}
        <polygon points="38,235 50,230 50,270 38,265" fill="#4B5563" />
        <polygon points="290,230 302,235 302,265 290,270" fill="#374151" />

        {/* ======================================================== */}
        {/* 4. CIRCULAR RECESSED DARK OLED SCREEN VISOR              */}
        {/* ======================================================== */}
        {/* Visor Bezel Ring */}
        <circle cx="170" cy="250" r="88" fill="#18181B" stroke="#27272A" strokeWidth="6" />
        <circle cx="170" cy="250" r="84" fill="#09090B" />

        {/* Visor Glass Highlight Arc */}
        <path d="M 115,210 Q 170,185 225,210" stroke="rgba(255,255,255,0.15)" strokeWidth="4" fill="none" strokeLinecap="round" />

        {/* ======================================================== */}
        {/* 5. DIGITAL GLOWING CAPSULE EYES & SOUND-WAVE EQUALIZER   */}
        {/* ======================================================== */}
        <g filter="url(#botGlow)">
          {/* Left Digital Eye (Capsule) */}
          <rect
            x="122"
            y={225 - eyeHeight / 2}
            width="32"
            height={eyeHeight}
            rx="6"
            fill="#FEF08A"
          />

          {/* Right Digital Eye (Capsule) */}
          <rect
            x="186"
            y={225 - eyeHeight / 2}
            width="32"
            height={eyeHeight}
            rx="6"
            fill="#FEF08A"
          />

          {/* Sound-Wave Equalizer Mouth (Reference Signature Vertical Pills!) */}
          {!isSpeaking ? (
            /* Idle calm line */
            <rect x="146" y="278" width="48" height="5" rx="2.5" fill="#FACC15" />
          ) : (
            /* 5 Animated Equalizer Vertical Bars */
            <g>
              <rect x="134" y={280 - pill1 / 2} width="6" height={pill1} rx="3" fill="#FACC15" />
              <rect x="146" y={280 - pill2 / 2} width="6" height={pill2} rx="3" fill="#FEF08A" />
              <rect x="158" y={280 - pill3 / 2} width="6" height={pill3} rx="3" fill="#FEF08A" />
              <rect x="170" y={280 - pill4 / 2} width="6" height={pill4} rx="3" fill="#FEF08A" />
              <rect x="182" y={280 - pill5 / 2} width="6" height={pill5} rx="3" fill="#FACC15" />
              <rect x="194" y={280 - pill1 / 2} width="6" height={pill1} rx="3" fill="#FACC15" />
            </g>
          )}
        </g>
      </svg>
    </div>
  );
};
