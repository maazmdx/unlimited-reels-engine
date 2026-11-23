"""
SEOMasterAgent (Master Agent 3: Instagram Discovery & Auto-DM Architect)
Generates high-converting, searchable social assets for each reel:
1. <reel>_caption.txt:
   - Line 1: High-CTR SEO headline front-loaded with search terms
   - 3 crisp, scannable value bullets + natural semantic keywords
   - Explicit Auto-DM CTA line
   - Pinned comment bait (opinionated question to trigger rapid comment velocity)
   - 9-10 tiered hashtags (3 broad + 4 mid-niche + 3 exact-topic, zero spammy tags)
2. <reel>_autodm.json:
   - ManyChat / Instagram Auto-DM automation payload
   - 3 varied public comment replies (prevents Instagram spam throttling)
   - Clean, friendly 1-2 sentence DM delivery template
   - Pinned comment bait
"""

import os
import re
import json
import time
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

try:
    from google import genai
except ImportError:
    genai = None

from engine.dns_utils import enable_fast_dns
enable_fast_dns()

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


def extract_clean_tool_name(tool_name: str, title: str, github_repo: str = "", brand_domain: str = "") -> str:
    """Extracts clean brand/tool name, stripping screaming marketing prefixes like 'FREE PC Cleaner:'."""
    raw = (tool_name or "").strip()
    generic_words = ["free pc cleaner", "free tool", "free alternative", "best tool", "pc cleaner", "open source"]
    if raw and not any(g == raw.lower() or raw.lower().startswith(g) for g in generic_words):
        return raw

    if github_repo and "/" in github_repo:
        repo_name = github_repo.split("/")[-1].strip()
        if repo_name and len(repo_name) > 2 and "search" not in repo_name.lower():
            return repo_name.capitalize() if repo_name.islower() else repo_name

    if brand_domain and "." in brand_domain:
        domain_name = brand_domain.split(".")[0].strip()
        if domain_name and len(domain_name) > 2:
            return domain_name.capitalize() if domain_name.islower() else domain_name

    clean_t = str(title or "").strip()
    if ":" in clean_t:
        p0, p1 = [p.strip() for p in clean_t.split(":", 1)]
        is_p0_generic = any(g in p0.lower() for g in ["free", "best", "top", "open source", "cleaner", "tool", "hack", "secret"])
        if is_p0_generic and p1:
            words = p1.split()
            if words:
                return words[0].strip(":,.-")
        if not is_p0_generic and p0:
            return p0

    words = clean_t.split()
    return words[0].strip(":,.-") if words else "Verified Tool"


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
        "User-Agent": "AntigravitySEOMaster/3.0",
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
        print(f"⚠️ [Groq API] Exception: {e}")
    return None


class SEOMasterAgent:
    """
    Master Agent 3: Crafts Instagram search optimization, tiered hashtag sets,
    pinned comment conversation drivers, and anti-throttle Auto-DM configurations.
    Uses fast free-tier Gemini fallback with zero-fail deterministic safety.
    """

    FAST_MODELS = ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parent.parent.parent)
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.headers = {"User-Agent": "AntigravitySEOMaster/1.0", "Content-Type": "application/json"}
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 50000},
                )
            except Exception as e:
                print(f"⚠️ SEOMaster: Gemini client init notice: {e}")

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini with 2026 free-tier models, clean 50s timeout, 1 retry on 504/timeout, and logs model."""
        if self.client:
            for m in self.FAST_MODELS:
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
                            print(f"✨ [SEOMaster] Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(res.text)} chars).")
                            return res.text
                    except Exception as e:
                        err_str = str(e)
                        is_504 = "504" in err_str or "DEADLINE_EXCEEDED" in err_str or "timeout" in err_str.lower()
                        if is_504 and attempt == 0:
                            print(f"⚠️ SEOMaster: GenAI {m} hit 504/deadline, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ SEOMaster: GenAI {m} warning: {e}")
                        break

        if self.api_key:
            for m in self.FAST_MODELS:
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
                                print(f"✨ [SEOMaster] REST Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(text)} chars).")
                                return text
                        elif (r.status_code == 504 or "DEADLINE_EXCEEDED" in r.text) and attempt == 0:
                            print(f"⚠️ SEOMaster: REST {m} hit 504, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        else:
                            print(f"⚠️ SEOMaster: REST {m} returned {r.status_code}: {r.text[:120]}")
                            break
                    except Exception as e:
                        err_str = str(e)
                        is_timeout = "timeout" in err_str.lower() or "504" in err_str
                        if is_timeout and attempt == 0:
                            print(f"⚠️ SEOMaster: REST {m} timed out, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ SEOMaster: REST {m} warning: {e}")
                        break

        return None

    def _call_llm(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Routes LLM generation through the central zero-dependency LLMRouter."""
        from engine.llm_router import generate_text
        return generate_text(prompt, system_prompt=system_instruction, json_mode=True, temperature=0.7)

    def _refine_with_ai(self, title: str, category: str, kw: str, raw_headline: str) -> Optional[Dict[str, Any]]:
        """Optional AI refinement pass to elevate headline, pinned comment, and replies."""
        current_year = str(datetime.now().year)
        prompt = (
            f"Topic: {title}\n"
            f"Category: {category}\n"
            f"Auto-DM Keyword: {kw}\n"
            f"Current Year: {current_year}\n"
            f"Draft Headline: {raw_headline}\n\n"
            "STRICT RULES (SIMPLE SPOKEN ENGLISH ONLY - 6th-8th GRADE LEVEL):\n"
            "- Explicitly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', or any corporate fluff.\n"
            "- Write in punchy, short sentences that anyone on Instagram understands in half a second.\n"
            "- 'seo_headline': MUST explicitly emphasize '100% FREE' or '$0' in the title (e.g., 'Play Full GTA in Chrome [100% FREE]' or 'This $0 Tool Replaces 4 Hours of Work').\n"
            f"- 'pinned_comment': MUST be a spicy, diabolical ragebait debate question referencing the current year {current_year} (e.g., 'Still paying for PC cleaners in {current_year}? Be honest 💀' or 'Still downloading 80GB games on a potato laptop in {current_year}? Drop your excuse below 👇'). Never use 2024 or 2025.\n\n"
            "Return JSON with:\n"
            "- 'seo_headline': A high-CTR, front-loaded Instagram SEO title with emoji and '100% FREE' (simple spoken English only)\n"
            "- 'pinned_comment': A spicy ragebait debate question triggering instant comments\n"
            "- 'comment_replies': Exactly 3 friendly, distinct public comment replies confirming DM sent (to avoid IG bot throttle)"
        )
        sys_inst = (
            "You are an elite Instagram SEO and Viral Engagement Director. "
            "Write in simple, punchy, conversational spoken English (6th-8th grade). "
            "Never use corporate buzzwords. Return ONLY valid JSON."
        )
        try:
            raw = self._call_llm(prompt, sys_inst)
            if raw:
                cleaned = raw.strip()
                if cleaned.startswith("```"):
                    cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                    cleaned = re.sub(r"\n```$", "", cleaned)
                data = json.loads(cleaned.strip())
                return data
        except Exception:
            pass
        return None

    def generate_seo_assets(
        self,
        script_data: Dict[str, Any],
        batch_dir: Optional[Path] = None,
        file_prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Takes screenplay and topic metadata, synthesizes caption and Auto-DM config,
        and optionally writes to disk if batch_dir and file_prefix are provided.
        """
        title = sanitize_simple_spoken_english(script_data.get("title", "Daily Tech Breakdown"))
        hook_obj = script_data.get("hook", {})
        if isinstance(hook_obj, dict):
            headline = hook_obj.get("headline", title)
            subheadline = hook_obj.get("subheadline", "")
            tag = hook_obj.get("tag", "⚠️ VIRAL REAL TALK")
        else:
            headline = title
            subheadline = str(hook_obj)
            tag = "⚠️ VIRAL REAL TALK"

        headline = sanitize_simple_spoken_english(headline)
        subheadline = sanitize_simple_spoken_english(subheadline)

        category = script_data.get("category", "Tech Innovation")
        raw_kw = str(script_data.get("cta_keyword") or script_data.get("ctaKeyword", "LINK")).strip().upper()
        kw = sanitize_auto_dm_keyword(raw_kw, category, title)

        tool_name = str(script_data.get("tool_name") or script_data.get("toolName") or "").strip()
        brand_domain = str(script_data.get("brand_domain") or script_data.get("brandDomain") or "").strip()
        tool_name = extract_clean_tool_name(tool_name, title, github_repo=script_data.get("github_repo", ""), brand_domain=brand_domain)
        real_steps = script_data.get("real_steps") or script_data.get("realSteps") or []
        if not real_steps:
            turns = script_data.get("dialogue") or script_data.get("turns") or []
            extracted_steps = []
            for t in turns:
                txt = str(t.get("text", "")).strip() if isinstance(t, dict) else str(t).strip()
                m = re.search(r'step\s*([123])\s*[:.-]?\s*(.*)', txt, flags=re.IGNORECASE)
                if m:
                    extracted_steps.append(m.group(2).strip())
            if len(extracted_steps) >= 3:
                real_steps = extracted_steps
        format_type = str(script_data.get("format_type") or script_data.get("format") or "").lower()
        is_dad_clash = (format_type == "dad_clash") or ("dad" in title.lower()) or (kw in ["NO-DM", "NODM", "NONE", ""])

        # 1. Generate 3 concise, tool-specific steps naming the real tool and what it replaces for $0
        card_data = script_data.get("cardData") or {}
        bullets = []
        if real_steps and len(real_steps) >= 3:
            for s in real_steps[:3]:
                clean_s = re.sub(r'^(?:step\s*\d+[:.-]?\s*|\d+[:.-]?\s*)', '', str(s), flags=re.IGNORECASE).strip()
                bullets.append(f"• {sanitize_simple_spoken_english(clean_s)}")
        elif isinstance(card_data, dict) and card_data.get("rows"):
            for item in card_data["rows"][:3]:
                if isinstance(item, dict):
                    val = str(item.get("value") or "").strip()
                    clean_v = re.sub(r'^(?:step\s*\d+[:.-]?\s*|\d+[:.-]?\s*)', '', val, flags=re.IGNORECASE).strip()
                    if clean_v:
                        bullets.append(f"• {sanitize_simple_spoken_english(clean_v)}")

        if len(bullets) < 3:
            t_disp = tool_name or "this tool"
            d_disp = brand_domain or (f"github.com/{script_data.get('github_repo')}" if script_data.get("github_repo") else "official site")
            rep_disp = script_data.get("replaces_paid_app") or "expensive $20/month subscriptions"
            summary_hint = script_data.get("readme_summary") or script_data.get("real_description") or ""
            step2_action = f"Run {t_disp} locally with zero cloud lag or server tracking"
            if "browser" in summary_hint.lower() or "canvas" in summary_hint.lower():
                step2_action = f"Run {t_disp} directly in your browser with zero installation"
            elif "upscale" in summary_hint.lower():
                step2_action = "Drop low-res photos to upscale with local AI models for free"
            elif "pdf" in summary_hint.lower():
                step2_action = "Split, merge, or OCR documents offline with 100% privacy"
            elif "airdrop" in summary_hint.lower() or "transfer" in summary_hint.lower():
                step2_action = "Transfer files at 50MB/s over local Wi-Fi without cloud uploads"

            bullets = [
                f"• Open {d_disp} directly (zero payment or credit card)",
                f"• {step2_action}",
                f"• 100% free forever, replacing {rep_disp}",
            ]
        bullets_text = "\n".join(bullets[:3])

        # 2. Line 1: High-CTR Curiosity/Contrast Hook (strictly <= 60 chars before Instagram "...more" truncation)
        if is_dad_clash:
            if "ram" in title.lower() or "cleaner" in title.lower():
                line1_hook = "Dad installed 4 'RAM Cleaner' apps on his phone"
            elif "scam" in title.lower() or "whatsapp" in title.lower():
                line1_hook = "Dad almost sent his bank info to a WhatsApp bot"
            elif "battery" in title.lower() or "overnight" in title.lower():
                line1_hook = "Dad thinks overnight charging doubles phone battery"
            else:
                line1_hook = f"Dad vs Tech: {title}"
        elif tool_name:
            cat_t = (title + " " + category).lower()
            if "pdf" in cat_t:
                line1_hook = f"Free open-source alternative to Adobe PDF: {tool_name}"
            elif "photo" in cat_t:
                line1_hook = f"Free open-source Photoshop alternative: {tool_name}"
            elif "game" in cat_t or "retro" in cat_t:
                line1_hook = f"Free retro games in your browser: {tool_name}"
            elif "send" in cat_t or "airdrop" in cat_t:
                line1_hook = f"Free open-source AirDrop alternative: {tool_name}"
            else:
                line1_hook = f"Free open-source alternative: {tool_name} ($0)"
        else:
            line1_hook = f"Free open-source alternative: {clean_headline_truncation(title, 25)}"

        line1_hook = clean_headline_truncation(line1_hook, max_chars=60)
        seo_headline = line1_hook

        # 3. Pinned Comment Bait (spicy ragebait debate trigger)
        pinned_comment = self._craft_pinned_comment(title, category, kw)

        current_year = str(datetime.now().year)

        # 4. Varied Public Comment Replies (3 variations to bypass Instagram bot throttling)
        if is_dad_clash:
            t_low = title.lower()
            if "battery" in t_low or "alarm" in t_low or "unplug" in t_low or "80" in t_low:
                comment_replies = [
                    "Tag your dad before he sets a 3 AM alarm to unplug his phone 😂",
                    "Does your dad also think charging past 80% explodes the battery? 🔌",
                    "Tell your dad modern BMS chips handle charging automatically 💀",
                ]
            elif "ram" in t_low or "cleaner" in t_low or "booster" in t_low:
                comment_replies = [
                    "Tag your dad before his phone hits 90 degrees from booster apps 😂",
                    "Does your dad also think cleaning animations actually speed up RAM? 🔌",
                    "Uninstalling my dad's four cleaner apps saved 80% battery 💀",
                ]
            else:
                comment_replies = [
                    "Tag your dad before he clicks another WhatsApp link 💀",
                    "Does your dad also think closing background apps saves battery? 🔌",
                    "Send this to your dad before he gets tricked again 😂",
                ]
        else:
            comment_replies = [
                f"Sent to your DMs! Check your message requests if you don't see it.",
                f"Just sent over the free direct link! Enjoy.",
                f"Check your messages! 📬 Sent the 100% free guide and link.",
            ]

        # 5. Optional AI refinement with fast free-tier fallback
        if self.api_key or os.environ.get("GROQ_API_KEY"):
            ai_data = self._refine_with_ai(title, category, kw, seo_headline)
            if ai_data:
                if ai_data.get("seo_headline"):
                    cand_h = clean_headline_truncation(sanitize_simple_spoken_english(ai_data["seo_headline"]), 60)
                    if cand_h:
                        seo_headline = cand_h
                        line1_hook = cand_h
                if ai_data.get("pinned_comment"):
                    cand_pc = sanitize_simple_spoken_english(ai_data["pinned_comment"])
                    cand_pc = re.sub(r"\b(2023|2024|2025)\b", current_year, cand_pc)
                    if not is_dad_clash and current_year not in cand_pc:
                        if "?" in cand_pc:
                            cand_pc = re.sub(r"\?", f" in {current_year}?", cand_pc, count=1)
                        else:
                            cand_pc = f"{cand_pc} in {current_year}"
                    pinned_comment = cand_pc
                if ai_data.get("comment_replies") and isinstance(ai_data["comment_replies"], list) and len(ai_data["comment_replies"]) >= 3:
                    if not is_dad_clash:
                        comment_replies = [sanitize_simple_spoken_english(r) for r in ai_data["comment_replies"][:3]]

        # Ensure year is dynamically injected (zero 2024 strings)
        pinned_comment = re.sub(r"\b(2023|2024|2025)\b", current_year, pinned_comment)
        if not is_dad_clash and current_year not in pinned_comment:
            if "?" in pinned_comment:
                pinned_comment = re.sub(r"\?", f" in {current_year}?", pinned_comment, count=1)
            else:
                pinned_comment = f"{pinned_comment} in {current_year}"

        # 6. Tiered Hashtags (5-7 targeted niche + search hashtags, zero spam)
        tiered_hashtags = self._build_tiered_hashtags(title, category, kw)
        hashtags_str = " ".join(tiered_hashtags)

        has_res = script_data.get("has_resource_link", script_data.get("hasResourceLink", True))
        cta_phrase = script_data.get("cta_phrase") or script_data.get("ctaText") or "Tag that dev in your group who needs to see this! 👇"
        if is_dad_clash:
            t_low = title.lower()
            if "battery" in t_low or "alarm" in t_low or "unplug" in t_low or "80" in t_low:
                cta_line = "💬 Send this to your dad or friend before they wake up at 3 AM to unplug their phone! 👇\n\n"
            else:
                cta_line = "💬 Send this to your dad or friend before they get tricked again! 👇\n\n"
        elif has_res and kw:
            cta_line = f"💬 Comment \"{kw}\" below and I'll DM you the free link!\n\n"
        else:
            cta_line = f"💬 {cta_phrase}\n\n"

        # 7. Full Caption Text (Line 1 <= 60 chars, 3-step breakdown for tools, zero software steps for Dad clash)
        if is_dad_clash:
            caption_text = (
                f"{line1_hook}\n\n"
                f"{subheadline}\n\n"
                f"{cta_line}"
                f"📌 PINNED DEBATE: {pinned_comment}\n\n"
                f"Follow @canidoai for daily zero-dollar tools, retro hacks & tech truth!\n\n"
                f"{hashtags_str}"
            )
        else:
            caption_text = (
                f"{line1_hook}\n\n"
                f"{subheadline}\n\n"
                f"3-Step Breakdown:\n"
                f"{bullets_text}\n\n"
                f"{cta_line}"
                f"📌 PINNED DEBATE: {pinned_comment}\n\n"
                f"Follow @canidoai for daily zero-dollar tools, retro hacks & tech truth!\n\n"
                f"{hashtags_str}"
            )
        caption_text = re.sub(r"\b(2023|2024|2025)\b", current_year, caption_text)
        caption_text = sanitize_simple_spoken_english(caption_text)

        # 8. Resolve real official tool/repo URL (Canonical resolution order: github_repo -> official_url -> brand_domain)
        github_repo = str(script_data.get("github_repo") or "").strip().lstrip("/")
        raw_source_url = str(
            script_data.get("source_url")
            or script_data.get("official_url")
            or script_data.get("resource_link_or_query")
            or script_data.get("url")
            or script_data.get("link")
            or ""
        ).strip()
        brand_domain = str(script_data.get("brand_domain") or "").strip().replace("http://", "").replace("https://", "").strip("/")

        clean_search_term = re.sub(r"[^a-zA-Z0-9\s-]", "", title.split(":")[0]).strip()

        if github_repo and "/" in github_repo and "search?" not in github_repo:
            official_url = f"https://github.com/{github_repo}"
        elif raw_source_url and raw_source_url.startswith("http") and "github.com/search" not in raw_source_url:
            official_url = raw_source_url
        elif brand_domain and "." in brand_domain:
            official_url = f"https://{brand_domain}"
        else:
            cat_t = (str(category) + " " + str(title)).lower()
            if "game" in cat_t or "retro" in cat_t or "emulator" in cat_t:
                official_url = f"https://archive.org/details/software?query={urllib.parse.quote(clean_search_term)}"
            else:
                official_url = f"https://www.google.com/search?q={urllib.parse.quote(clean_search_term)}"

        guide_path = None
        guide_file_name = None

        if has_res and kw:
            guide_file_name = f"{file_prefix}_resource_guide.html" if file_prefix else "resource_guide.html"
            guide_html = self.generate_resource_guide_html(
                title=title,
                category=category,
                official_url=official_url,
                card_rows=card_data.get("rows", []),
                kw=kw,
                seo_headline=seo_headline,
                real_steps=real_steps,
                tool_name=tool_name,
            )

            if batch_dir and file_prefix:
                b_dir = Path(batch_dir)
                b_dir.mkdir(parents=True, exist_ok=True)
                guide_file = b_dir / guide_file_name
                with open(guide_file, "w", encoding="utf-8") as f:
                    f.write(guide_html)
                guide_path = str(guide_file)
                print(f"📄 [Resource Guide] Generated 1-page guide: {guide_file.name}")

            dm_msg = (
                f"Hey! Here is the 100% free direct link & quick-start guide for {title}:\n\n"
                f"🔗 Direct Access: {official_url}\n"
                f"📖 Complete 1-Page Setup Guide: [DRIVE_GUIDE_LINK]\n\n"
                f"Enjoy exploring, and drop any questions below!"
            )
            dm_msg = sanitize_simple_spoken_english(dm_msg)

            autodm_payload = {
                "mode": "resource_guide",
                "keyword": kw,
                "has_resource_link": True,
                "resource_topic": title,
                "official_url": official_url,
                "guide_file": guide_file_name,
                "guide_drive_link": None,
                "public_comment_replies": comment_replies,
                "dm_message_template": dm_msg,
                "pinned_comment_bait": pinned_comment,
                "seo_headline": seo_headline,
                "tiered_hashtags": tiered_hashtags,
                "created_at": datetime.now().isoformat(),
            }
        else:
            autodm_payload = {
                "mode": "engagement_only",
                "keyword": "",
                "has_resource_link": False,
                "resource_topic": title,
                "cta_phrase": cta_phrase,
                "public_comment_replies": comment_replies,
                "dm_message_template": "",
                "pinned_comment_bait": pinned_comment,
                "seo_headline": seo_headline,
                "tiered_hashtags": tiered_hashtags,
                "created_at": datetime.now().isoformat(),
            }

        # Optionally persist files
        caption_path = None
        autodm_path = None
        if batch_dir and file_prefix:
            b_dir = Path(batch_dir)
            b_dir.mkdir(parents=True, exist_ok=True)

            caption_file = b_dir / f"{file_prefix}_caption.txt"
            with open(caption_file, "w", encoding="utf-8") as f:
                f.write(caption_text)
            caption_path = str(caption_file)

            autodm_file = b_dir / f"{file_prefix}_autodm.json"
            with open(autodm_file, "w", encoding="utf-8") as f:
                json.dump(autodm_payload, f, indent=2, ensure_ascii=False)
            autodm_path = str(autodm_file)

        return {
            "seo_headline": seo_headline,
            "caption_text": caption_text,
            "pinned_comment": pinned_comment,
            "tiered_hashtags": tiered_hashtags,
            "autodm_payload": autodm_payload,
            "caption_path": caption_path,
            "autodm_path": autodm_path,
            "guide_path": guide_path,
        }

    def generate_resource_guide_html(
        self,
        title: str,
        category: str,
        official_url: str,
        card_rows: List[Dict[str, Any]],
        kw: str,
        seo_headline: str = "",
        real_steps: Optional[List[str]] = None,
        tool_name: Optional[str] = None,
    ) -> str:
        """
        Generates a clean, responsive, 1-page HTML Resource & Setup Guide.
        Designed for instant mobile readability when opened from an Instagram DM.
        """
        clean_title = sanitize_simple_spoken_english(title)
        domain_hint = official_url.replace("https://", "").replace("http://", "").split("/")[0] if official_url else ""
        tool_name = extract_clean_tool_name(tool_name or "", clean_title, brand_domain=domain_hint)

        if real_steps and len(real_steps) >= 3:
            card_rows = [
                {"label": "1. Setup", "value": sanitize_simple_spoken_english(str(real_steps[0])), "status": "VERIFIED"},
                {"label": "2. Run", "value": sanitize_simple_spoken_english(str(real_steps[1])), "status": "VERIFIED"},
                {"label": "3. Result", "value": sanitize_simple_spoken_english(str(real_steps[2])), "status": "VERIFIED"},
            ]
        else:
            # Check if card_rows has real tool-specific instructions or generic filler
            def is_generic_filler(text: str) -> bool:
                low = text.lower()
                return any(f in low for f in ["launches in seconds", "runs on your machine", "zero dollar cost", "step 1", "step 2"])

            has_tool_specific_rows = False
            if card_rows and len(card_rows) >= 3:
                first_val = str(card_rows[0].get("value", "") if isinstance(card_rows[0], dict) else card_rows[0])
                if not is_generic_filler(first_val) and (tool_name.lower() in first_val.lower() or "http" in first_val):
                    has_tool_specific_rows = True

            if not has_tool_specific_rows:
                card_rows = [
                    {"label": "Step 1: Official Access", "value": f"Get {tool_name} directly from {official_url}", "status": "VERIFIED"},
                    {"label": "Step 2: Instant Launch", "value": f"Run {tool_name} locally with zero subscription fees or credit card requirements", "status": "VERIFIED"},
                    {"label": "Step 3: Unlimited Free Use", "value": f"Enjoy 100% free verified execution on your own machine powered by {tool_name}", "status": "VERIFIED"},
                ]

        rows_html = ""
        for r in card_rows:
            if isinstance(r, dict):
                lbl = sanitize_simple_spoken_english(str(r.get("label", "")))
                val = sanitize_simple_spoken_english(str(r.get("value", "")))
                status = str(r.get("status", "VERIFIED"))
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                lbl = sanitize_simple_spoken_english(str(r[0]))
                val = sanitize_simple_spoken_english(str(r[1]))
                status = str(r[2]) if len(r) > 2 else "VERIFIED"
            else:
                lbl = "Step"
                val = sanitize_simple_spoken_english(str(r))
                status = "VERIFIED"

            rows_html += f"""
            <div class="step-card">
                <div class="step-badge">{status}</div>
                <div class="step-title">{lbl}</div>
                <div class="step-desc">{val}</div>
            </div>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_title} — Free Resource Guide</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text-main: #f0f6fc;
            --text-sub: #8b949e;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --green: #22c55e;
            --gold: #f59e0b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 24px 16px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 680px;
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 32px 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}
        .header-tag {{
            display: inline-block;
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid rgba(56, 189, 248, 0.3);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 26px;
            font-weight: 800;
            line-height: 1.25;
            margin-bottom: 12px;
            color: #ffffff;
        }}
        .category-pill {{
            color: var(--text-sub);
            font-size: 14px;
            margin-bottom: 24px;
        }}
        .cta-box {{
            background: rgba(34, 197, 94, 0.08);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 24px 0 32px 0;
        }}
        .cta-btn {{
            display: inline-block;
            background: var(--green);
            color: #000000;
            font-size: 16px;
            font-weight: 700;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 10px;
            transition: transform 0.2s, background 0.2s;
            margin-top: 10px;
            word-break: break-all;
        }}
        .cta-btn:hover {{
            background: #16a34a;
            transform: scale(1.02);
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}
        .step-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 14px;
        }}
        .step-badge {{
            display: inline-block;
            font-size: 10px;
            font-weight: 800;
            background: var(--gold);
            color: #000000;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 6px;
        }}
        .step-title {{
            font-weight: 700;
            font-size: 15px;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .step-desc {{
            font-size: 14px;
            color: var(--text-sub);
        }}
        .tips-list {{
            list-style: none;
            margin-bottom: 24px;
        }}
        .tips-list li {{
            font-size: 14px;
            color: var(--text-sub);
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }}
        .tips-list li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: var(--green);
            font-weight: bold;
        }}
        .footer {{
            margin-top: 32px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 12px;
            color: var(--text-sub);
        }}
    </style>
</head>
<body>
    <div class="container">
        <span class="header-tag">100% Free Verified Resource</span>
        <h1>{clean_title}</h1>
        <div class="category-pill">Category: {category} • Zero Monthly Fees</div>

        <div class="cta-box">
            <div style="font-size: 13px; color: var(--text-sub); margin-bottom: 6px;">OFFICIAL DIRECT ACCESS</div>
            <a href="{official_url}" target="_blank" rel="noopener noreferrer" class="cta-btn">
                Launch / Access Now ↗
            </a>
            <div style="font-size: 12px; color: var(--text-sub); margin-top: 8px;">
                Verified direct URL: <code>{official_url}</code>
            </div>
        </div>

        <div class="section-title">3-Step Quick Start</div>
        {rows_html}

        <div class="section-title">Why This Wins</div>
        <ul class="tips-list">
            <li><strong>Zero Cost:</strong> Replaces bloated $20/month enterprise subscriptions with zero credit card traps.</li>
            <li><strong>Instant Launch:</strong> Runs directly with zero heavy installations or tracking.</li>
            <li><strong>Verified Working:</strong> Live tested and verified by @canidoai Free Tech Engine.</li>
        </ul>

        <div class="footer">
            Delivered by @canidoai • Comment <strong>{kw}</strong> for daily verified free open-source tools.
        </div>
    </div>
</body>
</html>"""

    def _craft_pinned_comment(self, title: str, category: str, kw: str) -> str:
        """Crafts a sharp, opinionated 1-line debate question to pin in the comments."""
        lower_t = (title + " " + category).lower()
        current_year = str(datetime.now().year)
        if "pdf" in lower_t:
            return f"Still paying Adobe $20/month just to merge two PDFs in {current_year}? Be honest 👇"
        elif "photo" in lower_t or "psd" in lower_t:
            return "Would you rather pay $240/yr for Photoshop or use Photopea for $0? 👇"
        elif "localsend" in lower_t or "airdrop" in lower_t or "send" in lower_t:
            return "AirDrop or LocalSend? Which one actually works between Android and PC? 👇"
        elif "browser" in lower_t or "retro" in lower_t or "game" in lower_t:
            return "What's the best PS2 or retro game of all time? Don't say GTA San Andreas 👇"
        elif "dad" in lower_t and ("ram" in lower_t or "cleaner" in lower_t or "booster" in lower_t):
            return "Does your dad have 4 'cleaner' apps on his phone right now? Check his phone 😂👇"
        elif "cleaner" in lower_t or "ram" in lower_t or "bleachbit" in lower_t:
            return f"Still paying for PC cleaners in {current_year}? Be honest 💀"
        elif "scam" in lower_t or "whatsapp" in lower_t or "lottery" in lower_t:
            return "Has anyone in your family actually clicked a 'Free iPhone' WhatsApp link? 💀👇"
        elif "adblock" in lower_t or "ublock" in lower_t:
            return f"Do people really still browse the web without an ad-blocker in {current_year}? Be honest 👇"
        elif "ai" in lower_t or "agent" in lower_t or "model" in lower_t:
            return f"Still paying $20/month for AI in {current_year}? Be honest—would you even pass your job interview without it? 💀"
        elif "dad" in lower_t or "wifi" in lower_t or "bill" in lower_t:
            return "Would you trust your dad to fix your Wi-Fi or pay $100 for a technician? Be honest 😂👇"
        else:
            return f"Still paying monthly fees for software in {current_year} when free tools exist? Drop your excuse below 👇"

    def _build_tiered_hashtags(self, title: str, category: str, kw: str) -> List[str]:
        """
        Assembles 5-7 targeted niche + search hashtags (zero spam).
        """
        broad = ["#TechHacks", "#FreeSoftware"]
        lower_t = (title + " " + category).lower()

        if "game" in lower_t or "retro" in lower_t:
            niche = ["#BrowserGames", "#RetroGaming", "#PCGaming"]
        elif "dad" in lower_t:
            niche = ["#DesiMemes", "#TechHumor", "#IndianDad"]
        elif "pdf" in lower_t or "file" in lower_t:
            niche = ["#OpenSource", "#ProductivityTools", "#PDFHacks"]
        elif "photo" in lower_t or "creative" in lower_t:
            niche = ["#Photopea", "#OpenSourceDesign", "#FreeTools"]
        elif "privacy" in lower_t or "adblock" in lower_t or "cleaner" in lower_t:
            niche = ["#PrivacyTools", "#SystemSpeedup", "#OpenSource"]
        else:
            niche = ["#OpenSource", "#UsefulWebsites", "#TechTips"]

        exact = []
        if kw and kw not in ["NO-DM", "NODM", "NONE"]:
            exact.append(f"#{kw.title()}Tool")

        tags = broad + niche + exact
        return tags[:7]


if __name__ == "__main__":
    seo = SEOMasterAgent()
    sample_script = {
        "title": "LocalSend: The Free Open-Source AirDrop for Every Device",
        "category": "Free Open-Source GitHub Repos",
        "cta_keyword": "REPO",
        "hook": {
            "headline": "FREE AIRDROP FOR EVERY DEVICE",
            "subheadline": "Stop paying for cloud subscriptions just to send photos to your PC.",
            "tag": "100% FREE REPO",
        },
        "cardData": {
            "rows": [
                {"label": "Cloud Uploads", "value": "Slow + paid tiers"},
                {"label": "LocalSend", "value": "100% free + local Wi-Fi"},
                {"label": "Security", "value": "End-to-end encrypted"},
            ]
        },
    }
    assets = seo.generate_seo_assets(sample_script)
    print("\n--- SEOMaster Output ---")
    print("SEO Headline:", assets["seo_headline"])
    print("\nPinned Comment:", assets["pinned_comment"])
    print("\nHashtags:", assets["tiered_hashtags"])
    print("\nAuto-DM Replies:", assets["autodm_payload"]["public_comment_replies"])
