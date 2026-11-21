"""
Media Fetcher Agent (Helper: Free Official App & Game Logo Resolver)
Fetches official crisp logos/icons for tech apps and games from free public sources:
1. Wikipedia / Wikimedia Commons REST API (covers games, brands, companies)
2. SimpleIcons CDN (covers tech, dev tools, AI companies)
3. Clearbit Logo fallback
Saves to my-edu-reels/public/assets/topic_logo.png with zero paid API keys.
"""

import os
import re
import urllib.parse
from pathlib import Path
from typing import Optional
import requests

from engine.dns_utils import enable_fast_dns
enable_fast_dns()

KNOWN_ENTITY_MAP = {
    # Tech & AI
    "apple": {"wiki": "Apple_Inc.", "slug": "apple"},
    "google": {"wiki": "Google", "slug": "google"},
    "chrome": {"wiki": "Google_Chrome", "slug": "googlechrome"},
    "notebooklm": {"wiki": "Google", "slug": "google"},
    "openrouter": {"wiki": "OpenRouter", "slug": "openrouter"},
    "nvidia": {"wiki": "Nvidia", "slug": "nvidia"},
    "github": {"wiki": "GitHub", "slug": "github"},
    "claude": {"wiki": "Anthropic", "slug": "anthropic"},
    "anthropic": {"wiki": "Anthropic", "slug": "anthropic"},
    "chatgpt": {"wiki": "OpenAI", "slug": "openai"},
    "openai": {"wiki": "OpenAI", "slug": "openai"},
    "grok": {"wiki": "X_Corp.", "slug": "x"},
    "gemini": {"wiki": "Google_Gemini", "slug": "googlegemini"},
    "docker": {"wiki": "Docker_(software)", "slug": "docker"},
    "python": {"wiki": "Python_(programming_language)", "slug": "python"},
    "linux": {"wiki": "Linux", "slug": "linux"},
    # Games & Franchises
    "gta vice city": {"wiki": "Grand_Theft_Auto:_Vice_City", "slug": "rockstargames"},
    "vice city": {"wiki": "Grand_Theft_Auto:_Vice_City", "slug": "rockstargames"},
    "gta san andreas": {"wiki": "Grand_Theft_Auto:_San_Andreas", "slug": "rockstargames"},
    "gta 5": {"wiki": "Grand_Theft_Auto_V", "slug": "rockstargames"},
    "skate 3": {"wiki": "Skate_3", "slug": "ea"},
    "call of duty": {"wiki": "Call_of_Duty", "slug": "activision"},
    "project igi": {"wiki": "Project_I.G.I.", "slug": ""},
    "minecraft": {"wiki": "Minecraft", "slug": "minecraft"},
    "counter strike": {"wiki": "Counter-Strike_(video_game)", "slug": "counterstrike"},
    "doom": {"wiki": "Doom_(1993_video_game)", "slug": ""},
}


def fetch_topic_logo(
    topic_title: str,
    entity_name: Optional[str] = None,
    out_path: Optional[str] = None,
) -> Optional[str]:
    """
    Fetches official crisp app/game logo or icon from free public sources.
    Returns relative path (e.g. 'assets/topic_logo.png') on success, or None on failure.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    if not out_path:
        out_target = project_root / "my-edu-reels" / "public" / "assets" / "topic_logo.png"
    else:
        out_target = Path(out_path)

    out_target.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "UnlimitedReelsEngine/1.0 (educational-reels-bot; contact@antigravity.run)",
        "Accept": "image/*,application/json;q=0.9",
    }

    query = (entity_name or topic_title).strip()
    query_lower = query.lower()

    # 1. Resolve candidates from known mapping
    matched = None
    for k, v in KNOWN_ENTITY_MAP.items():
        if k in query_lower or query_lower in k:
            matched = v
            break

    wiki_candidates = []
    slug_candidates = []

    if matched:
        if matched.get("wiki"):
            wiki_candidates.append(matched["wiki"])
        if matched.get("slug"):
            slug_candidates.append(matched["slug"])

    # Clean query for Wikipedia lookup
    clean_wiki = query.replace(" ", "_")
    wiki_candidates.extend([
        clean_wiki,
        f"{clean_wiki}_Inc.",
        f"{clean_wiki}_(video_game)",
        f"{clean_wiki}_(company)",
        f"{clean_wiki}_(software)",
    ])

    # Clean query for SimpleIcons lookup
    clean_slug = re.sub(r"[^a-zA-Z0-9]", "", query_lower)
    if clean_slug and clean_slug not in slug_candidates:
        slug_candidates.append(clean_slug)

    # Strategy A: Wikipedia REST page summary thumbnail (High quality PNG/JPG)
    for wiki_title in wiki_candidates:
        if not wiki_title:
            continue
        try:
            quoted = urllib.parse.quote(wiki_title, safe=":")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted}"
            r = requests.get(url, headers=headers, timeout=4.5)
            if r.status_code == 200:
                data = r.json()
                thumb_url = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if thumb_url:
                    img_r = requests.get(thumb_url, headers=headers, timeout=6.0)
                    if img_r.status_code == 200 and len(img_r.content) > 600:
                        out_target.write_bytes(img_r.content)
                        # Also mirror to public/assets if present
                        remotion_public = project_root / "public" / "assets" / "topic_logo.png"
                        if remotion_public.parent.exists():
                            remotion_public.write_bytes(img_r.content)
                        print(f"✅ [MediaFetcher] Saved Wikipedia logo for '{wiki_title}' ({len(img_r.content)} bytes) -> {out_target}")
                        return "assets/topic_logo.png"
        except Exception:
            continue

    # Strategy B: SimpleIcons CDN (Clean SVG)
    for slug in slug_candidates:
        if not slug:
            continue
        try:
            url = f"https://cdn.simpleicons.org/{slug}"
            r = requests.get(url, headers=headers, timeout=4.0)
            if r.status_code == 200 and len(r.content) > 150:
                out_target.write_bytes(r.content)
                remotion_public = project_root / "public" / "assets" / "topic_logo.png"
                if remotion_public.parent.exists():
                    remotion_public.write_bytes(r.content)
                print(f"✅ [MediaFetcher] Saved SimpleIcons logo for '{slug}' ({len(r.content)} bytes) -> {out_target}")
                return "assets/topic_logo.png"
        except Exception:
            continue

    print(f"ℹ️ [MediaFetcher] No public logo found for '{query}', omitting gracefully.")
    return None
