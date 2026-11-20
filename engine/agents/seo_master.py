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
import json
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


class SEOMasterAgent:
    """
    Master Agent 3: Crafts Instagram search optimization, tiered hashtag sets,
    pinned comment conversation drivers, and anti-throttle Auto-DM configurations.
    Uses fast free-tier Gemini fallback with zero-fail deterministic safety.
    """

    FAST_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parent.parent.parent)
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.headers = {"User-Agent": "AntigravitySEOMaster/1.0", "Content-Type": "application/json"}
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 20000},
                )
            except Exception as e:
                print(f"⚠️ SEOMaster: Gemini client init notice: {e}")

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini with fast free-tier fallback models and direct REST."""
        if self.client:
            for m in self.FAST_MODELS:
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
                    print(f"⚠️ SEOMaster: GenAI {m} warning: {e}")

        if self.api_key:
            for m in self.FAST_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"},
                }
                try:
                    r = requests.post(url, json=payload, headers=self.headers, timeout=20.0)
                    if r.status_code == 200:
                        parts = r.json().get("candidates", [])[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text")
                except Exception as e:
                    print(f"⚠️ SEOMaster: REST {m} warning: {e}")

        return None

    def _refine_with_ai(self, title: str, category: str, kw: str, raw_headline: str) -> Optional[Dict[str, Any]]:
        """Optional AI refinement pass to elevate headline, pinned comment, and replies."""
        prompt = (
            f"Topic: {title}\n"
            f"Category: {category}\n"
            f"Auto-DM Keyword: {kw}\n"
            f"Draft Headline: {raw_headline}\n\n"
            "Return JSON with:\n"
            "- 'seo_headline': A high-CTR, front-loaded Instagram SEO title with emoji\n"
            "- 'pinned_comment': An opinionated debate starter question for viewers to comment below\n"
            "- 'comment_replies': Exactly 3 friendly, distinct public comment replies confirming DM sent (to avoid IG bot throttle)"
        )
        sys_inst = "You are an elite Instagram SEO and Engagement Director. Return ONLY valid JSON."
        try:
            raw = self._call_gemini_api(prompt, sys_inst)
            if raw:
                data = json.loads(raw.strip().strip("`").replace("json\n", "", 1))
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
        title = script_data.get("title", "Daily Tech Breakdown")
        hook_obj = script_data.get("hook", {})
        if isinstance(hook_obj, dict):
            headline = hook_obj.get("headline", title)
            subheadline = hook_obj.get("subheadline", "")
            tag = hook_obj.get("tag", "⚠️ VIRAL REAL TALK")
        else:
            headline = title
            subheadline = str(hook_obj)
            tag = "⚠️ VIRAL REAL TALK"

        kw = str(script_data.get("cta_keyword") or script_data.get("ctaKeyword", "LINK")).strip().upper()
        category = script_data.get("category", "Tech Innovation")

        # 1. Generate 3 crisp value bullets from cardData or dialogue
        card_data = script_data.get("cardData") or {}
        bullets = []
        if isinstance(card_data, dict):
            for k, v in list(card_data.items())[:3]:
                clean_k = k.replace("_", " ").title()
                bullets.append(f"• {clean_k}: {v}")

        if not bullets:
            bullets = [
                "• 100% Free workflow running directly in your browser",
                "• Zero installation or bloated cloud subscriptions",
                "• Step-by-step setup and instant direct link",
            ]
        bullets_text = "\n".join(bullets)

        # 2. Front-loaded High-CTR SEO Headline
        seo_headline = f"{tag} {headline.title() if headline.isupper() else headline}"

        # 3. Pinned Comment Bait (opinionated question to trigger debate velocity)
        pinned_comment = self._craft_pinned_comment(title, category, kw)

        # 4. Varied Public Comment Replies (3 variations to bypass Instagram bot throttling)
        comment_replies = [
            f"Sent to your DMs! 🚀 Check your message requests if you don't see it.",
            f"Just sent over the direct link! ⚡ Enjoy.",
            f"Check your messages! 📬 Sent the full guide and link.",
        ]

        # 5. Optional AI refinement with fast free-tier fallback
        if self.api_key:
            ai_data = self._refine_with_ai(title, category, kw, seo_headline)
            if ai_data:
                if ai_data.get("seo_headline"):
                    seo_headline = ai_data["seo_headline"]
                if ai_data.get("pinned_comment"):
                    pinned_comment = ai_data["pinned_comment"]
                if ai_data.get("comment_replies") and isinstance(ai_data["comment_replies"], list) and len(ai_data["comment_replies"]) >= 3:
                    comment_replies = ai_data["comment_replies"][:3]

        # 6. Tiered Hashtags (3 broad + 4 mid-niche + 3 exact-topic, zero spam)
        tiered_hashtags = self._build_tiered_hashtags(title, category, kw)
        hashtags_str = " ".join(tiered_hashtags)

        # 7. Full Caption Text
        caption_text = (
            f"{seo_headline}\n\n"
            f"{subheadline}\n\n"
            f"Key Breakdown:\n"
            f"{bullets_text}\n\n"
            f"💬 Comment \"{kw}\" below and I'll DM you the link!\n\n"
            f"📌 PINNED DEBATE: {pinned_comment}\n\n"
            f"Follow @antigravity for daily zero-dollar workflows, retro hacks & unfiltered tech truth!\n\n"
            f"{hashtags_str}"
        )

        dm_msg = script_data.get("dm_message") or (
            f"Hey! 🚀 Here is the verified link and guide for {title}: https://antigravity.run/r/{kw.lower()}\n"
            f"Enjoy exploring, and drop any questions!"
        )

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
        """Crafts a sharp, opinionated debate starter to pin in the comments."""
        lower_t = title.lower()
        if "browser" in lower_t or "retro" in lower_t or "game" in lower_t:
            return "What's the #1 classic PC game that deserves a full browser remake next? Drop it below 👇"
        elif "ai" in lower_t or "agent" in lower_t or "model" in lower_t:
            return "Be honest: would you rather pay $20/month for an official AI agent or run a free one locally? Debate below 👇"
        elif "cost" in lower_t or "earn" in lower_t or "margin" in lower_t or "money" in lower_t:
            return "Is this business model genius or a complete customer trap? What do you think? 👇"
        elif "dad" in lower_t or "wifi" in lower_t or "bill" in lower_t:
            return "Has your dad ever done something like this? What's his craziest tech fix? 😂👇"
        else:
            return "Did this surprise you or did you already know this was possible? Drop your take below 👇"

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
        "title": "Developer builds complete Intel 486 PC emulator in browser",
        "category": "Retro & Browser Games",
        "cta_keyword": "RETRO",
        "hook": {
            "headline": "INTEL 486 RUNNING IN CHROME",
            "subheadline": "Someone just ported an entire 486 PC into Chrome.",
            "tag": "🕹️ RETRO BREAKTHROUGH",
        },
        "cardData": {
            "engine": "100% Pure JavaScript",
            "components": "Modular CPU, RAM, and VGA",
            "performance": "Instant Boot in Tab",
        },
    }
    assets = seo.generate_seo_assets(sample_script)
    print("\n--- SEOMaster Output ---")
    print("SEO Headline:", assets["seo_headline"])
    print("\nPinned Comment:", assets["pinned_comment"])
    print("\nHashtags:", assets["tiered_hashtags"])
    print("\nAuto-DM Replies:", assets["autodm_payload"]["public_comment_replies"])
