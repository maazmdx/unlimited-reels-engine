"""
HookMasterAgent (Master Agent 2: 0-3s Retention & Meme Screenplay Specialist)
Executes a 2-step craft pass via Gemini 2.5 Flash:
1. Hook Battle: Writes 3 competing 0-3s hooks (<= 10 words each) across Curiosity Gap,
   Contrarian Callout, and Relatable Shock; scores each and crowns the #1 scroll-stopper.
2. Screenplay: Writes a tight 6-7 turn dialogue (22-26s, <= 13 words/turn) strictly between
   left_character and right_character with dry wit, concrete metrics, upper-third proof card
   at Turn 3 (4.0s duration), and spoken Auto-DM CTA on the final turn.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.dns_utils import enable_fast_dns
enable_fast_dns()

try:
    from google import genai
except ImportError:
    genai = None


class HookMasterAgent:
    """
    Master Agent 2: Specializes in 0-3s retention hooks and high-engagement
    short-form Remotion screenplays.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        gemini_api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.timeout = timeout
        self.headers = {"User-Agent": "AntigravityHookMaster/3.0"}

        self.api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 30000},
                )
            except Exception as e:
                print(f"⚠️ HookMaster: Gemini client init notice: {e}")

    # =========================================================================
    # INTERNAL GEMINI CALLER
    # =========================================================================

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini 2.5 Flash with fallback to fast free-tier models and direct REST."""
        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

        if self.client:
            for m in models:
                try:
                    res = self.client.models.generate_content(
                        model=m,
                        contents=[prompt],
                        config=dict(
                            system_instruction=system_instruction,
                            temperature=0.7,
                            response_mime_type="application/json",
                        ),
                    )
                    if res and res.text:
                        return res.text
                except Exception as e:
                    print(f"⚠️ HookMaster: GenAI {m} warning: {e}")

        if self.api_key:
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"},
                }
                try:
                    r = requests.post(url, json=payload, headers=self.headers, timeout=25.0)
                    if r.status_code == 200:
                        parts = r.json().get("candidates", [])[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text")
                except Exception as e:
                    print(f"⚠️ HookMaster: REST {m} warning: {e}")

        return None

    # =========================================================================
    # STEP A: HOOK BATTLE (3 Competing Hooks Scored)
    # =========================================================================

    def conduct_hook_battle(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates 3 competing opening hooks (<= 10 words, zero filler intros)
        across 3 psychological angles, scores them (0-100), and crowns the winner.
        """
        title = topic.get("title") or topic.get("topic_title")
        category = topic.get("category", "Tech")
        conflict = topic.get("core_conflict", "Curiosity vs reality")
        kw = topic.get("auto_dm_keyword", "LINK")

        system_instruction = (
            "You are HookMaster: The World's Foremost 0-3s Short-Form Video Retention Scientist.\n"
            "Your motto: The first 3 seconds decide if 100,000 people watch or swipe away.\n"
            "Rules for viral hooks:\n"
            "- MAXIMUM 10 WORDS. Zero exceptions.\n"
            "- ZERO FILLER: Never start with 'Hey guys', 'Did you know', 'Check this out', 'So today'.\n"
            "- INSTANT CURIOSITY GAP or CONTRARIAN CALLOUT.\n"
            "You must write and score 3 distinct hooks:\n"
            "1. 'curiosity_gap': Teases a shocking capability, hidden secret, or zero-dollar workaround.\n"
            "2. 'contrarian_callout': Calls out overpaying for SaaS, corporate hype vs reality, or broken norms.\n"
            "3. 'relatable_shock': Generational shock, developer panic, or extreme disbelief."
        )

        prompt = f"""
Topic: {title}
Category: {category}
Core Conflict: {conflict}
Auto-DM Keyword: {kw}

TASK:
Write 3 competing opening hooks (each <= 10 words).
Score each hook from 0 to 100 on thumb-stopping power, and explain why one won.

JSON Schema:
{{
  "hooks": [
    {{
      "type": "curiosity_gap",
      "hook": "Full hook line max 10 words",
      "score": 94,
      "critique": "Why this creates an irresistible information gap"
    }},
    {{
      "type": "contrarian_callout",
      "hook": "Full hook line max 10 words",
      "score": 88,
      "critique": "Why this challenges mainstream assumptions"
    }},
    {{
      "type": "relatable_shock",
      "hook": "Full hook line max 10 words",
      "score": 85,
      "critique": "Why this triggers instant comedic recognition"
    }}
  ],
  "winning_index": 0,
  "winning_hook": "The highest scoring hook line",
  "selection_rationale": "Why this specific hook maximizes 0-3s retention"
}}
"""

        raw_json = self._call_gemini_api(prompt, system_instruction)
        if raw_json:
            try:
                cleaned = raw_json.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                    cleaned = re.sub(r"\n```$", "", cleaned)
                parsed = json.loads(cleaned.strip())
                if "winning_hook" in parsed:
                    return parsed
            except Exception as e:
                print(f"⚠️ HookMaster: Hook battle parse error: {e}")

        # Deterministic fallback battle
        fallback_h1 = f"You can play full {title[:25]} directly in Chrome."
        fallback_h2 = f"Stop paying monthly subscriptions for {title[:20]}."
        fallback_h3 = f"Why is nobody talking about {title[:25]}?"
        return {
            "hooks": [
                {"type": "curiosity_gap", "hook": fallback_h1, "score": 92, "critique": "High direct utility"},
                {"type": "contrarian_callout", "hook": fallback_h2, "score": 86, "critique": "Money-saving angle"},
                {"type": "relatable_shock", "hook": fallback_h3, "score": 82, "critique": "Curiosity trigger"},
            ],
            "winning_index": 0,
            "winning_hook": fallback_h1,
            "selection_rationale": "Direct curiosity and tangible utility in under 9 words.",
        }

    # =========================================================================
    # STEP B: TIGHT MEME SCREENPLAY (6-7 Turns, Proof Card, Spoken CTA)
    # =========================================================================

    def craft_screenplay(
        self,
        topic: Dict[str, Any],
        hook_battle_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Writes a tight 6-7 turn dialogue (22-26s, <= 13 words/turn) strictly between
        left_character and right_character.
        Turn 0 uses winning_hook.
        Turn 3 triggers upper-third cardData for 4.0s.
        Final turn ends with spoken CTA: 'Comment [KEYWORD] and I'll DM you the link.'
        """
        title = topic.get("title") or topic.get("topic_title")
        left_char = topic.get("left_character", "junior_dev")
        right_char = topic.get("right_character", "claude")
        scene_preset = topic.get("scene_preset", "diner")
        kw = str(topic.get("auto_dm_keyword", "LINK")).strip().upper()
        winning_hook = hook_battle_result.get("winning_hook", f"Look at {title}.")
        category = topic.get("category", "Tech")

        system_instruction = (
            "You are HookMaster: Screenplay & Dialogue Specialist for 9:16 vertical 3D reels.\n"
            "Your objective: Write high-retention, comedic dialogue that feels authentic, funny, and informative.\n\n"
            "STRICT SCREENPLAY RULES:\n"
            "1. EXACTLY 6 TO 7 TURNS: Target duration 22-26 seconds.\n"
            "2. MAXIMUM 13 WORDS PER TURN: Keep lines snappy, rhythmic, and punchy.\n"
            "3. STRICT 2-CHARACTER ALTERNATION: Alternate strictly between left_character and right_character.\n"
            "4. DRY WIT & CONCRETE FACTS: Use specific numbers, memory stats, or dollar amounts. Never robotic fluff.\n"
            "5. UPPER-THIRD CARD TRIGGER: Exactly Turn 3 must have 'cardTrigger': true and 'cardDuration': 4.0.\n"
            "6. FINAL TURN SPOKEN CTA: Final turn MUST end naturally with spoken: 'Comment " + kw + " and I'll DM you the link.'\n"
            "7. SCENE PRESET: Keep scenePreset matching requested preset ('diner' or 'desk')."
        )

        prompt = f"""
Topic: {title}
Category: {category}
Winning Hook (Turn 0 line): "{winning_hook}"
Cast: Left={left_char}, Right={right_char}
Scene Preset: {scene_preset}
Auto-DM Keyword: {kw}

TASK:
Write the complete Remotion screenplay JSON with exactly 6 snappy dialogue turns.
Turn 0 MUST be {left_char} speaking the winning hook.
Turn 3 MUST trigger the proof card (`cardTrigger`: true, `cardDuration`: 4.0).
Turn 5 (Final Turn) MUST be {right_char} delivering the punchline and closing with:
"Comment {kw} and I'll DM you the link."

JSON Schema:
{{
  "title": "{title[:50]}",
  "style": "{scene_preset}",
  "comp": "MasterAutonomousReel",
  "scenePreset": "{scene_preset}",
  "leftCharacterId": "{left_char}",
  "rightCharacterId": "{right_char}",
  "cast": {{
    "left": "{left_char}",
    "right": "{right_char}"
  }},
  "cta_keyword": "{kw}",
  "cta_phrase": "Comment {kw} and I'll DM you the link.",
  "cardType": "comparison",
  "badge": "VERIFIED PROOF",
  "explainerTitle": "Proof Card Title",
  "cardData": {{
    "point_1": "Concrete metric or comparison",
    "point_2": "Crucial technical detail",
    "point_3": "The surprising reality"
  }},
  "hook": {{
    "headline": "{title.upper()[:35]}",
    "subheadline": "{winning_hook}",
    "tag": "⚠️ VIRAL REAL TALK"
  }},
  "dialogue": [
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Snappy response <= 13 words", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Comedic comeback <= 13 words", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Proof reveal <= 13 words", "emotion": "smug", "cardTrigger": true, "cardDuration": 4.0, "pause_after": 0.40}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Realization or reaction <= 13 words", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Punchline. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40}}
  ]
}}
"""

        raw_json = self._call_gemini_api(prompt, system_instruction)
        screenplay = None
        if raw_json:
            try:
                cleaned = raw_json.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                    cleaned = re.sub(r"\n```$", "", cleaned)
                parsed = json.loads(cleaned.strip())
                if "dialogue" in parsed and len(parsed["dialogue"]) >= 5:
                    screenplay = parsed
            except Exception as e:
                print(f"⚠️ HookMaster: Screenplay parse error: {e}")

        if not screenplay:
            screenplay = self._fallback_screenplay(topic, winning_hook, left_char, right_char, scene_preset, kw)

        # Enforce guarantees
        screenplay["leftCharacterId"] = left_char
        screenplay["rightCharacterId"] = right_char
        screenplay["cast"] = {"left": left_char, "right": right_char}
        screenplay["scenePreset"] = scene_preset
        screenplay["style"] = scene_preset
        screenplay["cta_keyword"] = kw
        screenplay["ctaKeyword"] = kw
        screenplay["cta_phrase"] = f"Comment {kw} and I'll DM you the link."
        screenplay["cta_text"] = f"💬 Comment {kw} for the link"
        screenplay["ctaText"] = f"💬 Comment {kw} for the link"

        # Attach metadata
        screenplay["hook_battle"] = hook_battle_result
        screenplay["winning_hook"] = winning_hook
        screenplay["viral_score"] = topic.get("viral_score", 85)
        screenplay["category"] = topic.get("category", "Tech")

        return screenplay

    def _fallback_screenplay(
        self,
        topic: Dict[str, Any],
        hook: str,
        left_char: str,
        right_char: str,
        scene_preset: str,
        kw: str,
    ) -> Dict[str, Any]:
        """Deterministic broadcast-grade fallback screenplay."""
        title = topic.get("title", "Daily Tech Breakdown")
        return {
            "title": title[:50],
            "style": scene_preset,
            "comp": "MasterAutonomousReel",
            "scenePreset": scene_preset,
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": kw,
            "cta_phrase": f"Comment {kw} and I'll DM you the link.",
            "cardType": "comparison",
            "badge": "VERIFIED PROOF",
            "explainerTitle": f"{title[:25]} Breakdown",
            "cardData": {
                "metric_1": "100% Free WebAssembly Port",
                "metric_2": "Zero installation needed",
                "metric_3": "Runs smoothly in Google Chrome",
            },
            "hook": {
                "headline": title.upper()[:35],
                "subheadline": hook,
                "tag": "⚠️ REAL TALK",
            },
            "dialogue": [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "It is live right now with zero downloads.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Is this actually playable or just Twitter hype?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Look at the numbers on screen.", "emotion": "smug", "cardTrigger": True, "cardDuration": 4.0, "pause_after": 0.40},
                {"speaker": left_char, "character_id": left_char, "text": "My laptop struggles with Slack but runs this fine.", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": f"Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
            ],
        }

    # =========================================================================
    # PUBLIC METHOD: END-TO-END 2-STEP CRAFT PASS
    # =========================================================================

    def craft_reel_screenplay(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full 2-step craft pass:
        1. Hook Battle (3 competing hooks scored -> 1 winner)
        2. Screenplay (6 turns dialogue, proof card, spoken CTA)
        """
        print(f"\n⚡ [HookMaster] Initiating Hook Battle for topic: '{topic.get('title')}'...")
        battle = self.conduct_hook_battle(topic)
        winning_hook = battle.get("winning_hook")
        print(f"🥇 [HookMaster] Winner crowned: \"{winning_hook}\"")
        for h in battle.get("hooks", []):
            print(f"   • [{h.get('type')}] Score {h.get('score')}: \"{h.get('hook')}\"")

        print(f"✍️ [HookMaster] Writing 6-turn tight Remotion screenplay...")
        screenplay = self.craft_screenplay(topic, battle)
        print(f"🎬 [HookMaster] Screenplay ready! (Turns: {len(screenplay.get('dialogue', []))}, Preset: {screenplay.get('scenePreset')}, Cast: {screenplay['leftCharacterId']}&{screenplay['rightCharacterId']})")
        return screenplay


if __name__ == "__main__":
    hm = HookMasterAgent()
    sample_topic = {
        "title": "Developer builds complete Intel 486 PC emulator in browser",
        "category": "Retro & Browser Games",
        "auto_dm_keyword": "RETRO",
        "left_character": "junior_dev",
        "right_character": "claude",
        "scene_preset": "desk",
        "core_conflict": "Dev nostalgia vs JavaScript V8 emulator performance",
    }
    screenplay = hm.craft_reel_screenplay(sample_topic)
    print("\n--- HookMaster Output ---")
    print(json.dumps(screenplay, indent=2))
