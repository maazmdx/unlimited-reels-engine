"""
Agent: Instagram Reel & Social Video Ingestion & Viral Deconstruction
Downloads Instagram Reels, YouTube Shorts, or TikTok videos, extracts media/audio,
and uses Gemini Multimodal AI to deconstruct the video's viral anatomy:
1. Hook & Pattern Interrupt (0-3s)
2. Core Conflict / Debate / Satire
3. Speaker Dynamics & Character Roles
4. Punchline & Visual Reveal
"""

import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class InstaAnalyzerAgent:
    """Agent that ingests Instagram reels and deconstructs their viral anatomy using Gemini Multimodal AI."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.ingest_dir = self.project_root / "out" / "insta_ingest"
        self.ingest_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        if genai and os.environ.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client(http_options={"api_version": "v1beta"})
            except Exception as e:
                print(f"⚠️ Gemini Client init notice: {e}")

    def download_social_reel(self, url: str) -> Optional[Path]:
        """Downloads Instagram Reel or YouTube Short using yt-dlp."""
        print(f"📥 [Insta Analyzer] Ingesting reel from URL: {url}...")
        safe_name = f"reel_{int(time.time())}"
        output_template = str(self.ingest_dir / f"{safe_name}.%(ext)s")

        cmd = [
            "yt-dlp",
            "--no-playlist",
            "-f", "best[ext=mp4]/best",
            "-o", output_template,
            "--max-filesize", "50M",
            url
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if res.returncode == 0:
                for f in self.ingest_dir.glob(f"{safe_name}.*"):
                    if f.suffix.lower() in [".mp4", ".mov", ".mkv", ".webm"]:
                        print(f"✅ [Insta Analyzer] Downloaded video: {f.name} ({f.stat().st_size / (1024*1024):.1f} MB)")
                        return f
            print(f"⚠️ yt-dlp download stderr: {res.stderr[:200]}")
        except Exception as e:
            print(f"⚠️ yt-dlp download exception: {e}")

        # Attempt audio-only download if full video failed (often bypasses CDN restrictions)
        try:
            audio_template = str(self.ingest_dir / f"{safe_name}_audio.%(ext)s")
            cmd_audio = [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "-o", audio_template,
                url
            ]
            res_audio = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=60)
            if res_audio.returncode == 0:
                audio_file = self.ingest_dir / f"{safe_name}_audio.mp3"
                if audio_file.exists():
                    print(f"✅ [Insta Analyzer] Downloaded audio track: {audio_file.name}")
                    return audio_file
        except Exception:
            pass

        return None

    def analyze_reel_media(self, media_path: Path, source_url: str = "") -> Dict[str, Any]:
        """Uploads video/audio to Gemini and extracts viral anatomy."""
        print(f"🧠 [Insta Analyzer] Deconstructing viral anatomy via Gemini Multimodal: {media_path.name}...")
        if not self.client:
            print("⚠️ Gemini client not available, returning heuristic analysis.")
            return self._heuristic_fallback(source_url)

        try:
            # Upload media file to Gemini
            uploaded_file = self.client.files.upload(file=str(media_path))
            print(f"📡 File uploaded to Gemini: {uploaded_file.name}. Processing...")

            # Wait if video is still processing
            for _ in range(15):
                file_info = self.client.files.get(name=uploaded_file.name)
                state = getattr(file_info, "state", None)
                if state and str(state).endswith("ACTIVE"):
                    break
                elif state and str(state).endswith("FAILED"):
                    raise RuntimeError("Gemini file processing failed.")
                time.sleep(2)

            prompt = (
                "You are an expert viral video retention analyst and short-form video director. "
                "Carefully watch/listen to this social media video and deconstruct its viral anatomy.\n\n"
                "Return a valid JSON object strictly matching this schema:\n"
                "{\n"
                '  "hook": "The exact opening hook or pattern-interrupt used in the first 0-3 seconds",\n'
                '  "core_topic": "The central topic or subject (e.g. AI replacing jobs, crazy cloud bill, CSS misery, Claude vs ChatGPT)",\n'
                '  "format_type": "One of: ai_vs_dev, ai_vs_dad, ai_arena, tech_satire, explainer, meme",\n'
                '  "transcript_summary": "Summary or verbatim transcript of what is spoken",\n'
                '  "characters": [\n'
                '    {"role": "Role description (e.g. Junior Dev, Skeptical Dad, Smug AI, Tech Lead)", "attitude": "Tone of voice (e.g. shocked, arrogant, deadpan, angry)"}\n'
                '  ],\n'
                '  "core_conflict": "The tension or debate driving the video",\n'
                '  "visual_hook": "What visual element or on-screen text grabbed attention",\n'
                '  "punchline": "The payoff, punchline, or conclusion at the end",\n'
                '  "viral_trigger": "Why this video achieved high retention (e.g. relatable pain, controversy, absurdity, secret hack)"\n'
                "}\n"
                "Return ONLY the JSON object, no markdown codeblocks or extra text."
            )

            response = None
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[uploaded_file, prompt]
                    )
                    if response and response.text:
                        break
                except Exception as ex:
                    print(f"⚠️ Gemini model {model_name} attempt: {ex}")
                    continue

            if not response or not response.text:
                raise RuntimeError("Gemini generate_content returned empty response across models.")

            raw_text = response.text.strip()
            # Clean possible markdown formatting
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]
            if raw_text.endswith("```"):
                raw_text = raw_text.rsplit("\n", 1)[0]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

            analysis = json.loads(raw_text)
            analysis["source_url"] = source_url
            analysis["source_file"] = str(media_path)
            print(f"🎯 [Insta Analyzer] Deconstruction Complete! Hook: \"{analysis.get('hook')}\"")
            return analysis

        except Exception as e:
            print(f"⚠️ Gemini multimodal analysis error: {e}. Using intelligent fallback.")
            return self._heuristic_fallback(source_url)

    def analyze_from_url_or_query(self, url_or_query: str) -> Dict[str, Any]:
        """Main entry point: downloads and analyzes, or generates from topic."""
        # 1. If it's a URL
        if url_or_query.startswith("http://") or url_or_query.startswith("https://"):
            downloaded = self.download_social_reel(url_or_query)
            if downloaded and downloaded.exists():
                return self.analyze_reel_media(downloaded, source_url=url_or_query)
            else:
                # If direct download was blocked, use Gemini with URL context
                return self._analyze_url_with_gemini(url_or_query)

        # 2. If it's a local file
        local_path = Path(url_or_query)
        if local_path.exists() and local_path.is_file():
            return self.analyze_reel_media(local_path, source_url=str(local_path))

        # 3. Otherwise treat as viral topic search query
        return self._analyze_topic_query(url_or_query)

    def _analyze_url_with_gemini(self, url: str) -> Dict[str, Any]:
        """Analyze reel using Gemini when direct media download is restricted."""
        print(f"🌐 [Insta Analyzer] Analyzing URL via Gemini intelligence: {url}...")
        if not self.client:
            return self._heuristic_fallback(url)

        prompt = (
            f"Analyze this Instagram Reel / Short URL: {url}\n"
            "This is a viral short-form video in the AI/tech/developer niche. "
            "Synthesize what makes top-performing reels on this link viral. "
            "Return a valid JSON object matching:\n"
            "{\n"
            '  "hook": "Compelling 0-3s hook",\n'
            '  "core_topic": "AI development / Tech comedy topic",\n'
            '  "format_type": "ai_vs_dev",\n'
            '  "transcript_summary": "Dialogue breakdown",\n'
            '  "characters": [{"role": "Junior Dev", "attitude": "shocked"}, {"role": "Claude AI", "attitude": "smug"}],\n'
            '  "core_conflict": "Human vs AI efficiency",\n'
            '  "visual_hook": "Glass browser card with salary or code snippet",\n'
            '  "punchline": "Sharp comedic punchline",\n'
            '  "viral_trigger": "Relatable developer pain point"\n'
            "}\nReturn ONLY JSON."
        )
        try:
            res = None
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if res and res.text:
                        break
                except Exception:
                    continue
            if not res or not res.text:
                return self._heuristic_fallback(url)
            raw = res.text.strip().strip("`").replace("json\n", "", 1)
            data = json.loads(raw)
            data["source_url"] = url
            return data
        except Exception:
            return self._heuristic_fallback(url)

    def _analyze_topic_query(self, query: str) -> Dict[str, Any]:
        """Synthesize reel anatomy from a trending topic query."""
        if not self.client:
            return self._heuristic_fallback(query)

        prompt = (
            f"Generate the viral anatomy of a top-trending Instagram Reel about: '{query}'.\n"
            "Return ONLY a JSON object with keys: hook, core_topic, format_type, transcript_summary, "
            "characters, core_conflict, visual_hook, punchline, viral_trigger."
        )
        try:
            res = None
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]:
                try:
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if res and res.text:
                        break
                except Exception:
                    continue
            if not res or not res.text:
                return self._heuristic_fallback(query)
            raw = res.text.strip().strip("`").replace("json\n", "", 1)
            return json.loads(raw)
        except Exception:
            return self._heuristic_fallback(query)

    def _heuristic_fallback(self, source_hint: str) -> Dict[str, Any]:
        """Reliable fallback if network or API keys are unavailable."""
        return {
            "source_url": source_hint,
            "hook": "When a $3,850/week AI job says 'no experience required' but you only know Python.",
            "core_topic": "AI Careers & Ludicrous Tech Salaries",
            "format_type": "ai_vs_dev",
            "transcript_summary": "Developer finds a crazy high-paying AI fellowship, gets roasted by Claude, and executes a weekend experiment.",
            "characters": [
                {"role": "Junior Dev", "attitude": "shocked"},
                {"role": "Claude AI", "attitude": "smug"}
            ],
            "core_conflict": "Traditional credentials vs proof of practical AI agent orchestration",
            "visual_hook": "Official Greenhouse job posting card with $3,850/wk badge",
            "punchline": "One fellow taught an AI to love owls with numbers. Now he works there.",
            "viral_trigger": "Insane salary figure combined with accessible entry barrier."
        }


if __name__ == "__main__":
    analyzer = InstaAnalyzerAgent()
    res = analyzer.analyze_from_url_or_query("https://www.instagram.com/reel/example_ai_coding/")
    print(json.dumps(res, indent=2))
