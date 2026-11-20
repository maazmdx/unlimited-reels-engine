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
        cat_lower = str(category).lower() + " " + str(title).lower()
        if "game" in cat_lower or "retro" in cat_lower or "emulator" in cat_lower:
            fallback_h1 = f"You can play full {title[:20]} in Chrome right now."
            fallback_h2 = f"Zero downloads: {title[:22]} runs in browser."
            fallback_h3 = f"Why did nobody tell me about {title[:20]}?"
        elif "ai" in cat_lower or "llm" in cat_lower or "model" in cat_lower:
            fallback_h1 = f"This free AI tool replaces $50 monthly software."
            fallback_h2 = f"Stop overpaying for closed AI subscriptions."
            fallback_h3 = f"How is this free AI model outperforming paid SaaS?"
        elif "money" in cat_lower or "business" in cat_lower or "earn" in cat_lower or "margin" in cat_lower:
            fallback_h1 = f"The secret way {title[:22]} prints millions."
            fallback_h2 = f"Their free tier is actually a genius money trap."
            fallback_h3 = f"Why every competitor went broke copying this."
        elif "dad" in cat_lower:
            fallback_h1 = f"Your dad's craziest tech fix actually works."
            fallback_h2 = f"Never call IT support for this again."
            fallback_h3 = f"My dad solved this in ninety seconds."
        else:
            fallback_h1 = f"Why is nobody talking about this {title[:20]} trick?"
            fallback_h2 = f"This single zero-dollar tool changes everything."
            fallback_h3 = f"Stop doing this manually when {title[:18]} exists."

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
    # =========================================================================
    # STEP B: 5-ACT VIRAL MEME SCREENPLAY (11-13 Turns, Multi-Step Proof Card, Toast, End-Card)
    # =========================================================================

    def craft_screenplay(
        self,
        topic: Dict[str, Any],
        hook_battle_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Writes an 11-13 turn dialogue (40-52s, 8-14 words/turn) following a strict 5-act viral arc:
        - Act 1 (Turns 0-1): Scroll-Stop Hook & Immediate Reaction
        - Act 2 (Turns 2-4): Hype vs. Reality & Escalation (Skepticism -> Mechanism)
        - Act 3 (Turns 5-7): Step-by-Step Interactive Proof Card (Highlights Row 1 on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7)
        - Act 4 (Turns 8-10): Meme Twist + Animated iOS Notification Toast on Turn 9
        - Act 5 (Turns 11-12): Spoken CTA + 2.5s Clean Black End-Card Cliffhanger
        """
        title = topic.get("title") or topic.get("topic_title")
        left_char = topic.get("left_character", "junior_dev")
        right_char = topic.get("right_character", "claude")
        scene_preset = topic.get("scene_preset", "diner")
        kw = str(topic.get("auto_dm_keyword", "LINK")).strip().upper()
        winning_hook = hook_battle_result.get("winning_hook", f"Look at {title}.")
        category = topic.get("category", "Tech")

        system_instruction = (
            "You are HookMaster: Screenplay & Dialogue Specialist for 9:16 vertical 3D dialogue reels.\n"
            "Your objective: Write high-retention 40-52 second screenplays modeled on viral 2026 tech reels.\n\n"
            "STRICT 5-ACT SCREENPLAY RULES:\n"
            "1. EXACTLY 11 TO 13 SNAPPY TURNS (40-52 seconds total).\n"
            "2. 8 TO 14 WORDS PER TURN: Crisp, rhythmic, conversational, funny, and educational.\n"
            "3. STRICT 2-CHARACTER ALTERNATION: Alternate strictly between left_character and right_character.\n"
            "4. 5-ACT NARRATIVE STRUCTURE:\n"
            "   - Act 1 (Turns 0-1, 0-5s): Turn 0 is winning hook (<= 10 words). Turn 1 is immediate reaction.\n"
            "   - Act 2 (Turns 2-4, 5-16s): Skeptical challenge, calling out the catch, dropping surprising mechanism.\n"
            "   - Act 3 (Turns 5-7, 16-30s): Upper-third proof card open! Row 1 explained on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7.\n"
            "   - Act 4 (Turns 8-10, 30-43s): Relatable twist & real consequence backed by an iOS Notification Toast sliding in on Turn 9.\n"
            "   - Act 5 (Turns 11-12, 43-50s): Final punchline + spoken: 'Comment " + kw + " and I'll DM you the link.'\n"
            "5. NO ROBOTIC FLUFF: Concrete numbers, memory limits, real SaaS fees, or hilarious developer truths.\n"
            "6. TOAST DATA: Supply toastData (app_name, sender, message, icon) triggered on Turn 9.\n"
            "7. END-CARD: Supply endCard question (e.g. 'Would you switch to OpenRouter?') for the 2.5s black cliffhanger."
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
- Turns 5, 6, 7 MUST sequentially explain and highlight Rows 1, 2, and 3 of the Proof Card.
- Turn 9 MUST introduce the Meme Twist supported by the iOS Notification Toast.
- Final Turn MUST end with: "Comment {kw} and I'll DM you the link."

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
  "explainerTitle": "{title[:24]} Specs",
  "cardData": {{
    "title": "{title[:24]} Breakdown",
    "subtitle": "Step-by-step verified specs",
    "badge": "VERIFIED PROOF",
    "rows": [
      {{
        "label": "Step 1: Access / Core Tech",
        "value": "Concrete metric or spec",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 2: Performance / Catch",
        "value": "Speed or cost comparison",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 3: Bottom Line",
        "value": "Real-world result",
        "status": "PROVEN",
        "isPositive": true
      }}
    ],
    "startTurn": 5,
    "endTurn": 7,
    "durationSeconds": 12.0
  }},
  "toastData": {{
    "app_name": "Slack",
    "sender": "Tech Lead",
    "message": "Funny punchy 1-line reaction or consequence",
    "icon": "💬",
    "time": "now"
  }},
  "endCard": {{
    "question": "Short debate question for the audience?",
    "keyword": "{kw}",
    "cta_text": "Comment {kw} for the link",
    "subtext": "Follow for Part 2"
  }},
  "hook": {{
    "headline": "{title.upper()[:35]}",
    "subheadline": "{winning_hook}",
    "tag": "⚠️ VIRAL REAL TALK"
  }},
  "dialogue": [
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Snappy reaction 8-14 words", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Skeptical challenge calling out catch 8-14 words", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Drops surprising truth or mechanism 8-14 words", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Demands proof or asks how it works 8-14 words", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Explains Step 1 matching Row 1 8-14 words", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Reacts to Step 2 matching Row 2 8-14 words", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Delivers Step 3 matching Row 3 8-14 words", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Disbelief or realization 8-14 words", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Meme twist or real consequence 8-14 words", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Panicked or funny reaction 8-14 words", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Dry punchline. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40}}
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
        screenplay["cta_phrase"] = f"Comment {kw} and I'll DM you the link."
        screenplay["cta_text"] = f"💬 Comment {kw} for the link"
        screenplay["ctaText"] = f"💬 Comment {kw} for the link"

        # Ensure cardData exists and has multi-step structure
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
                {"label": "Step 1: Core Engine", "value": "Direct In-Browser Zero Cost", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Performance", "value": "10x Faster Execution Speed", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Bottom Line", "value": "Zero Subscription Needed", "status": "PROVEN", "isPositive": True},
            ]
        card_d["items"] = card_d["rows"]

        # Ensure toastData exists
        if not screenplay.get("toastData") or not isinstance(screenplay["toastData"], dict):
            screenplay["toastData"] = {
                "app_name": "Slack",
                "sender": "Tech Lead",
                "message": f"Why is our team using {title[:18]} in production?",
                "icon": "💬",
                "time": "now",
            }
        else:
            screenplay["toastData"].setdefault("app_name", "Slack")
            screenplay["toastData"].setdefault("sender", "Tech Lead")
            screenplay["toastData"].setdefault("message", f"Check {title[:18]} right now!")
            screenplay["toastData"].setdefault("icon", "💬")
            screenplay["toastData"].setdefault("time", "now")

        # Ensure endCard exists
        if not screenplay.get("endCard") or not isinstance(screenplay["endCard"], dict):
            screenplay["endCard"] = {
                "question": f"Would you try {title[:25]}?",
                "keyword": kw,
                "cta_text": f"Comment {kw} for the link",
                "subtext": "Follow for Part 2",
            }
        else:
            screenplay["endCard"].setdefault("question", f"Would you try {title[:25]}?")
            screenplay["endCard"]["keyword"] = kw
            screenplay["endCard"]["cta_text"] = f"Comment {kw} for the link"
            screenplay["endCard"].setdefault("subtext", "Follow for Part 2")

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
        """Deterministic, topic-aware broadcast-grade 12-turn 5-act fallback screenplay."""
        title = topic.get("title") or topic.get("topic_title") or "Daily Tech Breakdown"
        category = topic.get("category", "")
        cat_lower = (str(category) + " " + str(title)).lower()

        if "game" in cat_lower or "retro" in cat_lower or "emulator" in cat_lower:
            badge = "EMULATION STATS"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Core Engine", "value": "100% In-Browser WebAssembly", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Framerate", "value": "Locked 60 FPS in Chrome", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Storage", "value": "Zero Local Downloads Needed", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Steam",
                "sender": "Friend",
                "message": "Did you seriously boot Windows 95 inside Google Chrome?",
                "icon": "🎮",
                "time": "now",
            }
            end_question = "Which classic retro game should be ported next?"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "It is real. Someone ported the full machine architecture to WebAssembly.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Come on, running a full desktop operating system in a tab must crawl.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "V8 JIT compilation compiles the x86 instructions directly into near-native machine code.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "I need proof before I open this on my work laptop.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Step one on screen: it runs pure WebAssembly with zero extensions installed.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Wait, step two says locked sixty frames per second without stuttering?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "And step three: zero local disk storage. The entire disk image streams instantly.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "This means retro emulation just became entirely frictionless for everyone.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Watch this: my teammate just messaged me asking how I did it.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "If IT checks browser memory right now, I am getting promoted.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"Play it yourself right now. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "ai" in cat_lower or "llm" in cat_lower or "model" in cat_lower:
            badge = "AI WORKFLOW STATS"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Open Weights", "value": "100% Free Apache-2.0 License", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Cloud Cost", "value": "Saves $40/mo in Closed SaaS", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Inference Speed", "value": "Under 18ms First Token Latency", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Slack",
                "sender": "Tech Lead",
                "message": "Our OpenAI billing invoice just dropped by eighty percent.",
                "icon": "⚡",
                "time": "now",
            }
            end_question = "Would you switch your production pipeline to this free model?"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "You can replace that expensive monthly cloud subscription completely for free.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Every free open model claims that until you see the terrible hallucination rate.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "They distilled the reasoning tokens directly from frontier models with verified benchmarks.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Show me the real breakdown before I cancel my subscription.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Step one on screen: full open weights under an Apache license with no catch.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Step two saves forty dollars every month on single-seat developer licenses?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "And step three: eighteen millisecond latency because it runs locally on your machine.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am literally paying two different corporate providers for worse performance.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Check your notifications: the lead engineer just noticed the savings.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "My subscription cancellation emails are already queued up and sending.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"Grab the setup guide right now. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "money" in cat_lower or "business" in cat_lower or "earn" in cat_lower or "margin" in cat_lower:
            badge = "FINANCIAL TEARDOWN"
            card_title = f"{title[:22]} Economics"
            rows = [
                {"label": "Step 1: Front Product", "value": "100% Free Public Loss Leader", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Gross Margin", "value": "Over 85% on Enterprise Upgrades", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Cash Generated", "value": "Nine Figures on Zero Paid Ads", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Stripe",
                "sender": "Billing Alert",
                "message": "New Enterprise annual contract activated: $120,000.",
                "icon": "💰",
                "time": "now",
            }
            end_question = "Is this freemium flywheel the smartest business model in tech?"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Their actual revenue model is the opposite of what casual users assume.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "If their core software is totally free, how are they funding massive clusters?", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "The free tool is a Trojan horse that funnels corporate enterprise contracts.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Break down the exact math before I believe this.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Step one on screen: the consumer tier has near-zero marginal bandwidth cost.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Step two shows eighty-five percent margins once companies mandate compliance?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: they print hundreds of millions with zero dollars in paid marketing.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Every startup trying to charge twenty dollars upfront just got completely destroyed.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at the Stripe alert that just popped in. Pure organic inbound.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am never looking at consumer software pricing the same way again.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"Read the full financial teardown. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
            ]
        elif "dad" in cat_lower:
            badge = "VERIFIED FIX"
            card_title = f"{title[:22]} Fix"
            rows = [
                {"label": "Step 1: Zero Hardware", "value": "$0 Spent on New Modems", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Time to Fix", "value": "Solved in Under 90 Seconds", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Reliability", "value": "Zero Drops or Reboots All Week", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "Messages",
                "sender": "Dad",
                "message": "Wi-Fi is working! Don't touch any cables ever again.",
                "icon": "👨‍👧",
                "time": "now",
            }
            end_question = "What is the wildest tech fix your dad ever tried?"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Listen to me: you do not need to replace the entire network router.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "My dad has been power cycling the modem twelve times every single morning.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "It was never the hardware. The ISP default DNS was timing out constantly.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Show me the fix before he cuts all the ethernet cables.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Step one on screen: you spend exactly zero dollars on replacement hardware.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Step two says changing this single address fixes it in ninety seconds?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: rock solid connection with zero dropped packets all week long.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "He literally spent four hours yelling at customer support over this.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at the message that just arrived. He thinks he is a genius.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am quietly saving this before he tries reformatting the refrigerator.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"Share this fix right now. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
            ]
        else:
            badge = "TECH BREAKDOWN"
            card_title = f"{title[:22]} Specs"
            rows = [
                {"label": "Step 1: Direct Access", "value": "100% Free Public Availability", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Deployment", "value": "Runs Instantly With Zero Bloat", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Efficiency", "value": "10x Faster Than Legacy Approaches", "status": "PROVEN", "isPositive": True},
            ]
            toast = {
                "app_name": "GitHub",
                "sender": "Repo Alert",
                "message": "Trending #1 worldwide with 12,000 new stars today.",
                "icon": "⭐",
                "time": "now",
            }
            end_question = "Would you integrate this into your daily workflow?"
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "This just dropped publicly with zero corporate paywall or sign-up barrier.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": f"Why is nobody talking about this {title.split()[0]} tool yet?", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Because legacy vendors want you locked into their bloated closed ecosystem.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Check the numbers right now before I commit to anything.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Step one on screen: completely open and accessible directly in your browser.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "Step two shows instant execution with zero external runtime dependencies?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": right_char, "character_id": right_char, "text": "Step three: ten times faster throughput than standard enterprise solutions.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "This completely redefines how modern developers solve this problem.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Look at GitHub right now: it is already trending number one globally.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": left_char, "character_id": left_char, "text": "I am bookmarking this immediately before everyone else floods the servers.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": f"Grab the free link now. Comment {kw} and I'll DM you the link.", "emotion": "smug", "pause_after": 0.40},
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
            "cta_text": f"Comment {kw} for the link",
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
            "cta_phrase": f"Comment {kw} and I'll DM you the link.",
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
