"""
Agent: Viral AI Recreation & Remix Director
Transforms an ingested social reel's viral anatomy into our signature Remotion animated
visual engine, with slightly remixed narrative twists, fresh punchlines, our character rosters,
and our neural Edge-TTS voice synthesis.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.agents.trend_scout import enable_fast_dns
enable_fast_dns()
from engine.agents.hook_master import HookMasterAgent

try:
    from google import genai
except ImportError:
    genai = None


class RecreationDirectorAgent:
    """Agent that recreates and remixes social media reels with custom animations and voices."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.client = None
        if genai and os.environ.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client(http_options={"api_version": "v1beta", "timeout": 15000})
            except Exception as e:
                print(f"⚠️ Gemini Client init notice in Recreation Director: {e}")

        self.hook_master = HookMasterAgent(project_root=self.project_root)

        # Load content pillars matrix
        self.pillars_file = self.project_root / "engine" / "config" / "content_pillars.json"
        self.pillars_data = {}
        if self.pillars_file.exists():
            try:
                with open(self.pillars_file, "r", encoding="utf-8") as f:
                    self.pillars_data = json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load content_pillars.json: {e}")

    def recreate_reel(
        self,
        source_analysis: Dict[str, Any],
        target_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recreates and remixes the source video into our Remotion screenplay.
        Preserves viral retention psychology while changing specific jokes, characters, and visuals.
        """
        print(f"🎨 [Recreation Director] Remixing reel: '{source_analysis.get('hook', 'Trending Topic')}'...")

        format_type = source_analysis.get("format_type", "ai_vs_dev")
        if target_style:
            chosen_style = target_style
        elif "dad" in format_type or "dad" in str(source_analysis).lower():
            chosen_style = "ai_vs_dad"
        else:
            chosen_style = "diner_ai"

        if self.hook_master:
            try:
                topic_payload = {
                    "title": source_analysis.get("title") or source_analysis.get("topic") or source_analysis.get("core_topic") or "Viral Reel Remix",
                    "topic_title": source_analysis.get("title") or source_analysis.get("topic") or "Viral Reel Remix",
                    "category": source_analysis.get("category") or source_analysis.get("pillar_style") or "Trending Viral Remix",
                    "auto_dm_keyword": source_analysis.get("auto_dm_keyword") or source_analysis.get("cta_keyword") or "LINK",
                    "left_character": source_analysis.get("left_character") or ("dad" if "dad" in chosen_style else "junior_dev"),
                    "right_character": source_analysis.get("right_character") or "claude",
                    "scene_preset": source_analysis.get("scene_preset") or "diner",
                    "core_conflict": source_analysis.get("core_conflict") or "Internet debate vs engineering reality",
                    "viral_score": source_analysis.get("viral_score", 88),
                    "card_data": source_analysis.get("card_data") or source_analysis.get("cardData"),
                }
                return self.hook_master.craft_reel_screenplay(topic_payload)
            except Exception as e:
                print(f"⚠️ HookMaster delegation notice: {e}. Trying internal generator.")

        if self.client:
            try:
                return self._generate_screenplay_with_gemini(source_analysis, chosen_style)
            except Exception as e:
                print(f"⚠️ Gemini screenplay generation error: {e}. Using curated 6-pillar remix matrix.")

        return self._curated_remix_fallback(source_analysis, chosen_style)

    def _generate_screenplay_with_gemini(
        self,
        analysis: Dict[str, Any],
        chosen_style: str
    ) -> Dict[str, Any]:
        """Uses Gemini 2.5 Flash to generate a high-retention viral script with spoken Auto-DM CTA."""
        system_instruction = (
            "You are the Lead Screenwriter & Creative Director for an automated short-form viral video channel.\n"
            "Your channel revolves around 6 Viral Content Pillars:\n"
            "1. Retro & Browser Games (e.g. GTA Vice City or Project IGI in browser tab. CTA Keyword: VICE, IGI, PLAY)\n"
            "2. Underrated AI & App Workflows (e.g. NotebookLM turning PDFs into podcasts, Obsidian offline AI. CTA Keyword: NOTEBOOK, APPS)\n"
            "3. New Tech in the World (e.g. humanoid robots folding laundry, $6M open weights reasoning drops. CTA Keyword: TECH, LINK)\n"
            "4. How Companies Actually Earn (e.g. NVIDIA 75% margin on sand, Costco chicken loss-leader. CTA Keyword: MODEL, BIZ)\n"
            "5. Hype vs. Reality / Pros & Cons (e.g. OpenRouter 1-API switching vs latency markup. CTA Keyword: ROUTER, TRUTH)\n"
            "6. Relatable Tech / Dev / Indian Dad Memes (e.g. Friday 5pm production deployments, Dad vs Cloud storage. CTA Keyword: PROMPT, MEME)\n\n"
            "STRICT RULES:\n"
            "- STRICT 2-CHARACTER CAST ONLY: Exactly 2 characters per reel:\n"
            "  * left_character: strictly 'junior_dev' OR 'dad'\n"
            "  * right_character: strictly 'claude', 'gemini', or 'grok'\n"
            "- Every single dialogue turn MUST have speaker set to EITHER left_character OR right_character. Never introduce a 3rd speaker.\n"
            "- 0-3s SCROLL-STOP HOOK: Turn 0 must be an instant curiosity gap, bold claim, or relatable conflict. Never start with 'Hey guys'.\n"
            "- STRICT DURATION TARGET: Exactly 6 snappy turns (target duration: 22 to 26 seconds). Keep every turn under 14 words for maximum retention and comedic punch.\n"
            "- UPPER-THIRD PROOF CARD: Exactly one turn (Turn 2 or 3) must have 'cardTrigger': true where a structured table/checklist proof card appears.\n"
            "- SPOKEN AUTO-DM CTA ON FINAL TURN: The final turn MUST end naturally with spoken CTA: 'Comment [KEYWORD] and I'll DM you the exact link.' (using a single uppercase keyword matching the topic).\n"
            "- Return strictly a valid JSON object matching the requested schema."
        )

        pref_left = analysis.get("left_character") or ("dad" if "dad" in chosen_style else "junior_dev")
        pref_right = analysis.get("right_character") or "claude"
        pref_scene = analysis.get("scene_preset") or analysis.get("scenePreset") or "diner"
        cta_word = str(analysis.get("cta_keyword") or analysis.get("auto_dm_keyword") or "LINK").strip().upper()

        prompt = f"""
Source Topic / Inspiration:
- Topic: {analysis.get('topic') or analysis.get('core_topic') or analysis.get('topic_title') or analysis.get('title')}
- Hook: {analysis.get('hook') or analysis.get('hook_angle')}
- Core Conflict: {analysis.get('core_conflict')}
- Summary: {analysis.get('transcript_summary') or analysis.get('concept')}
- Punchline: {analysis.get('punchline') or analysis.get('meme_twist')}
- Chosen Style: {chosen_style}
- Recommended CTA Keyword: {cta_word}
- Preferred Cast: Left={pref_left}, Right={pref_right}
- Preferred Scene Preset: {pref_scene}

Produce a complete Remotion screenplay JSON with:
{{
  "title": "Short punchy title (max 50 chars)",
  "style": "{pref_scene}",
  "comp": "MasterAutonomousReel",
  "scenePreset": "{pref_scene}",
  "leftCharacterId": "{pref_left}",
  "rightCharacterId": "{pref_right}",
  "cast": {{
    "left": "{pref_left}",
    "right": "{pref_right}"
  }},
  "cta_keyword": "{cta_word}",
  "cta_phrase": "Comment {cta_word} and I'll DM you the exact link.",
  "environment": "diner",
  "weather": "raining",
  "cardType": "comparison",
  "badge": "VERIFIED PROOF",
  "explainerTitle": "Title on proof card",
  "cardData": {{
    "point_1": "Key metric or pro",
    "point_2": "Secondary detail or con",
    "point_3": "Crucial fact"
  }},
  "hook": {{
    "headline": "ALL-CAPS 3-5 WORD HEADLINE",
    "subheadline": "One punchy subtitle sentence",
    "tag": "⚠️ VIRAL REAL TALK"
  }},
  "seo_keywords": [
    "search query 1",
    "search query 2",
    "search query 3"
  ],
  "hashtags": [
    "#TechReels", "#DevHumor", "#AIUpdates"
  ],
  "characters": [
    {{"id": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "name": "{'Dad' if 'dad' in chosen_style else 'Junior Dev'}"}},
    {{"id": "claude", "name": "Claude"}}
  ],
  "dialogue": [
    {{"speaker": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "character_id": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "text": "Turn 0 instant scroll-stop hook...", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "claude", "character_id": "claude", "text": "Turn 1 dry sarcastic reply...", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "character_id": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "text": "Turn 2 question or disbelief...", "emotion": "shocked", "cardTrigger": true, "pause_after": 0.40}},
    {{"speaker": "claude", "character_id": "claude", "text": "Turn 3 proof card explanation...", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "character_id": "{'dad' if 'dad' in chosen_style else 'junior_dev'}", "text": "Turn 4 funny relatable punchline reaction...", "emotion": "smug", "pause_after": 0.35}},
    {{"speaker": "claude", "character_id": "claude", "text": "Comment {analysis.get('cta_keyword', 'LINK').upper()} and I'll DM you the exact link.", "emotion": "smug", "pause_after": 0.40}}
  ]
}}
Return ONLY valid JSON.
"""

        response = None
        for model_name in ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"]:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=[prompt],
                    config=dict(system_instruction=system_instruction)
                )
                if response and response.text:
                    break
            except Exception as e:
                err_msg = str(e).lower()
                print(f"⚠️ Gemini model {model_name} attempt: {e}")
                if "connect" in err_msg or "timeout" in err_msg or "network" in err_msg or "failed to establish" in err_msg:
                    print("⚠️ Network connection to Gemini API unavailable; fast-falling back to 6-pillar matrix.")
                    break
                continue

        if not response or not response.text:
            raise RuntimeError("Gemini generate_content returned empty response across models.")

        raw_text = response.text.strip().strip("`").replace("json\n", "", 1)
        screenplay = json.loads(raw_text)

        # Post-process & strictly enforce 2-character cast sync and CTA
        left_char = "dad" if ("dad" in chosen_style or "dad" in str(screenplay.get("leftCharacterId", "")).lower()) else "junior_dev"
        right_char = screenplay.get("rightCharacterId", "claude").lower()
        if "gemini" in right_char:
            right_char = "gemini"
        elif "grok" in right_char:
            right_char = "grok"
        else:
            right_char = "claude"

        screenplay["leftCharacterId"] = left_char
        screenplay["rightCharacterId"] = right_char
        screenplay["cast"] = {"left": left_char, "right": right_char}

        # Resolve CTA keyword
        cta_kw = (screenplay.get("cta_keyword") or analysis.get("cta_keyword") or analysis.get("auto_dm_keyword") or "LINK").strip().upper()
        screenplay["cta_keyword"] = cta_kw
        screenplay["ctaKeyword"] = cta_kw
        screenplay["cta_text"] = f"💬 Comment {cta_kw} for the link"
        screenplay["ctaText"] = f"💬 Comment {cta_kw} for the link"

        sanitized_dialogue = []
        raw_dialogue = screenplay.get("dialogue", [])
        for idx, turn in enumerate(raw_dialogue):
            spk = str(turn.get("speaker", "")).lower()
            cid = str(turn.get("character_id", "")).lower()
            token = f"{spk} {cid}"

            if "dad" in token or "junior" in token or "dev" in token or "son" in token or "human" in token:
                assigned = left_char
            else:
                assigned = right_char

            turn["character_id"] = assigned
            turn["speaker"] = assigned

            # Ensure final turn contains the spoken Auto-DM CTA
            if idx == len(raw_dialogue) - 1:
                t_text = turn.get("text", "")
                if "comment" not in t_text.lower():
                    turn["text"] = f"Comment {cta_kw} and I'll DM you the exact link."

            sanitized_dialogue.append(turn)

        screenplay["dialogue"] = sanitized_dialogue
        print(f"✅ [Recreation Director] Successfully remixed into: '{screenplay.get('title')}' (Cast: {left_char} & {right_char}, CTA: {cta_kw})")
        return screenplay

    def _build_screenplay_from_pillar_topic(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """Constructs a deterministic broadcast-grade Remotion screenplay from a curated pillar topic."""
        left_char = topic.get("left_character", "junior_dev")
        right_char = topic.get("right_character", "claude")
        cta_kw = str(topic.get("cta_keyword", "LINK")).strip().upper()
        cta_phrase = topic.get("cta_phrase") or f"Comment {cta_kw} and I'll DM you the exact link."

        hook_text = topic.get("hook", "Check out this wild new development.")
        punchline = topic.get("punchline", "And that is why the internet never sleeps.")
        card_title = topic.get("card_title", "Technical Breakdown")

        if left_char == "dad":
            d0 = f"Claude, {hook_text}"
            d1 = "It is mathematically verifiable engineering, sir."
            d2 = "In my day we solved this with five rupees and a screwdriver!"
            d3 = "Notice the metrics on the board, sir. Your screwdriver does not compile WebAssembly."
            d4 = f"{punchline}"
            d5 = f"{cta_phrase}"
        else:
            d0 = f"Claude, {hook_text}"
            d1 = "Let me guess, you just found out about it today."
            d2 = "Is this actually real or just Twitter engagement bait?"
            d3 = "Look at the benchmark on screen. It is running live right now."
            d4 = f"{punchline}"
            d5 = f"{cta_phrase}"

        dialogue = [
            {"speaker": left_char, "character_id": left_char, "text": d0, "emotion": "shocked", "pause_after": 0.35},
            {"speaker": right_char, "character_id": right_char, "text": d1, "emotion": "smug", "pause_after": 0.35},
            {"speaker": left_char, "character_id": left_char, "text": d2, "emotion": "shocked", "pause_after": 0.35},
            {"speaker": right_char, "character_id": right_char, "text": d3, "emotion": "smug", "cardTrigger": True, "pause_after": 0.40},
            {"speaker": left_char, "character_id": left_char, "text": d4, "emotion": "smug", "pause_after": 0.35},
            {"speaker": right_char, "character_id": right_char, "text": d5, "emotion": "smug", "pause_after": 0.40},
        ]

        return {
            "title": topic.get("title", "Daily Viral Tech Breakdown"),
            "style": "diner",
            "comp": "MasterAutonomousReel",
            "scenePreset": "diner",
            "leftCharacterId": left_char,
            "rightCharacterId": right_char,
            "cast": {"left": left_char, "right": right_char},
            "cta_keyword": cta_kw,
            "ctaKeyword": cta_kw,
            "cta_phrase": cta_phrase,
            "cta_text": f"💬 Comment {cta_kw} for the link",
            "ctaText": f"💬 Comment {cta_kw} for the link",
            "environment": "diner",
            "weather": "raining",
            "cardType": topic.get("card_type", "comparison"),
            "badge": topic.get("badge", "VERIFIED"),
            "explainerTitle": card_title,
            "cardData": topic.get("card_data", {}),
            "hook": {
                "headline": topic.get("title", "TECH BREAKTHROUGH").upper()[:35],
                "subheadline": hook_text,
                "tag": f"⚠️ {cta_kw} GUIDE"
            },
            "seo_keywords": topic.get("seo_keywords", []),
            "hashtags": topic.get("hashtags", []),
            "dm_message": topic.get("dm_message", f"Here is your link for {cta_kw}!"),
            "characters": [
                {"id": left_char, "name": "Dad" if left_char == "dad" else "Junior Dev"},
                {"id": right_char, "name": "Claude"}
            ],
            "dialogue": dialogue
        }

    def _curated_remix_fallback(
        self,
        analysis: Dict[str, Any],
        chosen_style: str
    ) -> Dict[str, Any]:
        """High-performing hand-crafted fallback matrix if API is unreachable."""
        # 1. Search loaded content pillars first
        all_topics = []
        if self.pillars_data and "pillars" in self.pillars_data:
            for p in self.pillars_data["pillars"]:
                all_topics.extend(p.get("topics", []))

        target_text = str(analysis.get("topic") or analysis.get("hook") or analysis.get("core_topic") or "").lower()
        if target_text:
            for t in all_topics:
                t_title = t.get("title", "").lower()
                t_core = t.get("core_topic", "").lower()
                if t_title in target_text or t_core in target_text or target_text in t_title:
                    return self._build_screenplay_from_pillar_topic(t)

        # 2. If analysis already contains full pillar data (from morning pool)
        if ("card_data" in analysis or "cardData" in analysis) and "hook" in analysis:
            return self._build_screenplay_from_pillar_topic(analysis)

        # 3. If chosen style is ai_vs_dad, select first dad topic
        if chosen_style == "ai_vs_dad":
            dad_topics = [t for t in all_topics if t.get("left_character") == "dad"]
            if dad_topics:
                return self._build_screenplay_from_pillar_topic(dad_topics[0])

        # 4. Fallback to first available pillar topic
        if all_topics:
            idx = int(time.time() / 86400) % len(all_topics)
            return self._build_screenplay_from_pillar_topic(all_topics[idx])

        # 5. Default static fallback if config file missing
        return {
            "title": "OpenRouter: Hype vs Reality",
            "style": "diner",
            "comp": "MasterAutonomousReel",
            "scenePreset": "diner",
            "leftCharacterId": "junior_dev",
            "rightCharacterId": "claude",
            "cast": {"left": "junior_dev", "right": "claude"},
            "cta_keyword": "ROUTER",
            "ctaKeyword": "ROUTER",
            "cta_phrase": "Comment ROUTER and I'll DM you the exact link.",
            "cta_text": "💬 Comment ROUTER for the link",
            "ctaText": "💬 Comment ROUTER for the link",
            "environment": "diner",
            "weather": "raining",
            "cardType": "comparison",
            "badge": "HONEST AUDIT",
            "explainerTitle": "OpenRouter: Pros vs Cons",
            "cardData": {
                "pro_1": "Single API for 200+ Models",
                "pro_2": "Zero monthly commitments",
                "con_1": "50-150ms Added Proxy Latency",
                "con_2": "Upstream rate limit throttling"
            },
            "hook": {
                "headline": "OPENROUTER: HYPE VS REALITY",
                "subheadline": "Everyone hypes OpenRouter, but nobody mentions the proxy latency",
                "tag": "⚡ HONEST REVIEW"
            },
            "seo_keywords": ["OpenRouter pros and cons", "OpenRouter latency", "best AI router"],
            "hashtags": ["#OpenRouter", "#AIModels", "#DevTools", "#TechTruth"],
            "dm_message": "Here is the honest OpenRouter cheat sheet with latency comparisons!",
            "characters": [
                {"id": "junior_dev", "name": "Junior Dev"},
                {"id": "claude", "name": "Claude"}
            ],
            "dialogue": [
                {"speaker": "junior_dev", "character_id": "junior_dev", "text": "Claude, everyone is hyping OpenRouter as the ultimate AI tool.", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": "claude", "character_id": "claude", "text": "It has three real pros, but three nasty cons nobody talks about.", "emotion": "smug", "pause_after": 0.35},
                {"speaker": "junior_dev", "character_id": "junior_dev", "text": "What cons? It connects to two hundred models with one key!", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": "claude", "character_id": "claude", "text": "Proxy latency adds up to one hundred fifty milliseconds.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.40},
                {"speaker": "junior_dev", "character_id": "junior_dev", "text": "So when the proxy lags, my entire production frontend freezes.", "emotion": "tired", "pause_after": 0.35},
                {"speaker": "claude", "character_id": "claude", "text": "Comment ROUTER and I'll DM you the exact link.", "emotion": "smug", "pause_after": 0.40}
            ]
        }


if __name__ == "__main__":
    recreator = RecreationDirectorAgent()
    screenplay = recreator.recreate_reel({
        "hook": "Why you should never pay for AI wrappers in 2026",
        "core_topic": "Free vs Paid AI Tools",
        "format_type": "ai_vs_dev",
        "transcript_summary": "Devs spend $200 a month on closed AI tools when open-source alternatives are free.",
        "punchline": "Stop donating to wrapper founders."
    })
    print("Recreation Title:", screenplay.get("title"))
    print("Dialogue Count:", len(screenplay.get("dialogue", [])))
