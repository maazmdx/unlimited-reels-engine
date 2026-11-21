"""
HookMasterAgent (Master Agent 2: 0-3s Retention & Meme Screenplay Specialist)
Executes a 2-step craft pass via Gemini 2.5 Flash / 3.5 Flash:
1. Hook Battle: Writes 3 competing 0-3s hooks (<= 10 words each) across Curiosity Gap,
   Contrarian Callout, and Relatable Shock; scores each and crowns the #1 scroll-stopper.
2. Screenplay: Writes a high-retention 11-13 turn dialogue (40-52s, 8-14 words/turn) strictly between
   left_character and right_character following a 5-act viral arc with multi-step interactive proof card
   highlighted row-by-row on Turns 5-7, iOS notification toast on Turn 9, spoken Auto-DM CTA, and 2.5s black end-card.
"""

import os
import sys
import json
import re
import time
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

# Strict Vocabulary Ban (Simple Spoken English ONLY - 6th-8th Grade Level)
BANNED_WORDS = [
    "framework", "paradigm", "optimize", "optimization", "optimizing",
    "biometric", "infrastructure", "synergy", "synergies", "utilize", "utilizing",
    "collaboration", "delivers", "delivering", "latency", "ecosystem"
]

VOCABULARY_REPLACEMENTS = [
    (re.compile(r"\bframeworks?\b", re.IGNORECASE), "tools"),
    (re.compile(r"\bparadigms?\b", re.IGNORECASE), "ways"),
    (re.compile(r"\boptimizations?\b", re.IGNORECASE), "speed boosts"),
    (re.compile(r"\boptimizing\b", re.IGNORECASE), "speeding up"),
    (re.compile(r"\boptimize\b", re.IGNORECASE), "speed up"),
    (re.compile(r"\bbiometrics?\b", re.IGNORECASE), "face scan"),
    (re.compile(r"\binfrastructure\b", re.IGNORECASE), "setup"),
    (re.compile(r"\bsynerg(y|ies)\b", re.IGNORECASE), "teamwork"),
    (re.compile(r"\butilizing\b", re.IGNORECASE), "using"),
    (re.compile(r"\butilize\b", re.IGNORECASE), "use"),
    (re.compile(r"\bcollaboration\b", re.IGNORECASE), "teamwork"),
    (re.compile(r"\bdelivering\b", re.IGNORECASE), "giving"),
    (re.compile(r"\bdelivers\b", re.IGNORECASE), "gives"),
    (re.compile(r"\blatency\b", re.IGNORECASE), "delay"),
    (re.compile(r"\becosystems?\b", re.IGNORECASE), "setup"),
]


def sanitize_simple_spoken_english(text: str) -> str:
    """Replaces corporate buzzwords with simple, 6th-8th grade conversational English."""
    cleaned = text
    for pattern, repl in VOCABULARY_REPLACEMENTS:
        cleaned = pattern.sub(repl, cleaned)
    return cleaned


class HookMasterAgent:
    """
    Master Agent 2: Specializes in 0-3s retention hooks and high-engagement
    short-form Remotion screenplays.
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        gemini_api_key: Optional[str] = None,
        timeout: float = 50.0,
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
                    http_options={"api_version": "v1beta", "timeout": 50000},
                )
            except Exception as e:
                print(f"⚠️ HookMaster: Gemini client init notice: {e}")

    # =========================================================================
    # INTERNAL GEMINI CALLER
    # =========================================================================

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini with 2026 free-tier models, clean 50s timeout, 1 retry on 504/timeout, and logs model."""
        models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]

        if self.client:
            for m in models:
                for attempt in range(2):
                    t0 = time.time()
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
                            elapsed = time.time() - t0
                            print(f"✨ [HookMaster] Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(res.text)} chars).")
                            return res.text
                    except Exception as e:
                        err_str = str(e)
                        is_504 = "504" in err_str or "DEADLINE_EXCEEDED" in err_str or "timeout" in err_str.lower()
                        if is_504 and attempt == 0:
                            print(f"⚠️ HookMaster: GenAI {m} hit 504/deadline, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ HookMaster: GenAI {m} warning: {e}")
                        break

        if self.api_key:
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"},
                }
                for attempt in range(2):
                    t0 = time.time()
                    try:
                        r = requests.post(url, json=payload, headers=self.headers, timeout=50.0)
                        if r.status_code == 200:
                            parts = r.json().get("candidates", [])[0].get("content", {}).get("parts", [])
                            if parts:
                                text = parts[0].get("text")
                                elapsed = time.time() - t0
                                print(f"✨ [HookMaster] REST Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(text)} chars).")
                                return text
                        elif (r.status_code == 504 or "DEADLINE_EXCEEDED" in r.text) and attempt == 0:
                            print(f"⚠️ HookMaster: REST {m} hit 504, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        else:
                            print(f"⚠️ HookMaster: REST {m} returned {r.status_code}: {r.text[:120]}")
                            break
                    except Exception as e:
                        err_str = str(e)
                        is_timeout = "timeout" in err_str.lower() or "504" in err_str
                        if is_timeout and attempt == 0:
                            print(f"⚠️ HookMaster: REST {m} timed out, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ HookMaster: REST {m} warning: {e}")
                        break

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
            "Your motto: The first 3 seconds decide if 100,000 people watch or swipe away.\n\n"
            "STRICT VOCABULARY RULE (SIMPLE SPOKEN ENGLISH ONLY - 6th to 8th GRADE LEVEL):\n"
            "- Explicitly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem'.\n"
            "- Write in short, punchy, everyday spoken English that anyone on Instagram understands instantly.\n\n"
            "DIABOLICAL AI-ROASTS-HUMAN RAGEBAIT DYNAMIC:\n"
            "- The hook must trigger instant shock, curiosity, or call out human laziness/struggle.\n"
            "- MAXIMUM 10 WORDS. Zero exceptions.\n"
            "- ZERO FILLER: Never start with 'Hey guys', 'Did you know', 'Check this out', 'So today'.\n\n"
            "You must write and score 3 distinct hooks:\n"
            "1. 'curiosity_gap': Teases a shocking capability, hidden secret, or zero-dollar workaround.\n"
            "2. 'contrarian_callout': Calls out overpaying for software, corporate hype vs reality, or broken norms.\n"
            "3. 'relatable_shock': Roasts human struggle, broken laptops, or hilarious developer panic."
        )

        prompt = f"""
Topic: {title}
Category: {category}
Core Conflict: {conflict}
Auto-DM Keyword: {kw}

TASK:
Write 3 competing opening hooks (each <= 10 words, simple spoken English only).
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
                    # Sanitize winning hook to simple spoken English
                    parsed["winning_hook"] = sanitize_simple_spoken_english(parsed["winning_hook"])
                    for h in parsed.get("hooks", []):
                        if "hook" in h:
                            h["hook"] = sanitize_simple_spoken_english(h["hook"])
                    return parsed
            except Exception as e:
                print(f"⚠️ HookMaster: Hook battle parse error: {e}")

        # Deterministic fallback battle in simple spoken English
        cat_lower = str(category).lower() + " " + str(title).lower()
        if "game" in cat_lower or "retro" in cat_lower or "emulator" in cat_lower:
            fallback_h1 = f"Play full {title[:16]} in your browser right now."
            fallback_h2 = f"Zero downloads. Your potato laptop can run this."
            fallback_h3 = f"Why did nobody tell me about this browser trick?"
        elif "ai" in cat_lower or "llm" in cat_lower or "model" in cat_lower:
            fallback_h1 = f"This free tool replaces fifty dollar monthly software."
            fallback_h2 = f"Stop overpaying fifty dollars for useless monthly apps."
            fallback_h3 = f"How is this free tool beating paid software?"
        elif "money" in cat_lower or "business" in cat_lower or "earn" in cat_lower or "margin" in cat_lower:
            fallback_h1 = f"The secret way this free app prints billions."
            fallback_h2 = f"Their free plan is actually a genius money trap."
            fallback_h3 = f"Why every competitor went broke copying this app."
        elif "dad" in cat_lower:
            fallback_h1 = f"Your dad's craziest tech fix actually worked."
            fallback_h2 = f"Never call customer support for broken internet again."
            fallback_h3 = f"My dad fixed this in ninety seconds flat."
        else:
            fallback_h1 = f"Why is nobody talking about this free tool?"
            fallback_h2 = f"This zero-dollar tool makes old skills look prehistoric."
            fallback_h3 = f"Stop doing this by hand when this tool exists."

        return {
            "hooks": [
                {"type": "curiosity_gap", "hook": fallback_h1, "score": 93, "critique": "High curiosity and tangible utility"},
                {"type": "contrarian_callout", "hook": fallback_h2, "score": 87, "critique": "Money-saving and calling out bad habits"},
                {"type": "relatable_shock", "hook": fallback_h3, "score": 84, "critique": "Instant relatable shock"},
            ],
            "winning_index": 0,
            "winning_hook": fallback_h1,
            "selection_rationale": "Direct curiosity and tangible utility in under 9 simple words.",
        }

    # =========================================================================
    # =========================================================================
    # STEP B: 5-ACT VIRAL MEME SCREENPLAY (11-12 Turns, Multi-Step Proof Card, Toast, End-Card)
    # =========================================================================

    def craft_screenplay(
        self,
        topic: Dict[str, Any],
        hook_battle_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Writes an 11-12 turn dialogue (40-50s, 8-14 words/turn) following a strict 5-act viral arc:
        - Act 1 (Turns 0-1): Scroll-Stop Hook & Smug AI Roast
        - Act 2 (Turns 2-4): Human Denial & Brutal AI Humbling
        - Act 3 (Turns 5-7): 3-Step Interactive Proof Card (Row 1 on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7)
        - Act 4 (Turns 8-10): Human Panic & Savage iOS Notification Twist on Turn 9
        - Act 5 (Turn 11): Final Diabolical Burn + Spoken CTA + 2.5s Black End-Card Ragebait Question
        """
        title = topic.get("title") or topic.get("topic_title")
        left_char = topic.get("left_character", "junior_dev")
        right_char = topic.get("right_character", "claude")
        scene_preset = topic.get("scene_preset", "diner")
        kw = str(topic.get("auto_dm_keyword", "LINK")).strip().upper()
        winning_hook = sanitize_simple_spoken_english(hook_battle_result.get("winning_hook", f"Look at {title}."))
        category = topic.get("category", "Tech")
        is_gh = any(term in str(category).lower() or term in str(title).lower() for term in ["github", "repo", "open-source", "open source"])
        link_target = "GitHub repo link" if is_gh else "free link"
        cta_phrase = topic.get("cta_phrase") or f"Comment {kw} and I'll DM you the {link_target}."

        system_instruction = (
            "You are HookMaster: Screenplay & Dialogue Specialist for 9:16 vertical 3D dialogue reels.\n"
            "Your objective: Write high-retention 40-50 second screenplays with DIABOLICAL AI-ROASTS-HUMAN RAGEBAIT HUMOR.\n\n"
            "STRICT VOCABULARY BAN (SIMPLE SPOKEN ENGLISH ONLY - 6th to 8th GRADE LEVEL):\n"
            "- Strictly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', or any corporate/academic buzzwords.\n"
            "- Write short, punchy sentences in 100% everyday spoken English that any teenager or casual scroller understands immediately.\n\n"
            "DIABOLICAL AI-ROASTS-HUMAN DYNAMIC:\n"
            "- The AI orb (claude, gemini, or grok) acts smug, brutally honest, and effortlessly superior—roasting the human's slow speed, bad habits, potato laptop, procrastination, or overpaying for tools.\n"
            "- Roasts must be clever, savage, and funny (roast human laziness, coding struggles, procrastination, overpaying, and slow reaction time—never hateful or abusive!).\n"
            "- The human character (junior_dev or dad) defends, denies, asks dumb questions, or panics as their effort gets humbled.\n"
            "- NATURAL EXPRESSIVE CUES: Include cues like 'Wait—', '[chuckle]', '[sigh]', 'Bro...', 'Seriously?' on emotional turns so neural TTS delivers real comedic emotion.\n\n"
            "STRICT 5-ACT SCREENPLAY STRUCTURE (EXACTLY 11 TO 12 SNAPPY TURNS, 40-50 SECONDS):\n"
            "1. Turn 0 (0-4s): Call out what people are wasting money or hours on + drop the 100% free shock reveal (<= 10 words).\n"
            "2. Turns 1-4 (4-16s): Brutal roast & denial. AI ruthlessly roasts the human for still paying subscriptions, downloading 80GB bloatware, or doing slow manual work like it's 2008.\n"
            "3. Turns 5-7 (16-30s): 3-Step Interactive Proof Card. Turn 5 highlights Row 1, Turn 6 reacts to Row 2, Turn 7 delivers Row 3 (contrasting exact '$0 / 100% FREE' vs 'What you're still paying for').\n"
            "4. Turns 8-10 (30-42s): Human realization/panic + Savage iOS Notification Twist on Turn 9 (brutal personal roast toast: bank alert for wasted subscription, storage 99% full, or boss/mom catching them—ZERO Slack templates!).\n"
            "5. Final Turn (Turn 11): Final savage burn + exact spoken CTA: 'Comment " + kw + " and I'll DM you the " + link_target + ".'\n"
            "6. 2.5s BLACK END-CARD: Supply endCard question with a spicy ragebait debate question (e.g., 'Still paying for this in 2026? Be honest 💀' or 'Still downloading 80GB games on a potato laptop? 💀')."
        )

        prompt = f"""
Topic: {title}
Category: {category}
Winning Hook (Turn 0 line): "{winning_hook}"
Cast: Left={left_char}, Right={right_char}
Scene Preset: {scene_preset}
Auto-DM Keyword: {kw}

TASK:
Write the complete 5-act Remotion screenplay JSON with 11-12 snappy dialogue turns.
- Turn 0 MUST be {left_char} speaking: "{winning_hook}"
- Turns 1-4 MUST have the AI ruthlessly roast the human for overpaying, procrastination, or slow manual work.
- Turns 5, 6, 7 MUST sequentially explain and highlight Rows 1, 2, and 3 of the Proof Card (showing exact $0 / 100% FREE vs paid tools).
- Turn 9 MUST introduce the Meme Twist supported by the iOS Notification Toast (personal roast: bank alert, storage full, boss catching them—NO Slack).
- Final Turn MUST end with: "Comment {kw} and I'll DM you the {link_target}."

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
  "cta_phrase": "Comment {kw} and I'll DM you the {link_target}.",
  "cardType": "comparison",
  "badge": "VERIFIED PROOF",
  "explainerTitle": "{title[:24]} Specs",
  "cardData": {{
    "title": "{title[:24]} Breakdown",
    "subtitle": "Step-by-step verified specs",
    "badge": "VERIFIED PROOF",
    "rows": [
      {{
        "label": "Step 1: Cost",
        "value": "$0 / 100% FREE (vs $20/mo)",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 2: Setup / Speed",
        "value": "Instant In Browser (0 Installs)",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 3: Bottom Line",
        "value": "Saves 10 Hours & $240/yr",
        "status": "PROVEN",
        "isPositive": true
      }}
    ],
    "startTurn": 5,
    "endTurn": 7,
    "durationSeconds": 12.0
  }},
  "toastData": {{
    "app_name": "Bank Alert",
    "sender": "Chase / Apple Pay",
    "message": "$20/mo recurring subscription charge declined. You saved $240 this year.",
    "icon": "💳",
    "time": "now"
  }},
  "endCard": {{
    "question": "Still paying for this in 2026? Be honest 💀",
    "keyword": "{kw}",
    "cta_text": "Comment {kw} for the free link",
    "subtext": "Follow for Part 2"
  }},
  "hook": {{
    "headline": "{title.upper()[:35]}",
    "subheadline": "{winning_hook}",
    "tag": "⚠️ VIRAL REAL TALK"
  }},
  "dialogue": [
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "[chuckle] Bro, your slow workflow is finally getting humbled.", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Wait—there is no way a free app replaces four hours of work.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "[sigh] Humans love doing things the hard way just to feel busy.", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Seriously? Prove it right now before I waste another morning.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Look at step one: it boots in two seconds with zero installs.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Wait, step two says it cuts my entire workload down to seconds?", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "And step three: it runs locally so nobody charges you fifty dollars.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Bro... I have been paying monthly fees like an amateur.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Look at your screen: your coworker is already using it to beat you.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "I am opening this right now before my boss finds out.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "[chuckle] Stop crying, human. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40}}
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
                if "dialogue" in parsed and len(parsed["dialogue"]) >= 11:
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
        screenplay["cta_phrase"] = cta_phrase
        screenplay["cta_text"] = f"💬 Comment {kw} for the {link_target}"
        screenplay["ctaText"] = f"💬 Comment {kw} for the {link_target}"

        # Ensure cardData exists and has multi-step structure in simple English
        if not screenplay.get("cardData") or not isinstance(screenplay["cardData"], dict):
            screenplay["cardData"] = {}
        card_d = screenplay["cardData"]
        card_d.setdefault("title", f"{title[:24]} Breakdown")
        card_d.setdefault("subtitle", "Step-by-step verified specs")
        card_d.setdefault("badge", "VERIFIED PROOF")
        card_d.setdefault("startTurn", 5)
        card_d.setdefault("endTurn", 7)
        card_d.setdefault("durationSeconds", 12.0)
        if "rows" not in card_d or not isinstance(card_d["rows"], list) or len(card_d["rows"]) < 3:
            card_d["rows"] = [
                {"label": "Step 1: Cost", "value": "$0 / 100% FREE (vs $20/mo)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Speed", "value": "Runs 10x Faster In Seconds", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Bottom Line", "value": "Zero Monthly Fees Needed", "status": "PROVEN", "isPositive": True},
            ]
        card_d["items"] = card_d["rows"]

        # Ensure toastData exists and banish old "Slack" templates
        if not screenplay.get("toastData") or not isinstance(screenplay["toastData"], dict):
            screenplay["toastData"] = {
                "app_name": "Bank Alert",
                "sender": "Card Alert",
                "message": f"Monthly subscription declined. You saved $240 on {title[:16]}.",
                "icon": "💳",
                "time": "now",
            }
        else:
            if str(screenplay["toastData"].get("app_name", "")).lower() == "slack":
                screenplay["toastData"]["app_name"] = "Bank Alert"
            screenplay["toastData"].setdefault("app_name", "Bank Alert")
            screenplay["toastData"].setdefault("sender", "Card Alert")
            screenplay["toastData"].setdefault("message", f"Monthly fee declined. You saved $240 on {title[:16]}!")
            screenplay["toastData"].setdefault("icon", "💳")
            screenplay["toastData"].setdefault("time", "now")

        # Ensure endCard exists with ragebait question
        if not screenplay.get("endCard") or not isinstance(screenplay["endCard"], dict):
            screenplay["endCard"] = {
                "question": f"Still paying for this in 2026? Be honest 💀",
                "keyword": kw,
                "cta_text": f"Comment {kw} for the {link_target}",
                "subtext": "Follow for Part 2",
            }
        else:
            screenplay["endCard"].setdefault("question", f"Still paying for this in 2026? Be honest 💀")
            screenplay["endCard"]["keyword"] = kw
            screenplay["endCard"]["cta_text"] = f"Comment {kw} for the {link_target}"
            screenplay["endCard"].setdefault("subtext", "Follow for Part 2")

        # STRICT VOCABULARY SANITIZATION PASS: Remove all fancy/corporate words
        if "dialogue" in screenplay and isinstance(screenplay["dialogue"], list):
            for d in screenplay["dialogue"]:
                if "text" in d:
                    d["text"] = sanitize_simple_spoken_english(d["text"])

        for row in screenplay["cardData"].get("rows", []):
            if isinstance(row, dict):
                if "label" in row:
                    row["label"] = sanitize_simple_spoken_english(row["label"])
                if "value" in row:
                    row["value"] = sanitize_simple_spoken_english(row["value"])

        if "toastData" in screenplay and isinstance(screenplay["toastData"], dict):
            if "message" in screenplay["toastData"]:
                screenplay["toastData"]["message"] = sanitize_simple_spoken_english(screenplay["toastData"]["message"])

        if "endCard" in screenplay and isinstance(screenplay["endCard"], dict):
            if "question" in screenplay["endCard"]:
                screenplay["endCard"]["question"] = sanitize_simple_spoken_english(screenplay["endCard"]["question"])

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
        """Deterministic, topic-aware broadcast-grade 12-turn 5-act fallback screenplay with diabolical roast humor."""
        title = topic.get("title") or topic.get("topic_title") or "Daily Tech Breakdown"
        category = topic.get("category", "")
        cat_lower = (str(category) + " " + str(title)).lower()
        is_gh = any(term in cat_lower for term in ["repo", "github", "open-source", "open source"])
        link_desc = "GitHub repo link" if is_gh else "free link"

        if "game" in cat_lower or "retro" in cat_lower or "emulator" in cat_lower:
            badge = "BROWSER STATS"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Cost", "value": "$0 / 100% FREE In Browser", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Storage", "value": "0 MB (vs 80GB Bloatware)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Framerate", "value": "Smooth 60 FPS On Potato Laptop", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Steam",
                "sender": "Gamer Friend",
                "message": "Bro are you really running full Vice City inside Chrome at work?",
                "icon": "🎮",
                "time": "now",
            }
            end_question = "Still downloading 80GB games on a dying laptop in 2026? Drop your excuse below 👇"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] Bro... your potato laptop can finally run a game without smoking.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—there is no way a full 3D game runs inside a tab.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] It compiles straight to your browser. Your Chrome tab is now a console.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Prove it right now before I open this at my desk.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: 100% free with zero file downloads.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two says zero megabytes instead of eighty gigabytes?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "And step three: locked sixty frames per second on your broken laptop.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... my boss thinks I am typing code while I am driving.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Check your screen: your teammate just messaged asking for your screen share.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, close the tab before he catches Tommy Vercetti on screen!", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] Too slow, human. Comment {kw} and I'll DM you the free link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif is_gh:
            badge = "FREE GITHUB REPO"
            card_title = f"{title[:22]} Repo"
            rows = [
                {"label": "Step 1: Cost", "value": "$0 / 100% Free Open Source", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Speed", "value": "Zero Cloud Lag / Fast Local", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Privacy", "value": "100% Local / Zero Tracking", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "GitHub",
                "sender": "Repo Star",
                "message": "Saved $240/yr replacing paid SaaS with this open-source repo.",
                "icon": "⭐",
                "time": "now",
            }
            end_question = "Still paying $20/mo subscriptions when free GitHub repos exist? Tell me why 👇"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] Humans pay twenty bucks a month for what a free GitHub repo does in two seconds.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—there is no way an open-source project replaces my paid subscription!", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] It has thirty thousand stars because it crushes the paid version without charging you a dime.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Prove it right now before I cancel my credit card.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: one hundred percent free open-source code with zero hidden fees.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two runs straight on my laptop with zero cloud delays?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: complete privacy with zero monthly subscriptions draining your account.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... I wasted hundreds of dollars paying software companies like a clown.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Check your phone: your bank alert for another useless renewal is waiting.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am deleting my paid account and starring this repo immediately.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] Finally woke up, human. Comment {kw} and I'll DM you the GitHub repo link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "ai" in cat_lower or "llm" in cat_lower or "model" in cat_lower:
            badge = "AI COST AUDIT"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Cost", "value": "$0 / 100% FREE (vs $20/mo)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Setup", "value": "Instant In Browser (0 Credit Cards)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Speed", "value": "Done In 2 Seconds (Saves 4 Hours)", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Bank of America",
                "sender": "Card Alert",
                "message": "Monthly $20 AI tool charge declined. You saved $240 this year.",
                "icon": "💳",
                "time": "now",
            }
            end_question = "Still paying $20/mo for AI in 2026? Be honest 💀"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] And you spent six months paying for tools you barely use.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—every free tool is usually completely broken garbage that hallucinates.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] Keep coping. This runs straight on your machine and beats paid apps.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Prove it before I cancel my fifty dollar monthly subscription.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: completely free with zero shady credit card traps.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two says zero credit card needed forever?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "And step three: finishes your four hour task in two seconds flat.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... I literally wasted hundreds of dollars doing everything by hand.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at your phone: your bank app just cheered for your wallet.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "My credit card bill feels personally attacked right now.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] Stop crying, human. Comment {kw} and I'll DM you the free link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "money" in cat_lower or "business" in cat_lower or "earn" in cat_lower or "margin" in cat_lower:
            badge = "PROFIT TEARDOWN"
            card_title = f"{title[:22]} Economics"
            rows = [
                {"label": "Step 1: Free Tier", "value": "$0 / 100% FREE For Normal Users", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Enterprise", "value": "Charges Companies $20,000", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: User Cost", "value": "$0 Forever If You Know This", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Stripe",
                "sender": "Billing Alert",
                "message": "New $20,000 team plan bought because free users shared the tool.",
                "icon": "💰",
                "time": "now",
            }
            end_question = "Did you think this app was free or did you just realize you're the product? 💀"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] You really thought they gave that away out of pure kindness?", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—if the entire app is free, how are they swimming in money?", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] You are the free bait they use to sell massive team contracts.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Break down the math before I believe they outsmarted everyone.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: normal users get 100% free access forever.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two shows huge profits the second a company signs up?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: they print hundreds of millions while you pay zero dollars.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... I was basically an unpaid salesperson and I had no idea.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Check your phone: a billing alert just proved my point completely.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am never looking at a free software download the same way.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] At least you learned today. Comment {kw} and I'll DM you the free link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "dad" in cat_lower:
            badge = "VERIFIED FIX"
            card_title = f"{title[:22]} Fix"
            rows = [
                {"label": "Step 1: Cost", "value": "$0 / 100% FREE (vs $100 Tech Fee)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Speed", "value": "Solved In Under 90 Seconds", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Reliability", "value": "Zero Drops Or Buffering All Week", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "WhatsApp",
                "sender": "Dad",
                "message": "Wi-Fi is blazing fast! I told you hitting the box works.",
                "icon": "👨‍👧",
                "time": "now",
            }
            end_question = "Would you trust your dad to fix your Wi-Fi or pay $100 for a technician? 😂👇"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] Your dad hit the plastic box with his shoe, didn't he?", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—he restarted the modem twelve times and wrapped antennas in foil!", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] Humans will wrap gadgets in foil before changing one simple free setting.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Show me the real fix before he takes apart the TV.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: 100% free with zero replacement junk.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two says changing this free address fixes it in seconds?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: rock solid connection with zero buffering all week long.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... he spent four hours yelling at customer support yesterday.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at your messages: your dad is already bragging that he fixed it.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "He is going to bring this up at every family dinner forever.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] Let him have his win. Comment {kw} and I'll DM you the free link.", "emotion": "smug", "pause_after": 0.40},
            ]
        else:
            badge = "TECH TEARDOWN"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Cost", "value": "$0 / 100% FREE (vs $50/mo)", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Speed", "value": "Runs Instantly With Zero Bloat", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Speedup", "value": "10x Faster Than Old School Ways", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Chrome",
                "sender": "Speed Alert",
                "message": "Task finished in 1.4 seconds. What took you 4 hours?",
                "icon": "⚡",
                "time": "now",
            }
            end_question = "Still paying for outdated tools in 2026? Drop your excuse below 👇"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[chuckle] Humans spend four years learning what takes two clicks now.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Wait—there is no way a free tool replaces years of hard practice.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "[sigh] People said the exact same thing about horses before cars showed up.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Seriously? Check the numbers before I throw away my entire degree.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at step one: 100% free right in your browser.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two shows instant execution with zero complicated setup?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "And step three: ten times faster than the bloated tools you use.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Bro... I feel like I just worked five years for nothing.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Check your screen: your browser just finished before you even started typing.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am grabbing this immediately before my coworker replaces me.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"[chuckle] Don't panic, human. Comment {kw} and I'll DM you the free link.", "emotion": "smug", "pause_after": 0.40},
            ]

        card_data = {
            "title": card_title,
            "subtitle": f"{title[:28]} Breakdown",
            "badge": badge,
            "rows": rows,
            "items": rows,
            "startTurn": 5,
            "endTurn": 7,
            "durationSeconds": 12.0,
        }

        end_card = {
            "question": end_question,
            "keyword": kw,
            "cta_text": f"Comment {kw} for the {link_desc}",
            "subtext": "Follow for Part 2",
        }

        return {
            "title": title[:50],
            "style": scene_preset,
            "comp": "MasterAutonomousReel",
            "scenePreset": scene_preset,
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": kw,
            "cta_phrase": f"Comment {kw} and I'll DM you the {link_desc}.",
            "cardType": "comparison",
            "badge": badge,
            "explainerTitle": card_title,
            "cardData": card_data,
            "toastData": toast,
            "endCard": end_card,
            "hook": {
                "headline": title.upper()[:35],
                "subheadline": hook,
                "tag": "⚠️ REAL TALK",
            },
            "dialogue": dialogue,
        }

    # =========================================================================
    # PUBLIC METHOD: END-TO-END 2-STEP CRAFT PASS
    # =========================================================================

    def craft_reel_screenplay(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full 2-step craft pass:
        1. Hook Battle (3 competing hooks scored -> 1 winner)
        2. Screenplay (11-13 turns 5-act viral dialogue, multi-step card, toast, end-card)
        """
        print(f"\n⚡ [HookMaster] Initiating Hook Battle for topic: '{topic.get('title')}'...")
        battle = self.conduct_hook_battle(topic)
        winning_hook = battle.get("winning_hook")
        print(f"🥇 [HookMaster] Winner crowned: \"{winning_hook}\"")
        for h in battle.get("hooks", []):
            print(f"   • [{h.get('type')}] Score {h.get('score')}: \"{h.get('hook')}\"")

        print(f"✍️ [HookMaster] Writing 5-act (11-13 turn, 40-52s) Remotion screenplay...")
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
