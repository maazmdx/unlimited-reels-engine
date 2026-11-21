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
        """
        Unified LLM fallback chain:
        1. Fast Gemini Free-tier (gemini-2.5-flash, gemini-3.5-flash-lite, gemini-3.8-flash) with 45s timeout.
        2. High-speed Groq API (llama-3.3-70b-versatile) fallback.
        """
        # Try Gemini first
        res = self._call_gemini_api(prompt, system_instruction)
        if res:
            return res

        # Try Groq API fallback
        print("⚡ [SEOMaster] Gemini unavailable/exhausted, switching to Groq llama-3.3-70b-versatile...")
        groq_res = call_groq_api(prompt, system_instruction)
        if groq_res:
            return groq_res

        return None

    def _refine_with_ai(self, title: str, category: str, kw: str, raw_headline: str) -> Optional[Dict[str, Any]]:
        """Optional AI refinement pass to elevate headline, pinned comment, and replies."""
        prompt = (
            f"Topic: {title}\n"
            f"Category: {category}\n"
            f"Auto-DM Keyword: {kw}\n"
            f"Draft Headline: {raw_headline}\n\n"
            "STRICT RULES (SIMPLE SPOKEN ENGLISH ONLY - 6th-8th GRADE LEVEL):\n"
            "- Explicitly FORBIDDEN words: 'framework', 'paradigm', 'optimize', 'biometric', 'infrastructure', 'synergy', 'utilize', 'collaboration', 'delivers', 'latency', 'ecosystem', or any corporate fluff.\n"
            "- Write in punchy, short sentences that anyone on Instagram understands in half a second.\n"
            "- 'seo_headline': MUST explicitly emphasize '100% FREE' or '$0' in the title (e.g., 'Play Full GTA in Chrome [100% FREE]' or 'This $0 Tool Replaces 4 Hours of Work').\n"
            "- 'pinned_comment': MUST be a spicy, diabolical ragebait question that forces people to comment or debate (e.g., 'Still paying for this in 2026? Be honest 💀' or 'Still downloading 80GB games on a potato laptop? Drop your excuse below 👇').\n\n"
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

        # 1. Generate 3 crisp value bullets from cardData rows (not raw metadata keys)
        card_data = script_data.get("cardData") or {}
        bullets = []
        if isinstance(card_data, dict):
            raw_rows = card_data.get("rows") or card_data.get("items")
            if isinstance(raw_rows, list) and len(raw_rows) > 0:
                for item in raw_rows[:3]:
                    if isinstance(item, dict):
                        lbl = str(item.get("label") or item.get("name") or "").strip()
                        val = str(item.get("value") or item.get("desc") or "").strip()
                        if lbl and val:
                            bullets.append(f"• {sanitize_simple_spoken_english(lbl)}: {sanitize_simple_spoken_english(val)}")
                        elif lbl:
                            bullets.append(f"• {sanitize_simple_spoken_english(lbl)}")
                        elif val:
                            bullets.append(f"• {sanitize_simple_spoken_english(val)}")
                    elif isinstance(item, str):
                        bullets.append(f"• {sanitize_simple_spoken_english(item.strip())}")
            else:
                # Filter out raw metadata keys (title, subtitle, badge, etc.)
                ignored_keys = {
                    "title", "subtitle", "badge", "type", "highlight",
                    "durationseconds", "durationframes", "startframe",
                    "toastdata", "topiclogopath", "rows", "items", "codesnippet", "language"
                }
                for k, v in card_data.items():
                    if k.lower() not in ignored_keys and not isinstance(v, (dict, list)):
                        clean_k = k.replace("_", " ").title()
                        bullets.append(f"• {sanitize_simple_spoken_english(clean_k)}: {sanitize_simple_spoken_english(str(v))}")
                        if len(bullets) >= 3:
                            break

        if not bullets:
            bullets = [
                "• 100% Free: $0 setup running directly in your browser",
                "• The Catch: What paid tools charged you $20/mo for",
                "• Instant Access: Step-by-step setup with zero installs",
            ]
        bullets_text = "\n".join(bullets)

        # 2. Front-loaded High-CTR SEO Headline (emphasize 100% FREE in simple spoken English)
        seo_headline = f"{tag} {headline.title() if headline.isupper() else headline}"
        if not any(f in seo_headline.lower() for f in ["100% free", "free", "$0", "zero dollar", "0 dollar"]):
            seo_headline = f"{seo_headline} [100% FREE]"
        seo_headline = sanitize_simple_spoken_english(seo_headline)

        # 3. Pinned Comment Bait (spicy ragebait debate trigger)
        pinned_comment = self._craft_pinned_comment(title, category, kw)

        # 4. Varied Public Comment Replies (3 variations to bypass Instagram bot throttling)
        comment_replies = [
            f"Sent to your DMs! 🚀 Check your message requests if you don't see it.",
            f"Just sent over the free direct link! ⚡ Enjoy.",
            f"Check your messages! 📬 Sent the 100% free guide and link.",
        ]

        # 5. Optional AI refinement with fast free-tier fallback
        if self.api_key or os.environ.get("GROQ_API_KEY"):
            ai_data = self._refine_with_ai(title, category, kw, seo_headline)
            if ai_data:
                if ai_data.get("seo_headline"):
                    seo_headline = sanitize_simple_spoken_english(ai_data["seo_headline"])
                    if not any(f in seo_headline.lower() for f in ["100% free", "free", "$0", "zero dollar", "0 dollar"]):
                        seo_headline = f"{seo_headline} [100% FREE]"
                if ai_data.get("pinned_comment"):
                    pinned_comment = sanitize_simple_spoken_english(ai_data["pinned_comment"])
                if ai_data.get("comment_replies") and isinstance(ai_data["comment_replies"], list) and len(ai_data["comment_replies"]) >= 3:
                    comment_replies = [sanitize_simple_spoken_english(r) for r in ai_data["comment_replies"][:3]]

        # 6. Tiered Hashtags (3 broad + 4 mid-niche + 3 exact-topic, zero spam)
        tiered_hashtags = self._build_tiered_hashtags(title, category, kw)
        hashtags_str = " ".join(tiered_hashtags)

        # 7. Full Caption Text (Simple, direct, searchable)
        caption_text = (
            f"{seo_headline}\n\n"
            f"{subheadline}\n\n"
            f"Key Breakdown:\n"
            f"{bullets_text}\n\n"
            f"💬 Comment \"{kw}\" below and I'll DM you the free link!\n\n"
            f"📌 PINNED DEBATE: {pinned_comment}\n\n"
            f"Follow @antigravity for daily zero-dollar workflows, retro hacks & unfiltered tech truth!\n\n"
            f"{hashtags_str}"
        )
        caption_text = sanitize_simple_spoken_english(caption_text)

        dm_msg = script_data.get("dm_message") or (
            f"Hey! 🚀 Here is the verified link and guide for {title}: https://antigravity.run/r/{kw.lower()}\n"
            f"Enjoy exploring, and drop any questions!"
        )
        dm_msg = sanitize_simple_spoken_english(dm_msg)

        autodm_payload = {
            "keyword": kw,
            "resource_topic": title,
            "public_comment_replies": comment_replies,
            "dm_message_template": dm_msg,
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
        }

    def _craft_pinned_comment(self, title: str, category: str, kw: str) -> str:
        """Crafts a sharp, opinionated ragebait debate question to pin in the comments."""
        lower_t = (title + " " + category).lower()
        if "browser" in lower_t or "retro" in lower_t or "game" in lower_t:
            return "Still downloading 80GB games on a dying potato laptop in 2026? Drop your excuse below 👇"
        elif "ai" in lower_t or "agent" in lower_t or "model" in lower_t:
            return "Still paying $20/month for AI in 2026? Be honest—would you even pass your job interview without it? 💀"
        elif "cost" in lower_t or "earn" in lower_t or "margin" in lower_t or "money" in lower_t or "business" in lower_t:
            return "Did you really think their free app was a gift or did you just realize you're the product? 💀 Debate below 👇"
        elif "dad" in lower_t or "wifi" in lower_t or "bill" in lower_t:
            return "Would you trust your dad to fix your Wi-Fi or pay $100 for a technician? Be honest 😂👇"
        else:
            return "Still paying monthly fees for software when 100% free tools exist? Drop your excuse below 👇"

    def _build_tiered_hashtags(self, title: str, category: str, kw: str) -> List[str]:
        """
        Assembles 9-10 tiered hashtags:
        - 3 broad reach tags
        - 4 mid-niche community tags
        - 3 exact-topic tags
        """
        broad = ["#TechReels", "#DeveloperLife", "#SoftwareEngineering"]

        lower_t = title.lower()
        if "game" in lower_t or "retro" in lower_t:
            mid = ["#BrowserGames", "#RetroGaming", "#WebAssembly", "#CodingHumor"]
            exact = ["#PCGaming", f"#{kw.title()}Game", "#WebDev"]
        elif "dad" in lower_t:
            mid = ["#IndianDad", "#TechHumor", "#FamilyHumor", "#RelatableMemes"]
            exact = ["#DesiMemes", "#DadLogic", f"#{kw.title()}Meme"]
        elif "money" in lower_t or "earn" in lower_t or "margin" in lower_t or "business" in lower_t:
            mid = ["#BusinessModels", "#TechEconomics", "#StartupStrategy", "#TechNews"]
            exact = ["#UnitEconomics", "#BusinessStrategy", f"#{kw.title()}Teardown"]
        else:
            mid = ["#AIUpdates", "#TechHacks", "#CodingCommunity", "#WebDevelopment"]
            exact = ["#ArtificialIntelligence", f"#{kw.title()}Guide", "#TechTrends"]

        return (broad + mid + exact)[:10]


if __name__ == "__main__":
    seo = SEOMasterAgent()
    sample_script = {
        "title": "LocalSend: The Free Open-Source AirDrop for Every Device",
        "category": "Free Open-Source GitHub Repos",
        "cta_keyword": "REPO",
        "hook": {
            "headline": "FREE AIRDROP FOR EVERY DEVICE",
            "subheadline": "Stop paying for cloud subscriptions just to send photos to your PC.",
            "tag": "⚡ 100% FREE REPO",
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
