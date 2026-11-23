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
from typing import Any, Dict, Optional, List
import requests

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

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
        "User-Agent": "UnlimitedReelsEngine/1.0 (educational-reels-bot; contact@canidoai.com)",
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
    # For comedy / dad clash topics: skip Wikipedia thumbnail scraping completely
    # (prevents random Wikipedia article images or crests appearing in comedy reels)
    is_comedy = "dad" in query_lower or (topic_title and "dad" in str(topic_title).lower()) or "clash" in query_lower
    if is_comedy:
        print(f"ℹ️ [MediaFetcher] Skipping Wikipedia logo scrape for comedy/dad topic '{query}'.")
        return None

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


def is_blank_or_invalid_image(file_path: Path) -> bool:
    """
    Checks if saved image is blank, uniform, or corrupted:
    - Size < 1200 bytes (< 1.2 KB).
    - If PIL/numpy available, checks if > 92% of pixels are uniform / white / black.
    """
    if not file_path.exists():
        return True
    try:
        size = file_path.stat().st_size
        if size < 1200:
            return True
        if not HAS_PIL:
            return False

        with Image.open(file_path) as img:
            rgb = img.convert("RGB")
            w, h = rgb.size
            if w < 100 or h < 100:
                return True

            if HAS_NUMPY:
                arr = np.array(rgb)
                # Check near-white pixels (R>235, G>235, B>235)
                white_pixels = np.all(arr > 235, axis=-1)
                white_ratio = float(np.mean(white_pixels))
                if white_ratio > 0.92:
                    return True
                # Check near-black pixels (R<15, G<15, B<15)
                black_pixels = np.all(arr < 15, axis=-1)
                black_ratio = float(np.mean(black_pixels))
                if black_ratio > 0.92:
                    return True
                # Check standard deviation across channels
                if float(np.std(arr)) < 5.0:
                    return True
            else:
                pixels = list(rgb.getdata())
                sample = pixels[::max(1, len(pixels) // 2000)]
                white_count = sum(1 for p in sample if p[0] > 235 and p[1] > 235 and p[2] > 235)
                if (white_count / len(sample)) > 0.92:
                    return True
        return False
    except Exception as e:
        print(f"⚠️ [MediaFetcher] Error inspecting image {file_path}: {e}")
        return True


def generate_dark_proof_card(
    tool_name: str,
    brand_domain: str,
    real_steps: Optional[List[Any]] = None,
    out_path: Optional[Path] = None,
    remotion_target: Optional[Path] = None,
) -> Optional[str]:
    """Generates a high-contrast dark card (900x600) so a reel NEVER renders a blank box."""
    if not HAS_PIL:
        return None
    try:
        width, height = 900, 600
        img = Image.new("RGB", (width, height), color=(15, 23, 42))  # #0F172A slate-900
        draw = ImageDraw.Draw(img)

        # Draw outer rounded border
        draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=24, outline=(51, 65, 85), width=3)  # slate-700
        # Draw header bar
        draw.rounded_rectangle([40, 40, width - 40, 130], radius=16, fill=(30, 41, 59))  # slate-800

        # Badge
        draw.rounded_rectangle([60, 58, 260, 112], radius=10, fill=(16, 185, 129))  # emerald-500
        draw.text((80, 72), "100% FREE PROOF", fill=(255, 255, 255))

        # Title
        display_title = (tool_name or "Verified Free Tool")[:35]
        draw.text((290, 68), display_title, fill=(248, 250, 252))

        # Subtitle / domain
        domain_disp = brand_domain or "Official Open-Source Software"
        draw.text((290, 96), domain_disp, fill=(148, 163, 184))

        # Draw 3 step rows
        steps = real_steps or [
            "1. Visit official link or GitHub release",
            "2. Run locally on device with zero tracking",
            "3. 100% free functionality replacing paid traps"
        ]
        y = 170
        for i, s in enumerate(steps[:3]):
            draw.rounded_rectangle([40, y, width - 40, y + 110], radius=14, fill=(24, 33, 47), outline=(51, 65, 85), width=2)
            # Step number circle
            draw.ellipse([65, y + 25, 125, y + 85], fill=(59, 130, 246))  # blue-500
            draw.text((88, y + 42), str(i + 1), fill=(255, 255, 255))
            # Step text
            clean_s = str(s).lstrip("0123456789. ")
            draw.text((150, y + 42), clean_s[:60], fill=(241, 245, 249))
            y += 130

        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(out_path, format="PNG")
        if remotion_target and remotion_target.resolve() != out_path.resolve():
            remotion_target.parent.mkdir(parents=True, exist_ok=True)
            img.save(remotion_target, format="PNG")

        print(f"✅ [MediaFetcher] Generated dark-mode proof card fallback -> {out_path}")
        return "assets/proof_card.png"
    except Exception as e:
        print(f"⚠️ [MediaFetcher] Failed to generate dark proof card: {e}")
        return None


def fetch_proof_card(
    github_repo: Optional[str] = None,
    official_url: Optional[str] = None,
    brand_domain: Optional[str] = None,
    tool_name: Optional[str] = None,
    real_steps: Optional[List[Any]] = None,
    out_path: Optional[str] = None,
) -> Optional[str]:
    """
    Fetches real visual proof card:
    (a) https://opengraph.githubassets.com/1/<github_repo> if GitHub repo exists.
    (b) Live website screenshot via https://image.thum.io/get/width/900/crop/600/noanimate/<official_url>
    (c) High-contrast dark-mode fallback proof card with PIL (never a blank white box).
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
                if not is_blank_or_invalid_image(out_target):
                    if remotion_target.resolve() != out_target.resolve():
                        remotion_target.write_bytes(r.content)
                    print(f"✅ [MediaFetcher] Saved GitHub proof card for '{clean_repo}' ({len(r.content)} bytes) -> {out_target}")
                    return "assets/proof_card.png"
                else:
                    print(f"⚠️ [MediaFetcher] GitHub OpenGraph returned blank/invalid image for '{clean_repo}'.")
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
                if not is_blank_or_invalid_image(out_target):
                    if remotion_target.resolve() != out_target.resolve():
                        remotion_target.write_bytes(r.content)
                    print(f"✅ [MediaFetcher] Saved live website screenshot for '{clean_url}' ({len(r.content)} bytes) -> {out_target}")
                    return "assets/proof_card.png"
                else:
                    print(f"⚠️ [MediaFetcher] Thum.io screenshot returned blank/white image for '{clean_url}'.")
        except Exception as e:
            print(f"⚠️ [MediaFetcher] Thum.io screenshot fetch failed for '{clean_url}': {e}")

    # 3. Strategy C: High-Contrast Dark-Mode Fallback Proof Card (Never render a blank box!)
    if tool_name or brand_domain or clean_repo:
        fallback_res = generate_dark_proof_card(
            tool_name=tool_name or brand_domain or "Free Open-Source App",
            brand_domain=brand_domain or (f"github.com/{clean_repo}" if clean_repo else "official site"),
            real_steps=real_steps,
            out_path=out_target,
            remotion_target=remotion_target,
        )
        if fallback_res:
            return fallback_res

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

    format_type = str(topic_data.get("format_type") or "").lower()
    left_char = str(topic_data.get("left_character") or "").lower()
    title_str = str(topic_data.get("title") or topic_data.get("topic_title") or "").lower()
    is_dad_skit = (format_type == "dad_clash") or (left_char == "dad") or ("dad" in title_str)

    t_path = (public_dir / "timeline.json") if public_dir else (PROJECT_ROOT / "public" / "timeline.json")

    if is_dad_skit:
        print(f"ℹ️ [MediaFetcher] Dad comedy skit detected ('{topic_data.get('title')}'): suppressing logo and proof card.")
        if t_path.exists():
            attach_media_to_timeline(t_path, None, None)
        return {
            "logoPath": None,
            "proofImagePath": None,
        }

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
        tool_name=tool_name,
        real_steps=topic_data.get("real_steps") or topic_data.get("realSteps"),
    )

    if t_path.exists():
        attach_media_to_timeline(t_path, logo_path, proof_image_path)

    return {
        "logoPath": logo_path,
        "proofImagePath": proof_image_path,
    }
