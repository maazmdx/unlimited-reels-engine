"""
Media Fetcher Agent (Helper: Free Official App, Game Logo & Real Visual Proof Resolver)
Fetches official crisp logos/icons and visual proof cards from free public sources:
1. SimpleIcons CDN (white SVG / slug resolution): https://cdn.simpleicons.org/<slug>/ffffff
2. IconHorse fallback (favicon/brand logo by domain): https://icon.horse/icon/<brand_domain>
3. GitHub OpenGraph proof card (for repos): https://opengraph.githubassets.com/1/<github_repo>
4. Thum.io Live Screenshot fallback (for web apps/tools): https://image.thum.io/get/width/900/crop/600/noanimate/<official_url>
5. Wikipedia / Wikimedia Commons REST API (covers games, brands, companies)

Caches locally into public/assets/ and updates timeline.json with logoPath & proofImagePath.
"""

import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from engine.dns_utils import enable_fast_dns
enable_fast_dns()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

KNOWN_ENTITY_MAP = {
    # Tech & AI
    "apple": {"wiki": "Apple_Inc.", "slug": "apple", "domain": "apple.com"},
    "google": {"wiki": "Google", "slug": "google", "domain": "google.com"},
    "chrome": {"wiki": "Google_Chrome", "slug": "googlechrome", "domain": "google.com/chrome"},
    "notebooklm": {"wiki": "Google", "slug": "google", "domain": "notebooklm.google"},
    "openrouter": {"wiki": "OpenRouter", "slug": "openrouter", "domain": "openrouter.ai"},
    "nvidia": {"wiki": "Nvidia", "slug": "nvidia", "domain": "nvidia.com"},
    "github": {"wiki": "GitHub", "slug": "github", "domain": "github.com"},
    "claude": {"wiki": "Anthropic", "slug": "anthropic", "domain": "anthropic.com"},
    "anthropic": {"wiki": "Anthropic", "slug": "anthropic", "domain": "anthropic.com"},
    "chatgpt": {"wiki": "OpenAI", "slug": "openai", "domain": "openai.com"},
    "openai": {"wiki": "OpenAI", "slug": "openai", "domain": "openai.com"},
    "grok": {"wiki": "X_Corp.", "slug": "x", "domain": "x.ai"},
    "gemini": {"wiki": "Google_Gemini", "slug": "googlegemini", "domain": "gemini.google.com"},
    "docker": {"wiki": "Docker_(software)", "slug": "docker", "domain": "docker.com"},
    "python": {"wiki": "Python_(programming_language)", "slug": "python", "domain": "python.org"},
    "linux": {"wiki": "Linux", "slug": "linux", "domain": "kernel.org"},
    "emulatorjs": {"wiki": "", "slug": "javascript", "domain": "emulatorjs.org"},
    # Games & Franchises
    "gta vice city": {"wiki": "Grand_Theft_Auto:_Vice_City", "slug": "rockstargames", "domain": "rockstargames.com"},
    "vice city": {"wiki": "Grand_Theft_Auto:_Vice_City", "slug": "rockstargames", "domain": "rockstargames.com"},
    "gta san andreas": {"wiki": "Grand_Theft_Auto:_San_Andreas", "slug": "rockstargames", "domain": "rockstargames.com"},
    "gta 5": {"wiki": "Grand_Theft_Auto_V", "slug": "rockstargames", "domain": "rockstargames.com"},
    "skate 3": {"wiki": "Skate_3", "slug": "ea", "domain": "ea.com"},
    "call of duty": {"wiki": "Call_of_Duty", "slug": "activision", "domain": "callofduty.com"},
    "project igi": {"wiki": "Project_I.G.I.", "slug": "", "domain": "eidos.com"},
    "minecraft": {"wiki": "Minecraft", "slug": "minecraft", "domain": "minecraft.net"},
    "counter strike": {"wiki": "Counter-Strike_(video_game)", "slug": "counterstrike", "domain": "counter-strike.net"},
    "doom": {"wiki": "Doom_(1993_video_game)", "slug": "", "domain": "idsoftware.com"},
}


def _clean_domain(domain_str: Optional[str]) -> Optional[str]:
    """Extracts raw hostname e.g. 'emulatorjs.org' from URL or domain string."""
    if not domain_str:
        return None
    d = domain_str.strip()
    d = re.sub(r"^https?://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0].strip()
    return d if d else None


def _clean_github_repo(repo_str: Optional[str]) -> Optional[str]:
    """Extracts 'owner/repo' from GitHub URL or repo string."""
    if not repo_str:
        return None
    r = repo_str.strip()
    r = re.sub(r"^https?://(?:www\.)?github\.com/", "", r)
    r = r.strip("/")
    parts = r.split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def fetch_topic_logo(
    tool_name: Optional[str] = None,
    brand_domain: Optional[str] = None,
    entity_name: Optional[str] = None,
    topic_title: Optional[str] = None,
    out_path: Optional[str] = None,
) -> Optional[str]:
    """
    Fetches official crisp app/game logo or icon from free public sources:
    1. SimpleIcons CDN: https://cdn.simpleicons.org/<slug>/ffffff
    2. IconHorse: https://icon.horse/icon/<brand_domain>
    3. Wikipedia REST API fallback.
    Never uses clickbait title if tool_name, brand_domain, or entity_name is available.
    Returns relative path ('assets/topic_logo.png') on success, or None on failure.
    """
    query = (tool_name or entity_name or "").strip()
    if not query and brand_domain:
        query = brand_domain.split(".")[0].strip()
    if not query and topic_title:
        # Avoid full clickbait titles
        query = topic_title.split(":")[0].split(" - ")[0].strip()

    if not query:
        return None

    project_root = PROJECT_ROOT
    if not out_path:
        out_target = project_root / "public" / "assets" / "topic_logo.png"
    else:
        out_target = Path(out_path)

    out_target.parent.mkdir(parents=True, exist_ok=True)
    remotion_target = project_root / "my-edu-reels" / "public" / "assets" / "topic_logo.png"
    remotion_target.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "UnlimitedReelsEngine/1.0 (educational-reels-bot; contact@antigravity.run)",
        "Accept": "image/*,application/json;q=0.9",
    }

    query_lower = query.lower()

    # 1. Resolve candidates from known mapping
    matched = None
    for k, v in KNOWN_ENTITY_MAP.items():
        if k in query_lower or query_lower in k:
            matched = v
            break

    slug_candidates = []
    if matched and matched.get("slug"):
        slug_candidates.append(matched["slug"])

    clean_slug = re.sub(r"[^a-zA-Z0-9]", "", query_lower)
    if clean_slug and clean_slug not in slug_candidates:
        slug_candidates.append(clean_slug)

    # Strategy A: SimpleIcons CDN (white SVG /ffffff -> fallback plain)
    for slug in slug_candidates:
        if not slug:
            continue
        for variant in [f"{slug}/ffffff", slug]:
            try:
                url = f"https://cdn.simpleicons.org/{variant}"
                r = requests.get(url, headers=headers, timeout=3.5)
                if r.status_code == 200 and len(r.content) > 150:
                    out_target.write_bytes(r.content)
                    if remotion_target.resolve() != out_target.resolve():
                        remotion_target.write_bytes(r.content)
                    print(f"✅ [MediaFetcher] Saved SimpleIcons logo '{slug}' ({len(r.content)} bytes) -> {out_target}")
                    return "assets/topic_logo.png"
            except Exception:
                continue

    # Strategy B: IconHorse Favicon by brand_domain
    domain = _clean_domain(brand_domain) or (matched.get("domain") if matched else None)
    if domain:
        try:
            url = f"https://icon.horse/icon/{domain}"
            r = requests.get(url, headers=headers, timeout=4.0)
            if r.status_code == 200 and len(r.content) > 300:
                out_target.write_bytes(r.content)
                if remotion_target.resolve() != out_target.resolve():
                    remotion_target.write_bytes(r.content)
                print(f"✅ [MediaFetcher] Saved IconHorse logo for domain '{domain}' ({len(r.content)} bytes) -> {out_target}")
                return "assets/topic_logo.png"
        except Exception:
            pass

    # Strategy C: Wikipedia REST page summary thumbnail fallback
    wiki_candidates = []
    if matched and matched.get("wiki"):
        wiki_candidates.append(matched["wiki"])
    clean_wiki = query.replace(" ", "_")
    wiki_candidates.extend([
        clean_wiki,
        f"{clean_wiki}_(software)",
        f"{clean_wiki}_(video_game)",
        f"{clean_wiki}_(company)",
    ])

    for wiki_title in wiki_candidates:
        if not wiki_title:
            continue
        try:
            quoted = urllib.parse.quote(wiki_title, safe=":")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quoted}"
            r = requests.get(url, headers=headers, timeout=4.0)
            if r.status_code == 200:
                data = r.json()
                thumb_url = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
                if thumb_url:
                    img_r = requests.get(thumb_url, headers=headers, timeout=5.0)
                    if img_r.status_code == 200 and len(img_r.content) > 600:
                        out_target.write_bytes(img_r.content)
                        if remotion_target.resolve() != out_target.resolve():
                            remotion_target.write_bytes(img_r.content)
                        print(f"✅ [MediaFetcher] Saved Wikipedia logo for '{wiki_title}' ({len(img_r.content)} bytes) -> {out_target}")
                        return "assets/topic_logo.png"
        except Exception:
            continue

    print(f"ℹ️ [MediaFetcher] No public logo found for tool '{query}', omitting gracefully.")
    return None


def fetch_proof_card(
    github_repo: Optional[str] = None,
    official_url: Optional[str] = None,
    brand_domain: Optional[str] = None,
    out_path: Optional[str] = None,
) -> Optional[str]:
    """
    Fetches real visual proof card:
    (a) https://opengraph.githubassets.com/1/<github_repo> if GitHub repo exists.
    (b) Live website screenshot via https://image.thum.io/get/width/900/crop/600/noanimate/<official_url>
    Saves to public/assets/proof_card.png and mirrors to my-edu-reels/public/assets/proof_card.png.
    Returns relative path ('assets/proof_card.png') on success, or None on failure.
    """
    project_root = PROJECT_ROOT
    if not out_path:
        out_target = project_root / "public" / "assets" / "proof_card.png"
    else:
        out_target = Path(out_path)

    out_target.parent.mkdir(parents=True, exist_ok=True)
    remotion_target = project_root / "my-edu-reels" / "public" / "assets" / "proof_card.png"
    remotion_target.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/webp,image/apng,image/png,image/*,*/*;q=0.8",
    }

    # 1. Strategy A: Real GitHub OpenGraph Card
    clean_repo = _clean_github_repo(github_repo)
    if clean_repo:
        try:
            og_url = f"https://opengraph.githubassets.com/1/{clean_repo}"
            r = requests.get(og_url, headers=headers, timeout=6.0)
            if r.status_code == 200 and len(r.content) > 1200:
                out_target.write_bytes(r.content)
                if remotion_target.resolve() != out_target.resolve():
                    remotion_target.write_bytes(r.content)
                print(f"✅ [MediaFetcher] Saved GitHub proof card for '{clean_repo}' ({len(r.content)} bytes) -> {out_target}")
                return "assets/proof_card.png"
        except Exception as e:
            print(f"⚠️ [MediaFetcher] GitHub OpenGraph fetch failed for '{clean_repo}': {e}")

    # 2. Strategy B: Live Screenshot via Thum.io
    target_url = official_url
    if not target_url and brand_domain:
        clean_d = _clean_domain(brand_domain)
        if clean_d:
            target_url = f"https://{clean_d}"

    if target_url:
        clean_url = target_url.strip()
        if not clean_url.startswith("http"):
            clean_url = f"https://{clean_url}"
        try:
            screenshot_url = f"https://image.thum.io/get/width/900/crop/600/noanimate/{clean_url}"
            r = requests.get(screenshot_url, headers=headers, timeout=7.5)
            if r.status_code == 200 and len(r.content) > 1200:
                out_target.write_bytes(r.content)
                if remotion_target.resolve() != out_target.resolve():
                    remotion_target.write_bytes(r.content)
                print(f"✅ [MediaFetcher] Saved live website screenshot for '{clean_url}' ({len(r.content)} bytes) -> {out_target}")
                return "assets/proof_card.png"
        except Exception as e:
            print(f"⚠️ [MediaFetcher] Thum.io screenshot fetch failed for '{clean_url}': {e}")

    print(f"ℹ️ [MediaFetcher] No proof card fetched for repo='{github_repo}', url='{target_url}'.")
    return None


def attach_media_to_timeline(
    timeline_path: Path,
    logo_path: Optional[str] = None,
    proof_image_path: Optional[str] = None,
) -> None:
    """
    Injects logoPath and proofImagePath into timeline.json in place,
    and mirrors to both public/timeline.json and my-edu-reels/public/timeline.json.
    """
    out_dirs = [
        timeline_path.parent,
        PROJECT_ROOT / "public",
        PROJECT_ROOT / "my-edu-reels" / "public",
    ]

    for d in set(out_dirs):
        t_file = d / "timeline.json"
        if t_file.exists():
            try:
                with open(t_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["logoPath"] = logo_path
                data["proofImagePath"] = proof_image_path
                with open(t_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ [MediaFetcher] Failed updating timeline.json at {t_file}: {e}")


def fetch_topic_media_assets(
    topic_data: Dict[str, Any],
    public_dir: Optional[Path] = None,
) -> Dict[str, Optional[str]]:
    """
    High-level orchestrator:
    Extracts tool_name, brand_domain, github_repo, official_url from topic_data.
    Fetches logo and proof card, attaches to timeline.json, and returns dictionary.
    """
    tool_name = (
        topic_data.get("tool_name")
        or topic_data.get("entity_name")
        or topic_data.get("entity")
        or topic_data.get("core_tool")
    )
    brand_domain = topic_data.get("brand_domain") or topic_data.get("domain")
    github_repo = topic_data.get("github_repo") or topic_data.get("repo")
    official_url = topic_data.get("official_url") or topic_data.get("url")

    # If tool_name is still missing, attempt heuristic from title
    if not tool_name and topic_data.get("title"):
        tool_name = topic_data["title"].split(":")[0].split(" - ")[0].strip()

    print(f"🔍 [MediaFetcher] Fetching verified assets for tool='{tool_name}', domain='{brand_domain}', repo='{github_repo}'")

    logo_path = fetch_topic_logo(
        tool_name=tool_name,
        brand_domain=brand_domain,
        topic_title=topic_data.get("title"),
    )

    proof_image_path = fetch_proof_card(
        github_repo=github_repo,
        official_url=official_url,
        brand_domain=brand_domain,
    )

    t_path = (public_dir / "timeline.json") if public_dir else (PROJECT_ROOT / "public" / "timeline.json")
    if t_path.exists():
        attach_media_to_timeline(t_path, logo_path, proof_image_path)

    return {
        "logoPath": logo_path,
        "proofImagePath": proof_image_path,
    }
