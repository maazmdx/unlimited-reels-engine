"""
TopicMasterAgent (Master Agent 1: Mass-Appeal Viral Topic Curator)
Replaces narrow CS-trivia bias with consumer-facing tech, viral AI tools, retro browser games,
and company business model teardowns.
Gathers live zero-cost signals from Google News RSS, Product Hunt, Hacker News, Reddit, and GitHub.
Executes an objective 3-criteria Viral Scoring Gate (0-100) via Gemini 2.5 Flash, rejecting anything < 78.
Deduplicates against inbox/covered_topics.json with emergency fallback to content_pillars.json.
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
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


class TopicMasterAgent:
    """
    Master Agent 1: Discovers and scores high-voltage, mass-appeal tech, gaming,
    AI workflow, and business model topics.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AntigravityTopicMaster/3.0"
    )

    CORE_CATEGORIES = [
        "Playable Retro & Browser Games (zero-install WebAssembly classics, emulator tricks)",
        "Underrated AI Apps & Workflows (free tools destroying paid SaaS, automated workflows)",
        "Shocking Company Business Models (hidden margins, loss-leaders, how tech giants print cash)",
        "Breaking Consumer Tech & Hardware (humanoid robots, wild gadgets, open weight drops)",
        "Hype vs. Reality / Pros & Cons (honest non-sponsored teardowns, latency traps, token math)",
        "Relatable Developer & Indian Dad Culture (production panic, generational tech clashes, WiFi physics)",
    ]

    def __init__(
        self,
        project_root: Optional[Path] = None,
        gemini_api_key: Optional[str] = None,
        timeout: float = 6.0,
    ):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.timeout = timeout
        self.headers = {"User-Agent": self.DEFAULT_USER_AGENT}
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        self.covered_topics_file = self.project_root / "inbox" / "covered_topics.json"
        self.pillars_file = self.project_root / "engine" / "config" / "content_pillars.json"

        self.api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 30000},
                )
            except Exception as e:
                print(f"⚠️ TopicMaster: Gemini client init notice: {e}")

    # =========================================================================
    # 1. LIVE SIGNAL HARVESTING (Consumer Tech, Games, AI Apps, Business)
    # =========================================================================

    def fetch_google_news_signals(self) -> List[Dict[str, Any]]:
        """
        Scrapes zero-cost Google News RSS feeds for consumer AI, browser games,
        viral tech launches, and company business model teardowns.
        """
        signals = []
        queries = [
            ("AI+tools+apps", "GoogleNews: AI Apps"),
            ("retro+games+browser", "GoogleNews: Browser Games"),
            ("tech+business+model+margin", "GoogleNews: Tech Business"),
            ("viral+tech+hardware", "GoogleNews: Viral Tech"),
        ]

        for query, label in queries:
            url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            try:
                r = self.session.get(url, timeout=3.5)
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    items = root.findall(".//item")[:5]
                    for it in items:
                        t = it.findtext("title")
                        link = it.findtext("link")
                        if t and " - " in t:
                            # Clean publisher suffix from title
                            t = t.rsplit(" - ", 1)[0].strip()
                        if t and len(t) > 10:
                            signals.append({
                                "source": label,
                                "title": t,
                                "url": link or url,
                            })
            except Exception as e:
                print(f"ℹ️ [TopicMaster] Google News query '{query}' notice: {e}")

        return signals

    def fetch_product_hunt_signals(self) -> List[Dict[str, Any]]:
        """Scrapes trending new tool launches from Product Hunt RSS."""
        signals = []
        try:
            url = "https://www.producthunt.com/feed"
            r = self.session.get(url, timeout=3.5)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")[:6]
                for e in entries:
                    t = e.findtext("{http://www.w3.org/2005/Atom}title")
                    link_el = e.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.get("href", "") if link_el is not None else ""
                    if t:
                        signals.append({
                            "source": "Product Hunt Trending",
                            "title": t.strip(),
                            "url": link,
                        })
        except Exception as e:
            print(f"ℹ️ [TopicMaster] Product Hunt RSS notice: {e}")
        return signals

    def fetch_hacker_news_signals(self, max_items: int = 10) -> List[Dict[str, Any]]:
        """Fetches Show HN and Top stories with high consumer/developer appeal."""
        signals = []
        endpoints = [
            ("https://hacker-news.firebaseio.com/v0/showstories.json", "Show HN (Apps/Games)"),
            ("https://hacker-news.firebaseio.com/v0/topstories.json", "HackerNews Top"),
        ]

        for ep_url, label in endpoints:
            try:
                r = self.session.get(ep_url, timeout=3.0)
                if r.status_code != 200:
                    continue
                ids = r.json()[:max_items]
                for item_id in ids:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
                    try:
                        ir = self.session.get(item_url, timeout=2.0)
                        if ir.status_code == 200:
                            data = ir.json()
                            title = data.get("title")
                            if title and len(title) > 6:
                                signals.append({
                                    "source": label,
                                    "title": title.strip(),
                                    "url": data.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                                })
                    except Exception:
                        continue
            except Exception as e:
                print(f"ℹ️ [TopicMaster] HN ({label}) notice: {e}")

        return signals

    def fetch_reddit_signals(self) -> List[Dict[str, Any]]:
        """Queries trending subreddits with graceful skip on 403 / 429."""
        signals = []
        subreddits = [
            "InternetIsBeautiful",
            "ChatGPT",
            "ArtificialInteligence",
            "webgames",
            "technology",
        ]
        reddit_headers = {
            "User-Agent": "AntigravityTopicMaster/3.0 (compatible; research; Linux x86_64)"
        }

        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=4"
            try:
                r = requests.get(url, headers=reddit_headers, timeout=2.0)
                if r.status_code == 200:
                    children = r.json().get("data", {}).get("children", [])
                    for c in children:
                        pdata = c.get("data", {})
                        t = pdata.get("title", "").strip()
                        if t and not pdata.get("stickied", False):
                            signals.append({
                                "source": f"Reddit r/{sub}",
                                "title": t,
                                "url": f"https://reddit.com{pdata.get('permalink', '')}",
                            })
            except Exception:
                continue

        return signals

    def fetch_tech_rss_and_github_signals(self) -> List[Dict[str, Any]]:
        """Queries The Verge RSS, Lobsters, Dev.to, and GitHub Search."""
        signals = []
        # Tech RSS
        feeds = [
            ("https://www.theverge.com/rss/index.xml", "The Verge"),
            ("https://lobste.rs/rss", "Lobsters"),
            ("https://dev.to/feed", "Dev.to"),
        ]
        for url, label in feeds:
            try:
                r = self.session.get(url, timeout=3.0)
                if r.status_code == 200:
                    root = ET.fromstring(r.content)
                    for it in root.findall(".//item")[:4]:
                        t = it.findtext("title")
                        link = it.findtext("link")
                        if t:
                            signals.append({"source": label, "title": t.strip(), "url": link or url})
                    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:4]:
                        t = entry.findtext("{http://www.w3.org/2005/Atom}title")
                        if t:
                            signals.append({"source": label, "title": t.strip(), "url": url})
            except Exception:
                continue

        # GitHub Trending Repos
        try:
            gh_url = "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-01-01&sort=updated&order=desc"
            r_gh = self.session.get(gh_url, timeout=3.0)
            if r_gh.status_code == 200:
                for it in r_gh.json().get("items", [])[:5]:
                    name = it.get("full_name") or it.get("name")
                    desc = it.get("description") or "Open source project"
                    signals.append({
                        "source": "GitHub Trending",
                        "title": f"{name}: {desc[:80]}",
                        "url": it.get("html_url", ""),
                    })
        except Exception:
            pass

        return signals

    def harvest_live_signals(self) -> List[Dict[str, Any]]:
        """Gathers and deduplicates all live signals across news, product hunt, HN, and GitHub."""
        raw = []
        raw.extend(self.fetch_google_news_signals())
        raw.extend(self.fetch_product_hunt_signals())
        raw.extend(self.fetch_hacker_news_signals(max_items=8))
        raw.extend(self.fetch_reddit_signals())
        raw.extend(self.fetch_tech_rss_and_github_signals())

        # Deduplicate
        seen = set()
        deduped = []
        for s in raw:
            norm = re.sub(r"[^a-zA-Z0-9]", "", s["title"].lower())[:45]
            if norm and norm not in seen:
                seen.add(norm)
                deduped.append(s)

        return deduped

    # =========================================================================
    # 2. DEDUPLICATION HISTORY (Never-Repeat Tracker)
    # =========================================================================

    def load_covered_history(self) -> List[Dict[str, Any]]:
        """Loads historical covered topics from inbox/covered_topics.json."""
        if not self.covered_topics_file.exists():
            return []
        try:
            with open(self.covered_topics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "covered_topics" in data:
                return data["covered_topics"]
        except Exception as e:
            print(f"⚠️ TopicMaster: Error reading covered_topics.json: {e}")
        return []

    def get_last_covered_topics(self, limit: int = 50) -> List[str]:
        """Returns the last N covered topic titles for exclusion in prompt."""
        history = self.load_covered_history()
        titles = []
        for item in history[-limit:]:
            t = item.get("title") or item.get("topic_title") or item.get("slug")
            if t:
                titles.append(t)
        return titles

    def record_covered_topics(self, new_topics: List[Dict[str, Any]]):
        """Appends freshly selected topics to inbox/covered_topics.json."""
        history = self.load_covered_history()
        today_str = datetime.now().strftime("%Y-%m-%d")

        for topic in new_topics:
            title = topic.get("topic_title") or topic.get("title", "Dynamic Topic")
            slug = topic.get("id") or "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")[:45]
            history.append({
                "slug": slug,
                "title": title,
                "date": today_str,
                "auto_dm_keyword": topic.get("auto_dm_keyword", "LINK"),
                "category": topic.get("category", "Trending Tech"),
                "viral_score": topic.get("viral_score", 85),
            })

        self.covered_topics_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.covered_topics_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print(f"💾 [TopicMaster] Saved {len(new_topics)} topic(s) into inbox/covered_topics.json.")
        except Exception as e:
            print(f"⚠️ TopicMaster: Failed to write covered_topics.json: {e}")

    # =========================================================================
    # 3. GEMINI 2.5 FLASH VIRAL SCORING GATE (0-100)
    # =========================================================================

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Calls Gemini 2.5 Flash with fallback to gemini-3.5-flash and direct REST."""
        models = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

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
                    print(f"⚠️ TopicMaster: GenAI {m} warning: {e}")

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
                    print(f"⚠️ TopicMaster: REST {m} warning: {e}")

        return None

    def curate_and_score_topics(
        self,
        signals: List[Dict[str, Any]],
        count: int,
        covered_history: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Generates 8 candidate angles and scores each (0-100) on:
        - Mass-Appeal Curiosity (0-35)
        - Save/DM Demand (0-35)
        - Meme & Debate Potential (0-30)
        Rejects anything < 78 or smelling like narrow CS trivia. Returns top N winners.
        """
        today_str = datetime.now().strftime("%B %d, %Y")

        signals_summary = []
        for idx, s in enumerate(signals[:20], 1):
            signals_summary.append(f"{idx}. [{s['source']}] {s['title']}")
        signals_text = "\n".join(signals_summary) if signals_summary else "No live feeds available."

        excluded_text = "\n".join(f"- {t}" for t in covered_history[-50:]) if covered_history else "- None."

        system_instruction = (
            "You are TopicMaster: The World-Class Viral Media Strategist for short-form video (Instagram Reels / YouTube Shorts).\n"
            "Your mandate: Select ONLY topics that have MASS CONSUMER APPEAL across college students, everyday developers, gamers, and tech fans.\n\n"
            "STRICT BAN ON DRY CS TRIVIA:\n"
            "- Strictly BANNED: RFC specs, obscure algorithmic puzzle solvers, low-level Linux kernel patches, academic math proofs, compiler edge-cases.\n"
            "- STRICTLY REWARDED: Playable retro games in browser, zero-cost AI workflows that replace $20/mo subscriptions, shocking company profit breakdowns (NVIDIA, Costco, Spotify), breaking humanoid robots / gadgets, and generational tech comedy (Dad vs WiFi / cloud bills).\n\n"
            "OBJECTIVE VIRAL SCORING RUBRIC (0-100):\n"
            "1. Mass-Appeal Curiosity (0-35): Would a casual viewer, student, or dev freeze their thumb in the first 2 seconds?\n"
            "2. Save/DM Demand (0-35): Would thousands of viewers comment a keyword to get the free link, playable port, or cheat sheet?\n"
            "3. Meme & Debate Potential (0-30): Does it spark energetic comments ('Wait really?', 'No way!', or generational conflict)?\n"
            "- MINIMUM PASSING SCORE: 78/100. Any topic scoring < 78 is automatically REJECTED."
        )

        prompt = f"""
Today's Date: {today_str}

LIVE SOURCE SIGNALS TODAY:
{signals_text}

PREVIOUSLY COVERED (DO NOT REPEAT):
{excluded_text}

TASK:
1. Brainstorm 8 diverse candidate reel angles inspired by the live signals and our core categories.
2. Score each candidate across the 3 rubric criteria (Curiosity 0-35, Save/DM Demand 0-35, Meme/Debate 0-30).
3. Compute total `viral_score` (0-100).
4. Strictly filter out anything scoring < 78.
5. Rank by total score descending, and return the candidates in valid JSON.

JSON Schema:
{{
  "candidates": [
    {{
      "topic_title": "Punchy title under 55 characters",
      "category": "Retro & Browser Games | Underrated AI Apps | Tech Business Model | Breaking Tech | Relatable Culture",
      "curiosity_score": 32,
      "save_demand_score": 30,
      "debate_potential_score": 26,
      "viral_score": 88,
      "why_viral": "1-2 sentences on why this explodes in reach and comments",
      "auto_dm_keyword": "ONEWORD",
      "left_character": "junior_dev or dad",
      "right_character": "claude, gemini, or grok",
      "scene_preset": "diner or desk",
      "resource_link_or_query": "Direct verifiable URL, search query, or tool name",
      "core_conflict": "Left character skepticism/nostalgia vs right character witty facts"
    }}
  ]
}}
"""

        raw_json = self._call_gemini_api(prompt, system_instruction)
        if not raw_json:
            raise RuntimeError("Gemini failed to return scored topic candidates.")

        cleaned = raw_json.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        candidates = parsed.get("candidates", []) if isinstance(parsed, dict) else parsed

        # Filter candidates by score gate (>= 78) and sort descending
        valid_candidates = []
        for c in candidates:
            score = c.get("viral_score", 0)
            if score >= 78:
                valid_candidates.append(c)

        if not valid_candidates and candidates:
            # If all were strictly below 78, pick highest scoring
            candidates.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
            valid_candidates = candidates

        valid_candidates.sort(key=lambda x: x.get("viral_score", 0), reverse=True)

        # Sanitize top N winners
        winners = []
        for item in valid_candidates[:count]:
            sanitized = self._sanitize_topic(item)
            winners.append(sanitized)

        return winners

    def _sanitize_topic(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes topic fields for downstream HookMaster and remotion screenplays."""
        title = str(item.get("topic_title") or item.get("title", "Viral Tech Breakdown")).strip()
        slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")[:45]

        left_char = "dad" if "dad" in str(item.get("left_character", "")).lower() else "junior_dev"
        right_char = str(item.get("right_character", "claude")).lower()
        if "gemini" in right_char:
            right_char = "gemini"
        elif "grok" in right_char:
            right_char = "grok"
        else:
            right_char = "claude"

        scene_preset = "desk" if "desk" in str(item.get("scene_preset", "")).lower() else "diner"

        raw_kw = str(item.get("auto_dm_keyword", "LINK")).strip().upper()
        clean_kw = re.sub(r"[^A-Z0-9]", "", raw_kw) or "LINK"

        score = int(item.get("viral_score") or 82)
        breakdown = {
            "curiosity": int(item.get("curiosity_score") or 28),
            "save_demand": int(item.get("save_demand_score") or 28),
            "debate_potential": int(item.get("debate_potential_score") or 26),
        }

        category = item.get("category", "Viral Tech")
        why_viral = item.get("why_viral", "High curiosity gap and immediate viewer DM demand.")
        conflict = item.get("core_conflict", f"{left_char} perspective vs {right_char} technical reality")

        return {
            "id": slug,
            "title": title,
            "topic_title": title,
            "topic": title,
            "core_topic": title,
            "category": category,
            "pillar_style": category,
            "viral_score": score,
            "score_breakdown": breakdown,
            "why_viral": why_viral,
            "auto_dm_keyword": clean_kw,
            "cta_keyword": clean_kw,
            "ctaKeyword": clean_kw,
            "cta_phrase": f"Comment {clean_kw} and I'll DM you the exact link.",
            "left_character": left_char,
            "right_character": right_char,
            "scene_preset": scene_preset,
            "scenePreset": scene_preset,
            "resource_link_or_query": item.get("resource_link_or_query", "https://antigravity.run"),
            "core_conflict": conflict,
            "style": "ai_vs_dad" if left_char == "dad" else "diner_ai",
            "format_type": "ai_vs_dad" if left_char == "dad" else "ai_vs_dev",
        }

    # =========================================================================
    # 4. EMERGENCY OFFLINE FALLBACK
    # =========================================================================

    def _offline_fallback(self, count: int, covered_history: List[str]) -> List[Dict[str, Any]]:
        """Selects high-performing uncovered topics from content_pillars.json."""
        print("⚠️ [TopicMaster] Live feeds/Gemini unreachable; falling back to content_pillars.json.")
        pool = []
        if self.pillars_file.exists():
            try:
                with open(self.pillars_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for pillar in data.get("pillars", []):
                    for topic in pillar.get("topics", []):
                        item = dict(topic)
                        item["category"] = pillar.get("name")
                        pool.append(item)
            except Exception as e:
                print(f"⚠️ TopicMaster: Failed reading content_pillars.json: {e}")

        uncovered = [t for t in pool if t.get("title") not in covered_history and t.get("id") not in covered_history]
        candidates = uncovered if uncovered else pool

        winners = []
        for i in range(count):
            pick = candidates[i % len(candidates)] if candidates else {}
            sanitized = self._sanitize_topic({
                "topic_title": pick.get("title", f"Tech Breakthrough #{i+1}"),
                "category": pick.get("category", "Retro Tech"),
                "viral_score": 84,
                "curiosity_score": 30,
                "save_demand_score": 28,
                "debate_potential_score": 26,
                "why_viral": "Proven high-retention evergreen archetype.",
                "auto_dm_keyword": pick.get("cta_keyword", "TECH"),
                "left_character": pick.get("left_character", "junior_dev"),
                "right_character": pick.get("right_character", "claude"),
                "scene_preset": "diner",
                "resource_link_or_query": "https://antigravity.run",
                "core_conflict": pick.get("core_conflict", "Dev nostalgia vs engineering facts"),
            })
            winners.append(sanitized)

        return winners

    # =========================================================================
    # 5. PUBLIC DISCOVERY INTERFACE
    # =========================================================================

    def curate_fresh_topics(self, count: int = 2) -> List[Dict[str, Any]]:
        """
        Main entry point for TopicMasterAgent:
        Harvests live signals -> Evaluates 8 candidates against 0-100 rubric ->
        Selects top N winners (score >= 78) -> Saves to covered history.
        """
        print(f"\n🧠 [TopicMaster] Scouting mass-appeal signals for {count} viral reel concept(s)...")
        covered = self.get_last_covered_topics(limit=50)
        print(f"📋 [TopicMaster] Loaded {len(covered)} historical covered topic(s) for deduplication.")

        signals = self.harvest_live_signals()
        print(f"🌐 [TopicMaster] Gathered {len(signals)} live headlines (Google News, Product Hunt, HN, Tech RSS).")

        winners = []
        if self.api_key:
            try:
                winners = self.curate_and_score_topics(signals, count, covered)
                print(f"🏆 [TopicMaster] Viral gate passed! Selected {len(winners)} top-scoring concept(s).")
                for w in winners:
                    print(f"   ★ {w['title']} | Score: {w['viral_score']}/100 [{w['category']}] | Keyword: {w['auto_dm_keyword']}")
            except Exception as e:
                print(f"⚠️ [TopicMaster] Gemini scoring pass warning: {e}")

        if not winners:
            winners = self._offline_fallback(count, covered)

        if winners:
            self.record_covered_topics(winners)

        return winners


if __name__ == "__main__":
    master = TopicMasterAgent()
    topics = master.curate_fresh_topics(count=2)
    print("\n--- TopicMaster Output ---")
    for t in topics:
        print(json.dumps(t, indent=2))
