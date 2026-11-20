import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

interface LowPolyRivalDevProps {
  isSpeaking: boolean;
  x?: number;
  y?: number;
  scale?: number;
}

export const LowPolyRivalDev: React.FC<LowPolyRivalDevProps> = ({
  isSpeaking,
  x = 380,
  y = 710,
  scale = 1.0,
}) => {
  const frame = useCurrentFrame();

  // Skeptical idle sway
  const breathY = Math.sin((frame + 10) / 19) * 3.5;
  const headSway = Math.sin((frame + 5) / 25) * 2.0;

  // Mouth animation when speaking
  const mouthOpen = isSpeaking
    ? interpolate(Math.sin(frame * 0.9), [-1, 1], [3, 14], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 2.5;

  // Speaking indicator pop (continuous smooth sine curve)
  const bubbleScale = isSpeaking ? (0.5 + 0.5 * Math.sin(frame * 0.25)) : 0;

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y + breathY,
        width: 320,
        height: 580,
        transform: `scale(${scale}) rotate(${headSway}deg)`,
        transformOrigin: "center bottom",
        pointerEvents: "none",
        zIndex: 20,
      }}
    >
      <svg width="320" height="580" viewBox="0 0 320 580">
        <defs>
          <filter id="rivalShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="rgba(0,0,0,0.6)" />
          </filter>
        </defs>

        {/* ======================================================== */}
        {/* 1. SPEECH BUBBLE (WHEN RIVAL SPEAKS)                     */}
        {/* ======================================================== */}
        {isSpeaking && (
          <g transform={`translate(150, 20) scale(${bubbleScale})`} filter="url(#rivalShadow)">
            <rect x="-55" y="-35" width="110" height="48" rx="20" fill="#FFFFFF" />
            <polygon points="-8,13 8,13 0,26" fill="#FFFFFF" />
            {/* Skeptical question/dots */}
            <circle cx="-20" cy="-11" r="4.5" fill="#EF4444" />
            <circle cx="0" cy="-11" r="4.5" fill="#EF4444" />
            <circle cx="20" cy="-11" r="4.5" fill="#EF4444" />
          </g>
        )}

        {/* ======================================================== */}
        {/* 2. COLLARED SHIRT BODY (FACETED PLANES)                  */}
        {/* ======================================================== */}
        {/* Main Torso */}
        <polygon points="40,430 160,395 280,430 290,580 30,580" fill="#1C382F" />
        {/* Left Shoulder Plane */}
        <polygon points="40,430 100,330 160,350 160,395" fill="#2D5A4C" />
        {/* Right Shoulder Plane */}
        <polygon points="160,350 220,330 280,430 160,395" fill="#3D7563" />
        {/* Collar V-Neck Fold */}
        <polygon points="120,350 160,400 200,350 160,365" fill="#142B24" />

        {/* ======================================================== */}
        {/* 3. NECK & FACETED HEAD                                   */}
        {/* ======================================================== */}
        <polygon points="140,300 180,300 185,355 135,355" fill="#BD8968" />
        <polygon points="135,355 160,355 155,300 140,300" fill="#9C6B4C" />

        {/* Head Facets */}
        <polygon points="105,255 135,295 185,295 215,255 190,205 130,205" fill="#D49E7C" />
        <polygon points="105,255 135,295 160,265" fill="#BA8463" />
        <polygon points="185,295 215,255 160,265" fill="#E8B290" />
        <polygon points="130,205 160,195 190,205 160,265" fill="#EDBFA1" />

        {/* Blocky Nose */}
        <polygon points="152,220 168,220 165,246 155,246" fill="#C48E6C" />

        {/* ======================================================== */}
        {/* 4. CURLY HAIR FACET CLUSTERS & LOW-POLY BEARD            */}
        {/* ======================================================== */}
        {/* Low-Poly Faceted Beard */}
        <polygon points="115,250 135,295 185,295 205,250 190,275 160,285 130,275" fill="#241B15" />
        <polygon points="135,295 160,315 185,295 160,285" fill="#17110E" />

        {/* Curly Hair Poly Clumps (Reference Style!) */}
        <polygon points="85,195 110,140 160,130 140,185" fill="#2E231C" />
        <polygon points="110,140 160,110 210,140 160,130" fill="#423329" />
        <polygon points="160,130 210,140 235,195 180,185" fill="#362921" />
        <polygon points="130,150 160,135 190,150 160,165" fill="#4F3E32" />

        {/* ======================================================== */}
        {/* 5. RECTANGULAR GLASSES (TRADITIONAL DEV TRADEMARK)       */}
        {/* ======================================================== */}
        {/* Glasses Left Frame */}
        <rect x="118" y="196" width="34" height="24" rx="4" fill="none" stroke="#18181B" strokeWidth="3" />
        {/* Glasses Right Frame */}
        <rect x="168" y="196" width="34" height="24" rx="4" fill="none" stroke="#18181B" strokeWidth="3" />
        {/* Glasses Bridge */}
        <line x1="152" y1="208" x2="168" y2="208" stroke="#18181B" strokeWidth="3" />

        {/* Eyes behind lenses */}
        <circle cx="135" cy="208" r="6" fill="#18181B" />
        <circle cx="137" cy="206" r="2" fill="#FFFFFF" />

        <circle cx="185" cy="208" r="6" fill="#18181B" />
        <circle cx="187" cy="206" r="2" fill="#FFFFFF" />

        {/* Block Eyebrows above glasses */}
        <polygon points="115,188 150,186 150,192 115,194" fill="#2E231C" />
        <polygon points="170,186 205,188 205,194 170,192" fill="#2E231C" />

        {/* ======================================================== */}
        {/* 6. MOUTH                                                 */}
        {/* ======================================================== */}
        <rect
          x="148"
          y="262 - mouthOpen / 2"
          width="24"
          height={mouthOpen}
          rx="2"
          fill="#3F1D1D"
        />
      </svg>
    </div>
  );
};
