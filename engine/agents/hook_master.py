"""
HookMasterAgent (Master Agent 2: 0-3s Retention & Meme Screenplay Specialist)
Executes a 2-step craft pass via Gemini 2.5 Flash / 3.5 Flash:
1. Hook Battle: Writes 3 competing 0-3s hooks (<= 10 words each) across Curiosity Gap,
   Contrarian Callout, and Relatable Shock; scores each and crowns the #1 scroll-stopper.
2. Screenplay: Writes a high-retention 14-turn dialogue (42-50s, 10-15 words/turn, ~165-195 words)
   strictly between left_character and right_character following a 5-act viral arc with multi-step
   interactive proof card highlighted row-by-row on Turns 5-7, iOS notification toast on Turn 9,
   spoken Auto-DM CTA, and 2.5s black end-card.
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

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
        elif r.status_code == 400 and ("json_validate_failed" in r.text.lower() or "response_format" in r.text.lower()):
            print(f"⚠️ [Groq API] HTTP 400 (json_validate_failed/response_format); retrying without response_format...")
            payload_retry = dict(payload)
            payload_retry.pop("response_format", None)
            r2 = requests.post(url, json=payload_retry, headers=headers, timeout=timeout)
            if r2.status_code == 200:
                res_json = r2.json()
                choices = res_json.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    m = re.search(r"\{[\s\S]*\}", text)
                    return m.group(0) if m else text
            else:
                print(f"⚠️ [Groq API] Retry HTTP {r2.status_code}: {r2.text[:140]}")
        else:
            print(f"⚠️ [Groq API] HTTP {r.status_code}: {r.text[:140]}")
    except Exception as e:
        print(f"⚠️ [Groq API] Request exception: {e}")

    return None


BANNED_PLACEHOLDERS = [
    "insert 1-click", "what happens live under the hood",
    "relevant punchy notification twist", "stop crying human", "stop crying, human",
    "in 2024", "replaces paid tools",
    "open official site in any chrome or safari tab",
    "fixes routers with a shoe", "exact 1-click action",
    "run free pc cleaner locally",
    "zero-dollar workflows", "zero dollar workflows",
    "game-changer", "game changer", "revolutionize",
    "verified zero local installation", "unlock",
    "tether gimmick", "skeptical hype", "verified locally",
    "🚀", "⚡️", "⚡", "🤯",
]

HUMAN_SPEAKERS = {"junior_dev", "senior_dev", "friend_riya", "dad"}

_TOOL_CAPABILITY_WORDS = (
    "send", "transfer", "share", "clean", "wipe", "remove", "delete", "speed up",
    "speeds up", "edit", "merge", "split", "convert", "compress", "play", "block",
    "scan", "backup", "sync", "record", "turn", "summarize", "generate", "chat",
    "translate", "download", "search", "organize", "fix", "encrypt", "stream",
    "transcribe", "automate", "free up", "over local wi-fi", "over wi-fi",
    "between iphone",
)

_ANNOYANCE_OR_PAID_WORDS = (
    "$", "dollar", "bucks", "pay", "paid", "paying", "cost", "subscri", "fee",
    "expensive", "monthly", "yearly", "froze", "freeze", "slow", "crash", "lag",
    "bloat", "stuck", "broken", "upload", "limit", "watermark", "paywall",
    "cable", "emailing", "junk", "hours", "waste", "wasting", "annoying",
    "adobe", "ccleaner", "airdrop", "dropbox", "notion", "slack",
)


_DAD_THIRD_PERSON_RE = re.compile(
    r"\b(dad'?s|dad just|my dad|dad thinks|dad sets|dad installed|dad downloaded|dad covers|dad believes|dad is|dad got|dad won|dad wrapped|your dad|my boss)\b|^dad\b",
    re.IGNORECASE,
)


def _dad_topic_opener(title: str, category: str = "") -> str:
    """Returns a 1st-person Dad opener strictly matching the topic title/category."""
    text = f"{title} {category}".lower()
    if any(k in text for k in ["ram", "booster", "cleaner", "storage", "memory", "slow"]):
        return "Look how fast this turbo rocket cleaner makes my phone fly today!"
    if any(k in text for k in ["tv", "towel", "mic", "spy", "listening"]):
        return "I covered our Smart TV with a towel so it stops spying on us!"
    if any(k in text for k in ["5g", "wifi", "wi-fi", "router", "tower", "signal"]):
        return "I wrapped our Wi-Fi router in foil so 5G waves stay out!"
    if any(k in text for k in ["gold", "mod", "deleted message", "shady", "apk"]):
        return "Beta, this Gold WhatsApp link gave me free themes and deleted chats!"
    if any(k in text for k in ["scam", "whatsapp", "lottery", "prize", "iphone", "bank"]):
        return "Beta, I just won a brand new phone in this WhatsApp group!"
    if any(k in text for k in ["printer", "ink", "cyan", "cartridge"]):
        return "Why does this useless printer want blue ink just to print black text?!"
    if any(k in text for k in ["battery", "alarm", "unplug", "80"]):
        return "Beta, unplug my phone at eighty percent before the battery swells up!"
    return "Beta, come look at my phone right now, something crazy just popped up!"


def validate_screenplay_quality_gate(screenplay: Dict[str, Any], topic: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Programmatic Script Quality Gate:
    1. Reject if any banned placeholder, cryptic fragment, or AI slop phrases appear.
    2. Dynamic Cast Lock & Strict Alternation (no 2 consecutive turns from same speaker).
    3. Humans NEVER read steps ("Step 1/2/3") or install commands — only questions & reactions.
    4. Reel #1 (Tool/Repo):
       - 'tool_name' MUST be spoken naturally by Turn 2 or Turn 3.
       - Paid alternative / cost mention MUST appear in Turns 0..2.
       - Turns 0..4 MUST state in plain English the annoyance/paid app replaced AND what the tool does.
       - Average words per turn <= 16 words; total spoken words >= 135.
    5. Reel #2 (Dad clash / comedy):
       - dad MUST speak in FIRST PERSON. Reject if dad refers to 'Dad' in 3rd person.
       - Zero developer / GitHub / software-install / APK / 'use dad' / 'grab dad' terminology.
    6. Turn 9 Notification:
       - Must NOT match reel title or toast message verbatim.
       - Must NOT contain bullet symbols (•, |, —).
    7. Dialog turn count >= 13 and <= 15 (target 14 turns, ~165-195 words, 42-50s).
    """
    violations = []
    dialogue = screenplay.get("dialogue") or []
    if not isinstance(dialogue, list) or len(dialogue) < 13 or len(dialogue) > 15:
        violations.append(f"Dialogue turn count is {len(dialogue)}, must be between 13 and 15 turns.")
        return False, violations

    title = str(topic.get("title") or topic.get("topic_title") or "").lower()
    format_type = str(topic.get("format_type") or "").lower()
    left_char = str(topic.get("left_character") or screenplay.get("leftCharacterId") or "junior_dev").lower()
    right_char = str(topic.get("right_character") or screenplay.get("rightCharacterId") or "claude").lower()
    is_dad_skit = ("dad" in format_type) or (left_char == "dad") or ("dad" in title)

    # 1. Banned placeholder and AI slop check across all fields
    all_text_blobs = [str(d.get("text", "")) for d in dialogue]
    card_data = screenplay.get("cardData") or {}
    if isinstance(card_data, dict):
        for r in (card_data.get("rows") or []):
            if isinstance(r, dict):
                all_text_blobs.append(str(r.get("label", "")))
                all_text_blobs.append(str(r.get("value", "")))
    toast_data = screenplay.get("toastData") or {}
    if isinstance(toast_data, dict):
        all_text_blobs.append(str(toast_data.get("app_name", "")))
        all_text_blobs.append(str(toast_data.get("message", "")))
    end_card = screenplay.get("endCard") or {}
    if isinstance(end_card, dict):
        all_text_blobs.append(str(end_card.get("question", "")))
        all_text_blobs.append(str(end_card.get("cta_text", "")))

    full_screenplay_str = " ".join(all_text_blobs).lower()
    for ph in BANNED_PLACEHOLDERS:
        if ph in full_screenplay_str:
            violations.append(f"Found banned placeholder string '{ph}' in screenplay.")

    banned_generic = [
        "company documentation", "entire workflow", "manual work",
        "hours of coding", "manual coding", "overdue tickets"
    ]
    for phrase in banned_generic:
        if phrase in full_screenplay_str:
            violations.append(f"Found banned generic phrase '{phrase}' in screenplay.")

    if "monthly router bill" in full_screenplay_str and "router" not in title and "wifi" not in title:
        violations.append("Found 'monthly router bill' in screenplay for non-router topic.")

    # 2. Dynamic Cast Lock & Strict Alternation
    active_cast = topic.get("active_cast") or screenplay.get("active_cast")
    if not active_cast or not isinstance(active_cast, (list, tuple)):
        active_cast = [left_char, right_char]
    cast_set = {str(c).lower().strip() for c in active_cast}

    # Verify every cast member has a Kokoro voice spec
    try:
        from engine.tts_engine import CHARACTER_VOICE_REF_SPECS
        for c in cast_set:
            if c not in CHARACTER_VOICE_REF_SPECS:
                violations.append(f"Cast member '{c}' is missing from CHARACTER_VOICE_REF_SPECS.")
    except ImportError:
        pass

    prev_speaker = None
    for idx, d in enumerate(dialogue):
        spk = str(d.get("speaker") or d.get("character_id") or "").lower()
        if spk not in cast_set:
            violations.append(f"Turn {idx} speaker '{spk}' is not one of cast {cast_set}.")
        if prev_speaker and spk == prev_speaker:
            violations.append(f"Consecutive turns {idx-1} and {idx} have same speaker '{spk}' (strict alternation required).")
        prev_speaker = spk

        # Human rule: Humans never read steps or install commands!
        if spk in HUMAN_SPEAKERS:
            txt_low = str(d.get("text", "")).lower()
            if any(s in txt_low for s in ["step 1", "step 2", "step 3", "step one", "step two", "step three"]):
                violations.append(f"Human speaker '{spk}' recited tutorial steps in Turn {idx}: '{txt_low[:35]}...'")
            if any(cmd in txt_low for cmd in ["git clone", "pip install", "npm install", "brew install", "apt-get"]):
                violations.append(f"Human speaker '{spk}' recited CLI install command in Turn {idx}: '{txt_low[:35]}...'")

    # 3. Turn 9 Notification Checks
    if len(dialogue) > 9:
        turn_9 = dialogue[9]
        t9_text = str(turn_9.get("text", "")).strip()
        t9_lower = t9_text.lower()
        clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", title).strip()
        if len(clean_title) > 10 and clean_title in t9_lower:
            violations.append("Turn 9 repeats the reel title verbatim instead of reacting in character.")
        toast_msg = str(toast_data.get("message", "")).lower()
        if len(toast_msg) > 10 and toast_msg in t9_lower:
            violations.append("Turn 9 repeats the notification toast message verbatim.")
        if any(sym in t9_text for sym in ["•", "|", "—"]):
            violations.append("Turn 9 contains forbidden bullet/glitch symbols ('•', '|', '—').")

    # 4. Word count checks (minimum 135 spoken words so video stays >40s)
    word_counts = [len(str(d.get("text", "")).split()) for d in dialogue]
    total_words = sum(word_counts)
    avg_words = total_words / len(word_counts) if word_counts else 0
    if total_words < 135:
        violations.append(f"Total spoken word count is {total_words} (minimum: 135 words for >40s duration).")
    if avg_words > 16.0:
        violations.append(f"Average turn length is {avg_words:.1f} words (limit: 16 words per turn).")

    # 5. Reel #1 vs Reel #2 checks
    all_turns_text = " ".join(str(d.get("text", "")) for d in dialogue).lower()
    if is_dad_skit:
        banned_dad_terms = ["github", "repo", "git clone", "pip install", "npm install", "pull request"]
        for term in banned_dad_terms:
            if term in all_turns_text:
                violations.append(f"Found developer term '{term}' in Dad clash comedy script.")
        for term in ("free apk", "from its site", "use dad", "grab dad"):
            if re.search(rf"\b{re.escape(term)}\b", full_screenplay_str):
                violations.append(f"Found forbidden software-template phrase '{term}' in Dad clash script.")

        # Dad 1st-person POV lock: Dad must NEVER speak about himself as 'Dad' in 3rd person!
        dad_turns = [d.get("text", "") for d in dialogue if str(d.get("speaker") or d.get("character_id")).lower() == "dad"]
        for dt in dad_turns:
            if _DAD_THIRD_PERSON_RE.search(dt):
                violations.append(f"Dad spoke in 3rd person in turn: '{dt[:45]}...'")
    else:
        tool_name = str(topic.get("tool_name") or topic.get("toolName") or "").strip().lower()
        if tool_name and tool_name not in {"opentool", "ai", "app", "tool", "freetool"}:
            early_turns = " ".join(str(dialogue[i].get("text", "")) for i in range(min(4, len(dialogue)))).lower()
            if tool_name not in early_turns:
                violations.append(f"tool_name '{tool_name}' was not spoken in Turns 0-3.")

        turns_0_2 = " ".join(str(dialogue[i].get("text", "")) for i in range(min(3, len(dialogue)))).lower()
        cost_indicators = ["$", "dollar", "pay", "paid", "cost", "subscri", "fee", "twenty", "expensive", "free", "hundred"]
        if not any(ci in turns_0_2 for ci in cost_indicators):
            violations.append("No paid alternative, cost ($/dollars), or fee contrast in Turns 0-2.")

        turns_0_4 = " ".join(str(dialogue[i].get("text", "")) for i in range(min(5, len(dialogue)))).lower()
        replaces_paid = str(topic.get("replaces_paid_app") or "").strip().lower()
        replaces_tokens = [w for w in re.findall(r"[a-z0-9]+", replaces_paid) if len(w) >= 4]
        has_annoyance_or_paid = any(tok in turns_0_4 for tok in replaces_tokens) or any(w in turns_0_4 for w in _ANNOYANCE_OR_PAID_WORDS)
        if not has_annoyance_or_paid:
            violations.append("Turns 0-4 must clearly name the everyday annoyance or paid app being replaced.")

        title_tokens = {
            w for w in re.findall(r"[a-z0-9]+", title)
            if len(w) >= 4 and w not in {"free", "open", "source", "tool", "apps", "best", "this", "that", "with", "your", "from"} and w != tool_name
        }
        has_capability = any(
            re.search(rf"\b{re.escape(w)}", turns_0_4) for w in _TOOL_CAPABILITY_WORDS
        ) or any(re.search(rf"\b{re.escape(tok)}\b", turns_0_4) for tok in title_tokens)
        if not has_capability:
            violations.append("Turns 0-4 must state in plain conversational English what the free tool actually does.")

    return len(violations) == 0, violations


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
        format_type = str(topic.get("format_type") or "").lower()
        is_dad_topic = (
            "dad" in format_type
            or str(topic.get("left_character") or "").lower() == "dad"
            or "dad" in str(title or "").lower()
        )

        dad_hook_rule = (
            "\nDAD CLASH 1ST-PERSON POV LOCK (CRITICAL):\n"
            "- Turn 0 is spoken BY Dad himself. Write ALL 3 hooks in Dad's 1st-person voice ('Beta, this Gold WhatsApp link gave me free themes!', 'I covered the TV with a towel!').\n"
            "- STRICTLY FORBIDDEN: Never start with 'Dad', 'Dad's', or 'My dad' in 3rd person.\n"
            if is_dad_topic
            else ""
        )

        system_instruction = (
            "You are HookMaster: The World's Foremost 0-3s Short-Form Video Retention Scientist.\n"
            "Your motto: The first 3 seconds decide if 100,000 people watch or swipe away.\n\n"
            "STRICT VOCABULARY RULE (SIMPLE SPOKEN ENGLISH ONLY - 6th to 8th GRADE LEVEL):\n"
            "- Explicitly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', 'workflow', 'manual coding', 'leverage', 'unlock'.\n"
            "- Write in short, punchy, everyday spoken English that anyone on Instagram understands instantly.\n\n"
            "STORY-FIRST DRAMATIC PATTERN-INTERRUPT HOOK (ZERO GENERIC / AD OPENERS):\n"
            "- STRICTLY BANNED OPENERS: 'Bro your slow workflow...', 'Humans love doing...', 'Humans love...', 'Wait there is no way...', 'There is no way...', 'Look at this tool right now...', 'Stop doing X by hand...', 'Why is nobody talking about...', 'Check this tool out'.\n"
            "- MANDATORY: Start with a concrete 0-3s pattern-interrupt contrast or shock (e.g. 'Still paying twenty dollars a month to edit PDFs?', 'Beta, this Gold WhatsApp link gave me free themes!', 'My laptop literally froze opening a two-megabyte file.').\n"
            "- MAXIMUM 10 WORDS. Zero exceptions.\n"
            "- ZERO FILLER: Never start with 'Hey guys', 'Did you know', 'So today'."
            f"{dad_hook_rule}\n\n"
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
Write 3 competing opening hooks (each <= 10 words, simple spoken English only, {"1st-person Dad voice speaking Turn 0 ('Beta, ...' or 'I ...', NEVER 'Dad...')" if is_dad_topic else "story-first human shock mid-conversation"}).
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
                        elif is_dad_topic:
                            win_h = _dad_topic_opener(title or "", category)
                        else:
                            win_h = f"Wait... why am I paying monthly fees for this?"
                    if is_dad_topic and _DAD_THIRD_PERSON_RE.search(win_h):
                        win_h = _dad_topic_opener(title or "", category)
                    parsed["winning_hook"] = win_h
                    for h in parsed.get("hooks", []):
                        if "hook" in h:
                            cleaned_h = sanitize_simple_spoken_english(h["hook"])
                            if is_dad_topic and _DAD_THIRD_PERSON_RE.search(cleaned_h):
                                cleaned_h = _dad_topic_opener(title or "", category)
                            h["hook"] = cleaned_h
                    return parsed
            except Exception as e:
                print(f"⚠️ HookMaster: Hook battle parse error: {e}")

        # Deterministic fallback battle in story-first spoken English
        cat_lower = str(category).lower() + " " + str(title).lower()
        is_dad_topic = "dad" in cat_lower or "dad" in str(topic.get("format_type", "")).lower() or topic.get("left_character") == "dad"
        if is_dad_topic:
            fallback_h1 = _dad_topic_opener(title or "", category)
            fallback_h2 = "Beta, stop touching my phone settings, I know what I am doing!"
            fallback_h3 = "Why is my device acting weird after I followed that WhatsApp video?"
        elif "pdf" in cat_lower:
            fallback_h1 = "Still paying twenty dollars a month to edit PDFs?"
            fallback_h2 = "Wait... Adobe charged me twenty bucks just to sign this?"
            fallback_h3 = "Why am I paying twenty dollars to merge two files?"
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
    # STEP B: 5-ACT VIRAL MEME SCREENPLAY (14 Natural Turns, 42-50s, Multi-Step Proof Card, Toast, End-Card)
    # =========================================================================

    def craft_screenplay(
        self,
        topic: Dict[str, Any],
        hook_battle_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Writes a 14-turn dialogue (42-50s, 10-15 words/turn, ~165-195 spoken words) following a 5-act viral arc:
        - Act 1 (Turns 0-1): Scroll-Stop Hook & Smug AI Roast
        - Act 2 (Turns 2-4): Everyday Annoyance / Paid App Replaced + What Tool Does
        - Act 3 (Turns 5-7): 3-Step Interactive Proof Card (Row 1 on Turn 5, Row 2 on Turn 6, Row 3 on Turn 7)
        - Act 4 (Turns 8-10): Human Reaction & Savage iOS Notification Twist on Turn 9
        - Act 5 (Turns 11-13): Payoff Banter + Final Burn + Spoken CTA + 2.5s Black End-Card Ragebait Question
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
        is_dad = "dad" in format_type or left_char == "dad" or "dad" in str(topic.get("title", "")).lower()
        is_gh = any(term in str(category).lower() or term in str(title).lower() for term in ["github", "repo", "open-source", "open source"])
        link_target = "GitHub repo link" if is_gh else "free link"

        # Cast resolution: support topic-specified active_cast or default to left/right pair
        raw_cast = topic.get("active_cast")
        if raw_cast and isinstance(raw_cast, (list, tuple)) and len(raw_cast) >= 2:
            active_cast = [str(c).strip() for c in raw_cast]
            left_char = active_cast[0]
            right_char = active_cast[1]
        elif is_dad:
            left_char = "dad"
            right_char = "gemini" if "gemini" in str(topic.get("right_character", "")).lower() else "claude"
            active_cast = [left_char, right_char]
        else:
            left_char = str(topic.get("left_character") or "junior_dev")
            right_char = str(topic.get("right_character") or ("claude" if "claude" in str(topic.get("right_character", "")).lower() else "gemini"))
            active_cast = [left_char, right_char]

        real_steps = topic.get("real_steps") or topic.get("realSteps") or []
        replaces_paid = str(topic.get("replaces_paid_app") or "").strip()
        what_it_does = str(topic.get("real_description") or topic.get("description") or topic.get("readme_summary") or topic.get("core_conflict") or "").strip()

        if is_dad:
            # Never derive a software tool_name (like "Dad") for dad_clash scripts
            tool_name = ""
            brand_domain = ""
            github_repo = ""
        else:
            tool_name = str(topic.get("tool_name") or topic.get("toolName") or "").strip()
            brand_domain = str(topic.get("brand_domain") or topic.get("brandDomain") or "").strip()
            github_repo = str(topic.get("github_repo") or topic.get("githubRepo") or "").strip()
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
            final_turn_cta = f"Comment {kw} and I will send you the {link_target} right now."
            end_card_cta = f"Comment {kw} for the {link_target}"
            end_card_question = f"Still paying for this when {tool_name} exists? Be honest"
        else:
            kw = ""
            if is_doc:
                cta_phrase = topic.get("cta_phrase") or "Tag that dev in your group whose credits just ran out."
                final_turn_cta = "Tag that dev in your group whose credits just ran out."
                end_card_cta = "TAG THAT DEV BELOW"
                end_card_question = "Could you survive 24 hours coding without AI?"
            elif is_dad:
                cta_phrase = topic.get("cta_phrase") or "Send this to your Dad before he gets tricked again!"
                t_lower = (str(title) + " " + format_type).lower()
                if "battery" in t_lower or "alarm" in t_lower or "unplug" in t_lower or "80" in t_lower:
                    final_turn_cta = "Send this to your Dad before he wakes up at 3 AM to unplug his phone!"
                elif "ram" in t_lower or "cleaner" in t_lower or "booster" in t_lower:
                    final_turn_cta = "Send this to your Dad before he installs another phone booster app!"
                elif "gold" in t_lower or "mod" in t_lower or "deleted message" in t_lower or "shady" in t_lower:
                    final_turn_cta = "Send this to your Dad before a shady chat theme steals his contacts!"
                elif "scam" in t_lower or "whatsapp" in t_lower or "lottery" in t_lower or "prize" in t_lower:
                    final_turn_cta = "Send this to your Dad before he forwards another lottery link!"
                elif "printer" in t_lower or "cartridge" in t_lower:
                    final_turn_cta = "Send this to your Dad before he attacks the printer with a hammer!"
                elif "tv" in t_lower or "mic" in t_lower or "towel" in t_lower:
                    final_turn_cta = "Send this to your Dad before he wraps the TV in another towel!"
                elif "5g" in t_lower or "wifi" in t_lower or "wi-fi" in t_lower or "router" in t_lower:
                    final_turn_cta = "Send this to your Dad before he wraps the Wi-Fi router in foil!"
                else:
                    final_turn_cta = "Send this to your Dad or friend before they get tricked again!"
                end_card_cta = "SEND TO YOUR DAD OR FRIEND"
                end_card_question = "Does your Dad do this with his tech too? Be honest"
            else:
                cta_phrase = topic.get("cta_phrase") or "Tag that dev in your group who still codes without AI."
                final_turn_cta = "Tag that dev in your group who still codes without AI."
                end_card_cta = "TAG THAT DEV IN YOUR GROUP"
                end_card_question = "Who in your group is this developer?"

        winning_hook = sanitize_simple_spoken_english(hook_battle_result.get("winning_hook", f"Look at {title}."))
        if is_dad:
            # Ensure winning hook for Dad is strictly 1st-person and matches the actual topic
            if (
                not winning_hook
                or _DAD_THIRD_PERSON_RE.search(winning_hook)
                or ("unplug" in winning_hook.lower() and not any(k in str(title).lower() for k in ["battery", "alarm", "unplug", "80"]))
            ):
                winning_hook = _dad_topic_opener(title or "", category)

        step1_val = real_steps[0] if len(real_steps) > 0 else f"Open {brand_domain or tool_name} in your browser"
        step2_val = real_steps[1] if len(real_steps) > 1 else f"Run {tool_name} directly with zero setup"
        step3_val = real_steps[2] if len(real_steps) > 2 else f"100% Free with zero monthly fees"

        system_instruction = (
            "You are HookMaster: Screenplay & Dialogue Specialist writing 9:16 vertical 3D dialogue reels.\n"
            "DURATION & LENGTH TARGET (42-50 SECONDS, NEVER UNDER 40s):\n"
            "- Write EXACTLY 14 natural conversational turns (10-15 words per turn, ~165-195 total spoken words).\n"
            "- Never write short cryptic fragments or fewer than 135 total spoken words.\n\n"
            "VOICE & TONE (NATURAL CONVERSATIONAL ENGLISH):\n"
            "- Write like a real 3-year experienced software engineer talking naturally to a peer (or stubborn Dad vs AI for dad_clash).\n"
            "- Natural contractions (you're, didn't, don't, I'm, that's), zero hype fluff, zero corporate buzzwords.\n\n"
            "STRICT VOCABULARY BAN (SIMPLE SPOKEN ENGLISH ONLY - 6th to 8th GRADE LEVEL):\n"
            "- Strictly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', 'workflow', 'manual coding', 'leverage', 'unlock', or any corporate buzzwords.\n\n"
            "EXPLICITLY BANNED AI SLOP, CRYPTIC FRAGMENTS & PLACEHOLDERS:\n"
            "- Do NOT use: '🚀', '⚡️', '⚡', '🤯', 'Unlock', 'zero-dollar workflows', 'Stop crying human', 'game-changer', 'revolutionize', 'verified zero local installation', 'verified locally', 'tether gimmick', 'Skeptical hype', 'in 2024', 'insert 1-click', 'what happens live under the hood', 'Wait there is no way', 'There is no way', 'Humans love', 'Look at step one', 'Wait step two says', 'zero dollar cost', 'fixes routers with a shoe'.\n\n"
            "- CHARACTER ROLES & POV LOCK:\n"
            f"- Cast Roster: {active_cast}. All dialogue turns MUST come from this roster.\n"
            "- HUMANS (junior_dev, senior_dev, friend_riya, dad) NEVER recite 'Step 1/2/3', install commands, or tutorial lists. They ONLY react, push back, or ask sharp practical questions ('Wait, does it wipe my browser logins?', 'Does that actually run offline?').\n"
            "- REEL #1 (Software/Tool) RULE FOR TURNS 0-4: Clearly state in plain conversational English (1) the exact everyday annoyance or paid app being replaced, and (2) what the free tool actually does (e.g., sends files between iPhone, Android, and Windows over local Wi-Fi).\n"
            "- DAD CLASH RULE: Pure funny Dad-vs-AI banter matched strictly to the topic title. Dad MUST speak in FIRST PERSON ('Beta, ...', 'My phone...', 'I read on WhatsApp...'). NEVER mention 'free apk', 'from its site', 'use dad', 'grab dad', GitHub, or software install instructions.\n"
            "- ACT 3 BEAT SHEET (Turns 5-9):\n"
            f"  * Turn 5 ({right_char} / AI): Explains how it works / real facts (part 1).\n"
            f"  * Turn 6 ({left_char} / Human): Pushes back or asks a sharp, skeptical follow-up question — NEVER recite steps.\n"
            f"  * Turn 7 ({right_char} / AI): Answers clearly with the practical payoff.\n"
            f"  * Turn 8 ({left_char} / Human): Reacts in character.\n"
            f"  * Turn 9 ({right_char} / AI): In-character reaction to the notification toast (never repeating the toast or title verbatim).\n"
            "- STRICT ALTERNATION: Never have 2 consecutive turns from the same speaker.\n"
            "- Turn 9 DIALOGUE: Spoken by one of the cast reacting in character. NEVER read notification or title verbatim, NEVER include bullets ('•', '|', '—').\n"
            f"- Turn 13 (Final Turn) MUST end with: '{final_turn_cta}'"
        )

        if is_dad:
            topic_context_block = (
                f"Topic: {title}\nCategory: {category}\nFormat Type: {format_type}\n"
                f"Comedy Structure: {comedy_structure}\nWinning Hook (Turn 0 line): \"{winning_hook}\"\n"
                f"Cast: {active_cast}\nScene Preset: {scene_preset}"
            )
            task_rules_block = (
                f"Write the complete 5-act Remotion screenplay JSON with 14 natural dialogue turns (10-15 words/turn, 165-195 total words).\n"
                f"- Turn 0 MUST be {left_char} speaking: \"{winning_hook}\"\n"
                f"- Turns 1-12: Pure funny Dad-vs-AI household tech banter strictly about '{title}', Dad in 1st person.\n"
                f"- Zero APK, install, GitHub, 'from its site', or 'use dad' talk.\n"
                f"- Turn 9 ({right_char}): In-character reaction to the notification toast (never repeating toast or title verbatim).\n"
                f"- Turn 13 ({right_char}): Final punchline ending with: \"{final_turn_cta}\""
            )
            card_schema_block = '"cardData": null,'
            toast_msg_example = "Household Alert: Dad's WhatsApp myth has been officially debunked"
            dialogue_schema_lines = (
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Dad, please stop believing every wild tech rumor people forward on WhatsApp.", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "The video had a doctor and three warning sirens so it must be true!", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Anyone can add fake sirens to a clip just to get clicks.", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Then explain why the exact thing happened to my cousin last week!", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "That happened for a completely normal reason, not the scary myth online.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Wait, so I have been panicking in the living room for nothing?", "emotion": "shocked", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Yes, modern devices already protect themselves without any weird household tricks.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Fine, let me check this notification that just popped up right now.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Even your own phone is telling you to relax and leave it alone.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Okay, I admit you were right this one time, do not tell mom.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Deal, just promise you will ask me before trying the next viral hack.", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Fine, I am deleting that family forward before anyone else copies me.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "{final_turn_cta}", "emotion": "smug", "pause_after": 0.40}}'
            )
        else:
            topic_context_block = (
                f"Topic: {title}\nCategory: {category}\nFormat Type: {format_type}\n"
                f"Tool Name: {tool_name}\nBrand Domain: {brand_domain}\nGitHub Repo: {github_repo}\n"
                f"Replaces Paid App / Annoyance: {replaces_paid}\nWhat It Does: {what_it_does}\n"
                f"Comedy Structure: {comedy_structure}\nWinning Hook (Turn 0 line): \"{winning_hook}\"\n"
                f"Cast: {active_cast}\nScene Preset: {scene_preset}\nAuto-DM Keyword: {kw}"
            )
            task_rules_block = (
                f"Write the complete 5-act Remotion screenplay JSON with 14 natural dialogue turns (10-15 words/turn, 165-195 total words).\n"
                f"- Turn 0 MUST be {left_char} speaking: \"{winning_hook}\"\n"
                f"- Turns 0-4: Clearly state in plain conversational English (1) the exact everyday annoyance or paid app being replaced, and (2) what '{tool_name}' actually does.\n"
                f"- By Turn 2 or Turn 3: The exact name '{tool_name}' MUST be spoken naturally.\n"
                f"- Turn 5 ({right_char} / AI): Explains how to get and run {tool_name} (part 1).\n"
                f"- Turn 6 ({left_char} / Human): Asks a sharp, skeptical follow-up question — NEVER a step.\n"
                f"- Turn 7 ({right_char} / AI): Answers the question and finishes the practical payoff.\n"
                f"- Turn 8 ({left_char} / Human): Reacts to seeing it actually work.\n"
                f"- Turn 9 ({right_char} / AI): In-character reaction to the notification toast (never repeating the toast or title verbatim).\n"
                f"- Turns 10-12: Natural techie payoff and cancellation reaction.\n"
                f"- Turn 13 ({right_char} / AI): MUST end with: \"{final_turn_cta}\""
            )
            card_schema_block = f'''"cardData": {{
    "title": "{clean_headline_truncation(title, 26)} Breakdown",
    "subtitle": "Step-by-step verified specs",
    "badge": "VERIFIED PROOF",
    "rows": [
      {{
        "label": "Step 1: Setup",
        "value": "{step1_val}",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 2: Execution",
        "value": "{step2_val}",
        "status": "VERIFIED",
        "isPositive": true
      }},
      {{
        "label": "Step 3: Payoff",
        "value": "{step3_val}",
        "status": "PROVEN",
        "isPositive": true
      }}
    ],
    "startTurn": 5,
    "endTurn": 7,
    "durationSeconds": 12.0
  }},'''
            toast_msg_example = f"Task complete with {tool_name}: $0 spent on your own device"
            dialogue_schema_lines = (
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "{winning_hook}", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Why are you still paying twenty dollars a month when {tool_name} is free?", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Wait, what does {tool_name} actually do instead of that paid app?", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "It handles the whole job right on your own computer without monthly fees.", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Okay, show me how it works before my card gets charged again.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "First, open {brand_domain or tool_name} and run it directly with zero bloat.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Wait, does that wipe my saved files or require any paid account?", "emotion": "shocked", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Not at all, everything stays completely private on your device for zero dollars.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Whoa, it just finished in two seconds without freezing my whole screen.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "And your card app just saved you two hundred dollars this year.", "emotion": "smug", "pause_after": 0.30}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "I cannot believe I paid every single month for something this simple.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "Cancel that subscription tonight and keep your money in your own pocket.", "emotion": "smug", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{left_char}", "character_id": "{left_char}", "text": "Done, I am switching our entire team over to {tool_name} right now.", "emotion": "shocked", "pause_after": 0.25}},\n'
                f'    {{"speaker": "{right_char}", "character_id": "{right_char}", "text": "{final_turn_cta}", "emotion": "smug", "pause_after": 0.40}}'
            )

        prompt = f"""
{topic_context_block}

TASK:
{task_rules_block}

JSON Schema:
{{
  "title": "{title[:50]}",
  "style": "{scene_preset}",
  "comp": "MasterAutonomousReel",
  "scenePreset": "{scene_preset}",
  "leftCharacterId": "{left_char}",
  "rightCharacterId": "{right_char}",
  "active_cast": {json.dumps(active_cast)},
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
  {card_schema_block}
  "toastData": {{
    "app_name": "System Alert",
    "sender": "Security",
    "message": "{toast_msg_example}",
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
{dialogue_schema_lines}
  ]
}}
"""

        screenplay = None
        current_prompt = prompt
        for attempt in range(4):
            if attempt > 0:
                time.sleep(3)
            raw_json = self._call_llm(current_prompt, system_instruction)
            if raw_json:
                try:
                    cleaned = raw_json.strip()
                    if cleaned.startswith("```"):
                        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                        cleaned = re.sub(r"\n```$", "", cleaned)
                    parsed = json.loads(cleaned.strip())
                    if "dialogue" in parsed and len(parsed["dialogue"]) >= 13:
                        cast_val = parsed.get("cast")
                        if (
                            is_dad
                            or "dad" in format_type
                            or str(parsed.get("leftCharacterId") or "").lower() == "dad"
                            or (isinstance(cast_val, dict) and str(cast_val.get("left") or "").lower() == "dad")
                        ):
                            parsed["cardData"] = None
                            parsed["proof_steps"] = []
                            parsed["proofImagePath"] = None
                            parsed["logoPath"] = None
                        is_valid, violations = validate_screenplay_quality_gate(parsed, topic)
                        if is_valid:
                            screenplay = parsed
                            break
                        else:
                            print(f"⚠️ [HookMaster] LLM screenplay attempt {attempt + 1} failed quality gate: {violations}")
                            extra_rule = (
                                "keep Dad in 1st person with zero APK/install/software-site talk"
                                if is_dad
                                else f"ensure tool_name '{tool_name}' is spoken by Turn 2-3, paid app/annoyance AND what the tool does are clear in plain English in Turns 0-4"
                            )
                            current_prompt = prompt + f"\n\nCRITICAL FIXES REQUIRED (Previous attempt failed with: {violations}):\nWrite 14 natural turns (10-15 words/turn, >=135 total words), strict alternation between {left_char} and {right_char}, {extra_rule}, Turn 9 reacts in character without bullets, and strictly avoid any banned fragments or placeholder phrases."
                except Exception as e:
                    print(f"⚠️ HookMaster: Screenplay parse error attempt {attempt + 1}: {e}")

        if not screenplay:
            print("⚠️ [HookMaster] LLM unavailable or failed quality gate; using broadcast fallback screenplay.")
            screenplay = self._fallback_screenplay(topic, winning_hook, left_char, right_char, scene_preset, kw)
            is_valid, violations = validate_screenplay_quality_gate(screenplay, topic)
            if not is_valid:
                raise RuntimeError(f"Fallback screenplay failed quality gate: {violations}")

        # Enforce guarantees
        screenplay["leftCharacterId"] = left_char
        screenplay["rightCharacterId"] = right_char
        screenplay["active_cast"] = active_cast
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

        # Ensure cardData exists and has multi-step structure in simple English for tools (never dad_clash)
        if not is_dad and format_type != "dad_clash" and left_char != "dad":
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
                    {"label": "Step 1: Setup", "value": step1_val, "status": "VERIFIED", "isPositive": True},
                    {"label": "Step 2: Execution", "value": step2_val, "status": "VERIFIED", "isPositive": True},
                    {"label": "Step 3: Payoff", "value": step3_val, "status": "PROVEN", "isPositive": True},
                ]
            card_d["items"] = card_d["rows"]
        else:
            screenplay["cardData"] = None
            screenplay["proof_steps"] = []
            screenplay["proofImagePath"] = None
            screenplay["logoPath"] = None

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

        card_d = screenplay.get("cardData")
        if card_d and isinstance(card_d, dict):
            for row in card_d.get("rows", []):
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
        screenplay["format_type"] = format_type

        cast_val = screenplay.get("cast")
        if (
            is_dad
            or "dad" in format_type
            or str(screenplay.get("leftCharacterId") or "").lower() == "dad"
            or (isinstance(cast_val, dict) and str(cast_val.get("left") or "").lower() == "dad")
        ):
            screenplay["cardData"] = None
            screenplay["proof_steps"] = []
            screenplay["proofImagePath"] = None
            screenplay["logoPath"] = None

        return screenplay

    def _describe_tool_for_dialogue(
        self,
        topic: Dict[str, Any],
        tool_name: str,
        title: str,
        cat_lower: str,
        real_steps: List[str],
    ) -> Tuple[str, str]:
        """Returns plain-English (annoyance_or_paid_app, what_tool_does) for Reel #1 Turns 0-4."""
        replaces_paid = str(topic.get("replaces_paid_app") or "").strip()
        real_desc = sanitize_simple_spoken_english(
            str(topic.get("real_description") or topic.get("description") or topic.get("readme_summary") or "").strip()
        )
        t_low = f"{cat_lower} {tool_name.lower()}"

        if any(k in t_low for k in ["localsend", "airdrop", "transfer", "file share"]):
            annoyance = replaces_paid or "emailing yourself files or fighting AirDrop across Android and Windows"
            does = f"{tool_name} sends full-size files between iPhone, Android, and Windows over local Wi-Fi"
        elif any(k in t_low for k in ["bleachbit", "cleaner", "bloat", "ccleaner"]):
            annoyance = replaces_paid or "CCleaner Pro subscriptions and a freezing, bloated laptop"
            does = f"{tool_name} wipes hidden junk files, browser cache, and old system logs fast"
        elif any(k in t_low for k in ["pdf", "stirling"]):
            annoyance = replaces_paid or "paying Adobe twenty dollars every month just to edit files"
            does = f"{tool_name} merges, splits, signs, and converts huge PDF files right on your machine"
        elif any(k in t_low for k in ["vice", "gta", "emulator", "retro", "game"]):
            annoyance = replaces_paid or "downloading eighty gigabytes of bloated game installers"
            does = f"{tool_name} lets you play classic retro console games smoothly inside your browser"
        elif any(k in t_low for k in ["notebook", "podcast", "summary"]):
            annoyance = replaces_paid or "spending hours reading two-hundred-page documents by hand"
            does = f"{tool_name} turns messy documents into clear audio briefings and grounded answers"
        elif any(k in t_low for k in ["ollama", "local ai", "llm"]):
            annoyance = replaces_paid or "paying twenty-dollar monthly AI subscriptions"
            does = f"{tool_name} lets you chat with fast open-weight AI models privately on your laptop"
        else:
            annoyance = replaces_paid or "paying twenty dollars every month for bloated cloud apps"
            if real_desc:
                snippet = clean_headline_truncation(real_desc.split(".")[0], 68).rstrip(".")
                does = f"{tool_name} {snippet[0].lower() + snippet[1:]}" if len(snippet) > 3 else f"{tool_name} automates the whole job on your device"
            elif real_steps:
                step_clean = re.sub(r"^\d+\.\s*", "", str(real_steps[0])).strip()
                does = f"{tool_name} lets you {step_clean[0].lower() + step_clean[1:]}" if step_clean else f"{tool_name} automates the task cleanly in seconds"
            else:
                does = f"{tool_name} automates {clean_headline_truncation(title, 34).lower()} without monthly fees"
        return annoyance, does

    def _fallback_screenplay(
        self,
        topic: Dict[str, Any],
        hook: str,
        left_char: str,
        right_char: str,
        scene_preset: str,
        kw: str,
    ) -> Dict[str, Any]:
        """Deterministic, topic-aware 14-turn 5-act fallback screenplay (42-50s, ~165-195 spoken words)."""
        title = topic.get("title") or topic.get("topic_title") or "Daily Tech Breakdown"
        category = topic.get("category", "")
        cat_lower = (str(category) + " " + str(title)).lower()
        format_type = str(topic.get("format_type") or "").lower()
        is_dad = (left_char == "dad") or ("dad" in str(title).lower()) or ("dad" in format_type)
        has_res = topic.get("has_resource_link", not (format_type in ["discovery_doc", "funny_story"] or "discovery" in cat_lower or is_dad))
        is_gh = any(term in cat_lower for term in ["repo", "github", "open-source", "open source"])
        link_desc = "GitHub repo link" if is_gh else "free link"
        real_steps = topic.get("real_steps") or topic.get("realSteps") or []

        if is_dad:
            # Completely separate Dad clash from software-tool fields
            tool_name = ""
            brand_domain = ""
            github_repo = ""
            structure = "dad_interrogation"
            if (
                not hook
                or re.search(r"\b(dad just|my dad|dad sets|dad thinks|dad installed|dad downloaded|dad covers)\b", str(hook).lower())
                or ("unplug" in str(hook).lower() and not any(k in cat_lower for k in ["battery", "alarm", "unplug", "80"]))
            ):
                hook = _dad_topic_opener(title, category)

            badge = "DAD TECH AUDIT"
            card_title = clean_headline_truncation(title, 20)
            rows = []
            has_res = False
            kw = ""
            cta_phrase = "Send this to your Dad before he gets tricked again!"
            end_card_cta = "SEND TO YOUR DAD OR FRIEND"
            end_question = "Does your Dad do this with his tech too? Be honest"

            if any(k in cat_lower for k in ["battery", "alarm", "unplug", "80"]):
                final_turn_cta = "Send this to your Dad before he wakes up at 3 AM to unplug his phone!"
                toast = {
                    "app_name": "Battery Guard",
                    "sender": "Battery Guard",
                    "message": "Charging paused automatically at 80% to preserve lifespan",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, modern phones have smart charge chips inside, so nothing is going to explode tonight.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "My WhatsApp uncle group sent a video saying one hundred percent ruins the battery!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your phone automatically stops drawing wall power the second it hits full charge.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Then explain why Sharma ji's phone battery swelled up like a cricket ball!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Because he bought a cheap two-dollar fake cable outside the railway station.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, so I have been waking up at three every morning for nothing?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Yes, your phone slows down charging overnight by itself to protect battery health.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hold on, why did my screen just light up on the coffee table?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "See, your phone paused charging on its own without any midnight alarm clock.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, that built-in setting actually saved me from losing sleep every night?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Exactly, now turn off those four alarms and finally get some proper sleep.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Fine, I am cancelling the three AM alarm, do not tell your mother.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif any(k in cat_lower for k in ["gold", "mod", "deleted message", "shady", "apk"]):
                final_turn_cta = "Send this to your Dad before a shady chat theme steals his contacts!"
                toast = {
                    "app_name": "Phone Shield",
                    "sender": "Device Guard",
                    "message": "Suspicious app blocked from reading SMS codes and contacts",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, where on earth did you even get a golden chat theme from?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Gupta ji forwarded it in our morning walk group, it looks very royal!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Official chat apps never come in shiny gold editions with secret spying powers.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Why are you panicking? It already showed me who deleted messages last Tuesday!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Meanwhile that shady theme just copied every contact number and photo on your phone.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, why would a gold colour theme care about my family phone numbers?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Because scammers use shiny fake themes to read your bank alert text messages.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hold on, why are fifteen random flashlights and popups blinking on my screen?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your phone security just caught that gold app sneaking into your text codes.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Delete that golden rubbish right now, I do not need deleted messages!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Already removed, and stick to the normal green app from now on please.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "I am calling Gupta ji right now to warn the whole morning walk group.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif any(k in cat_lower for k in ["scam", "whatsapp", "lottery", "iphone", "bank"]):
                final_turn_cta = "Send this to your Dad before he forwards another lottery link!"
                toast = {
                    "app_name": "Security Guard",
                    "sender": "Security Alert",
                    "message": "Phishing Link Blocked: Fake Prize Neutralized",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, please do not forward that prize message to twenty different family groups.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Look at the message, it has a gold badge and says congratulations, sir!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Scammers built that fake page three hours ago just to steal bank passwords.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "They only asked for my card number to pay ten rupees courier shipping!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "That tiny ten-rupee shipping form empties your entire savings account in thirty seconds.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, so nobody is actually sending a free flagship phone to our house?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Not a single company gives away phones through random forwarded WhatsApp chain messages.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hey, why did a loud red warning just pop up on my screen?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your security shield caught the trap before you typed a single digit.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Thank goodness, delete that link right now and check my bank balance please!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your money is completely safe, just stop trusting random congratulations messages.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "I am never touching another WhatsApp lucky draw button in my whole life.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif any(k in cat_lower for k in ["tv", "towel", "mic", "spy", "listening"]):
                final_turn_cta = "Send this to your Dad before he wraps the TV in another towel!"
                toast = {
                    "app_name": "Privacy Check",
                    "sender": "Home Network",
                    "message": "Smart TV microphone is already turned off in settings",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, why is our fifty-inch living room screen wearing a damp bath towel?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "We talked about running shoes at dinner and suddenly my phone showed shoe ads!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "First, a cotton towel does not block sound, and second, our TV has no mic.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Then how did the internet know I wanted blue walking shoes size nine?!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Because you searched running shoes on three shopping apps yesterday afternoon on Wi-Fi.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, so the shopping apps tracked my clicks, not the television remote?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Yes, advertisers link accounts on the same Wi-Fi, no towel required at all.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hold on, let me pull off this tape and check the television menu.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Look at that alert, voice control has been switched off since day one.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, so I have been whispering inside my own living room for three days?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Yes, and you almost overheated the TV vents wrapping it in laundry.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Okay, take the towel back to the bathroom before your mother sees it.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif any(k in cat_lower for k in ["5g", "wifi", "wi-fi", "router", "tower", "signal"]):
                final_turn_cta = "Send this to your Dad before he wraps the Wi-Fi router in foil!"
                toast = {
                    "app_name": "Home Wi-Fi",
                    "sender": "Router Status",
                    "message": "Signal dropped 95% due to aluminum kitchen foil wrap",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, why does our living room Wi-Fi box look like a baked potato?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "WhatsApp said five-gigahertz Wi-Fi waves cook your brain while you sleep at night!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "First, five-gigahertz Wi-Fi is not 5G cellular, and second, it cannot cook anything.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Do not argue science with me, my headache vanished the minute I wrapped it!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "No, your headache went away because you finally stopped staring at WhatsApp forwards.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, then why did my cricket match stream freeze right in the middle?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Because aluminum foil blocks radio waves, and you literally trapped your own internet.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hey, why is the router flashing red and throwing alerts on my phone?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Even the box is begging you to unwrap the kitchen foil before it overheats.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, so this foil hat was only killing my own cricket livestream?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Yes, unwrap it right now and your match will load in two seconds.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Fine, I am taking the foil off, just never mention this to anyone.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif any(k in cat_lower for k in ["printer", "ink", "cyan", "cartridge"]):
                final_turn_cta = "Send this to your Dad before he attacks the printer with a hammer!"
                toast = {
                    "app_name": "Printer Alert",
                    "sender": "Print Queue",
                    "message": "Print job paused: Cyan cartridge at 0% for monochrome text",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, please put the screwdriver down before you break the office printer forever.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "I only want one black-and-white tax form, why does it scream about cyan?!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Ink companies mix tiny drops of blue into black text to drain cartridges faster.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "That is daylight robbery! I paid three thousand rupees for this plastic box!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "They sell the printer cheap because ink cartridges cost more per drop than gold.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "So how do I force it to print my form before five PM?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Switch the print setting to grayscale mode so it skips color cartridges completely.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, why did my laptop just chime with another angry popup message?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your printer still wants blue ink, so let us flip on black-only mode.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hey, it actually started printing my tax form without buying new ink!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Next time we are buying a laser printer so this nonsense never happens again.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Thank goodness, you just saved this printer from going straight out the window.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            else:
                # RAM booster / phone cleaner / general Dad clash
                final_turn_cta = "Send this to your Dad before he installs another phone booster app!"
                toast = {
                    "app_name": "Battery Guard",
                    "sender": "Android System",
                    "message": "Overheating Alert: Cleaner apps drained 65% battery in background",
                    "icon": "ALERT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Dad, why are there four different rocket cleaner icons sitting on your home screen?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Every time I tap the green rocket, it says it cleaned ninety percent!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Modern phones manage memory automatically, those fake rockets do nothing except show ads.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Impossible! Look how shiny the broom animation is when it sweeps my memory!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "That animation is a fake loading bar designed to keep you watching loud commercials.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Then why did my phone feel slightly faster right after I pressed boost?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "It kills your background apps, so your phone works twice as hard reopening them.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, why is the back of my phone suddenly hot enough to fry eggs?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Your system warning just caught all four cleaner apps chewing through your battery.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "So those speed boosters are the actual reason my battery dies before lunch?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Yes, delete every single one of them and your phone will double battery life.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Removing all four rockets right now, no more shady memory boosters ever again.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
        else:
            tool_name = str(topic.get("tool_name") or topic.get("toolName") or "").strip()
            brand_domain = str(topic.get("brand_domain") or topic.get("brandDomain") or "").strip()
            github_repo = str(topic.get("github_repo") or topic.get("githubRepo") or "").strip()
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

            structure_options = ["brutal_roast", "speedrun_expose", "friend_betrayal"]
            hash_val = sum(ord(c) for c in (topic.get("id") or str(title) or "reel"))
            structure = structure_options[hash_val % len(structure_options)]

            badge = "VERIFIED PROOF"
            card_title = f"{tool_name} Specs"
            step1_text = real_steps[0] if len(real_steps) > 0 else f"1. Open {brand_domain or tool_name}"
            step2_text = real_steps[1] if len(real_steps) > 1 else f"2. Run {tool_name} directly on your device"
            step3_text = real_steps[2] if len(real_steps) > 2 else "3. 100% Free with zero subscription fees"
            rows = [
                {"label": "Step 1: Setup", "value": step1_text, "status": "VERIFIED", "isPositive": True},
                {"label": "Step 2: Execution", "value": step2_text, "status": "VERIFIED", "isPositive": True},
                {"label": "Step 3: Payoff", "value": step3_text, "status": "PROVEN", "isPositive": True},
            ]

            annoyance_line, does_line = self._describe_tool_for_dialogue(topic, tool_name, title, cat_lower, real_steps)
            final_turn_cta = f"Comment {kw} and I will send you the {link_desc} right now." if has_res else "Tag that dev in your group who needs this!"
            cta_phrase = f"Comment {kw} and I'll DM you the {link_desc}." if has_res else "Tag that dev in your group who needs to see this!"
            end_card_cta = f"Comment {kw} for the {link_desc}" if has_res else "Tag that dev in your group who needs to see this!"
            end_question = f"Still paying subscriptions when {tool_name} exists? Be honest"

            if structure == "speedrun_expose":
                badge = "SPEEDRUN EXPOSE"
                card_title = f"{tool_name} Hack"
                toast = {
                    "app_name": "System Alert",
                    "sender": "Speedrun Alert",
                    "message": f"{tool_name} finished the job in 1.2s with zero paid account.",
                    "icon": "SPEED",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"Stop wasting time on {annoyance_line} when {tool_name} is completely free.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"Wait, what does {tool_name} actually do instead of charging twenty bucks monthly?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"{does_line} without any paywall.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "No way it handles all of that without forcing an enterprise license upgrade.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"Open {brand_domain or tool_name}, launch the main tool, and run it right on your machine.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Hold on, does that upload my private files to some sketchy random cloud server?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Not at all, everything stays directly on your own computer with zero server fees.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, I just tested it and the whole task finished in two seconds flat!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "And your screen just proved you never needed that paid monthly software again.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Our team literally spent hundreds of dollars on tools that were slower than this.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "That is why smart engineers check open-source projects before pulling out a credit card.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"I am cancelling our paid plan tonight and moving everyone onto {tool_name}.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            elif structure == "friend_betrayal":
                badge = "TASK BUSTED"
                card_title = f"{tool_name} Reveal"
                toast = {
                    "app_name": "Team Chat",
                    "sender": "Coworker",
                    "message": f"Wait how did you finish with {tool_name} so fast?",
                    "icon": "CHAT",
                    "time": "now",
                }
                dialogue = [
                    {"speaker": left_char, "character_id": left_char, "text": hook, "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"You are still dealing with {annoyance_line} while {tool_name} is free?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"Wait, how does {tool_name} replace a twenty-dollar app with zero subscription?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"{does_line} cleanly in seconds.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Hold up, why did nobody on my engineering team tell me this existed?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"Grab it from {brand_domain or tool_name} and run the built-in tool without signing up.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, will it lock my best features behind a sneaky seven-day trial paywall?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "Zero trial traps, zero watermarks, and zero credit cards required to finish the job.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Bro, my coworker just walked behind my desk and saw me finish in seconds!", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Look at his message, he cannot believe you wrapped up before lunch break.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "I used to burn three hours every Friday fighting crashes and annoying file limits.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Now you get your whole afternoon back and keep two hundred bucks a year.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"I am bookmarking {tool_name} right now and never paying for bloatware again.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]
            else:  # brutal_roast
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
                    {"speaker": right_char, "character_id": right_char, "text": f"You really tolerated {annoyance_line} when {tool_name} costs zero dollars?", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"Wait, what can {tool_name} even do compared to my twenty-dollar paid app?", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"{does_line} right on your own screen.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": "Seriously? I have been paying monthly fees for years just to avoid slowdowns.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": f"Just open {brand_domain or tool_name}, pick what you need, and let it run cleanly.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Wait, is it going to slow down my laptop or break my saved logins?", "emotion": "shocked", "pause_after": 0.30},
                    {"speaker": right_char, "character_id": right_char, "text": "No, it keeps everything safe and skips all the heavy background junk completely.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "Okay, I just ran it and my whole system feels brand new again.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Even your bank app is celebrating because that annoying recurring charge is finally dead.", "emotion": "smug", "pause_after": 0.30},
                    {"speaker": left_char, "character_id": left_char, "text": "They literally wanted to charge me a sneaky cancellation fee just to leave.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": "Classic subscription trap, which is why free open-source tools always win in the end.", "emotion": "smug", "pause_after": 0.25},
                    {"speaker": left_char, "character_id": left_char, "text": f"I deleted my paid account and saved two hundred dollars using {tool_name}.", "emotion": "shocked", "pause_after": 0.25},
                    {"speaker": right_char, "character_id": right_char, "text": final_turn_cta, "emotion": "smug", "pause_after": 0.40},
                ]

        card_data = None if is_dad else {
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
            "cta_text": end_card_cta,
            "subtext": "Follow for Part 2",
            "has_resource_link": has_res,
            "hasResourceLink": has_res,
        }

        headline_text = clean_headline_truncation(title.upper(), 38)

        fallback_res = {
            "title": title[:50],
            "style": scene_preset,
            "comp": "MasterAutonomousReel",
            "scenePreset": scene_preset,
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "active_cast": [left_char, right_char],
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": kw if has_res else "",
            "cta_phrase": cta_phrase,
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
            "format_type": format_type,
        }
        if is_dad:
            fallback_res["cardData"] = None
            fallback_res["proof_steps"] = []
            fallback_res["proofImagePath"] = None
            fallback_res["logoPath"] = None
        return fallback_res

    # =========================================================================
    # PUBLIC METHOD: END-TO-END 2-STEP CRAFT PASS
    # =========================================================================

    def craft_reel_screenplay(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full 2-step craft pass:
        1. Hook Battle (3 competing hooks scored -> 1 winner)
        2. Screenplay (14 natural turns 5-act viral dialogue, 42-50s, multi-step card, toast, end-card)
        """
        print(f"\n⚡ [HookMaster] Initiating Hook Battle for topic: '{topic.get('title')}'...")
        battle = self.conduct_hook_battle(topic)
        winning_hook = battle.get("winning_hook")
        print(f"🥇 [HookMaster] Winner crowned: \"{winning_hook}\"")
        for h in battle.get("hooks", []):
            print(f"   • [{h.get('type')}] Score {h.get('score')}: \"{h.get('hook')}\"")

        print(f"✍️ [HookMaster] Writing 5-act (14-turn, 42-50s) Remotion screenplay...")
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
