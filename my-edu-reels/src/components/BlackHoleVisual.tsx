import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const BlackHoleVisual: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const introSpring = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.7, stiffness: 140 },
  });

  // Rotation of accretion disk
  const diskRotation = (frame * 1.2) % 360;
  const lensingWave = Math.sin((frame / fps) * 3) * 6;

  // Accretion disk pulsation
  const glowPulse = 0.85 + Math.sin((frame / fps) * 4) * 0.15;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        transform: `scale(${introSpring})`,
        opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" }),
      }}
    >
      {/* Category Pill */}
      <div
        style={{
          background: "linear-gradient(90deg, #FF5500, #FF0055)",
          padding: "10px 28px",
          borderRadius: 999,
          boxShadow: "0 0 24px rgba(255, 85, 0, 0.6)",
          marginBottom: 20,
        }}
      >
        <span
          style={{
            fontFamily: "system-ui, sans-serif",
            fontWeight: 900,
            fontSize: 24,
            letterSpacing: "3px",
            color: "#FFFFFF",
            textTransform: "uppercase",
          }}
        >
          ASTROPHYSICS BREAKTHROUGH
        </span>
      </div>

      {/* Main Hook Header */}
      <h1
        style={{
          fontFamily: "system-ui, sans-serif",
          fontWeight: 900,
          fontSize: 68,
          textAlign: "center",
          lineHeight: 1.15,
          color: "#FFFFFF",
          margin: "0 0 40px 0",
          textShadow: "0 0 30px rgba(0, 240, 255, 0.4)",
          maxWidth: 900,
        }}
      >
        Gravitational{" "}
        <span
          style={{
            background: "linear-gradient(90deg, #00F0FF, #7000FF, #FF007F)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            display: "inline-block",
          }}
        >
          Time Dilation
        </span>
      </h1>

      {/* Glowing Black Hole SVG Illustration */}
      <div
        style={{
          position: "relative",
          width: 520,
          height: 520,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          margin: "20px 0",
        }}
      >
        {/* Background Photon Lensing Halo */}
        <div
          style={{
            position: "absolute",
            width: 460,
            height: 460,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(255, 140, 0, 0.45) 0%, rgba(255, 60, 0, 0.15) 50%, transparent 70%)",
            filter: "blur(40px)",
            transform: `scale(${glowPulse})`,
          }}
        />

        <svg width="520" height="520" viewBox="0 0 520 520">
          <defs>
            {/* Accretion Disk Gradients */}
            <linearGradient id="diskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#FFE066" stopOpacity="1" />
              <stop offset="35%" stopColor="#FF7700" stopOpacity="0.95" />
              <stop offset="70%" stopColor="#FF0055" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#4A00E0" stopOpacity="0.4" />
            </linearGradient>

            <linearGradient id="lensingGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#FFE599" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#FF6B00" stopOpacity="0.5" />
              <stop offset="100%" stopColor="transparent" stopOpacity="0" />
            </linearGradient>

            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Spacetime Distortion Funnel Lines */}
          <g opacity="0.35" stroke="#00F0FF" strokeWidth="1.5" fill="none">
            <ellipse cx="260" cy="260" rx="230" ry={75 + lensingWave} />
            <ellipse cx="260" cy="260" rx="190" ry={60 + lensingWave * 0.8} />
            <ellipse cx="260" cy="260" rx="150" ry={45 + lensingWave * 0.5} />
          </g>

          {/* Upper Gravitational Lensed Arc (Bent light over the top) */}
          <path
            d="M 90 260 C 130 110, 390 110, 430 260"
            fill="none"
            stroke="url(#lensingGradient)"
            strokeWidth="38"
            strokeLinecap="round"
            filter="url(#glow)"
          />

          {/* Rotating Accretion Disk (Elliptical ring around event horizon) */}
          <g transform={`rotate(${diskRotation} 260 260)`}>
            <ellipse
              cx="260"
              cy="260"
              rx="210"
              ry="65"
              fill="none"
              stroke="url(#diskGradient)"
              strokeWidth="42"
              strokeLinecap="round"
              filter="url(#glow)"
            />
          </g>

          {/* Relativistic Beaming Sparkle Points */}
          <circle
            cx={260 + Math.cos((diskRotation * Math.PI) / 180) * 190}
            cy={260 + Math.sin((diskRotation * Math.PI) / 180) * 58}
            r="7"
            fill="#FFFFFF"
            filter="url(#glow)"
          />

          {/* Photon Sphere (Bright golden razor-thin border) */}
          <circle
            cx="260"
            cy="260"
            r="92"
            fill="none"
            stroke="#FFE599"
            strokeWidth="4"
            filter="url(#glow)"
          />

          {/* Event Horizon (Pure Absolute Black Void) */}
          <circle
            cx="260"
            cy="260"
            r="88"
            fill="#030508"
            stroke="#1A202C"
            strokeWidth="2"
          />

          {/* Lower Accretion Disk Arc (Crossing in front) */}
          <path
            d="M 80 260 C 120 360, 400 360, 440 260"
            fill="none"
            stroke="url(#diskGradient)"
            strokeWidth="34"
            strokeLinecap="round"
            filter="url(#glow)"
          />
        </svg>
      </div>

      {/* Sub-card: Hook Statement */}
      <div
        style={{
          background: "rgba(255, 255, 255, 0.05)",
          border: "1px solid rgba(255, 255, 255, 0.12)",
          borderRadius: 24,
          padding: "20px 36px",
          textAlign: "center",
          marginTop: 10,
          maxWidth: 820,
        }}
      >
        <p
          style={{
            fontFamily: "system-ui, sans-serif",
            fontSize: 32,
            fontWeight: 700,
            color: "#E2E8F0",
            margin: 0,
            letterSpacing: "-0.2px",
          }}
        >
          Near infinite mass, the fabric of spacetime stretches so fiercely that{" "}
          <span style={{ color: "#FFE600", fontWeight: 900 }}>
            time itself slows down.
          </span>
        </p>
      </div>
    </div>
  );
};
