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
    "collaboration", "delivers", "delivering", "latency", "ecosystem",
    "workflow", "workflows", "manual coding", "leverage", "leveraging", "unlock", "unlocking"
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
    (re.compile(r"\bworkflows?\b", re.IGNORECASE), "setup"),
    (re.compile(r"\bmanual coding\b", re.IGNORECASE), "coding by hand"),
    (re.compile(r"\bleverag(e|ed|es|ing)\b", re.IGNORECASE), "use"),
    (re.compile(r"\bunlock(ed|s|ing)?\b", re.IGNORECASE), "get"),
    (re.compile(r"\bhumans love doing\b", re.IGNORECASE), "why do people"),
]


def strip_emojis(text: str) -> str:
    """Strips Unicode emoji characters so Linux/Kaggle renders without □ glyph boxes."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010FFFF\u2600-\u27BF\uFE00-\uFE0F\uD83C-\uDBFF\uDC00-\uDFFF]",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()


def sanitize_simple_spoken_english(text: str) -> str:
    """Replaces corporate buzzwords with simple, 6th-8th grade conversational English and strips emojis."""
    cleaned = text
    for pattern, repl in VOCABULARY_REPLACEMENTS:
        cleaned = pattern.sub(repl, cleaned)
    return strip_emojis(cleaned)


def sanitize_auto_dm_keyword(raw_kw: str, category: str = "", title: str = "") -> str:
    """Enforces single pronounceable dictionary English words for auto_dm_keyword (never RETROPC)."""
    cleaned = re.sub(r"[^A-Z]", "", (raw_kw or "").strip().upper())
    if cleaned in ["RETROPC", "RETRO_PC", "INTEL486", "PC", "BROWSER"]:
        return "PLAY" if any(w in (category + title).lower() for w in ["game", "retro", "emulator"]) else "FREE"
    if not cleaned or len(cleaned) < 3 or len(cleaned) > 7:
        cat_lower = (str(category) + " " + str(title)).lower()
        if any(w in cat_lower for w in ["repo", "github", "open-source", "open source"]):
            return "REPO"
        elif any(w in cat_lower for w in ["game", "retro", "play"]):
            return "PLAY"
        elif any(w in cat_lower for w in ["ai", "tool", "app"]):
            return "TOOL"
        else:
            return "FREE"
    return cleaned


def clean_headline_truncation(text: str, max_chars: int = 40) -> str:
    """Truncates text at a word boundary without cutting off mid-word."""
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(" ", 1)[0]
    return truncated if len(truncated) > 10 else text[:max_chars]


def call_groq_api(prompt: str, system_instruction: str, timeout: float = 35.0) -> Optional[str]:
    """
    Calls Groq Cloud API with llama-3.3-70b-versatile for ultra-fast, zero-cost JSON completions.
    100% free via GROQ_API_KEY env var / Kaggle Secret, zero extra pip packages (uses requests).
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        try:
            from kaggle_secrets import UserSecretsClient
            groq_api_key = UserSecretsClient().get_secret("GROQ_API_KEY")
        except Exception:
            pass

    if not groq_api_key:
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json",
        "User-Agent": "AntigravityHookMaster/3.0",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    t0 = time.time()
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if r.status_code == 200:
            res_json = r.json()
            choices = res_json.get("choices", [])
            if choices:
                text = choices[0].get("message", {}).get("content", "")
                elapsed = time.time() - t0
                print(f"⚡ [Groq API] Model 'llama-3.3-70b-versatile' succeeded in {elapsed:.2f}s ({len(text)} chars).")
                return text
        else:
            print(f"⚠️ [Groq API] HTTP {r.status_code}: {r.text[:140]}")
    except Exception as e:
        print(f"⚠️ [Groq API] Request exception: {e}")

    return None


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
        """Calls Gemini with 2026 free-tier models, clean 45s timeout, 1 retry on 504/timeout, and logs model."""
        models = ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

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
                        r = requests.post(url, json=payload, headers=self.headers, timeout=45.0)
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

    def _call_llm(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Routes LLM generation through the central zero-dependency LLMRouter."""
        from engine.llm_router import generate_text
        return generate_text(prompt, system_prompt=system_instruction, json_mode=True, temperature=0.8)

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
            "- Explicitly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', 'workflow', 'manual coding', 'leverage', 'unlock'.\n"
            "- Write in short, punchy, everyday spoken English that anyone on Instagram understands instantly.\n\n"
            "STORY-FIRST DRAMATIC PATTERN-INTERRUPT HOOK (ZERO GENERIC / AD OPENERS):\n"
            "- STRICTLY BANNED OPENERS: 'Bro your slow workflow...', 'Humans love doing...', 'Humans love...', 'Wait there is no way...', 'There is no way...', 'Look at this tool right now...', 'Stop doing X by hand...', 'Why is nobody talking about...', 'Check this tool out'.\n"
            "- MANDATORY: Start with a concrete 0-3s pattern-interrupt contrast or shock (e.g. 'Still paying twenty dollars a month to edit PDFs?', 'Dad, why did you install 4 RAM booster apps?', 'My laptop literally froze opening a two-megabyte file.').\n"
            "- MAXIMUM 10 WORDS. Zero exceptions.\n"
            "- ZERO FILLER: Never start with 'Hey guys', 'Did you know', 'So today'.\n\n"
            "You must write and score 3 distinct hooks:\n"
            "1. 'curiosity_gap': Mid-conversation human shock uncovering a ridiculous zero-dollar trick.\n"
            "2. 'contrarian_callout': Human complaining about an expensive tool, slow laptop, or wasted bill.\n"
            "3. 'relatable_shock': Comedic panic about dying laptops, broken apps, or angry bosses."
        )

        prompt = f"""
Topic: {title}
Category: {category}
Core Conflict: {conflict}
Auto-DM Keyword: {kw}

TASK:
Write 3 competing opening hooks (each <= 10 words, simple spoken English only, story-first human shock mid-conversation).
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

        raw_json = self._call_llm(prompt, system_instruction)
        if raw_json:
            try:
                cleaned = raw_json.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                    cleaned = re.sub(r"\n```$", "", cleaned)
                parsed = json.loads(cleaned.strip())
                if "winning_hook" in parsed:
                    # Sanitize winning hook to simple spoken English
                    win_h = sanitize_simple_spoken_english(parsed["winning_hook"])
                    # Guard against generic openers
                    banned_prefixes = [
                        "bro your slow workflow", "humans love doing", "humans love",
                        "wait there is no way", "there is no way", "look at this tool",
                        "stop doing", "why is nobody talking", "check this tool out"
                    ]
                    if any(win_h.lower().startswith(bp) for bp in banned_prefixes) or len(win_h.split()) < 3:
                        if "pdf" in (str(category) + " " + str(title)).lower():
                            win_h = "Still paying twenty dollars a month to edit PDFs?"
                        elif "dad" in (str(category) + " " + str(title)).lower() or "ram" in (str(category) + " " + str(title)).lower():
                            win_h = "Dad, why did you install four RAM booster apps?"
                        else:
                            win_h = f"Wait... why am I paying monthly fees for this?"
                    parsed["winning_hook"] = win_h
                    for h in parsed.get("hooks", []):
                        if "hook" in h:
                            h["hook"] = sanitize_simple_spoken_english(h["hook"])
                    return parsed
            except Exception as e:
                print(f"⚠️ HookMaster: Hook battle parse error: {e}")

        # Deterministic fallback battle in story-first spoken English
        cat_lower = str(category).lower() + " " + str(title).lower()
        if "pdf" in cat_lower:
            fallback_h1 = "Still paying twenty dollars a month to edit PDFs?"
            fallback_h2 = "Wait... Adobe charged me twenty bucks just to sign this?"
            fallback_h3 = "Why am I paying twenty dollars to merge two files?"
        elif "ram" in cat_lower or "cleaner" in cat_lower or ("dad" in cat_lower and "booster" in cat_lower):
            fallback_h1 = "Dad, why did you install four RAM booster apps?"
            fallback_h2 = "Dad, your phone is literally burning hot right now."
            fallback_h3 = "Dad believes downloading four cleaner apps doubles his RAM."
        elif "scam" in cat_lower or "whatsapp" in cat_lower or "lottery" in cat_lower:
            fallback_h1 = "Dad is about to send bank details on WhatsApp."
            fallback_h2 = "Dad, you did not win a free iPhone on WhatsApp."
            fallback_h3 = "Dad is forwarding scam lottery links to twenty family groups."
        elif "game" in cat_lower or "retro" in cat_lower or "emulator" in cat_lower:
            fallback_h1 = "Bro... my laptop literally starts smoking when I open Steam."
            fallback_h2 = "Wait... my fan sounds like a dying jet engine right now."
            fallback_h3 = "Bro... I am not downloading eighty gigabytes just to play."
        elif "repo" in cat_lower or "github" in cat_lower or "open-source" in cat_lower:
            fallback_h1 = "Bro... my credit card just got charged twenty dollars again."
            fallback_h2 = "Wait... why am I paying twenty bucks a month for this?"
            fallback_h3 = "Claude... I am officially broke from all these software tools."
        elif "ai" in cat_lower or "llm" in cat_lower or "model" in cat_lower:
            fallback_h1 = "Bro... I spent three hours on this and it looks awful."
            fallback_h2 = "Wait... my bank just charged me twenty dollars for an AI tool."
            fallback_h3 = "Claude... I think I just got scammed by another subscription."
        elif "money" in cat_lower or "business" in cat_lower or "earn" in cat_lower or "margin" in cat_lower:
            fallback_h1 = "Wait... why did my bank balance drop fifty bucks this morning?"
            fallback_h2 = "Bro... this free app made twenty billion dollars off us."
            fallback_h3 = "Claude... tell me why everyone is going broke on subscriptions."
        elif "dad" in cat_lower:
            fallback_h1 = "Dad, why did you install four RAM booster apps?"
            fallback_h2 = "Dad... why did you just hit the router with a shoe?"
            fallback_h3 = "Bro... my internet went down right before my meeting."
        else:
            fallback_h1 = "Bro... my laptop literally froze trying to do this."
            fallback_h2 = "Claude... tell me I didn't just waste fifty dollars on this."
            fallback_h3 = "Bro... I spent all morning doing this by hand like an idiot."

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
        category = topic.get("category", "Tech")

        format_type = str(topic.get("format_type") or "informative_roast").lower()
        has_res = topic.get("has_resource_link")
        if has_res is None:
            has_res = not any(k in format_type for k in ["doc", "dad", "meme", "funny", "secret"])

        is_doc = "doc" in format_type or "discovery" in format_type
        is_dad = "dad" in format_type or left_char == "dad"
        is_gh = any(term in str(category).lower() or term in str(title).lower() for term in ["github", "repo", "open-source", "open source"])
        link_target = "GitHub repo link" if is_gh else "free link"

        tool_name = str(topic.get("tool_name") or topic.get("toolName") or "").strip()
        brand_domain = str(topic.get("brand_domain") or topic.get("brandDomain") or "").strip()
        github_repo = str(topic.get("github_repo") or topic.get("githubRepo") or "").strip()
        real_steps = topic.get("real_steps") or topic.get("realSteps") or []

        if not tool_name:
            if "vice" in str(title).lower() or "gta" in str(title).lower():
                tool_name = "EmulatorJS"
                brand_domain = "emulatorjs.org"
            elif "pdf" in str(title).lower():
                tool_name = "Stirling-PDF"
                brand_domain = "stirlingpdf.com"
            elif "notebook" in str(title).lower():
                tool_name = "NotebookLM"
                brand_domain = "notebooklm.google.com"
            else:
                tool_name = str(title).split()[0] if title else "OpenTool"

        # 4 Rotating comedy structures
        structure_options = ["brutal_roast", "dad_interrogation", "speedrun_expose", "friend_betrayal"]
        if is_dad:
            comedy_structure = "dad_interrogation"
        else:
            hash_val = sum(ord(c) for c in (topic.get("id") or str(title) or "reel"))
            comedy_structure = structure_options[hash_val % len(structure_options)]

        if has_res:
            raw_kw = str(topic.get("auto_dm_keyword", "FREE")).strip().upper()
            kw = sanitize_auto_dm_keyword(raw_kw, category, title)
            cta_phrase = topic.get("cta_phrase") or f"Comment {kw} and I'll DM you the {link_target}."
            final_turn_cta = f"Stop crying, human. Comment {kw} and I'll DM you the {link_target}."
            end_card_cta = f"Comment {kw} for the {link_target}"
            end_card_question = f"Still paying for this when {tool_name} exists? Be honest"
        else:
            kw = ""
            if is_doc:
                cta_phrase = topic.get("cta_phrase") or "Tag that dev in your group whose credits just ran out."
                final_turn_cta = "Nature is cruel, human. Tag that dev in your group whose credits just ran out."
                end_card_cta = "TAG THAT DEV BELOW"
                end_card_question = "Could you survive 24 hours coding without AI?"
            elif is_dad:
                cta_phrase = topic.get("cta_phrase") or "Send this to your Dad or dev friend."
                final_turn_cta = "Send this to your Dad or friend who still fixes routers with a shoe."
                end_card_cta = "SEND TO YOUR DAD OR FRIEND"
                end_card_question = "Would you trust your dad to fix your tech?"
            else:
                cta_phrase = topic.get("cta_phrase") or "Tag that dev in your group who still codes without AI."
                final_turn_cta = "Tag that dev in your group who still codes without AI."
                end_card_cta = "TAG THAT DEV IN YOUR GROUP"
                end_card_question = "Who in your group is this developer?"

        winning_hook = sanitize_simple_spoken_english(hook_battle_result.get("winning_hook", f"Look at {title}."))

        system_instruction = (
            "You are HookMaster: Screenplay & Dialogue Specialist for 9:16 vertical 3D dialogue reels.\n"
            f"Your objective: Write high-retention 40-50s screenplays using the comedy structure: '{comedy_structure}'.\n\n"
            "STRICT VOCABULARY BAN (SIMPLE SPOKEN ENGLISH ONLY - 6th to 8th GRADE LEVEL):\n"
            "- Strictly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', 'workflow', 'manual coding', 'leverage', 'unlock', or any corporate/academic buzzwords.\n\n"
            "EXPLICITLY BANNED REPETITIVE FILLER PHRASES:\n"
            "- Do NOT use: 'Wait there is no way', 'There is no way', 'Humans love', 'Look at step one', 'Wait step two says', 'zero dollar cost', 'before my ... explodes', 'bro your slow workflow'.\n\n"
            f"COMEDY STRUCTURE: '{comedy_structure}'\n"
            "- 'brutal_roast': AI orb savagely mocks human laziness, slow manual coding, or paying subscriptions. Human in deep denial until proved wrong.\n"
            "- 'dad_interrogation': Dad fiercely grills dev or gets busted over RAM booster apps, scam WhatsApp links, or battery myths.\n"
            "- 'speedrun_expose': High-octane expose tearing down a corporate paywall in record time.\n"
            "- 'friend_betrayal': Smug mockery of a friend or coworker who wasted 4 hours on what takes 2 seconds for free.\n\n"
            f"MANDATORY PACING RULES:\n"
            "- Fast punchy 8 to 14 word turns (snappy back-and-forth banter, zero monologues, natural contractions).\n"
            f"- The exact tool_name '{tool_name}' MUST be spoken naturally by Turn 2 or Turn 3 for Reel #1 (NEVER delay until Turn 5).\n"
            "- Turn 8-9 Escalation: MUST feature a genuine relatable escalation or roast twist tied directly to the topic (e.g. unexpected cancellation fee, overheating phone alert, boss walking by). NEVER generic office ticket filler.\n"
            f"- Turn 9 Notification: MUST match the exact topic '{title}' (e.g. 'Task Finished • 0 Ads • $0 Saved' or 'Battery Alert • 88°C').\n"
            f"- Final Turn MUST end with: '{final_turn_cta}'"
        )

        prompt = f"""
Topic: {title}
Category: {category}
Format Type: {format_type}
Tool Name: {tool_name}
Brand Domain: {brand_domain}
GitHub Repo: {github_repo}
Comedy Structure: {comedy_structure}
Winning Hook (Turn 0 line): "{winning_hook}"
Cast: Left={left_char}, Right={right_char}
Scene Preset: {scene_preset}
Auto-DM Keyword: {kw}

TASK:
Write the complete 5-act Remotion screenplay JSON with 11-12 snappy dialogue turns.
- Turn 0 MUST be {left_char} speaking: "{winning_hook}"
- Turns 1-4: Fast punchy comedic escalation (5-12 words/turn) following '{comedy_structure}'.
- By Turn 2 or Turn 3: The exact name '{tool_name}' MUST be spoken naturally.
- Turns 5, 6, 7: Walk through the 3 concrete verified steps cleanly without repetitive filler.
- Turn 9: Notification popup alert that strictly matches the topic '{title}'.
- Final Turn MUST end with: "{final_turn_cta}"

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
  "cta_phrase": "{cta_phrase}",
  "has_resource_link": {str(has_res).lower()},
  "cardType": "comparison",
  "badge": "VERIFIED PROOF",
  "explainerTitle": "{clean_headline_truncation(title, 26)} Specs",
  "cardData": {{
    "title": "{clean_headline_truncation(title, 26)} Breakdown",
    "subtitle": "Step-by-step verified specs",
    "badge": "VERIFIED PROOF",
    "rows": [
      {{
        "label": "Step 1: Setup",
        "value": "Exact 1-click action, URL, or command",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 2: Execution",
        "value": "What happens live under the hood",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 3: Payoff",
        "value": "$0 / 100% Free (replaces paid tools)",
        "status": "PROVEN",
        "isPositive": true
      }}
    ],
    "startTurn": 5,
    "endTurn": 7,
    "durationSeconds": 12.0
  }},
  "toastData": {{
    "app_name": "System Alert",
    "sender": "Security / Usage",
    "message": "Relevant punchy notification twist.",
    "icon": "ALERT",
    "time": "now"
  }},
  "endCard": {{
    "question": "{end_card_question}",
    "keyword": "{kw}",
    "cta_text": "{end_card_cta}",
    "subtext": "Follow for Part 2",
    "has_resource_link": {str(has_res).lower()}
  }},
  "hook": {{
    "headline": "{clean_headline_truncation(title.upper(), 38)}",
    "subheadline": "{winning_hook}",
    "tag": "⚠️ VIRAL REAL TALK"
  }},
  "dialogue": [
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Stop overpaying for software when {tool_name} is free.", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Are you sure {tool_name} handles this with zero fees?", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Verified open-source execution directly on your device.", "emotion": "smug", "pause_after": 0.30}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Show me the real breakdown right now.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Step one: open {brand_domain or tool_name} in your browser.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "And it runs instantly without installing sketchy software?", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Completely free with zero subscription charges.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "I was paying every single month for this.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Your account just confirmed your savings on screen.", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "I am switching to {tool_name} right now.", "emotion": "shocked", "pause_after": 0.30}},
    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "{final_turn_cta}", "emotion": "smug", "pause_after": 0.40}}
  ]
}}
"""

        raw_json = self._call_llm(prompt, system_instruction)
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
        screenplay["has_resource_link"] = has_res
        screenplay["hasResourceLink"] = has_res
        screenplay["cta_keyword"] = kw
        screenplay["ctaKeyword"] = kw
        screenplay["cta_phrase"] = cta_phrase
        screenplay["cta_text"] = f"💬 Comment {kw} for the {link_target}" if has_res else f"💬 {cta_phrase}"
        screenplay["ctaText"] = f"💬 Comment {kw} for the {link_target}" if has_res else f"💬 {cta_phrase}"

        # Ensure cardData exists and has multi-step structure in simple English
        if not screenplay.get("cardData") or not isinstance(screenplay["cardData"], dict):
            screenplay["cardData"] = {}
        card_d = screenplay["cardData"]
        card_d.setdefault("title", f"{clean_headline_truncation(title, 26)} Breakdown")
        card_d.setdefault("subtitle", "Step-by-step verified specs")
        card_d.setdefault("badge", "VERIFIED PROOF")
        card_d.setdefault("startTurn", 5)
        card_d.setdefault("endTurn", 7)
        card_d.setdefault("durationSeconds", 12.0)
        if "rows" not in card_d or not isinstance(card_d["rows"], list) or len(card_d["rows"]) < 3:
            card_d["rows"] = [
                {"label": "Step 1: Setup", "value": "1-Click Launch In Seconds", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Execution", "value": "Direct Local Performance", "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Payoff", "value": "$0 / 100% Free Forever", "status": "PROVEN", "isPositive": True},
            ]
        card_d["items"] = card_d["rows"]

        # Ensure toastData exists and banish old "Slack" templates
        if not screenplay.get("toastData") or not isinstance(screenplay["toastData"], dict):
            screenplay["toastData"] = {
                "app_name": "Bank Alert",
                "sender": "Card Alert",
                "message": f"Monthly subscription declined. You saved $240 on {clean_headline_truncation(title, 16)}.",
                "icon": "CARD",
                "time": "now",
            }
        else:
            if str(screenplay["toastData"].get("app_name", "")).lower() == "slack":
                screenplay["toastData"]["app_name"] = "Bank Alert"
            screenplay["toastData"].setdefault("app_name", "Bank Alert")
            screenplay["toastData"].setdefault("sender", "Card Alert")
            screenplay["toastData"].setdefault("message", f"Monthly fee declined. You saved $240 on {clean_headline_truncation(title, 16)}!")
            screenplay["toastData"].setdefault("icon", "CARD")
            screenplay["toastData"].setdefault("time", "now")

        # Ensure endCard exists with ragebait question and context-aware CTA
        if not screenplay.get("endCard") or not isinstance(screenplay["endCard"], dict):
            screenplay["endCard"] = {
                "question": end_card_question,
                "keyword": kw,
                "cta_text": end_card_cta,
                "subtext": "Follow for Part 2",
                "has_resource_link": has_res,
                "hasResourceLink": has_res,
            }
        else:
            screenplay["endCard"].setdefault("question", end_card_question)
            screenplay["endCard"]["keyword"] = kw
            screenplay["endCard"]["cta_text"] = end_card_cta
            screenplay["endCard"]["has_resource_link"] = has_res
            screenplay["endCard"]["hasResourceLink"] = has_res
            screenplay["endCard"].setdefault("subtext", "Follow for Part 2")

        # STRICT VOCABULARY & EMOJI SANITIZATION PASS: Remove all fancy words & emojis
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
            if "icon" in screenplay["toastData"]:
                screenplay["toastData"]["icon"] = strip_emojis(screenplay["toastData"]["icon"]) or "ALERT"

        if "endCard" in screenplay and isinstance(screenplay["endCard"], dict):
            if "question" in screenplay["endCard"]:
                screenplay["endCard"]["question"] = sanitize_simple_spoken_english(screenplay["endCard"]["question"])

        if "hook" in screenplay and isinstance(screenplay["hook"], dict):
            raw_h = screenplay["hook"].get("headline", title)
            screenplay["hook"]["headline"] = clean_headline_truncation(raw_h.upper(), 38)

        # Attach metadata
        screenplay["hook_battle"] = hook_battle_result
        screenplay["winning_hook"] = winning_hook
        screenplay["viral_score"] = topic.get("viral_score", 85)
        screenplay["category"] = topic.get("category", "Tech")
        screenplay["tool_name"] = tool_name
        screenplay["toolName"] = tool_name
        screenplay["brand_domain"] = brand_domain
        screenplay["brandDomain"] = brand_domain
        screenplay["github_repo"] = github_repo
        screenplay["githubRepo"] = github_repo
        screenplay["real_steps"] = real_steps
        screenplay["realSteps"] = real_steps
        screenplay["comedy_structure"] = comedy_structure

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
        """Deterministic, topic-aware broadcast-grade 12-turn 5-act fallback screenplay with 4 rotating comedy structures."""
        title = topic.get("title") or topic.get("topic_title") or "Daily Tech Breakdown"
        category = topic.get("category", "")
        cat_lower = (str(category) + " " + str(title)).lower()
        format_type = topic.get("format_type", "")
        has_res = topic.get("has_resource_link", not (format_type in ["discovery_doc", "funny_story"] or "discovery" in cat_lower))
        is_gh = any(term in cat_lower for term in ["repo", "github", "open-source", "open source"])
        link_desc = "GitHub repo link" if is_gh else "free link"

        tool_name = str(topic.get("tool_name") or topic.get("toolName") or "").strip()
        brand_domain = str(topic.get("brand_domain") or topic.get("brandDomain") or "").strip()
        github_repo = str(topic.get("github_repo") or topic.get("githubRepo") or "").strip()
        real_steps = topic.get("real_steps") or topic.get("realSteps") or []

        if not tool_name:
            if "vice" in str(title).lower() or "gta" in str(title).lower():
                tool_name = "EmulatorJS"
                brand_domain = "emulatorjs.org"
            elif "pdf" in str(title).lower():
                tool_name = "Stirling-PDF"
                brand_domain = "stirlingpdf.com"
            elif "notebook" in str(title).lower():
                tool_name = "NotebookLM"
                brand_domain = "notebooklm.google.com"
            else:
                tool_name = str(title).split()[0] if title else "OpenTool"

        if left_char == "dad" or "dad" in format_type:
            structure = "dad_interrogation"
        else:
            structure_options = ["brutal_roast", "speedrun_expose", "friend_betrayal"]
            hash_val = sum(ord(c) for c in (topic.get("id") or str(title) or "reel"))
            structure = structure_options[hash_val % len(structure_options)]

        badge = "VERIFIED PROOF"
        card_title = f"{tool_name} Specs"
        step1_text = real_steps[0] if len(real_steps) > 0 else f"1. Open {brand_domain or tool_name}"
        step2_text = real_steps[1] if len(real_steps) > 1 else f"2. Run {tool_name} engine in browser"
        step3_text = real_steps[2] if len(real_steps) > 2 else "3. 100% Free with zero subscription fees"

        rows = [
            {"label": "Step 1: Setup", "value": step1_text, "status": "VERIFIED", "isPositive": True},
            {"label": "Step 2: Execution", "value": step2_text, "status": "VERIFIED", "isPositive": True},
            {"label": "Step 3: Payoff", "value": step3_text, "status": "PROVEN", "isPositive": True},
        ]

        final_turn_cta = f"Stop crying, human. Comment {kw} and I'll DM you the {link_desc}." if has_res else "Tag that dev in your group who needs this!"
        end_question = f"Still paying subscriptions when {tool_name} exists? Be honest"

        if structure == "dad_interrogation":
            badge = "DAD TECH AUDIT"
            card_title = f"{clean_headline_truncation(title, 20)}"
            if any(k in cat_lower for k in ["scam", "whatsapp", "lottery", "iphone", "bank"]):
                toast = {
                    "app_name": "WhatsApp",
                    "sender": "Security Alert",
                    "message": "Phishing Blocked • Scam Link Neutralized",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "I just won a brand new phone on WhatsApp today!", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Dad, please do not forward that link to your family groups.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "The message has a gold badge and says congratulations, sir!", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Scammers made that fake website three hours ago to steal passwords.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "They only asked for my card details to pay ten rupees shipping.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "That small shipping fee will empty your entire retirement bank account.", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Wait, so nobody is delivering a free smartphone to our door?", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Your bank app just blocked two unauthorized foreign transaction attempts!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Delete that message immediately and lock my online debit card.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Never click random WhatsApp prize links ever again in your life.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            else:
                toast = {
                    "app_name": "Android System",
                    "sender": "Battery Guard",
                    "message": "Overheating Alert • CPU 88°C • Cleaner Apps Active",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Because the turbo rocket animation speeds up my phone memory nicely!", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Modern phones manage memory automatically without downloading shady task killer apps.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Then why did the speed booster app give me ninety percent?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Those apps show full-screen ads and drain eighty percent of battery.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "They promised to clean junk files and double my processor speed.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Your phone is literally burning hot right now in your hand.", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "That warmth means the turbo cleaner engine is running very hard!", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Look at this notification: your battery temperature just reached eighty degrees.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Uninstall them quickly before this phone explodes in the living room.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Deleting all four apps right now, and stop clicking random ads.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
        elif structure == "speedrun_expose":
            badge = "SPEEDRUN EXPOSE"
            card_title = f"{tool_name} Hack"
            toast = {
                "app_name": "Terminal",
                "sender": "Speedrun Alert",
                "message": f"{tool_name} completed task in 1.2s. Paywall bypassed.",
                "icon": "SPEED",
                "time": "now",
            }
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Corporate software companies pray you never discover this free trick.", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": f"Wait, {tool_name} actually bypasses their entire expensive paywall?", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": f"Everyone switched to {tool_name} because it runs directly on your machine.", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": "They charge enterprise teams thousands of dollars every single month.", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Because naive users keep swiping their cards without searching first.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": f"So {tool_name} handles all heavy compute without any server fees?", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Instant execution in your browser with zero delay and zero limits.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "The sales team just emailed asking why we cancelled enterprise licenses!", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Tell them open-source software just saved the company thirty thousand dollars.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "I am sending this to our whole team right now.", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
            ]
        elif structure == "friend_betrayal":
            badge = "TASK BUSTED"
            card_title = f"{tool_name} Reveal"
            toast = {
                "app_name": "Slack",
                "sender": "Coworker",
                "message": f"Wait how did you finish with {tool_name} so fast?",
                "icon": "CHAT",
                "time": "now",
            }
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "You spent four hours doing this by hand like that?", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": f"Is there a secret tool that finishes this immediately?", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": f"Use {tool_name} and finish the entire setup in two clicks.", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": f"{tool_name} replaces my entire afternoon of manual boring work?", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "One click in your browser with verified zero subscription fees.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "My coworker just saw my finished screen and gasped aloud.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "Send him the link before he copies your old method.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Our boss just walked in asking how we finished so fast!", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Tell him free tools just saved our entire team four hours.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "I am never doing this by hand ever again.", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
            ]
        else: # brutal_roast
            badge = "BRUTAL ROAST"
            card_title = f"{tool_name} Reality"
            toast = {
                "app_name": "Card Alert",
                "sender": "Bank App",
                "message": f"Monthly fee cancelled! Switched to free {tool_name}.",
                "icon": "CARD",
                "time": "now",
            }
            dialogue = [
                {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "You really spent twenty dollars on that bloated subscription app?", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": "My paid subscription works fine, so why change anything?", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": f"Because {tool_name} does the exact same thing completely free.", "emotion": "smug", "pause_after": 0.25},
                {"speaker": left_char, "character_id": left_char, "text": f"Wait, {tool_name} runs locally without any monthly subscription fees?", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Zero subscription fees, zero cloud bloat, and runs right now.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Show me how it finishes this task without paid plugins.", "emotion": "shocked", "pause_after": 0.30},
                {"speaker": right_char, "character_id": right_char, "text": "One click in your browser and your file is ready.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "Adobe just sent an alert trying to charge a cancellation fee!", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": "Classic paywall panic when humans discover free open-source software.", "emotion": "smug", "pause_after": 0.30},
                {"speaker": left_char, "character_id": left_char, "text": "I am deleting that paid account and saving two hundred dollars.", "emotion": "shocked", "pause_after": 0.25},
                {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
            ]

        card_data = {
            "title": card_title,
            "subtitle": f"{tool_name} Breakdown",
            "badge": badge,
            "rows": rows,
            "items": rows,
            "startTurn": 5,
            "endTurn": 7,
            "durationSeconds": 12.0,
            "tool_name": tool_name,
            "brand_domain": brand_domain,
            "github_repo": github_repo,
            "real_steps": real_steps,
        }

        end_card = {
            "question": end_question,
            "keyword": kw if has_res else "",
            "cta_text": f"Comment {kw} for the {link_desc}" if has_res else "Tag that dev in your group who needs to see this!",
            "subtext": "Follow for Part 2",
            "has_resource_link": has_res,
            "hasResourceLink": has_res,
        }

        headline_text = clean_headline_truncation(title.upper(), 38)

        return {
            "title": title[:50],
            "style": scene_preset,
            "comp": "MasterAutonomousReel",
            "scenePreset": scene_preset,
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": kw if has_res else "",
            "cta_phrase": f"Comment {kw} and I'll DM you the {link_desc}." if has_res else "Tag that dev in your group who needs to see this!",
            "has_resource_link": has_res,
            "hasResourceLink": has_res,
            "cardType": "comparison",
            "badge": badge,
            "explainerTitle": card_title,
            "cardData": card_data,
            "toastData": toast,
            "endCard": end_card,
            "hook": {
                "headline": headline_text,
                "subheadline": hook,
                "tag": "⚠️ REAL TALK",
            },
            "dialogue": dialogue,
            "tool_name": tool_name,
            "toolName": tool_name,
            "brand_domain": brand_domain,
            "brandDomain": brand_domain,
            "github_repo": github_repo,
            "githubRepo": github_repo,
            "real_steps": real_steps,
            "realSteps": real_steps,
            "comedy_structure": structure,
        }

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
            "keyword": kw if has_res else "",
            "cta_text": f"Comment {kw} for the {link_desc}" if has_res else "Tag that dev in your group who needs to see this!",
            "subtext": "Follow for Part 2",
            "has_resource_link": has_res,
            "hasResourceLink": has_res,
        }

        headline_text = clean_headline_truncation(title.upper(), 38)

        return {
            "title": title[:50],
            "style": scene_preset,
            "comp": "MasterAutonomousReel",
            "scenePreset": scene_preset,
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": kw if has_res else "",
            "cta_phrase": f"Comment {kw} and I'll DM you the {link_desc}." if has_res else "Tag that dev in your group who needs to see this!",
            "has_resource_link": has_res,
            "hasResourceLink": has_res,
            "cardType": "comparison",
            "badge": badge,
            "explainerTitle": card_title,
            "cardData": card_data,
            "toastData": toast,
            "endCard": end_card,
            "hook": {
                "headline": headline_text,
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
        "title": "LocalSend: The Free Open-Source AirDrop for Every Device",
        "category": "Free Open-Source GitHub Repos",
        "auto_dm_keyword": "REPO",
        "left_character": "junior_dev",
        "right_character": "claude",
        "scene_preset": "desk",
        "core_conflict": "Human struggling with cloud upload subscriptions vs instant local P2P transfer",
    }
    screenplay = hm.craft_reel_screenplay(sample_topic)
    print("\n--- HookMaster Output ---")
    print(json.dumps(screenplay, indent=2))
