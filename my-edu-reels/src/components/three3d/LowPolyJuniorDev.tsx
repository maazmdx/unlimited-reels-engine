import React from "react";
import { useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";

interface LowPolyJuniorDevProps {
  isSpeaking: boolean;
  x?: number;
  y?: number;
  scale?: number;
}

export const LowPolyJuniorDev: React.FC<LowPolyJuniorDevProps> = ({
  isSpeaking,
  x = 60,
  y = 700,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Idle natural breathing and head bob
  const breathY = Math.sin(frame / 18) * 4;
  const headTilt = Math.sin(frame / 22) * 1.8;

  // Mouth animation when speaking
  const mouthOpen = isSpeaking
    ? interpolate(Math.sin(frame * 0.95), [-1, 1], [3, 16], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 3;

  // Speaking indicator pop-in
  const speechBubblePop = isSpeaking
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
        top: y + breathY,
        width: 320,
        height: 580,
        transform: `scale(${scale}) rotate(${headTilt}deg)`,
        transformOrigin: "center bottom",
        pointerEvents: "none",
        zIndex: 20,
      }}
    >
      <svg width="320" height="580" viewBox="0 0 320 580">
        <defs>
          {/* Subtle directional drop shadow */}
          <filter id="charShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="rgba(0,0,0,0.6)" />
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* 1. SPEECH BUBBLE INDICATOR (WHEN JUNIOR SPEAKS)          */}
        {/* ======================================================== */}
        {isSpeaking && (
          <g transform={`translate(140, 20) scale(${speechBubblePop})`} filter="url(#charShadow)">
            <rect x="-55" y="-35" width="110" height="48" rx="20" fill="#FFFFFF" />
            <polygon points="-8,13 8,13 0,26" fill="#FFFFFF" />
            <circle cx="-20" cy="-11" r="4.5" fill="#0284C7" />
            <circle cx="0" cy="-11" r="4.5" fill="#0284C7" />
            <circle cx="20" cy="-11" r="4.5" fill="#0284C7" />
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. HOODIE BODY & TORSO (FACETED PLANES)                  */}
        {/* ======================================================== */}
        {/* Main Torso Facets */}
        <polygon points="50,420 160,390 270,420 280,580 40,580" fill="#152843" />
        {/* Left Shoulder Plane */}
        <polygon points="50,420 100,320 160,340 160,390" fill="#1E3A5F" />
        {/* Right Shoulder Plane (Light side) */}
        <polygon points="160,340 220,320 270,420 160,390" fill="#244570" />
        {/* Chest Central Fold */}
        <polygon points="110,340 160,370 210,340 160,340" fill="#0F1D30" />

        {/* 3D Rectangular Block Drawstrings */}
        <rect x="130" y="345" width="8" height="65" rx="2" fill="#E2D0B8" stroke="#8C7355" strokeWidth="1.5" />
        <rect x="182" y="345" width="8" height="65" rx="2" fill="#E2D0B8" stroke="#8C7355" strokeWidth="1.5" />

        {/* ======================================================== */}
        {/* 3. NECK & FACETED 3D LOW-POLY HEAD                       */}
        {/* ======================================================== */}
        {/* Neck Planar Column */}
        <polygon points="140,290 180,290 185,340 135,340" fill="#B37854" />
        <polygon points="135,340 160,340 155,290 140,290" fill="#945F3E" />

        {/* Low-Poly Head Facets (Faceted Planar Shading) */}
        {/* Chin / Jaw Plate */}
        <polygon points="130,290 160,310 190,290 160,285" fill="#9E6845" />
        {/* Left Jaw Facet */}
        <polygon points="105,250 130,290 160,285 135,245" fill="#A86E49" />
        {/* Right Jaw Facet (Lit side) */}
        <polygon points="160,285 190,290 215,250 185,245" fill="#BA7F59" />
        {/* Left Cheek */}
        <polygon points="95,190 105,250 135,245 130,195" fill="#C48862" />
        {/* Right Cheek (Key Light) */}
        <polygon points="185,245 215,250 225,190 190,195" fill="#D69A73" />
        {/* Center Face / Nose Bridge */}
        <polygon points="130,195 160,185 190,195 185,245 160,255 135,245" fill="#E0A47D" />

        {/* Blocky Low-Poly 3D Nose */}
        <polygon points="152,210 168,210 165,238 155,238" fill="#B87B56" />
        <polygon points="155,238 165,238 160,244" fill="#8C5535" />

        {/* ======================================================== */}
        {/* 4. BEANIE / CAP & LOW-POLY HAIR                          */}
        {/* ======================================================== */}
        {/* Black Low-Poly Beanie (Faceted Dome) */}
        <polygon points="90,180 120,135 160,120 200,135 230,180 160,185" fill="#18181B" />
        <polygon points="120,135 160,105 200,135 160,120" fill="#27272A" />
        <polygon points="85,185 160,190 235,185 230,175 90,175" fill="#09090B" />

        {/* ======================================================== */}
        {/* 5. EYES & BLOCKY RECTANGULAR EYEBROWS                    */}
        {/* ======================================================== */}
        {/* Blocky Rectangular Eyebrows (Reference Signature!) */}
        {/* Left Eyebrow (3D Prism) */}
        <polygon points="120,176 148,172 148,182 120,186" fill="#18181B" />
        <polygon points="120,172 148,168 148,172 120,176" fill="#27272A" />

        {/* Right Eyebrow (3D Prism) */}
        <polygon points="172,172 200,176 200,186 172,182" fill="#18181B" />
        <polygon points="172,168 200,172 200,176 172,172" fill="#27272A" />

        {/* Spherical Glossy Black Eyes */}
        <circle cx="134" cy="198" r="8" fill="#09090B" />
        <circle cx="136" cy="196" r="2.5" fill="#FFFFFF" />

        <circle cx="186" cy="198" r="8" fill="#09090B" />
        <circle cx="188" cy="196" r="2.5" fill="#FFFFFF" />

        {/* ======================================================== */}
        {/* 6. MOUTH & RECTANGULAR BLOCK TEETH                       */}
        {/* ======================================================== */}
        <rect
          x="146"
          y="262 - mouthOpen / 2"
          width="28"
          height={mouthOpen}
          rx="3"
          fill="#3F1D1D"
        />
        {/* White Rectangular Teeth Block (Like Reference!) */}
        <rect x="150" y="260" width="20" height="4" rx="1" fill="#FFFFFF" />
      </svg>
    </div>
  );
};
