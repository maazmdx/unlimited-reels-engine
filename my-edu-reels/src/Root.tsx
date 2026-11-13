import React from "react";
import { Composition, CalculateMetadataFunction } from "remotion";
import { EduReel, EduReelProps } from "./EduReel";
import { AnimeEduReel, AnimeEduReelProps } from "./AnimeEduReel";
import { FunnyReel } from "./FunnyReel";
import { UniversalReel } from "./UniversalReel";
import { DinerAgentReel, DinerAgentReelProps } from "./DinerAgentReel";
import {
  ThreeWayComparisonReel,
  ThreeWayComparisonReelProps,
} from "./ThreeWayComparisonReel";
import {
  MasterAutonomousReel,
  MasterAutonomousReelProps,
} from "./MasterAutonomousReel";
import { TestThree } from "./TestThree";
import { DEFAULT_SUBTITLES } from "./data/defaultSubs";

const calculateEduMetadata: CalculateMetadataFunction<EduReelProps> = async ({
  props,
}) => {
  const chunks = props.subtitles?.chunks || DEFAULT_SUBTITLES.chunks;
  const lastChunk = chunks[chunks.length - 1];
  const audioDurationSec = lastChunk ? lastChunk.end + 0.6 : 15.0;
  const computedFrames = Math.ceil(audioDurationSec * 30);

  return {
    durationInFrames: computedFrames > 0 ? computedFrames : 462,
    props: {
      ...props,
      subtitles: props.subtitles || DEFAULT_SUBTITLES,
    },
  };
};

const calculateAnimeMetadata: CalculateMetadataFunction<AnimeEduReelProps> = async ({
  props,
}) => {
  const chunks = props.subtitles?.chunks || DEFAULT_SUBTITLES.chunks;
  const lastChunk = chunks[chunks.length - 1];
  const audioDurationSec = lastChunk ? lastChunk.end + 0.6 : 15.0;
  const computedFrames = Math.ceil(audioDurationSec * 30);

  return {
    durationInFrames: computedFrames > 0 ? computedFrames : 462,
    props: {
      ...props,
      subtitles: props.subtitles || DEFAULT_SUBTITLES,
    },
  };
};

const calculateDinerMetadata: CalculateMetadataFunction<DinerAgentReelProps> = async ({
  props,
}) => {
  const subs = props.subtitles || (DEFAULT_SUBTITLES as any);
  const chunks = subs?.chunks || [];
  const turns = subs?.turns || [];
  let audioDurationSec = 15.0;
  if (turns.length > 0) {
    audioDurationSec = turns[turns.length - 1].end + 0.6;
  } else if (chunks.length > 0) {
    audioDurationSec = chunks[chunks.length - 1].end + 0.6;
  }
  const computedFrames = Math.ceil(audioDurationSec * 30);

  return {
    durationInFrames: computedFrames > 0 ? computedFrames : 450,
    props: {
      ...props,
      subtitles: subs,
    },
  };
};

const calculateThreeWayMetadata: CalculateMetadataFunction<ThreeWayComparisonReelProps> = async ({
  props,
}) => {
  const subs = props.subtitles || (DEFAULT_SUBTITLES as any);
  const chunks = subs?.chunks || [];
  const turns = subs?.turns || [];
  let audioDurationSec = 15.0;
  if (turns.length > 0) {
    audioDurationSec = turns[turns.length - 1].end + 0.6;
  } else if (chunks.length > 0) {
    audioDurationSec = chunks[chunks.length - 1].end + 0.6;
  }
  const computedFrames = Math.ceil(audioDurationSec * 30);

  return {
    durationInFrames: computedFrames > 0 ? computedFrames : 450,
    props: {
      ...props,
      subtitles: subs,
      audioEnvelope: (props as any).audioEnvelope || [],
    },
  };
};

const calculateMasterMetadata: CalculateMetadataFunction<MasterAutonomousReelProps> = async ({
  props,
}) => {
  const subs = props.subtitles || (DEFAULT_SUBTITLES as any);
  const chunks = subs?.chunks || [];
  const turns = subs?.turns || [];
  let audioDurationSec = 15.0;
  if (turns.length > 0) {
    audioDurationSec = turns[turns.length - 1].end + 0.6;
  } else if (chunks.length > 0) {
    audioDurationSec = chunks[chunks.length - 1].end + 0.6;
  }
  const computedFrames = Math.ceil(audioDurationSec * 30);

  return {
    durationInFrames: computedFrames > 0 ? computedFrames : 450,
    props: {
      ...props,
      subtitles: subs,
    },
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 
        Official EduReel Composition (9:16 Instagram Reel & YouTube Short)
        Dimensions: 1080 x 1920, 30fps
      */}
      <Composition
        id="EduReel"
        component={EduReel}
        durationInFrames={462}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateEduMetadata}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES,
          audioSrc: "voice.mp3",
          title: "Gravitational Time Dilation",
        }}
      />

      {/* 
        Anime Educational Reel Composition (Shonen/Jujutsu/DragonBall Science)
        Dimensions: 1080 x 1920, 30fps
      */}
      <Composition
        id="AnimeEduReel"
        component={AnimeEduReel}
        durationInFrames={462}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateAnimeMetadata}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES,
          audioSrc: "voice.mp3",
          title: "Gojo's Infinity Explained by Calculus",
          kanji: "領域展開",
        }}
      />

      {/* 
        Funny / Meme Viral Reel Composition
        High-energy physics and humor breakdown
      */}
      <Composition
        id="FunnyReel"
        component={FunnyReel}
        durationInFrames={360}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES,
          audioSrc: "voice.mp3",
          topic: "Why Your Brain Reminds You of Cringe at 3 AM",
        }}
      />

      {/* 
        Universal Dynamic Script Explainer
        Accepts any topic, script, and auto-generates scenes
      */}
      <Composition
        id="UniversalReel"
        component={UniversalReel}
        durationInFrames={462}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: "Universal Science Breakdown",
          tag: "DID YOU KNOW?",
          subtitles: DEFAULT_SUBTITLES,
          audioSrc: "voice.mp3",
          accentColor: "#00F0FF",
        }}
      />

      {/* 
        Viral Late-Night Diner Dialogue Reel (Human + Antigravity Bot)
        Reference: Instagram Viral Reel with Dual Speakers & Explainer UI Card
        Dimensions: 1080 x 1920, 30fps
      */}
      <Composition
        id="DinerAgentReel"
        component={DinerAgentReel}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateDinerMetadata}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES as any,
          audioSrc: "voice.mp3",
          title: "Antigravity & Gemini Setup",
        }}
      />

      {/* 
        3D Multi-Character Comparison Reel (Junior Dev vs Rival Dev vs Antigravity Bot)
        Features 3D low-poly faceted characters, floating 3D comparison card, and studio audio
        Dimensions: 1080 x 1920, 30fps
      */}
      <Composition
        id="ThreeWayComparisonReel"
        component={ThreeWayComparisonReel}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateThreeWayMetadata}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES as any,
          audioSrc: "voice.mp3",
          title: "Claude vs Google Antigravity",
        }}
      />

      {/* 
        Master Autonomous Reel Composition (AI vs Humans / Multi-Character / Dynamic Backgrounds & Props)
        Full 2.5D Animated Vector Pipeline with dynamic weather, coffee mug, screens, and ragebait zoom camera
        Dimensions: 1080 x 1920, 30fps
      */}
      <Composition
        id="MasterAutonomousReel"
        component={MasterAutonomousReel}
        durationInFrames={450}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calculateMasterMetadata}
        defaultProps={{
          subtitles: DEFAULT_SUBTITLES as any,
          audioSrc: "voice.mp3",
          environment: "diner",
          weather: "raining",
        }}
      />

      <Composition
        id="TestThree"
        component={TestThree}
        durationInFrames={30}
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
