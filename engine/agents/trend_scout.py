"""
Trend Scout Agent (Agent 0: Dynamic Live Trend Scout & Reel Concept Generator)
Discovers fresh, trending, never-repeated topics dynamically every day
using free public sources (Hacker News API, Reddit public JSON, Tech RSS, GitHub)
and synthesizes scroll-stopping 9:16 reel screenplays with Gemini 2.5 Flash (v1beta).
Includes automatic deduplication against inbox/covered_topics.json and
emergency offline fallback to content_pillars.json.
"""

import os
import sys
import json
import re
import socket
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Attempt Google GenAI import
try:
    from google import genai
except ImportError:
    genai = None


def enable_fast_dns():
    """
    Ensures immediate DNS resolution against local systemd-resolved (127.0.0.53)
    if the primary /etc/resolv.conf nameserver is unreachable or packet-dropping.
    """
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.settimeout(0.4)
        test_sock.sendto(
            b"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01",
            ("127.0.0.53", 53),
        )
        resp, _ = test_sock.recvfrom(512)
        test_sock.close()
        if not resp:
            return
    except Exception:
        return

    _orig_getaddrinfo = socket.getaddrinfo
    _cache: Dict[str, str] = {}

    def _dns_query(host: str, dns_ip: str = "127.0.0.53") -> List[str]:
        header = struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
        query = b""
        for part in host.split("."):
            query += struct.pack("B", len(part)) + part.encode()
        query += b"\x00"
        query += struct.pack(">HH", 1, 1)
        packet = header + query

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.2)
        sock.sendto(packet, (dns_ip, 53))
        data, _ = sock.recvfrom(1024)
        sock.close()

        offset = len(packet)
        ips = []
        ancount = struct.unpack(">H", data[6:8])[0]
        for _ in range(ancount):
            if offset >= len(data):
                break
            if data[offset] & 0xC0 == 0xC0:
                offset += 2
            else:
                while data[offset] != 0:
                    offset += 1 + data[offset]
                offset += 1
            rtype, rclass, ttl, rdlength = struct.unpack(">HHIH", data[offset : offset + 10])
            offset += 10
            if rtype == 1 and rdlength == 4:
                ips.append(socket.inet_ntoa(data[offset : offset + 4]))
            offset += rdlength
        return ips

    def fast_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if isinstance(host, str) and not host.replace(".", "").isdigit() and host not in ("localhost", "127.0.0.1"):
            if host not in _cache:
                try:
                    ips = _dns_query(host)
                    if ips:
                        _cache[host] = ips[0]
                except Exception:
                    pass
            if host in _cache:
                return _orig_getaddrinfo(_cache[host], port, family, type, proto, flags)
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = fast_getaddrinfo


# Activate fast DNS immediately upon module import
enable_fast_dns()


class TrendScoutAgent:
    """
    Agent 0: Autonomous Trend Scout & Concept Synthesizer.
    Scrapes live zero-cost feeds across tech, developer discussions, and retro tech,
    deduplicates against past topics, and uses Gemini 2.5 Flash to synthesize
    scroll-stopping short-form viral concepts.
    """

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AntigravityScout/2.0"
    )

    STYLE_ARCHETYPES = [
        "Retro & Browser Games (WebAssembly ports, classic games in Chrome, zero-install retro emulators)",
        "Underrated AI & App Workflows (hidden features, free tools beating paid SaaS, offline second brain)",
        "Breaking Tech & World Hardware (robotics, open-source weight releases, next-gen hardware)",
        "How Companies Actually Earn (hidden margins, loss-leaders, subscription traps, unit economics)",
        "Hype vs. Reality / Pros & Cons (honest teardowns, latency markups, benchmarks vs marketing)",
        "Relatable Dev / Dad Memes (production disasters, Friday deploys, generational tech clashes)",
    ]

    def __init__(
        self,
        project_root: Optional[Path] = None,
        gemini_api_key: Optional[str] = None,
        timeout: float = 8.0,
    ):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.timeout = timeout
        self.headers = {"User-Agent": self.DEFAULT_USER_AGENT}
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.covered_topics_file = self.project_root / "inbox" / "covered_topics.json"
        self.pillars_file = self.project_root / "engine" / "config" / "content_pillars.json"

        # Gemini Client Initialization
        self.api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 35000},
                )
            except Exception as e:
                print(f"⚠️ TrendScout: Gemini client initialization warning: {e}")

    # =========================================================================
    # 1. LIVE SIGNAL HARVESTING (Zero API Cost, 8s Timeouts, Rate-Limit Safe)
    # =========================================================================

    def fetch_hacker_news_signals(self, max_items: int = 10) -> List[Dict[str, Any]]:
        """
        Fetches live top stories and show stories from official Hacker News Firebase API.
        """
        signals = []
        endpoints = [
            ("https://hacker-news.firebaseio.com/v0/topstories.json", "HackerNews Top"),
            ("https://hacker-news.firebaseio.com/v0/showstories.json", "Show HN"),
        ]

        for ep_url, label in endpoints:
            try:
                r = self.session.get(ep_url, timeout=3.5)
                if r.status_code != 200:
                    continue
                story_ids = r.json()[:max_items]

                for sid in story_ids:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                    try:
                        ir = self.session.get(item_url, timeout=2.0)
                        if ir.status_code == 200:
                            data = ir.json()
                            title = data.get("title")
                            if title and len(title) > 6:
                                signals.append({
                                    "source": label,
                                    "title": title.strip(),
                                    "url": data.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                                    "score": data.get("score", 0),
                                })
                    except Exception:
                        continue
            except Exception as e:
                print(f"ℹ️ [TrendScout] Hacker News ({label}) scan skipped: {e}")

        return signals

    def fetch_reddit_signals(self, max_per_sub: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches top hot posts from curated tech subreddits via public .json endpoints.
        Gracefully catches 403 / 429 rate-limiting without crashing.
        """
        subreddits = [
            "InternetIsBeautiful",
            "LocalLLaMA",
            "technology",
            "SideProject",
        ]
        signals = []
        reddit_headers = {
            "User-Agent": "AntigravityScoutBot/2.0 (compatible; research tool; Linux x86_64)"
        }

        for sub in subreddits:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit={max_per_sub}"
            try:
                r = requests.get(url, headers=reddit_headers, timeout=2.5)
                if r.status_code == 200:
                    children = r.json().get("data", {}).get("children", [])
                    for child in children:
                        pdata = child.get("data", {})
                        title = pdata.get("title", "").strip()
                        post_url = pdata.get("url") or f"https://reddit.com{pdata.get('permalink', '')}"
                        if title and not pdata.get("stickied", False):
                            signals.append({
                                "source": f"Reddit r/{sub}",
                                "title": title,
                                "url": post_url,
                                "score": pdata.get("score", 0),
                            })
                else:
                    # Graceful skip for 403 / 429
                    pass
            except Exception:
                continue

        return signals

    def fetch_tech_rss_and_github_signals(self) -> List[Dict[str, Any]]:
        """
        Fetches breaking tech stories from public RSS feeds (The Verge, Lobsters, Dev.to)
        and trending repositories from the GitHub Search API.
        """
        signals = []

        # 1. GitHub API for active trending repositories
        try:
            gh_url = "https://api.github.com/search/repositories?q=stars:>500+pushed:>2026-01-01&sort=updated&order=desc"
            r_gh = self.session.get(gh_url, timeout=3.5)
            if r_gh.status_code == 200:
                items = r_gh.json().get("items", [])[:8]
                for item in items:
                    repo_name = item.get("full_name") or item.get("name")
                    desc = item.get("description") or "Open-source development project"
                    signals.append({
                        "source": "GitHub Trending",
                        "title": f"{repo_name}: {desc[:90]}",
                        "url": item.get("html_url", ""),
                        "score": item.get("stargazers_count", 0),
                    })
        except Exception as e:
            print(f"ℹ️ [TrendScout] GitHub trending scan notice: {e}")

        # 2. Public RSS Feeds
        rss_feeds = [
            ("https://lobste.rs/rss", "Lobste.rs Tech"),
            ("https://www.theverge.com/rss/index.xml", "The Verge Tech"),
            ("https://dev.to/feed", "Dev.to Community"),
        ]

        for feed_url, label in rss_feeds:
            try:
                r_rss = self.session.get(feed_url, timeout=3.5)
                if r_rss.status_code == 200:
                    root = ET.fromstring(r_rss.content)
                    # RSS 2.0 items
                    for item in root.findall(".//item")[:6]:
                        t = item.findtext("title")
                        link = item.findtext("link")
                        if t:
                            signals.append({
                                "source": label,
                                "title": t.strip(),
                                "url": link.strip() if link else feed_url,
                                "score": 100,
                            })
                    # Atom entries
                    for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:6]:
                        t = entry.findtext("{http://www.w3.org/2005/Atom}title")
                        link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
                        link = link_elem.get("href", "") if link_elem is not None else ""
                        if t:
                            signals.append({
                                "source": label,
                                "title": t.strip(),
                                "url": link.strip() if link else feed_url,
                                "score": 100,
                            })
            except Exception:
                continue

        return signals

    def harvest_live_signals(self) -> List[Dict[str, Any]]:
        """
        Gathers live trending signals across all free public sources and removes duplicates.
        """
        all_signals = []
        all_signals.extend(self.fetch_hacker_news_signals(max_items=15))
        all_signals.extend(self.fetch_reddit_signals(max_per_sub=5))
        all_signals.extend(self.fetch_tech_rss_and_github_signals())

        # Deduplicate signals by normalized title
        seen_titles = set()
        deduped = []
        for s in all_signals:
            norm = re.sub(r"[^a-zA-Z0-9]", "", s["title"].lower())[:40]
            if norm and norm not in seen_titles:
                seen_titles.add(norm)
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
            print(f"⚠️ TrendScout: Error reading covered_topics.json: {e}")
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
        """Appends freshly generated topics to inbox/covered_topics.json."""
        history = self.load_covered_history()
        today_str = datetime.now().strftime("%Y-%m-%d")

        for topic in new_topics:
            title = topic.get("topic_title") or topic.get("title", "Dynamic Topic")
            slug = topic.get("id") or "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")[:40]
            history.append({
                "slug": slug,
                "title": title,
                "date": today_str,
                "auto_dm_keyword": topic.get("auto_dm_keyword") or topic.get("cta_keyword", "LINK"),
                "pillar_style": topic.get("pillar_style", "Dynamic Trend"),
            })

        self.covered_topics_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.covered_topics_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print(f"💾 [TrendScout] Recorded {len(new_topics)} fresh topic(s) into inbox/covered_topics.json.")
        except Exception as e:
            print(f"⚠️ TrendScout: Failed to write to covered_topics.json: {e}")

    # =========================================================================
    # 3. GEMINI 2.5 FLASH DYNAMIC SYNTHESIS
    # =========================================================================

    def _call_gemini_api(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Executes Gemini 2.5 Flash request with multi-model and REST fallback."""
        model_candidates = ["gemini-2.5-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]

        # 1. Try google.genai Client
        if self.client:
            for model_name in model_candidates:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[prompt],
                        config=dict(
                            system_instruction=system_instruction,
                            temperature=0.7,
                            response_mime_type="application/json",
                        ),
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    print(f"⚠️ TrendScout: genai {model_name} attempt warning: {e}")

        # 2. Try direct REST endpoint fallback
        if self.api_key:
            for model_name in model_candidates:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {
                        "temperature": 0.7,
                        "responseMimeType": "application/json",
                    },
                }
                try:
                    resp = requests.post(url, json=payload, headers=self.headers, timeout=30.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text")
                except Exception as e:
                    print(f"⚠️ TrendScout: REST fallback {model_name} warning: {e}")

        return None

    def synthesize_with_gemini(
        self,
        signals: List[Dict[str, Any]],
        count: int,
        covered_history: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes brand-new, scroll-stopping reel concepts using live headlines,
        today's date, style archetypes, and deduplication history.
        """
        today_str = datetime.now().strftime("%B %d, %Y")

        # Format live signals summary
        signals_summary = []
        for idx, s in enumerate(signals[:15], 1):
            signals_summary.append(f"{idx}. [{s['source']}] {s['title']}")
        signals_text = "\n".join(signals_summary) if signals_summary else "No live feeds available."

        # Format covered topics exclusion list
        excluded_text = "\n".join(f"- {t}" for t in covered_history[-50:]) if covered_history else "- None yet."

        system_instruction = (
            "You are the Lead Creative Director and Viral Algorithm Strategist for a high-retention 9:16 reels channel.\n"
            "Your mission: synthesize brand-new, scroll-stopping, high-comment reel concepts from live trending tech signals.\n\n"
            "CORE STYLE ARCHETYPES:\n"
            + "\n".join(f"- {sa}" for sa in self.STYLE_ARCHETYPES)
            + "\n*PLUS: You have full permission to invent fresh high-virality tech/internet angles outside these 6!*\n\n"
            "STRICT RULES:\n"
            "1. DEDUPLICATION ABSOLUTE RULE: You must NEVER repeat, repurpose, or closely copy any topic listed in PREVIOUSLY COVERED TOPICS.\n"
            "2. CAST RESTRICTION:\n"
            "   - left_character MUST be strictly either 'junior_dev' OR 'dad'\n"
            "   - right_character MUST be strictly either 'claude', 'gemini', or 'grok'\n"
            "3. SCENE PRESET:\n"
            "   - scene_preset MUST be strictly either 'diner' OR 'desk'\n"
            "4. AUTO-DM KEYWORD:\n"
            "   - auto_dm_keyword MUST be a single short uppercase word (e.g., 'VICE', 'ROUTER', 'CHIP', 'VAULT', 'BOT', 'SPEED', 'APPS').\n"
            "5. OUTPUT FORMAT:\n"
            "   - Return strictly a valid JSON array containing exactly N objects."
        )

        prompt = f"""
Today's Date: {today_str}

LIVE TRENDING HEADLINES & SIGNALS (Zero-Cost Scraped Today):
{signals_text}

PREVIOUSLY COVERED TOPICS (DO NOT REPEAT ANY OF THESE):
{excluded_text}

TASK:
Synthesize exactly {count} BRAND-NEW, distinct, scroll-stopping reel concepts inspired by the live signals above.
Ensure maximum contrast between characters, high comment engagement, and strong virality.

Return a JSON array of {count} objects matching this exact structure:
[
  {{
    "topic_title": "Punchy headline max 55 chars",
    "pillar_style": "Specific style or invented angle",
    "hook_angle": "0-3s retention hook line designed to stop scrolling instantly",
    "left_character": "junior_dev or dad",
    "right_character": "claude, gemini, or grok",
    "scene_preset": "diner or desk",
    "auto_dm_keyword": "ONEWORD",
    "resource_link_or_query": "Direct verifiable URL, GitHub repo, or search query",
    "meme_twist": "Punchline or sarcastic conflict for the final turn",
    "card_title": "Headline on upper-third proof card",
    "card_type": "comparison, benchmark, breakdown, or checklist",
    "badge": "3-4 word uppercase badge like 'VERIFIED METRICS' or '100% FREE'",
    "card_data": {{
      "metric_or_point_1": "Crucial fact or stat",
      "metric_or_point_2": "Secondary detail or comparison",
      "metric_or_point_3": "Surprising truth"
    }},
    "seo_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4"],
    "hashtags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4", "#Tag5", "#Tag6", "#Tag7", "#Tag8"],
    "dm_message": "Friendly 1-2 sentence text delivered to user DMs when they comment the keyword."
  }}
]
"""

        raw_json = self._call_gemini_api(prompt, system_instruction)
        if not raw_json:
            raise RuntimeError("Gemini failed to return content for dynamic topic synthesis.")

        cleaned = raw_json.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "topics" in parsed:
            parsed = parsed["topics"]
        if not isinstance(parsed, list):
            parsed = [parsed]

        sanitized_topics = []
        for item in parsed[:count]:
            sanitized = self._sanitize_topic_concept(item)
            sanitized_topics.append(sanitized)

        return sanitized_topics

    def _sanitize_topic_concept(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizes and harmonizes generated topic concept for all downstream agents."""
        title = str(item.get("topic_title") or item.get("title", "Daily Tech Breakdown")).strip()
        slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")[:45]

        left_char = str(item.get("left_character", "junior_dev")).lower()
        if "dad" in left_char:
            left_char = "dad"
        else:
            left_char = "junior_dev"

        right_char = str(item.get("right_character", "claude")).lower()
        if "gemini" in right_char:
            right_char = "gemini"
        elif "grok" in right_char:
            right_char = "grok"
        else:
            right_char = "claude"

        scene_preset = str(item.get("scene_preset", "diner")).lower()
        if "desk" in scene_preset:
            scene_preset = "desk"
        else:
            scene_preset = "diner"

        raw_kw = str(item.get("auto_dm_keyword") or item.get("cta_keyword", "LINK")).strip().upper()
        # Ensure single uppercase word
        kw_clean = re.sub(r"[^A-Z0-9]", "", raw_kw) or "LINK"

        hook = str(item.get("hook_angle") or item.get("hook", f"Look at {title}.")).strip()
        twist = str(item.get("meme_twist") or item.get("punchline", "And that is the real tea.")).strip()

        pillar_style = item.get("pillar_style") or item.get("pillar_name") or "Dynamic Viral Tech"

        card_title = item.get("card_title") or f"{title[:25]} Breakdown"
        card_type = item.get("card_type") or ("comparison" if "vs" in title.lower() else "breakdown")
        badge = str(item.get("badge") or "VERIFIED PROOF").upper()[:20]
        card_data = item.get("card_data") or {
            "key_takeaway": "Discovered via live signal tracking",
            "production_impact": "Tested in live engineering workflows",
            "cost_differential": "$0 vs overpriced alternatives",
        }

        seo_keywords = item.get("seo_keywords") or [title, f"{title} 2026", "tech trends", "AI workflows"]
        hashtags = item.get("hashtags") or [
            "#TechNews", "#AIUpdates", "#DeveloperLife", "#CodingHumor",
            "#SoftwareEngineering", "#TechHacks", "#WebDevelopment", "#TechReels"
        ]
        dm_message = item.get("dm_message") or f"Here is the verified link and guide for {title}: https://antigravity.run/r/{kw_clean.lower()}"

        return {
            "id": slug,
            "title": title,
            "topic_title": title,
            "topic": title,
            "core_topic": title,
            "pillar_style": pillar_style,
            "pillar_name": pillar_style,
            "style": "ai_vs_dad" if left_char == "dad" else "diner_ai",
            "hook": hook,
            "hook_angle": hook,
            "left_character": left_char,
            "right_character": right_char,
            "scene_preset": scene_preset,
            "scenePreset": scene_preset,
            "auto_dm_keyword": kw_clean,
            "cta_keyword": kw_clean,
            "ctaKeyword": kw_clean,
            "cta_phrase": f"Comment {kw_clean} and I'll DM you the exact link.",
            "resource_link_or_query": item.get("resource_link_or_query", "https://antigravity.run"),
            "meme_twist": twist,
            "punchline": twist,
            "core_conflict": f"{left_char} perspective vs {right_char} technical reality",
            "format_type": "ai_vs_dad" if left_char == "dad" else "ai_vs_dev",
            "card_title": card_title,
            "card_type": card_type,
            "badge": badge,
            "card_data": card_data,
            "seo_keywords": seo_keywords,
            "hashtags": hashtags,
            "dm_message": dm_message,
        }

    # =========================================================================
    # 4. EMERGENCY OFFLINE FALLBACK (From content_pillars.json)
    # =========================================================================

    def _offline_fallback_topics(self, count: int, covered_history: List[str]) -> List[Dict[str, Any]]:
        """
        Picks offline fallback topics from content_pillars.json,
        prioritizing topics that have NOT been covered recently.
        """
        print("⚠️ [TrendScout] Live feeds or Gemini unavailable; using emergency offline content pillars matrix.")
        fallback_pool = []
        if self.pillars_file.exists():
            try:
                with open(self.pillars_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for pillar in data.get("pillars", []):
                    for topic in pillar.get("topics", []):
                        item = dict(topic)
                        item["pillar_style"] = pillar.get("name", "Tech Pillar")
                        fallback_pool.append(item)
            except Exception as e:
                print(f"⚠️ TrendScout: Error reading content_pillars.json: {e}")

        # Filter out covered topics
        uncovered = [
            t for t in fallback_pool
            if t.get("title") not in covered_history and t.get("id") not in covered_history
        ]
        candidates = uncovered if uncovered else fallback_pool

        results = []
        for i in range(count):
            pick = candidates[i % len(candidates)] if candidates else {}
            sanitized = self._sanitize_topic_concept({
                "topic_title": pick.get("title", f"Tech Breakthrough #{i+1}"),
                "pillar_style": pick.get("pillar_style", "Offline Archetype"),
                "hook_angle": pick.get("hook", "Check out this wild tech discovery."),
                "left_character": pick.get("left_character", "junior_dev"),
                "right_character": pick.get("right_character", "claude"),
                "scene_preset": "diner",
                "auto_dm_keyword": pick.get("cta_keyword", "TECH"),
                "resource_link_or_query": "https://antigravity.run",
                "meme_twist": pick.get("punchline", "And that's why we never push directly to main."),
                "card_title": pick.get("card_title", "Offline Tech Breakdown"),
                "card_type": pick.get("card_type", "comparison"),
                "badge": pick.get("badge", "OFFLINE ARCHETYPE"),
                "card_data": pick.get("card_data", {}),
                "seo_keywords": pick.get("seo_keywords", []),
                "hashtags": pick.get("hashtags", []),
                "dm_message": pick.get("dm_message", "Here is your link!"),
            })
            results.append(sanitized)

        return results

    # =========================================================================
    # 5. MAIN PUBLIC INTERFACE
    # =========================================================================

    def discover_fresh_topics(self, count: int = 2) -> List[Dict[str, Any]]:
        """
        Discovers N brand-new, trending, non-repeated reel concepts:
        1. Loads covered topics history.
        2. Scrapes live signals from Hacker News, Reddit, Tech RSS, and GitHub.
        3. Calls Gemini 2.5 Flash to synthesize scroll-stopping reel concepts.
        4. Saves new topics into inbox/covered_topics.json.
        5. Falls back to content_pillars.json if completely offline.
        """
        print(f"\n📡 [TrendScout] Scouting live trending tech signals for {count} fresh dynamic reels...")
        covered_history = self.get_last_covered_topics(limit=50)
        print(f"📋 [TrendScout] Loaded {len(covered_history)} recent covered topic(s) for deduplication.")

        # 1. Harvest live signals
        signals = self.harvest_live_signals()
        print(f"🌐 [TrendScout] Harvested {len(signals)} live headlines from Hacker News, GitHub & Tech RSS.")

        discovered_topics = []

        # 2. Try Gemini 2.5 Flash synthesis
        if self.api_key:
            try:
                discovered_topics = self.synthesize_with_gemini(
                    signals=signals,
                    count=count,
                    covered_history=covered_history,
                )
                print(f"✨ [TrendScout] Gemini 2.5 Flash successfully synthesized {len(discovered_topics)} brand-new concepts!")
            except Exception as e:
                print(f"⚠️ [TrendScout] Dynamic synthesis notice: {e}")

        # 3. Emergency offline fallback if synthesis failed or empty
        if not discovered_topics:
            discovered_topics = self._offline_fallback_topics(count, covered_history)

        # 4. Save to covered topics tracker
        if discovered_topics:
            self.record_covered_topics(discovered_topics)

        return discovered_topics


if __name__ == "__main__":
    scout = TrendScoutAgent()
    topics = scout.discover_fresh_topics(count=2)
    print("\n" + "=" * 60)
    print("🎯 TREND SCOUT DRY-RUN TEST RESULTS:")
    print("=" * 60)
    for idx, t in enumerate(topics, 1):
        print(f"\nReel #{idx}: {t['title']}")
        print(f"  • Pillar Style : {t['pillar_style']}")
        print(f"  • Hook Angle   : \"{t['hook_angle']}\"")
        print(f"  • Cast         : Left: {t['left_character']} | Right: {t['right_character']}")
        print(f"  • Scene Preset : {t['scene_preset']}")
        print(f"  • Auto-DM Word : {t['auto_dm_keyword']}")
        print(f"  • Resource Link: {t['resource_link_or_query']}")
        print(f"  • Meme Twist   : {t['meme_twist']}")
