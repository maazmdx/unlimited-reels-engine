import React from "react";
import {
  Sequence,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BackgroundGrid } from "./components/BackgroundGrid";
import { ProgressBar } from "./components/ProgressBar";
import { MangaSpeedLines } from "./components/anime/MangaSpeedLines";
import { AuraEnergy } from "./components/anime/AuraEnergy";
import { AnimeBadge } from "./components/anime/AnimeBadge";
import { KaraokeCaptions, SubtitleData } from "./components/KaraokeCaptions";
import { DEFAULT_SUBTITLES } from "./data/defaultSubs";

export interface AnimeEduReelProps {
  [key: string]: unknown;
  subtitles?: SubtitleData;
  audioSrc?: string;
  title?: string;
  kanji?: string;
}

export const AnimeEduReel: React.FC<AnimeEduReelProps> = ({
  subtitles = DEFAULT_SUBTITLES,
  audioSrc = "voice.mp3",
  title = "Gojo's Infinity Explained by Calculus",
  kanji = "領域展開",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Pulse & eye glow calculations
  const glowPulse = 0.85 + Math.sin((frame / fps) * 6) * 0.15;
  const hexRotation = (frame * 0.8) % 360;

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#07040E",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile(audioSrc)} />
      <ProgressBar color="#00F0FF" />
      <BackgroundGrid theme="cyber" />
      <MangaSpeedLines intensity={1.2} />

      {/* Safe Area Container */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: 1080,
          height: 1920,
          boxSizing: "border-box",
          paddingTop: 220,
          paddingBottom: 280,
          paddingLeft: 64,
          paddingRight: 64,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          zIndex: 10,
        }}
      >
        <AnimeBadge kanji={kanji} label="ANIME SCIENCE EXPANSION" accentColor="#00F0FF" />

        {/* Dynamic Title */}
        <h1
          style={{
            fontFamily:
              "'Noto Sans Kannada', 'Noto Sans Devanagari', 'Impact', system-ui, sans-serif",
            fontWeight: 900,
            fontSize: 64,
            textAlign: "center",
            color: "#FFFFFF",
            lineHeight: 1.15,
            margin: "0 0 32px 0",
            textShadow: "0 0 30px #00F0FF, 3px 3px 0 #FF007F",
            maxWidth: 920,
          }}
        >
          {title}
        </h1>

        {/* SCENE 1 (Frames 0–120): The Infinity Barrier & Six Eyes */}
        <Sequence from={0} durationInFrames={120}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
            }}
          >
            {/* Six Eyes Glowing Hexagonal Shield SVG */}
            <div
              style={{
                position: "relative",
                width: 480,
                height: 480,
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                margin: "10px 0 24px 0",
              }}
            >
              <AuraEnergy color="#00F0FF" />

              <svg width="480" height="480" viewBox="0 0 480 480">
                <defs>
                  <filter id="animeGlow" x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation="10" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                </defs>

                {/* Rotating Hexagonal Infinity Rings */}
                <g transform={`rotate(${hexRotation} 240 240)`}>
                  <polygon
                    points="240,60 395,150 395,330 240,420 85,330 85,150"
                    fill="none"
                    stroke="#00F0FF"
                    strokeWidth="4"
                    strokeDasharray="30 20"
                    filter="url(#animeGlow)"
                  />
                </g>

                <g transform={`rotate(${-hexRotation * 1.5} 240 240)`}>
                  <polygon
                    points="240,100 360,170 360,310 240,380 120,310 120,170"
                    fill="none"
                    stroke="#FF007F"
                    strokeWidth="3"
                    opacity="0.8"
                  />
                </g>

                {/* Central Six-Eyes Infinity Core */}
                <circle
                  cx="240"
                  cy="240"
                  r="70"
                  fill="#000F2E"
                  stroke="#00F0FF"
                  strokeWidth="5"
                  filter="url(#animeGlow)"
                />

                <circle
                  cx="240"
                  cy="240"
                  r={45 * glowPulse}
                  fill="radial-gradient(circle, #FFFFFF 0%, #00F0FF 70%, transparent 100%)"
                  opacity="0.9"
                />

                <text
                  x="240"
                  y="252"
                  textAnchor="middle"
                  fill="#FFFFFF"
                  fontFamily="sans-serif"
                  fontWeight="900"
                  fontSize="38"
                  filter="url(#animeGlow)"
                >
                  ∞
                </text>
              </svg>
            </div>

            <div
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: "2px solid #00F0FF",
                borderRadius: 24,
                padding: "18px 36px",
                textAlign: "center",
                maxWidth: 860,
              }}
            >
              <p
                style={{
                  fontFamily:
                    "'Noto Sans Kannada', 'Noto Sans Devanagari', system-ui, sans-serif",
                  fontSize: 32,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  margin: 0,
                }}
              >
                Gojo doesn't stop attacks with force —{" "}
                <span style={{ color: "#FFE600" }}>
                  he divides distance into infinity!
                </span>
              </p>
            </div>
          </div>
        </Sequence>

        {/* SCENE 2 (Frames 120–240): Zeno's Paradox & The Calculus Formula */}
        <Sequence from={120} durationInFrames={120}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
            }}
          >
            <div
              style={{
                background: "rgba(18, 14, 35, 0.9)",
                backdropFilter: "blur(20px)",
                border: "3px solid #FF007F",
                borderRadius: 36,
                padding: "36px 40px",
                width: "100%",
                maxWidth: 900,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                boxShadow: "0 20px 50px rgba(255, 0, 128, 0.3)",
              }}
            >
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontWeight: 900,
                  fontSize: 24,
                  letterSpacing: "2px",
                  color: "#FF007F",
                  textTransform: "uppercase",
                  marginBottom: 16,
                }}
              >
                Mathematical Principle
              </span>

              <h3
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: 48,
                  fontWeight: 900,
                  color: "#FFFFFF",
                  margin: "0 0 16px 0",
                  textAlign: "center",
                }}
              >
                Zeno's Dichotomy Paradox
              </h3>

              {/* Calculus Limit Display */}
              <div
                style={{
                  background: "rgba(0, 0, 0, 0.6)",
                  border: "2px solid #FFE600",
                  borderRadius: 24,
                  padding: "20px 40px",
                  margin: "12px 0 20px 0",
                }}
              >
                <span
                  style={{
                    fontFamily: "'Times New Roman', serif",
                    fontStyle: "italic",
                    fontSize: 52,
                    fontWeight: 700,
                    color: "#FFE600",
                    textShadow: "0 0 16px rgba(255, 230, 0, 0.8)",
                  }}
                >
                  lim<sub>n → ∞</sub> (1 / 2<sup>n</sup>) = 0
                </span>
              </div>

              <p
                style={{
                  fontFamily:
                    "'Noto Sans Kannada', 'Noto Sans Devanagari', system-ui, sans-serif",
                  fontSize: 30,
                  fontWeight: 700,
                  textAlign: "center",
                  color: "#E2E8F0",
                  lineHeight: 1.4,
                  margin: 0,
                }}
              >
                The punch covers 1/2 the distance, then 1/4, then 1/8...
                <br />
                It moves infinitely closer, but mathematically never reaches!
              </p>
            </div>
          </div>
        </Sequence>

        {/* SCENE 3 (Frames 240+): Power Level & Final Flex */}
        <Sequence from={240}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
            }}
          >
            {/* Anime Power Meter */}
            <div
              style={{
                background: "linear-gradient(90deg, #FF0055, #FFE600)",
                borderRadius: 36,
                padding: "36px 44px",
                width: "100%",
                maxWidth: 900,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                boxShadow: "0 25px 60px rgba(255, 0, 85, 0.4)",
              }}
            >
              <span
                style={{
                  fontFamily: "Impact, system-ui, sans-serif",
                  fontSize: 32,
                  letterSpacing: "3px",
                  color: "#000000",
                  textTransform: "uppercase",
                }}
              >
                ANIME POWER LEVEL
              </span>

              <h3
                style={{
                  fontFamily: "Impact, system-ui, sans-serif",
                  fontSize: 64,
                  color: "#000000",
                  margin: "8px 0 16px 0",
                  letterSpacing: "2px",
                }}
              >
                OVER 9,000! ⚡
              </h3>

              <p
                style={{
                  fontFamily:
                    "'Noto Sans Kannada', 'Noto Sans Devanagari', system-ui, sans-serif",
                  fontSize: 30,
                  fontWeight: 900,
                  textAlign: "center",
                  color: "#1A202C",
                  margin: 0,
                }}
              >
                Real math is the ultimate flex in fiction and reality!
              </p>
            </div>

            <div
              style={{
                marginTop: 36,
                background: "linear-gradient(90deg, #00F0FF, #7000FF)",
                borderRadius: 999,
                padding: "18px 48px",
                boxShadow: "0 10px 30px rgba(0, 240, 255, 0.4)",
              }}
            >
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontWeight: 900,
                  fontSize: 28,
                  color: "#FFFFFF",
                  letterSpacing: "1.5px",
                  textTransform: "uppercase",
                }}
              >
                Follow for More Anime Science! 🚀
              </span>
            </div>
          </div>
        </Sequence>
      </div>

      <KaraokeCaptions subtitles={subtitles} />
    </div>
  );
};
