import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface AntigravityBotProps {
  isSpeaking: boolean;
}

export const AntigravityBot: React.FC<AntigravityBotProps> = ({ isSpeaking }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Smooth floating hover physics
  const hoverY = Math.sin(frame / 16) * 9;
  const hoverTilt = Math.sin(frame / 24) * 2.5;

  // Eye blinking every 120 frames (~4 seconds)
  const isBlinking = frame % 120 > 114;
  const eyeHeight = isBlinking ? 2 : 10;

  // Sound wave speaker indicator pop when speaking
  const indicatorScale = isSpeaking
    ? spring({
        frame: frame % 30,
        fps,
        config: { damping: 14, stiffness: 160 },
      })
    : 0;

  // OLED mouth equalizer waveform when speaking
  const wave1 = isSpeaking ? interpolate(Math.sin(frame * 0.9), [-1, 1], [3, 16]) : 3;
  const wave2 = isSpeaking ? interpolate(Math.cos(frame * 1.1), [-1, 1], [4, 22]) : 3;
  const wave3 = isSpeaking ? interpolate(Math.sin(frame * 1.3), [-1, 1], [3, 18]) : 3;
  const wave4 = isSpeaking ? interpolate(Math.cos(frame * 0.7), [-1, 1], [2, 12]) : 3;

  return (
    <div
      style={{
        position: "absolute",
        right: 110,
        top: 670 + hoverY,
        width: 380,
        height: 640,
        pointerEvents: "none",
        transform: `rotate(${hoverTilt}deg)`,
        transformOrigin: "center bottom",
      }}
    >
      <svg width="380" height="640" viewBox="0 0 380 640">
        <defs>
          {/* Spherical Orange/Bronze Metallic Gradient */}
          <radialGradient id="botSphereGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#FFA654" />
            <stop offset="35%" stopColor="#E66A23" />
            <stop offset="75%" stopColor="#B8420B" />
            <stop offset="100%" stopColor="#662103" />
          </radialGradient>

          {/* Antigravity Blue Energy Ring */}
          <linearGradient id="energyRing" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00F0FF" />
            <stop offset="50%" stopColor="#38BDF8" />
            <stop offset="100%" stopColor="#0284C7" />
          </linearGradient>

          {/* OLED Screen Dark Gloss */}
          <linearGradient id="oledVisor" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#181E29" />
            <stop offset="50%" stopColor="#0B0F17" />
            <stop offset="100%" stopColor="#05070B" />
          </linearGradient>

          {/* Screen Cyan Neon Glow Filter */}
          <filter id="cyanGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* 1. SPEAKER AUDIO RIPPLE INDICATOR (WHEN BOT SPEAKS)      */}
        {/* ======================================================== */}
        {isSpeaking && (
          <g
            transform={`translate(200, 25) scale(${indicatorScale})`}
            filter="drop-shadow(0 0 10px rgba(0, 240, 255, 0.7))"
          >
            {/* Center Speaker Icon Pill */}
            <circle cx="0" cy="0" r="24" fill="#FFFFFF" />
            {/* Speaker Cone */}
            <path
              d="M -10,-8 L -4,-8 L 4,-14 L 4,14 L -4,8 L -10,8 Z"
              fill="#0F172A"
            />
            {/* Sound Wave Arc 1 */}
            <path
              d="M 8,-7 A 9,9 0 0,1 8,7"
              fill="none"
              stroke="#0284C7"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
            {/* Sound Wave Arc 2 */}
            <path
              d="M 12,-12 A 15,15 0 0,1 12,12"
              fill="none"
              stroke="#0284C7"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. ANTENNA ON TOP                                        */}
        {/* ======================================================== */}
        {/* Antenna Stem */}
        <line
          x1="190"
          y1="130"
          x2="190"
          y2="70"
          stroke="#475569"
          strokeWidth="6"
          strokeLinecap="round"
        />
        {/* Antenna Glowing Orb */}
        <circle
          cx="190"
          cy="65"
          r="13"
          fill={isSpeaking ? "#00F0FF" : "#FFA654"}
          filter="drop-shadow(0 0 12px rgba(0, 240, 255, 0.9))"
        />

        {/* ======================================================== */}
        {/* 3. MAIN SPHERICAL ROBOT BODY                             */}
        {/* ======================================================== */}
        {/* Spherical Outer Shell */}
        <circle
          cx="190"
          cy="260"
          r="125"
          fill="url(#botSphereGrad)"
          stroke="#421401"
          strokeWidth="6"
        />

        {/* Antigravity Blue Accent Ring Trim */}
        <circle
          cx="190"
          cy="260"
          r="122"
          fill="none"
          stroke="url(#energyRing)"
          strokeWidth="3.5"
          opacity="0.85"
        />

        {/* Ear Bolts / Pegs on Sides */}
        <rect x="52" y="246" width="16" height="28" rx="6" fill="#334155" stroke="#1E293B" strokeWidth="2" />
        <rect x="312" y="246" width="16" height="28" rx="6" fill="#334155" stroke="#1E293B" strokeWidth="2" />

        {/* ======================================================== */}
        {/* 4. OLED CURVED VISOR SCREEN                              */}
        {/* ======================================================== */}
        {/* Screen Recess */}
        <rect
          x="100"
          y="180"
          width="180"
          height="140"
          rx="32"
          fill="url(#oledVisor)"
          stroke="#1E293B"
          strokeWidth="6"
          filter="drop-shadow(0 4px 15px rgba(0, 0, 0, 0.8))"
        />

        {/* Visor Gloss Reflection Curve */}
        <path
          d="M 115,195 Q 190,185 265,195"
          stroke="rgba(255, 255, 255, 0.18)"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
        />

        {/* ======================================================== */}
        {/* 5. DIGITAL GLOWING EYES & MOUTH                          */}
        {/* ======================================================== */}
        <g filter="url(#cyanGlow)">
          {/* Left Digital Eye (Cyan/White Capsule) */}
          <rect
            x="132"
            y={225 - eyeHeight / 2}
            width="34"
            height={eyeHeight}
            rx="5"
            fill="#E0F2FE"
          />

          {/* Right Digital Eye (Cyan/White Capsule) */}
          <rect
            x="214"
            y={225 - eyeHeight / 2}
            width="34"
            height={eyeHeight}
            rx="5"
            fill="#E0F2FE"
          />

          {/* Digital Equalizer Mouth */}
          {!isSpeaking ? (
            /* Idle calm smile line */
            <line
              x1="160"
              y1="278"
              x2="220"
              y2="278"
              stroke="#38BDF8"
              strokeWidth="4"
              strokeLinecap="round"
            />
          ) : (
            /* Animated 4-bar equalizer waveform */
            <g>
              <rect x="155" y={278 - wave1 / 2} width="8" height={wave1} rx="4" fill="#38BDF8" />
              <rect x="172" y={278 - wave2 / 2} width="8" height={wave2} rx="4" fill="#00F0FF" />
              <rect x="190" y={278 - wave3 / 2} width="8" height={wave3} rx="4" fill="#00F0FF" />
              <rect x="208" y={278 - wave4 / 2} width="8" height={wave4} rx="4" fill="#38BDF8" />
            </g>
          )}
        </g>

        {/* ======================================================== */}
        {/* 6. GOOGLE GEMINI / ANTIGRAVITY EMBLEM BADGE              */}
        {/* ======================================================== */}
        <g transform="translate(190, 350)">
          <circle cx="0" cy="0" r="16" fill="#0F172A" stroke="#38BDF8" strokeWidth="2" />
          {/* Gemini Four-Point Star */}
          <path
            d="M 0,-10 Q 0,0 10,0 Q 0,0 0,10 Q 0,0 -10,0 Q 0,0 0,-10 Z"
            fill="#00F0FF"
          />
        </g>
      </svg>
    </div>
  );
};
