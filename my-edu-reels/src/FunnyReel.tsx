import React from "react";
import {
  Sequence,
  Audio,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { BackgroundGrid } from "./components/BackgroundGrid";
import { ProgressBar } from "./components/ProgressBar";
import { KaraokeCaptions, SubtitleData } from "./components/KaraokeCaptions";
import { DEFAULT_SUBTITLES } from "./data/defaultSubs";

export interface FunnyReelProps {
  [key: string]: unknown;
  subtitles?: SubtitleData;
  audioSrc?: string;
  topic?: string;
}

export const FunnyReel: React.FC<FunnyReelProps> = ({
  subtitles = DEFAULT_SUBTITLES,
  audioSrc = "voice.mp3",
  topic = "Why Your Brain Reminds You of Cringe at 3 AM",
}) => {
  const frame = useCurrentFrame();

  // Smooth continuous breathing curve (zero modulo reset)
  const memeSpring = 0.5 + 0.5 * Math.sin(frame * 0.15);

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: "#0F0B18",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Audio src={staticFile(audioSrc)} />
      <ProgressBar color="#FFE600" />
      <BackgroundGrid theme="meme" />

      {/* Safe Container */}
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
        {/* SCENE 1: The Relatable Ambush */}
        <Sequence from={0} durationInFrames={120}>
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
                background: "linear-gradient(90deg, #FFE600, #FF007F)",
                padding: "12px 32px",
                borderRadius: 999,
                boxShadow: "0 0 24px rgba(255, 230, 0, 0.6)",
                marginBottom: 24,
              }}
            >
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontWeight: 900,
                  fontSize: 26,
                  color: "#000000",
                  letterSpacing: "2px",
                  textTransform: "uppercase",
                }}
              >
                DAILY LIFE ANOMALY 💀
              </span>
            </div>

            <h1
              style={{
                fontFamily: "Impact, system-ui, sans-serif",
                fontSize: 72,
                textAlign: "center",
                color: "#FFFFFF",
                textTransform: "uppercase",
                letterSpacing: "1px",
                margin: "0 0 36px 0",
                textShadow: "4px 4px 0 #FF007F, -2px -2px 0 #000",
                lineHeight: 1.1,
              }}
            >
              The 3 AM Brain Hijack
            </h1>

            {/* Meme Graphic Card */}
            <div
              style={{
                background: "rgba(255, 255, 255, 0.08)",
                border: "3px solid #FFE600",
                borderRadius: 36,
                padding: "40px",
                width: "100%",
                maxWidth: 880,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                transform: `scale(${0.96 + memeSpring * 0.04})`,
                boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
              }}
            >
              <div style={{ fontSize: 130, marginBottom: 20 }}>🧠💤</div>
              <p
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: 38,
                  fontWeight: 900,
                  textAlign: "center",
                  color: "#FFFFFF",
                  margin: 0,
                  lineHeight: 1.3,
                }}
              >
                You: *trying to sleep at 3:00 AM*
                <br />
                <span style={{ color: "#FFE600" }}>
                  Brain: "Remember when you said 'you too' to the ticket inspector?"
                </span>
              </p>
            </div>
          </div>
        </Sequence>

        {/* SCENE 2: The Science Breakdown */}
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
                background: "linear-gradient(90deg, #00F0FF, #7000FF)",
                padding: "12px 32px",
                borderRadius: 999,
                marginBottom: 24,
              }}
            >
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontWeight: 900,
                  fontSize: 26,
                  color: "#FFFFFF",
                  letterSpacing: "2px",
                }}
              >
                THE SCIENTIFIC REASON 🔬
              </span>
            </div>

            <h2
              style={{
                fontFamily: "Impact, system-ui, sans-serif",
                fontSize: 66,
                textAlign: "center",
                color: "#FFE600",
                margin: "0 0 36px 0",
                textShadow: "3px 3px 0 #000",
              }}
            >
              Default Mode Network
            </h2>

            <div
              style={{
                background: "rgba(255, 0, 128, 0.15)",
                border: "3px solid #FF007F",
                borderRadius: 36,
                padding: "44px 36px",
                width: "100%",
                maxWidth: 880,
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 110, marginBottom: 16 }}>🚨👀</div>
              <p
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: 34,
                  fontWeight: 800,
                  color: "#FFFFFF",
                  margin: 0,
                  lineHeight: 1.4,
                }}
              >
                When visual input stops, your brain reviews survival archives...
                <br />
                mistaking social cringe for an{" "}
                <span style={{ color: "#FF007F", fontWeight: 900 }}>
                  active predator threat!
                </span>
              </p>
            </div>
          </div>
        </Sequence>

        {/* SCENE 3: The Punchline & CTA */}
        <Sequence from={240}>
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
                background: "linear-gradient(90deg, #FFE600, #FF5500)",
                borderRadius: 36,
                padding: "44px 40px",
                width: "100%",
                maxWidth: 900,
                textAlign: "center",
                boxShadow: "0 20px 40px rgba(255, 230, 0, 0.3)",
              }}
            >
              <div style={{ fontSize: 100, marginBottom: 16 }}>😭🛌</div>
              <h3
                style={{
                  fontFamily: "Impact, system-ui, sans-serif",
                  fontSize: 54,
                  color: "#000000",
                  margin: "0 0 16px 0",
                  textTransform: "uppercase",
                }}
              >
                Nobody Else Remembers It!
              </h3>
              <p
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontSize: 32,
                  fontWeight: 800,
                  color: "#1A202C",
                  margin: 0,
                  lineHeight: 1.3,
                }}
              >
                They are too busy lying awake replaying their own awkward handshakes.
              </p>
            </div>

            <div
              style={{
                marginTop: 36,
                background: "#FFFFFF",
                borderRadius: 999,
                padding: "18px 48px",
                boxShadow: "0 10px 30px rgba(255, 255, 255, 0.4)",
              }}
            >
              <span
                style={{
                  fontFamily: "system-ui, sans-serif",
                  fontWeight: 900,
                  fontSize: 28,
                  color: "#000000",
                  letterSpacing: "1px",
                }}
              >
                Send this to a friend who can't sleep! 🚀
              </span>
            </div>
          </div>
        </Sequence>
      </div>

      <KaraokeCaptions subtitles={subtitles} />
    </div>
  );
};
