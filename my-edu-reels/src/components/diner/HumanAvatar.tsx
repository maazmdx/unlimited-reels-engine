import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface HumanAvatarProps {
  isSpeaking: boolean;
}

export const HumanAvatar: React.FC<HumanAvatarProps> = ({ isSpeaking }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Subtle natural breathing sway
  const breathY = Math.sin(frame / 20) * 4;

  // Mouth animation when speaking
  const mouthOpen = isSpeaking
    ? interpolate(Math.sin(frame * 0.9), [-1, 1], [4, 18], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 3;

  // Eye blinking every 90 frames (~3 seconds)
  const isBlinking = frame % 90 > 84;
  const eyeHeight = isBlinking ? 1 : 9;

  // Speech bubble pop animation when speaking starts
  const bubbleScale = isSpeaking
    ? spring({
        frame: frame % 30,
        fps,
        config: { damping: 12, stiffness: 150 },
      })
    : 0;

  return (
    <div
      style={{
        position: "absolute",
        left: 120,
        top: 680 + breathY,
        width: 360,
        height: 640,
        pointerEvents: "none",
      }}
    >
      <svg width="360" height="640" viewBox="0 0 360 640">
        <defs>
          {/* Hoodie Teal Gradient */}
          <linearGradient id="hoodieGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1E3A5F" />
            <stop offset="40%" stopColor="#152843" />
            <stop offset="100%" stopColor="#0B1728" />
          </linearGradient>

          {/* Skin Tone Gradient */}
          <linearGradient id="skinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F5D0B5" />
            <stop offset="100%" stopColor="#E2AC8A" />
          </linearGradient>

          {/* Hair Dark Tone */}
          <linearGradient id="hairGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2D2522" />
            <stop offset="100%" stopColor="#120E0D" />
          </linearGradient>

          {/* Speech Bubble Glow */}
          <filter id="bubbleShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="rgba(0,0,0,0.5)" />
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* 1. SPEAKING THOUGHT/SPEECH BUBBLE (WHEN HUMAN SPEAKS)     */}
        {/* ======================================================== */}
        {isSpeaking && (
          <g
            transform={`translate(140, 20) scale(${bubbleScale})`}
            filter="url(#bubbleShadow)"
          >
            {/* Bubble Pill Container */}
            <rect
              x="-60"
              y="-40"
              width="120"
              height="55"
              rx="22"
              fill="#FFFFFF"
              stroke="#E2E8F0"
              strokeWidth="2"
            />
            {/* Tail */}
            <polygon points="-10,15 10,15 -5,32" fill="#FFFFFF" />

            {/* Three Animated Thought Dots */}
            {[0, 1, 2].map((i) => {
              const dotBounce = Math.sin((frame * 0.4) + i * 1.2) * 4;
              return (
                <circle
                  key={i}
                  cx={-24 + i * 24}
                  cy={-14 + dotBounce}
                  r="5"
                  fill="#0284C7"
                />
              );
            })}
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. BODY & HOODIE (TEAL/NAVY WITH DRAWSTRINGS)            */}
        {/* ======================================================== */}
        {/* Shoulders / Torso */}
        <path
          d="M 60,320 C 90,260 170,240 230,260 C 270,275 300,320 310,480 L 40,480 Z"
          fill="url(#hoodieGrad)"
          stroke="#0F172A"
          strokeWidth="4"
        />

        {/* Hoodie Collar / Hood Fold */}
        <path
          d="M 100,260 C 130,290 190,290 220,260 C 240,240 250,220 230,210 C 200,200 120,200 90,210 C 70,220 80,240 100,260 Z"
          fill="#142236"
          stroke="#0B1320"
          strokeWidth="3"
        />

        {/* Light Blue Drawstrings */}
        <path
          d="M 130,275 Q 128,320 125,360"
          stroke="#7DD3FC"
          strokeWidth="4"
          strokeLinecap="round"
          fill="none"
        />
        <circle cx="125" cy="362" r="4" fill="#38BDF8" />

        <path
          d="M 190,275 Q 192,320 195,360"
          stroke="#7DD3FC"
          strokeWidth="4"
          strokeLinecap="round"
          fill="none"
        />
        <circle cx="195" cy="362" r="4" fill="#38BDF8" />

        {/* ======================================================== */}
        {/* 3. NECK & HEAD                                           */}
        {/* ======================================================== */}
        {/* Neck */}
        <rect x="140" y="210" width="40" height="45" fill="url(#skinGrad)" rx="8" />

        {/* Head / Face */}
        <ellipse cx="160" cy="180" rx="55" ry="65" fill="url(#skinGrad)" />

        {/* Ear (Profile/Three-Quarter Angle) */}
        <ellipse cx="108" cy="180" rx="12" ry="18" fill="#E2AC8A" />

        {/* Hair - Modern Side-Swept Texture */}
        <path
          d="M 105,175 C 95,130 130,105 170,105 C 215,105 230,135 225,165 C 220,150 195,140 180,140 C 160,140 140,155 125,165 Z"
          fill="url(#hairGrad)"
        />
        <path
          d="M 105,175 C 100,160 105,135 120,120 C 140,100 190,100 215,115 C 210,125 180,120 160,125 C 140,130 120,145 110,170 Z"
          fill="#1C1614"
        />

        {/* Eye (Looking towards the robot on the right) */}
        <ellipse
          cx="185"
          cy="172"
          rx="6"
          ry={eyeHeight}
          fill="#1E293B"
        />
        {/* Eye Catchlight (White sparkle) */}
        {!isBlinking && <circle cx="187" cy="170" r="2" fill="#FFFFFF" />}

        {/* Eyebrow */}
        <path
          d="M 172,160 Q 186,155 198,162"
          stroke="#1C1614"
          strokeWidth="3.5"
          strokeLinecap="round"
          fill="none"
        />

        {/* Nose (Subtle 3/4 profile line) */}
        <path
          d="M 194,175 L 202,185 L 194,188"
          stroke="#C89070"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />

        {/* Mouth (Animates when speaking) */}
        <ellipse
          cx="188"
          cy="204"
          rx="10"
          ry={mouthOpen}
          fill={isSpeaking ? "#5C1D24" : "#C89070"}
        />
        {isSpeaking && (
          /* Subtle teeth highlight inside mouth */
          <line
            x1="182"
            y1={204 - mouthOpen + 2}
            x2="194"
            y2={204 - mouthOpen + 2}
            stroke="#FFFFFF"
            strokeWidth="2"
          />
        )}
      </svg>
    </div>
  );
};
