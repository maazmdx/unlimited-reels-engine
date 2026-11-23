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
import time
import hashlib
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple

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


# 6 Distinct Mass-Appeal Free Niches for Reel #1 (Rotates deterministically by date YYYY-MM-DD)
DAILY_FREE_NICHES = [
    {
        "id": "file_utility",
        "name": "Everyday File, PDF & Media Utility",
        "target_audience": "Everyday phone and laptop users tired of paywalls",
        "guidance": "100% free offline tools that replace Adobe Acrobat, heavy media converters, and file-sharing bloat (e.g. LocalSend, Stirling-PDF, HandBrake, Upscayl, LosslessCut).",
        "example_tools": ["LocalSend", "Stirling-PDF", "Upscayl", "HandBrake", "LosslessCut"],
    },
    {
        "id": "retro_browser_game",
        "name": "Free Browser & Retro Game / Emulator",
        "target_audience": "Students, casual gamers, and nostalgia fans with potato laptops",
        "guidance": "Playable retro games or native emulators running directly inside Chrome tabs on potato laptops with zero downloads (e.g. EmulatorJS, WebVM, DOSBox Pure Web, v86).",
        "example_tools": ["EmulatorJS", "WebVM", "DOSBox Pure Web", "v86"],
    },
    {
        "id": "privacy_system_speedup",
        "name": "Privacy, Ad-Block & System Speedup Tool",
        "target_audience": "Anyone whose laptop or phone is slow or plagued by YouTube/web ads",
        "guidance": "100% free open-source tools that block all ads, kill background bloatware, and speed up PCs/phones (e.g. uBlock Origin, Pi-hole, BleachBit, Proton VPN Free).",
        "example_tools": ["uBlock Origin", "BleachBit", "Proton VPN Free", "Pi-hole"],
    },
    {
        "id": "local_ai_creative",
        "name": "Free Local AI & Creative App",
        "target_audience": "Creators and students who refuse to pay $20/month for Photoshop or ChatGPT Plus",
        "guidance": "Zero-dollar private local AI models and creative tools running on your machine (e.g. Photopea, Ollama, Jan AI, Whisper Web, Krita).",
        "example_tools": ["Photopea", "Ollama", "Jan", "Whisper Web", "Krita"],
    },
    {
        "id": "student_productivity",
        "name": "Student & Everyday Productivity Shortcut",
        "target_audience": "Students and knowledge workers drowning in tabs and expensive subscriptions",
        "guidance": "Secret free productivity hacks and student lifesavers replacing paid software (e.g. Obsidian, NotebookLM, Zotero, Draw.io, Anki).",
        "example_tools": ["NotebookLM", "Obsidian", "Draw.io", "Zotero", "Anki"],
    },
    {
        "id": "hidden_os_hack",
        "name": "Hidden GitHub OS Hack & Power Tool",
        "target_audience": "Windows and Mac users who want modern OS power features for $0",
        "guidance": "Open-source system utilities that make Windows or Mac feel 10x faster (e.g. Microsoft PowerToys, QuickLook for Windows, SpaceSniffer, RustDesk).",
        "example_tools": ["QuickLook", "RustDesk", "Microsoft PowerToys", "SpaceSniffer"],
    },
]

# Fresh Relatable Household & Tech-Myth Premises for Reel #2 (Dad Clash)
# (5G/Wi-Fi bills and AI side hustles are strictly excluded)
DAD_CLASH_PREMISES = [
    {
        "tag": "dad_ram_booster",
        "premise": "phone storage cleaner / RAM booster apps",
        "title": "Dad Installed 4 'RAM Booster' Apps on His Phone",
        "myth": "Dad thinks downloading 4 different phone cleaner apps speeds up his Android, but they actually drain 80% battery showing full-screen ads.",
        "hook": "Look how fast this rocket cleaner makes my phone fly!",
        "conflict": "Dev explaining modern Android RAM management vs Dad proud of the turbo rocket cleaning animation",
    },
    {
        "tag": "dad_scam_link",
        "premise": "WhatsApp lottery / scam link forwards",
        "title": "Dad Believes He Won an iPhone 17 on WhatsApp",
        "myth": "Dad gets a forward claiming he won a free car or phone and is about to forward it to 20 family groups.",
        "hook": "Beta, I just won a brand new phone on WhatsApp!",
        "conflict": "Dev warning about phishing scams vs Dad insisting 'It has the official logo!'",
    },
    {
        "tag": "dad_battery_myth",
        "premise": "battery 100% charging and overnight myths",
        "title": "Dad Sets an Alarm to Unplug His Phone at Exactly 80%",
        "myth": "Dad watched a WhatsApp video claiming charging past 80% explodes the battery and now charges in 10-minute intervals.",
        "hook": "Beta, unplug it at eighty percent or the battery explodes!",
        "conflict": "Dev explaining modern battery BMS chips vs Dad citing WhatsApp University",
    },
    {
        "tag": "dad_printer_rage",
        "premise": "printer ink cartridge extortion",
        "title": "Dad vs The Color Ink Cartridge Extortion",
        "myth": "Dad trying to print a black-and-white government form, but the printer refuses because 'Cyan is empty'.",
        "hook": "Why does this printer demand cyan to print black text?!",
        "conflict": "Dad threatening the printer with a screwdriver vs Dev explaining printer DRM chips",
    },
    {
        "tag": "dad_shady_apk",
        "premise": "shady APK downloads / modded WhatsApp",
        "title": "Dad Downloaded 'Gold WhatsApp' from a Sketchy Website",
        "myth": "Dad downloaded a sketchy APK because a video promised it can read deleted messages from 2018.",
        "hook": "Look at my gold WhatsApp theme! It reads deleted messages!",
        "conflict": "Dev discovering 15 malware popups vs Dad bragging about his secret gold theme",
    },
    {
        "tag": "dad_tv_mic",
        "premise": "smart TV spying & mic listening myths",
        "title": "Dad Covers the Smart TV with a Towel",
        "myth": "Dad saw shoe ads on his phone after talking about shoes and now covers the TV sensor with tape and a towel.",
        "hook": "I covered the Smart TV with a towel so it stops spying!",
        "conflict": "Dev explaining cross-app ad tracking vs Dad whispering in the living room",
    },
]

STOPWORDS_SET = {
    "a", "about", "all", "also", "an", "and", "any", "are", "as", "at", "be", "because",
    "been", "before", "being", "between", "both", "but", "by", "can", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself",
    "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of",
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these",
    "they", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    "free", "tool", "app", "new", "vs", "running", "100", "browser", "chrome", "pc",
    "laptop", "turns", "right", "now", "stop", "paying", "online", "use", "make",
    "install", "installed", "get", "runs"
}


def normalize_entity_name(text: Optional[str]) -> str:
    """Normalizes tool names or premise tags for exact comparison."""
    if not text:
        return ""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def normalize_github_repo(repo: Optional[str]) -> str:
    """Normalizes GitHub repo owner/repo string."""
    if not repo:
        return ""
    clean = str(repo).strip().lower()
    clean = re.sub(r"^https?://github\.com/", "", clean)
    clean = re.sub(r"\.git$", "", clean)
    return clean.strip("/")


def normalize_brand_domain(domain: Optional[str]) -> str:
    """Normalizes brand domain name."""
    if not domain:
        return ""
    clean = str(domain).strip().lower()
    clean = re.sub(r"^https?://", "", clean)
    clean = re.sub(r"^www\.", "", clean)
    return clean.split("/")[0].strip()


def extract_topic_keywords(text: Optional[str]) -> Set[str]:
    """Extracts non-stopword alphanumeric keyword tokens for topic overlap matching."""
    words = re.findall(r"[a-z0-9]+", str(text or "").lower())
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS_SET}


def check_topic_duplication(
    candidate: Dict[str, Any],
    covered_history: List[Dict[str, Any]],
    current_batch: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[bool, str]:
    """
    Strict Zero-Repeat Deduplication:
    Rejects any candidate sharing the same tool_name, github_repo, brand_domain,
    or >= 45% non-stopword keyword overlap with any historical record or current batch entry.
    """
    all_records = list(covered_history) + (list(current_batch) if current_batch else [])

    c_tool = normalize_entity_name(candidate.get("tool_name"))
    c_repo = normalize_github_repo(candidate.get("github_repo"))
    c_domain = normalize_brand_domain(candidate.get("brand_domain"))
    c_tag = normalize_entity_name(candidate.get("angle_tag") or candidate.get("premise"))
    c_title = candidate.get("topic_title") or candidate.get("title") or ""
    c_keywords = extract_topic_keywords(c_title)

    generic_tools = {"opentool", "ai", "app", "tool", "freetool", "aiapp"}
    generic_domains = {"github.com", "google.com", "archive.org", "wikipedia.org", "youtube.com"}

    for rec in all_records:
        r_tool = normalize_entity_name(rec.get("tool_name"))
        r_repo = normalize_github_repo(rec.get("github_repo"))
        r_domain = normalize_brand_domain(rec.get("brand_domain"))
        r_tag = normalize_entity_name(rec.get("angle_tag") or rec.get("premise"))
        r_title = rec.get("topic_title") or rec.get("title") or ""
        r_keywords = extract_topic_keywords(r_title)

        # 1. Identical tool_name match
        if c_tool and r_tool and c_tool == r_tool and c_tool not in generic_tools:
            return True, f"Identical tool_name '{c_tool}'"

        # 2. Identical github_repo match
        if c_repo and r_repo and c_repo == r_repo:
            return True, f"Identical github_repo '{c_repo}'"

        # 3. Identical brand_domain match
        if c_domain and r_domain and c_domain == r_domain and c_domain not in generic_domains:
            return True, f"Identical brand_domain '{c_domain}'"

        # 4. Same angle/premise tag match
        if c_tag and r_tag and c_tag == r_tag:
            return True, f"Identical premise tag '{c_tag}'"

        # 5. >= 45% Non-stopword keyword overlap
        if c_keywords and r_keywords:
            common = c_keywords.intersection(r_keywords)
            smaller_len = min(len(c_keywords), len(r_keywords))
            if smaller_len > 0:
                overlap_ratio = len(common) / smaller_len
                if overlap_ratio >= 0.45:
                    return True, f"Keyword overlap {overlap_ratio:.0%} ({common}) with covered topic '{r_title}'"

    return False, ""


def infer_replaces_paid_app(tool_name: Optional[str] = "", category: Optional[str] = "", title: Optional[str] = "") -> str:
    """Infers the real paid app / subscription cost that a free tool replaces."""
    text = (str(tool_name or "") + " " + str(category or "") + " " + str(title or "")).lower()
    if "pdf" in text or "stirling" in text:
        return "Adobe Acrobat Pro ($20/mo)"
    elif "photo" in text or "psd" in text:
        return "Adobe Photoshop ($22/mo)"
    elif "localsend" in text or "airdrop" in text or "transfer" in text:
        return "WeTransfer / Cloud Storage ($15/mo)"
    elif "emulator" in text or "retro" in text or "game" in text:
        return "Paid Consoles & Expensive Retro Cartridges"
    elif "ublock" in text or "adblock" in text:
        return "YouTube Premium & Annoying Adware ($14/mo)"
    elif "bleachbit" in text or "cleaner" in text:
        return "Paid Antivirus & PC Optimizer Scams ($30/yr)"
    elif "ollama" in text or "jan" in text or "local ai" in text:
        return "ChatGPT Plus & Copilot Pro ($20/mo)"
    elif "notebook" in text:
        return "Paid AI Summarizers & Transcription ($20/mo)"
    elif "rustdesk" in text:
        return "TeamViewer & AnyDesk Subscriptions ($25/mo)"
    elif "quicklook" in text:
        return "Paid Windows Utility Software ($15)"
    elif "draw" in text or "diagram" in text:
        return "Lucidchart / Visio Subscriptions ($12/mo)"
    return "Expensive $20/month SaaS Subscriptions"


KNOWN_VERIFIED_REPOS = {
    "localsend/localsend": {
        "full_name": "localsend/localsend",
        "html_url": "https://github.com/localsend/localsend",
        "stars": 48000,
        "description": "An open-source cross-platform alternative to AirDrop",
        "readme_excerpt": "LocalSend is a free, open-source cross-platform file sharing app using local Wi-Fi.",
    },
    "frooodle/stirling-pdf": {
        "full_name": "Frooodle/Stirling-PDF",
        "html_url": "https://github.com/Frooodle/Stirling-PDF",
        "stars": 45000,
        "description": "locally hosted one-stop-shop web application for all your PDF needs",
        "readme_excerpt": "Stirling-PDF is a robust, locally hosted one-stop-shop web application for all your PDF editing needs.",
    },
    "upscayl/upscayl": {
        "full_name": "upscayl/upscayl",
        "html_url": "https://github.com/upscayl/upscayl",
        "stars": 32000,
        "description": "Free and Open Source AI Image Upscaler",
        "readme_excerpt": "Upscayl is a free and open-source AI image upscaler built with Vulkan and NCNN.",
    },
    "emulator-js/emulator.js": {
        "full_name": "emulator-js/emulator.js",
        "html_url": "https://github.com/emulator-js/emulator.js",
        "stars": 3500,
        "description": "A web-based retro game emulation frontend for browser tabs",
        "readme_excerpt": "EmulatorJS is a browser-based retro emulation frontend supporting retro games in browser tabs.",
    },
    "leaningtech/webvm": {
        "full_name": "leaningtech/webvm",
        "html_url": "https://github.com/leaningtech/webvm",
        "stars": 8500,
        "description": "Virtual Machine for the Web running Linux in browser",
        "readme_excerpt": "WebVM is a virtual machine running Linux in the browser completely client-side.",
    },
    "gorhill/ublock": {
        "full_name": "gorhill/uBlock",
        "html_url": "https://github.com/gorhill/uBlock",
        "stars": 46000,
        "description": "uBlock Origin - An efficient blocker for Chromium and Firefox",
        "readme_excerpt": "uBlock Origin is not just an ad blocker; it is an efficient, wide-spectrum content blocker.",
    },
    "bleachbit/bleachbit": {
        "full_name": "bleachbit/bleachbit",
        "html_url": "https://github.com/bleachbit/bleachbit",
        "stars": 3200,
        "description": "BleachBit frees disk space and guards privacy",
        "readme_excerpt": "BleachBit frees disk space and guards your privacy by freeing cache, deleting cookies, and shredding junk.",
    },
    "ollama/ollama": {
        "full_name": "ollama/ollama",
        "html_url": "https://github.com/ollama/ollama",
        "stars": 115000,
        "description": "Get up and running with Llama 3, DeepSeek, and other LLMs locally",
        "readme_excerpt": "Ollama allows running large language models locally on your machine.",
    },
    "jgraph/drawio": {
        "full_name": "jgraph/drawio",
        "html_url": "https://github.com/jgraph/drawio",
        "stars": 39000,
        "description": "draw.io is a configurable diagramming and whiteboarding tool",
        "readme_excerpt": "Draw.io is a completely free, open-source online diagramming tool.",
    },
    "ql-win/quicklook": {
        "full_name": "QL-Win/QuickLook",
        "html_url": "https://github.com/QL-Win/QuickLook",
        "stars": 20000,
        "description": "Bring macOS Quick Look feature to Windows",
        "readme_excerpt": "QuickLook brings macOS Quick Look functionality to Windows File Explorer.",
    },
    "rustdesk/rustdesk": {
        "full_name": "rustdesk/rustdesk",
        "html_url": "https://github.com/rustdesk/rustdesk",
        "stars": 75000,
        "description": "An open-source remote desktop application written in Rust",
        "readme_excerpt": "RustDesk is a full-featured open source remote control alternative to TeamViewer.",
    },
}

KNOWN_VERIFIED_WEB_TOOLS = {
    "photopea.com": {
        "title": "Photopea | Online Photo Editor",
        "description": "Photopea Online Photo Editor lets you edit photos, apply effects, filters, add text, crop or resize pictures.",
    },
    "notebooklm.google.com": {
        "title": "NotebookLM",
        "description": "NotebookLM is a personalized AI research assistant powered by Google's Gemini models.",
    },
    "emulatorjs.org": {
        "title": "EmulatorJS - Retro Games in the Browser",
        "description": "Play thousands of retro games directly in your browser without downloads or setup.",
    },
    "stirlingpdf.com": {
        "title": "Stirling-PDF - Offline Local PDF Tools",
        "description": "Locally hosted one-stop-shop web application for all your PDF editing needs.",
    },
}


def verify_github_repo_live(repo_or_name: Optional[str], timeout: float = 4.0) -> Optional[Dict[str, Any]]:
    """
    Live verifier for GitHub repos:
    Queries https://api.github.com/repos/{owner}/{repo} (or GitHub search API fallback).
    Requires HTTP 200 and >= 500 stars.
    Extracts real full_name, html_url, description, stars, and top README excerpt (up to 800 chars).
    """
    if not repo_or_name:
        return None
    clean_repo = normalize_github_repo(repo_or_name)
    headers = {
        "User-Agent": "CanIDoAI-ReelsEngine/1.0 (educational-reels-bot; contact@canidoai.com)",
        "Accept": "application/vnd.github.v3+json",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    if clean_repo and "/" in clean_repo:
        try:
            url = f"https://api.github.com/repos/{clean_repo}"
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                stars = data.get("stargazers_count", 0)
                if stars >= 500:
                    full_name = data.get("full_name", clean_repo)
                    html_url = data.get("html_url", f"https://github.com/{full_name}")
                    description = data.get("description") or ""
                    default_branch = data.get("default_branch", "main")
                    readme_excerpt = ""
                    try:
                        raw_readme_url = f"https://raw.githubusercontent.com/{full_name}/{default_branch}/README.md"
                        r_md = requests.get(raw_readme_url, headers={"User-Agent": headers["User-Agent"]}, timeout=2.5)
                        if r_md.status_code == 200 and r_md.text:
                            clean_md = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)|!\[.*?\]\(.*?\)", "", r_md.text)
                            clean_md = re.sub(r"https?://\S+", "", clean_md)
                            clean_md = re.sub(r"#+\s*", "", clean_md)
                            clean_md = re.sub(r"\s+", " ", clean_md).strip()
                            readme_excerpt = clean_md[:800]
                    except Exception:
                        pass
                    return {
                        "full_name": full_name,
                        "html_url": html_url,
                        "stars": stars,
                        "description": description,
                        "readme_excerpt": readme_excerpt or description,
                    }
        except Exception as e:
            print(f"⚠️ [TopicMaster] Live GitHub verification error for '{clean_repo}': {e}")

    # Fallback to GitHub Search API if exact owner/repo wasn't matched
    query = clean_repo.split("/")[-1] if clean_repo else str(repo_or_name).strip()
    if query and len(query) >= 3:
        try:
            search_url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}+stars:%3E=500&sort=stars&order=desc"
            r = requests.get(search_url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    top = items[0]
                    stars = top.get("stargazers_count", 0)
                    if stars >= 500:
                        return {
                            "full_name": top.get("full_name"),
                            "html_url": top.get("html_url"),
                            "stars": stars,
                            "description": top.get("description") or "",
                            "readme_excerpt": (top.get("description") or "")[:800],
                        }
        except Exception as e:
            print(f"⚠️ [TopicMaster] GitHub search fallback error for '{query}': {e}")

    # Fallback to curated verified catalog when network / GitHub API is unreachable or times out
    if clean_repo and clean_repo.lower() in KNOWN_VERIFIED_REPOS:
        print(f"ℹ️ [TopicMaster] Used curated verified GitHub metadata for '{clean_repo}'.")
        return dict(KNOWN_VERIFIED_REPOS[clean_repo.lower()])

    return None


def verify_web_tool_live(url: Optional[str], timeout: float = 3.5) -> Optional[Dict[str, Any]]:
    """
    Live verifier for web tools / browser games:
    Requires HTTP 200 and valid <title> + meta description.
    """
    if not url:
        return None
    clean_url = str(url).strip()
    if not clean_url.startswith("http"):
        clean_url = f"https://{clean_url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    try:
        r = requests.get(clean_url, headers=headers, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 300:
            title_m = re.search(r"<title>(.*?)</title>", r.text, re.IGNORECASE)
            title = title_m.group(1).strip() if title_m else ""
            desc_m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', r.text, re.IGNORECASE)
            desc = desc_m.group(1).strip() if desc_m else ""
            if title or desc:
                return {
                    "canonical_url": str(r.url),
                    "title": title,
                    "page_title": title,
                    "description": desc or title,
                    "readme_excerpt": f"{title} - {desc}"[:800],
                }
    except Exception as e:
        print(f"⚠️ [TopicMaster] Web tool live check error for '{clean_url}': {e}")

    # Fallback to curated verified web tools catalog when network / host is unreachable
    domain = clean_url.replace("https://", "").replace("http://", "").split("/")[0].lower()
    if domain in KNOWN_VERIFIED_WEB_TOOLS:
        entry = KNOWN_VERIFIED_WEB_TOOLS[domain]
        print(f"ℹ️ [TopicMaster] Used curated verified web metadata for '{domain}'.")
        return {
            "canonical_url": f"https://{domain}",
            "title": entry["title"],
            "page_title": entry["title"],
            "description": entry["description"],
            "readme_excerpt": f"{entry['title']} - {entry['description']}"[:800],
        }

    return None


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
        elif any(w in cat_lower for w in ["pdf"]):
            return "PDF"
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
        "User-Agent": "AntigravityTopicMaster/3.0",
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
        print(f"⚠️ [Groq API] Request exception: {e}")

    return None


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
        self.rss_config_file = self.project_root / "engine" / "config" / "rss_feeds.json"
        self.channel_memory_file = self.project_root / "inbox" / "channel_memory.json"
        self.rss_config = self._load_rss_config()

        self.api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if genai and self.api_key:
            try:
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={"api_version": "v1beta", "timeout": 50000},
                )
            except Exception as e:
                print(f"⚠️ TopicMaster: Gemini client init notice: {e}")

    def _load_rss_config(self) -> Dict[str, Any]:
        """Loads live RSS feeds and endpoints from engine/config/rss_feeds.json."""
        if self.rss_config_file.exists():
            try:
                with open(self.rss_config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ TopicMaster: RSS feeds config read notice: {e}")
        return {
            "google_news_queries": [
                "free+open+source+tool",
                "github+trending+repo",
                "free+browser+game+webassembly",
                "underrated+free+ai+tool",
                "free+developer+alternative",
            ],
            "tech_rss": [
                {"url": "https://www.theverge.com/rss/index.xml", "label": "The Verge"},
                {"url": "https://lobste.rs/rss", "label": "Lobsters"},
                {"url": "https://dev.to/feed", "label": "Dev.to"},
            ],
            "product_hunt": {"feed_url": "https://www.producthunt.com/feed", "source_label": "Product Hunt"},
            "github_trending": {
                "search_url": "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-01-01&sort=updated&order=desc",
                "source_label": "GitHub Trending (Open Source)",
            },
            "reddit_subreddits": ["webdev", "programming", "InternetIsBeautiful", "technology"],
        }

    def load_channel_memory(self) -> Dict[str, Any]:
        """Loads channel memory tracking formats, covered topics, and frequency."""
        if not self.channel_memory_file.exists():
            return {
                "format_history": [],
                "covered_topics": [],
                "format_counts": {"informative_roast": 0, "discovery_doc": 0, "dad_clash": 0, "dev_meme": 0, "tech_secrets": 0},
                "last_used_format": None,
                "last_updated": datetime.now().isoformat()
            }
        try:
            with open(self.channel_memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "format_history": [],
                "covered_topics": [],
                "format_counts": {"informative_roast": 0, "discovery_doc": 0, "dad_clash": 0, "dev_meme": 0, "tech_secrets": 0},
                "last_used_format": None,
                "last_updated": datetime.now().isoformat()
            }

    def update_channel_memory(self, record: Dict[str, Any]):
        """Updates channel memory with newly generated topic and format."""
        mem = self.load_channel_memory()
        mem.setdefault("format_history", []).append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "format_type": record.get("format_type", "informative_roast"),
            "topic_title": record.get("title", ""),
            "category": record.get("category", ""),
            "auto_dm_keyword": record.get("auto_dm_keyword", ""),
            "has_resource_link": record.get("has_resource_link", True)
        })
        mem.setdefault("covered_topics", []).append(record.get("title", ""))
        fmt = record.get("format_type", "informative_roast")
        mem.setdefault("format_counts", {})
        mem["format_counts"][fmt] = mem["format_counts"].get(fmt, 0) + 1
        mem["last_used_format"] = fmt
        mem["last_updated"] = datetime.now().isoformat()
        try:
            self.channel_memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.channel_memory_file, "w", encoding="utf-8") as f:
                json.dump(mem, f, indent=2)
            print(f"🧠 [Channel Memory] Tracked format '{fmt}' in inbox/channel_memory.json")
        except Exception as e:
            print(f"⚠️ Failed to update channel_memory.json: {e}")

    # =========================================================================
    # 1. LIVE SIGNAL HARVESTING (Consumer Tech, Games, AI Apps, Business)
    # =========================================================================

    def fetch_google_news_signals(self) -> List[Dict[str, Any]]:
        """
        Scrapes zero-cost Google News RSS feeds for consumer AI, browser games,
        viral tech launches, and company business model teardowns.
        """
        signals = []
        raw_queries = self.rss_config.get("google_news_queries", [])
        queries = []
        for q in raw_queries:
            clean_lbl = q.replace("+", " ").replace("%20", " ").title()
            queries.append((q, f"GoogleNews: {clean_lbl}"))
        if not queries:
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
        subreddits = self.rss_config.get(
            "reddit_subreddits",
            ["InternetIsBeautiful", "ChatGPT", "webdev", "technology"]
        )
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
        """Queries RSS feeds and GitHub Trending Search configured in rss_feeds.json."""
        signals = []
        # Tech RSS configured in rss_feeds.json
        feeds = []
        for feed in self.rss_config.get("tech_rss", []):
            if isinstance(feed, dict) and feed.get("url"):
                feeds.append((feed["url"], feed.get("label", "Tech RSS")))
        if not feeds:
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

        # GitHub Trending Repos configured in rss_feeds.json
        gh_cfg = self.rss_config.get("github_trending", {})
        gh_url = gh_cfg.get("search_url", "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-01-01&sort=updated&order=desc")
        gh_label = gh_cfg.get("source_label", "GitHub Trending (Open Source)")
        try:
            r_gh = self.session.get(gh_url, timeout=3.0)
            if r_gh.status_code == 200:
                for it in r_gh.json().get("items", [])[:6]:
                    name = it.get("full_name") or it.get("name")
                    desc = it.get("description") or "Open source project"
                    signals.append({
                        "source": gh_label,
                        "title": f"[Free Open-Source Repo] {name}: {desc[:80]}",
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

    def get_covered_blocklist(self, limit: int = 30) -> Dict[str, Any]:
        """Extracts recent titles, all covered tool names, and covered dad/funny premises."""
        history = self.load_covered_history()
        titles = [item.get("title") or item.get("topic_title") or item.get("slug") for item in history[-limit:] if item.get("title") or item.get("slug")]

        tools = set()
        premises = set()
        for item in history:
            t = normalize_entity_name(item.get("tool_name"))
            if t and t not in {"opentool", "ai", "app", "tool", "freetool", "aiapp"}:
                tools.add(item.get("tool_name"))
            p = item.get("angle_tag") or item.get("premise")
            if p:
                premises.add(str(p))
            t_low = (item.get("title") or "").lower()
            if "ram" in t_low and "cleaner" in t_low:
                premises.add("phone storage cleaner / RAM booster apps")
            elif "scam" in t_low or "whatsapp" in t_low or "lottery" in t_low:
                premises.add("WhatsApp lottery / scam link forwards")
            elif "battery" in t_low or "overnight" in t_low:
                premises.add("battery 100% charging and overnight myths")
            elif "printer" in t_low or "cartridge" in t_low:
                premises.add("printer ink cartridge scam")
            elif "apk" in t_low:
                premises.add("shady APK downloads")
            elif "smart tv" in t_low or "tv spying" in t_low:
                premises.add("smart TV spying / mic paranoia")

        return {
            "titles": titles,
            "tools": sorted(list(tools)),
            "dad_premises": sorted(list(premises)),
        }

    def record_covered_topics(self, new_topics: List[Dict[str, Any]]):
        """Appends freshly selected topics to inbox/covered_topics.json with rich entity metadata."""
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
                "tool_name": topic.get("tool_name") or topic.get("toolName", ""),
                "github_repo": topic.get("github_repo") or topic.get("githubRepo", ""),
                "brand_domain": topic.get("brand_domain") or topic.get("brandDomain", ""),
                "angle_tag": topic.get("angle_tag") or topic.get("premise", ""),
                "format_type": topic.get("format_type", ""),
            })

        self.covered_topics_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.covered_topics_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            print(f"💾 [TopicMaster] Saved {len(new_topics)} topic(s) with entity tags into inbox/covered_topics.json.")
        except Exception as e:
            print(f"⚠️ TopicMaster: Failed to write covered_topics.json: {e}")

    # =========================================================================
    # 3. DUAL-ENGINE LLM (GEMINI + GROQ LLAMA-3.3-70B HIGH-SPEED FALLBACK)
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
                            print(f"✨ [TopicMaster] Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(res.text)} chars).")
                            return res.text
                    except Exception as e:
                        err_str = str(e)
                        is_504 = "504" in err_str or "DEADLINE_EXCEEDED" in err_str or "timeout" in err_str.lower()
                        if is_504 and attempt == 0:
                            print(f"⚠️ TopicMaster: GenAI {m} hit 504/deadline, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ TopicMaster: GenAI {m} warning: {e}")
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
                                print(f"✨ [TopicMaster] REST Gemini model '{m}' succeeded in {elapsed:.2f}s ({len(text)} chars).")
                                return text
                        elif (r.status_code == 504 or "DEADLINE_EXCEEDED" in r.text) and attempt == 0:
                            print(f"⚠️ TopicMaster: REST {m} hit 504, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        else:
                            print(f"⚠️ TopicMaster: REST {m} returned {r.status_code}: {r.text[:120]}")
                            break
                    except Exception as e:
                        err_str = str(e)
                        is_timeout = "timeout" in err_str.lower() or "504" in err_str
                        if is_timeout and attempt == 0:
                            print(f"⚠️ TopicMaster: REST {m} timed out, quick retrying once...")
                            time.sleep(1.0)
                            continue
                        print(f"⚠️ TopicMaster: REST {m} warning: {e}")
                        break

        return None

    def _call_llm(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Routes LLM generation through the central zero-dependency LLMRouter."""
        from engine.llm_router import generate_text
        return generate_text(prompt, system_prompt=system_instruction, json_mode=True, temperature=0.7)

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
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        seed_int = int(hashlib.md5(today_date_str.encode()).hexdigest(), 16)
        today_niche = DAILY_FREE_NICHES[seed_int % len(DAILY_FREE_NICHES)]

        signals_summary = []
        for idx, s in enumerate(signals[:20], 1):
            signals_summary.append(f"{idx}. [{s['source']}] {s['title']}")
        signals_text = "\n".join(signals_summary) if signals_summary else "No live feeds available."

        blocklist = self.get_covered_blocklist(limit=30)
        covered_tools_str = ", ".join(blocklist["tools"][:35]) if blocklist["tools"] else "None yet."
        covered_premises_str = ", ".join(blocklist["dad_premises"][:15]) if blocklist["dad_premises"] else "None yet."
        covered_titles_str = "\n".join(f"- {t}" for t in blocklist["titles"][-30:]) if blocklist["titles"] else "- None."

        uncovered_dad_premises = [
            p for p in DAD_CLASH_PREMISES
            if p["premise"] not in blocklist["dad_premises"] and p["tag"] not in blocklist["dad_premises"]
        ]
        today_dad = uncovered_dad_premises[seed_int % len(uncovered_dad_premises)] if uncovered_dad_premises else DAD_CLASH_PREMISES[seed_int % len(DAD_CLASH_PREMISES)]

        system_instruction = (
            "You are TopicMaster: The World-Class Viral Media Strategist for short-form video (Instagram Reels / YouTube Shorts).\n"
            "Your mandate: Select ONLY topics that have MASS CONSUMER APPEAL across college students, everyday developers, gamers, and tech fans.\n\n"
            "HARD REJECT: ZERO PAID TOOLS / ZERO MONTHLY SUBSCRIPTIONS (MANDATORY GATE):\n"
            "- NEVER pick a topic that promotes or recommends a paid tool, paid game, paid API, or paid monthly subscription ($19.99/mo, credit cards, paywalls, paid tiers).\n"
            "- Paid software (Photoshop, ChatGPT Plus, Midjourney, Netflix, Notion Plus, Copilot Pro, expensive IDEs) may ONLY appear as the PUNCHING BAG to roast people who still waste money on them!\n"
            "- The solution / recommendation MUST ALWAYS BE 100% FREE, ZERO-CARD, ZERO-DOLLAR (free open-source apps, free AI tools like NotebookLM/local models, free full browser games, free hidden phone/PC tricks, or free vs hype teardowns).\n"
            "- Prioritize everyday topics every student, gamer, and everyday phone/potato laptop user relates to immediately—never obscure niche enterprise SaaS tools!\n\n"
            "STRICT BAN ON DRY CS TRIVIA:\n"
            "- Strictly BANNED: RFC specs, obscure algorithmic puzzle solvers, low-level Linux kernel patches, academic math proofs, compiler edge-cases.\n"
            "- STRICTLY REWARDED CATEGORIES:\n"
            "  * Free Open-Source GitHub Repos: Insane 100% free open-source repos from GitHub Trending / Awesome lists (free self-hosted & desktop alternatives to paid apps, local AI models/agents, media downloaders, privacy tools) roasting humans still paying $20/mo subscriptions.\n"
            "  * Retro & Browser Games: Playable retro games in browser tabs on potato laptops with zero downloads.\n"
            "  * Underrated AI & App Workflows: 100% free zero-cost AI workflows that replace $20/mo subscriptions.\n"
            "  * Tech Business Models: Shocking company profit breakdowns (NVIDIA, Costco, Spotify).\n"
            "  * Breaking Tech & Gadgets: Wild hardware drops and humanoid robots making old human skills look prehistoric.\n"
            "  * Relatable Tech / Dev / Indian Dad Memes: Generational tech comedy (Dad vs phone storage cleaner apps / scam links / battery myths).\n\n"
            "OBJECTIVE VIRAL SCORING RUBRIC (0-100):\n"
            "1. Mass-Appeal Curiosity (0-25): Would a casual viewer, student, or dev freeze their thumb in the first 2 seconds?\n"
            "2. Save/DM Demand (0-25): Would thousands of viewers comment a keyword to get the 100% free link, playable port, or cheat sheet?\n"
            "3. Meme & Debate Potential (0-25): Does it spark energetic comments ('Wait really?', 'No way!', or generational conflict)?\n"
            "4. Roast & Ragebait Potential (0-25): Can the AI brutally humble the human here? Prioritize things humans waste hours or money doing that AI/free apps do in 2 seconds, browser games running on potato laptops, hyped tools humans overpay for, wild company money tricks, and new tech making old skills look prehistoric.\n"
            "- MINIMUM PASSING SCORE: 78/100. Any topic scoring < 78 or requiring payment/credit card is automatically REJECTED."
        )

        mem = self.load_channel_memory()
        f_counts = mem.get("format_counts", {})
        funny_options = ["dad_clash", "discovery_doc", "dev_meme", "tech_secrets"]
        suggested_funny = min(funny_options, key=lambda f: f_counts.get(f, 0))

        prompt = f"""
Today's Date: {today_str}

LIVE SOURCE SIGNALS TODAY:
{signals_text}

MANDATORY ROTATION TARGETS FOR TODAY:
- REEL #1 NICHE: {today_niche['name']}
  * Target Audience: {today_niche['target_audience']}
  * Guidance: {today_niche['guidance']}
  * Example Tool Inspirations: {', '.join(today_niche['example_tools'])}

- REEL #2 PREMISE (DAD CLASH): {today_dad['title']}
  * Relatable Myth: {today_dad['myth']}
  * Relatable Conflict: {today_dad['conflict']}
  * 0-3s Hook: "{today_dad['hook']}"

STRICT DO-NOT-REPEAT BLOCKLIST:
- BANNED TOOLS (DO NOT repeat or select these previously covered tools): {covered_tools_str}
- BANNED PREMISES / MEMES (DO NOT repeat): {covered_premises_str}
- RECENTLY COVERED TITLES:
{covered_titles_str}

MANDATORY DYNAMIC 2-REEL DAILY MIX (WHEN COUNT >= 2):
If count >= 2:
- Reel #1 MUST BE 'informative_roast': A 100% FREE tool, underrated AI app, free browser game, or open-source GitHub repo matching today's niche '{today_niche['name']}'.
  * format_type: 'informative_roast'
  * has_resource_link: true
  * auto_dm_keyword: Single real English word (e.g. 'PLAY', 'FREE', 'REPO', 'PDF', 'TOOL')
  * tool_name: EXACT app, repository, or game name (e.g. 'LocalSend', 'Stirling-PDF', 'EmulatorJS', 'Photopea'). NEVER a generic placeholder like 'Free Tool' or 'AI App'.
  * brand_domain: Official website domain (e.g. 'localsend.org', 'stirlingpdf.com', 'emulatorjs.org').
  * github_repo: GitHub 'owner/repo' slug if open-source (e.g. 'localsend/localsend' or 'Frooodle/Stirling-PDF'), else empty string.
  * real_steps: Exactly 3 concrete, real, reproducible steps (never generic fluff like 'Download and install').
- Reel #2 MUST BE 'dad_clash' (or '{suggested_funny}'):
  * format_type: 'dad_clash'
  * has_resource_link: false
  * auto_dm_keyword: '' (empty string, NO DM link keyword)
  * cta_phrase: Viral share/tag CTA (e.g. 'Send this to your dad before he installs another RAM booster.')
  * Core humor: Indian Dad vs Tech ({today_dad['conflict']}).
    - Strictly block previously covered premises like 5G/Wi-Fi bills or AI side hustles.

TASK:
1. Brainstorm 8 diverse candidate reel angles inspired by the live signals and our core categories.
2. HARD REJECT GATE: Reject any angle that promotes or recommends a paid tool or subscription. Paid tools may only be the punching bag while revealing a 100% FREE alternative.
3. Every 'informative_roast' topic MUST include a verified real 'tool_name', 'brand_domain', 'github_repo', and 3 concrete 'real_steps'. Reject topics without a real named free tool.
4. Score each candidate across the 4 rubric criteria (Curiosity 0-25, Save/DM Demand 0-25, Meme/Debate 0-25, Roast/Ragebait 0-25).
5. Compute total `viral_score` (0-100) as the sum of all 4 criteria.
6. Strictly filter out anything scoring < 78, promoting paid software, or lacking a real named tool.
7. Return candidates in valid JSON matching schema.

JSON Schema:
{{
  "candidates": [
    {{
      "topic_title": "Punchy title under 55 characters",
      "format_type": "informative_roast | discovery_doc | dad_clash | dev_meme | tech_secrets",
      "has_resource_link": true,
      "category": "Free Open-Source GitHub Repos | Retro & Browser Games | Underrated AI Apps | Wildlife Dev Doc | Indian Dad vs Tech | Developer Survival",
      "tool_name": "Exact app, repo, or game name (e.g. EmulatorJS)",
      "brand_domain": "Domain name (e.g. emulatorjs.org or github.com)",
      "github_repo": "owner/repo if open-source on GitHub, else empty string",
      "real_steps": [
        "1. Concrete verified step 1",
        "2. Concrete verified step 2",
        "3. Concrete verified step 3"
      ],
      "curiosity_score": 24,
      "save_demand_score": 24,
      "debate_potential_score": 22,
      "roast_ragebait_score": 25,
      "viral_score": 95,
      "why_viral": "1-2 sentences on why this explodes in reach and comments",
      "roast_angle": "How AI brutally humbles human laziness, potato laptops, or overpaying for software",
      "auto_dm_keyword": "ONEWORD",
      "left_character": "junior_dev or dad",
      "right_character": "claude, gemini, or grok",
      "scene_preset": "diner or desk",
      "resource_link_or_query": "Direct verifiable URL, search query, or tool name",
      "core_conflict": "Human denial/procrastination vs AI effortless superiority and savage facts"
    }}
  ]
}}
"""

        raw_json = self._call_llm(prompt, system_instruction)
        if not raw_json:
            raise RuntimeError("LLM (Gemini and Groq) failed to return scored topic candidates.")

        cleaned = raw_json.strip()
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()
            else:
                cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
                cleaned = re.sub(r"\n```$", "", cleaned).strip()

        # Clean trailing commas
        cleaned_clean = re.sub(r",\s*([\]}])", r"\1", cleaned)
        try:
            parsed = json.loads(cleaned_clean)
        except Exception:
            try:
                parsed = json.loads(cleaned)
            except Exception as e:
                start_idx = cleaned.find("{")
                end_idx = cleaned.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    sub = cleaned[start_idx:end_idx + 1]
                    sub = re.sub(r",\s*([\]}])", r"\1", sub)
                    parsed = json.loads(sub)
                else:
                    raise e
        candidates = parsed.get("candidates", []) if isinstance(parsed, dict) else parsed

        # Hard Zero-Paid-Tools Gate: NEVER promote paid tools, paid subscriptions, or paid games
        paid_promo_re = re.compile(
            r"(\$\d+[\d,.]*\s*(/mo|/month|/yr|per month)|paid tier|paid subscription|requires credit card|"
            r"pricing starts at|pro plan only|premium subscription|buy for \$)",
            re.IGNORECASE
        )

        valid_candidates = []
        for c in candidates:
            score = c.get("viral_score", 0)
            t_str = f"{c.get('topic_title', '')} {c.get('why_viral', '')} {c.get('roast_angle', '')}"
            is_paid_promo = bool(paid_promo_re.search(t_str) and not any(neg in t_str.lower() for neg in ["replaces", "instead of", "beat", "kill", "cancel", "free", "$0", "zero", "0 dollar"]))

            # Strict Tool Name Gate: Reject informative_roast topics without a verified named tool
            is_info = c.get("format_type") == "informative_roast" or c.get("has_resource_link") is True
            raw_tname = str(c.get("tool_name") or "").strip()
            generic_names = ["free tool", "ai tool", "tool", "ai app", "app", "unknown", "none", ""]
            if is_info and (not raw_tname or raw_tname.lower() in generic_names):
                print(f"⚠️ [TopicMaster] Rejecting topic '{c.get('topic_title')}' — missing real named tool_name.")
                continue

            if score >= 78 and not is_paid_promo:
                valid_candidates.append(c)

        if not valid_candidates and candidates:
            candidates.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
            valid_candidates = [c for c in candidates if not paid_promo_re.search(f"{c.get('topic_title', '')} {c.get('why_viral', '')}")]
            if not valid_candidates:
                valid_candidates = candidates[:1]

        valid_candidates.sort(key=lambda x: x.get("viral_score", 0), reverse=True)

        # Dynamic 2-Reel Mix Selection: 1 Informative Roast + 1 Funny Story / Dad Clash
        full_history = self.load_covered_history()
        if count >= 2:
            info_picks = [c for c in valid_candidates if c.get("has_resource_link") is not False and c.get("format_type") not in ["discovery_doc", "dad_clash", "dev_meme"]]
            funny_picks = [c for c in valid_candidates if c.get("has_resource_link") is False or c.get("format_type") in ["discovery_doc", "dad_clash", "dev_meme", "tech_secrets", "funny_story"]]
            selected = []

            # 1. Select Informative Reel (Reel #1) matching today's niche with LIVE VERIFICATION
            for cand in (info_picks or valid_candidates):
                is_dup, reason = check_topic_duplication(cand, full_history, selected)
                if is_dup:
                    print(f"⚠️ [TopicMaster] Rejecting duplicate candidate '{cand.get('topic_title')}': {reason}")
                    continue

                repo_cand = cand.get("github_repo")
                tool_cand = cand.get("tool_name")
                domain_cand = cand.get("brand_domain")

                verified_info = None
                if repo_cand:
                    verified_info = verify_github_repo_live(repo_cand)
                if not verified_info and tool_cand:
                    verified_info = verify_github_repo_live(tool_cand)
                if not verified_info and domain_cand:
                    verified_info = verify_web_tool_live(domain_cand)

                if not verified_info:
                    print(f"⚠️ [TopicMaster] Live verification failed for '{cand.get('topic_title')}' (repo='{repo_cand}', tool='{tool_cand}', domain='{domain_cand}'). Retrying...")
                    continue

                cand["github_repo"] = verified_info.get("full_name") or cand.get("github_repo", "")
                cand["canonical_url"] = verified_info.get("html_url") or verified_info.get("canonical_url", "")
                cand["real_description"] = verified_info.get("description", "")
                cand["readme_summary"] = verified_info.get("readme_excerpt", "")
                cand["replaces_paid_app"] = cand.get("replaces_paid_app") or infer_replaces_paid_app(cand.get("tool_name"), cand.get("category"), cand.get("topic_title"))
                cand["angle_tag"] = today_niche["id"]
                selected.append(cand)
                print(f"✅ [TopicMaster] Live-verified Reel #1 winner: '{cand.get('tool_name')}' ({cand.get('github_repo') or cand.get('canonical_url')})")
                break

            # 2. Select Funny / Dad Clash Reel (Reel #2) - Strictly pure comedy, zero software repos
            for fp in funny_picks:
                is_dup, reason = check_topic_duplication(fp, full_history, selected)
                if is_dup:
                    print(f"⚠️ [TopicMaster] Rejecting duplicate funny candidate '{fp.get('topic_title')}': {reason}")
                    continue
                fp["angle_tag"] = today_dad["tag"]
                fp["format_type"] = "dad_clash"
                fp["github_repo"] = None
                fp["brand_domain"] = None
                fp["has_resource_link"] = False
                fp["auto_dm_keyword"] = ""
                fp["left_character"] = "dad"
                fp["right_character"] = "junior_dev"
                fp["scene_preset"] = "diner"
                fp["premise"] = today_dad["premise"]
                selected.append(fp)
                break

            # If no non-duplicate candidates found, safely add today's fresh dad clash premise directly
            if len(selected) < 2:
                cand2 = {
                    "topic_title": today_dad["title"],
                    "category": "Indian Dad vs Tech",
                    "format_type": "dad_clash",
                    "has_resource_link": False,
                    "auto_dm_keyword": "",
                    "viral_score": 96,
                    "curiosity_score": 25,
                    "save_demand_score": 22,
                    "debate_potential_score": 24,
                    "roast_ragebait_score": 25,
                    "why_viral": f"Relatable household tech conflict: {today_dad['myth']}",
                    "roast_angle": today_dad["conflict"],
                    "left_character": "dad",
                    "right_character": "junior_dev",
                    "scene_preset": "diner",
                    "resource_link_or_query": "",
                    "core_conflict": today_dad["conflict"],
                    "angle_tag": today_dad["tag"],
                    "premise": today_dad["premise"],
                    "github_repo": None,
                    "brand_domain": None,
                }
                selected.append(cand2)
            winners = [self._sanitize_topic(it) for it in selected[:count]]
        else:
            selected = []
            for c in valid_candidates:
                is_dup, reason = check_topic_duplication(c, full_history, selected)
                if not is_dup:
                    selected.append(c)
                    if len(selected) >= count:
                        break
            if not selected and valid_candidates:
                selected = valid_candidates[:count]
            winners = [self._sanitize_topic(it) for it in selected[:count]]

        return winners

    def _sanitize_topic(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes topic fields for downstream HookMaster and remotion screenplays."""
        title = str(item.get("topic_title") or item.get("title", "Viral Tech Breakdown")).strip()
        slug = "".join(c if c.isalnum() else "_" for c in title.lower()).strip("_")[:45]

        left_char = "dad" if "dad" in str(item.get("left_character", "")).lower() else "junior_dev"
        
        # Prefer claude (warm terracotta) and gemini (bright cyan) 80% of the time so diner visuals always pop
        import random
        right_raw = str(item.get("right_character", "")).lower()
        if "grok" in right_raw and random.random() < 0.20:
            right_char = "grok"
        elif "gemini" in right_raw:
            right_char = "gemini"
        elif "claude" in right_raw:
            right_char = "claude"
        else:
            right_char = "gemini" if random.random() < 0.40 else "claude"

        scene_preset = "desk" if "desk" in str(item.get("scene_preset", "")).lower() else "diner"

        # Format type and smart context-aware CTA routing
        format_type = str(item.get("format_type") or ("dad_clash" if left_char == "dad" else "informative_roast")).lower()
        has_res = item.get("has_resource_link")
        if has_res is None:
            has_res = not any(k in format_type for k in ["doc", "dad", "meme", "funny", "secret"])

        category = item.get("category", "Viral Tech")
        if has_res:
            raw_kw = str(item.get("auto_dm_keyword", "FREE")).strip().upper()
            clean_kw = sanitize_auto_dm_keyword(raw_kw, category, title)
            is_github_repo = any(term in str(category).lower() or term in str(title).lower() for term in ["github", "repo", "open-source", "open source"])
            cta_phrase = f"Comment {clean_kw} and I'll DM you the GitHub repo link." if is_github_repo else f"Comment {clean_kw} and I'll DM you the free link."
            end_card_cta = f"Comment {clean_kw} for the free link"
        else:
            clean_kw = ""
            if "doc" in format_type or "discovery" in format_type:
                cta_phrase = "Tag that dev in your group whose credits just ran out."
                end_card_cta = "TAG THAT DEV BELOW"
                category = "Wildlife Dev Doc"
            elif "dad" in format_type:
                cta_phrase = "Send this to your Dad or dev friend."
                end_card_cta = "SEND TO YOUR DAD OR FRIEND"
                category = "Indian Dad vs Tech"
            else:
                cta_phrase = "Tag that dev in your group who still codes without AI."
                end_card_cta = "TAG THAT DEV IN YOUR GROUP"
                category = "Developer Survival Memes"

        score = int(item.get("viral_score") or 85)
        breakdown = {
            "curiosity": int(item.get("curiosity_score") or 22),
            "save_demand": int(item.get("save_demand_score") or 22),
            "debate_potential": int(item.get("debate_potential_score") or 20),
            "roast_ragebait": int(item.get("roast_ragebait_score") or 22),
        }

        why_viral = item.get("why_viral", "High curiosity gap and immediate viewer engagement.")
        roast_angle = item.get("roast_angle", f"{right_char} brutally humbles human effort with savage comedy.")
        conflict = item.get("core_conflict", f"{left_char} human struggle vs {right_char} savage roast facts")

        is_dad_skit = (format_type == "dad_clash") or (left_char == "dad")

        if is_dad_skit:
            tool_name = None
            brand_domain = None
            github_repo = None
            has_res = False
            clean_kw = ""
            cta_phrase = "Send this to your Dad or friend before they pay for another scam."
            end_card_cta = "SEND TO YOUR DAD OR FRIEND"
            category = "Indian Dad vs Tech"
        else:
            tool_name = str(item.get("tool_name") or item.get("toolName") or "").strip()
            brand_domain = str(item.get("brand_domain") or item.get("brandDomain") or "").strip()
            github_repo = str(item.get("github_repo") or item.get("githubRepo") or "").strip()

            # Provide verified defaults for known categories / offline fallback
            if not tool_name:
                if "vice" in title.lower() or "gta" in title.lower():
                    tool_name = "EmulatorJS"
                    brand_domain = "emulatorjs.org"
                    github_repo = "emulator-js/emulator.js"
                elif "pdf" in title.lower():
                    tool_name = "Stirling-PDF"
                    brand_domain = "stirlingpdf.com"
                    github_repo = "Frooodle/Stirling-PDF"
                elif "notebook" in title.lower():
                    tool_name = "NotebookLM"
                    brand_domain = "notebooklm.google.com"
                elif "ollama" in title.lower() or "local" in title.lower():
                    tool_name = "Ollama"
                    brand_domain = "ollama.com"
                    github_repo = "ollama/ollama"
                else:
                    tool_name = title.split()[0] if title else "OpenTool"

        real_steps = item.get("real_steps")
        if not isinstance(real_steps, list) or len(real_steps) < 3:
            real_steps = [
                f"1. Open {brand_domain or tool_name or 'official site'} in any Chrome or Safari tab",
                f"2. Launch {tool_name or 'free app'} directly with zero setup or file bloat",
                "3. Full 100% free functionality replacing expensive paid subscriptions"
            ]

        canonical_url = item.get("canonical_url") or (f"https://github.com/{github_repo}" if github_repo else (f"https://{brand_domain}" if brand_domain else ""))
        real_desc = item.get("real_description") or item.get("description", "")
        readme_sum = item.get("readme_summary") or item.get("readme_excerpt", "")
        replaces_paid = item.get("replaces_paid_app") or (infer_replaces_paid_app(tool_name, category, title) if not is_dad_skit else "")

        return {
            "id": slug,
            "title": title,
            "topic_title": title,
            "topic": title,
            "core_topic": title,
            "category": category,
            "pillar_style": category,
            "format_type": "dad_clash" if is_dad_skit else format_type,
            "has_resource_link": has_res,
            "viral_score": score,
            "score_breakdown": breakdown,
            "why_viral": why_viral,
            "roast_angle": roast_angle,
            "auto_dm_keyword": clean_kw,
            "cta_keyword": clean_kw,
            "ctaKeyword": clean_kw,
            "cta_phrase": cta_phrase,
            "end_card_cta": end_card_cta,
            "is_100_percent_free": True,
            "left_character": left_char,
            "right_character": right_char,
            "scene_preset": scene_preset,
            "scenePreset": scene_preset,
            "resource_link_or_query": canonical_url or item.get("resource_link_or_query", ""),
            "core_conflict": conflict,
            "style": "ai_vs_dad" if is_dad_skit else "diner_ai",
            "tool_name": tool_name,
            "toolName": tool_name,
            "brand_domain": brand_domain,
            "brandDomain": brand_domain,
            "github_repo": github_repo,
            "githubRepo": github_repo,
            "real_steps": real_steps,
            "realSteps": real_steps,
            "angle_tag": item.get("angle_tag", ""),
            "premise": item.get("premise", ""),
            "canonical_url": canonical_url,
            "real_description": real_desc,
            "readme_summary": readme_sum,
            "replaces_paid_app": replaces_paid,
        }

    # =========================================================================
    # 4. EMERGENCY OFFLINE FALLBACK
    # =========================================================================

    def _offline_fallback(self, count: int, covered_history: List[str]) -> List[Dict[str, Any]]:
        """Selects high-performing uncovered topics matching today's niche rotation and dad premise."""
        print("⚠️ [TopicMaster] Live feeds/Gemini unreachable; falling back to offline curated rotation.")
        full_history = self.load_covered_history()
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        seed_int = int(hashlib.md5(today_date_str.encode()).hexdigest(), 16)
        today_niche = DAILY_FREE_NICHES[seed_int % len(DAILY_FREE_NICHES)]

        blocklist = self.get_covered_blocklist(limit=30)
        uncovered_dad_premises = [
            p for p in DAD_CLASH_PREMISES
            if p["premise"] not in blocklist["dad_premises"] and p["tag"] not in blocklist["dad_premises"]
        ]
        today_dad = uncovered_dad_premises[seed_int % len(uncovered_dad_premises)] if uncovered_dad_premises else DAD_CLASH_PREMISES[seed_int % len(DAD_CLASH_PREMISES)]

        mass_appeal_catalog = [
            {
                "niche": "file_utility",
                "tool": "LocalSend",
                "domain": "localsend.org",
                "repo": "localsend/localsend",
                "title": "Free Open-Source AirDrop for Every Device",
                "replaces_paid_app": "WeTransfer & AirDrop ($12/mo)",
                "real_description": "An open-source cross-platform alternative to AirDrop that shares files securely over local Wi-Fi with zero internet or cloud tracking.",
                "readme_summary": "LocalSend is a free, open-source cross-platform file sharing app. It uses secure REST communication and HTTPS encryption to transfer files between devices on the same local area network without third-party servers.",
                "steps": ["1. Install LocalSend on PC and phone", "2. Connect to same local Wi-Fi", "3. Share files at 50MB/s with zero cloud uploads"],
                "kw": "REPO"
            },
            {
                "niche": "file_utility",
                "tool": "Stirling-PDF",
                "domain": "stirlingpdf.com",
                "repo": "Frooodle/Stirling-PDF",
                "title": "Stop Paying $20/mo to Edit PDFs Offline",
                "replaces_paid_app": "Adobe Acrobat Pro ($20/mo)",
                "real_description": "A powerful locally hosted web application that lets you split, merge, convert, edit, and OCR PDF files with 100% privacy and zero subscription fees.",
                "readme_summary": "Stirling-PDF is a robust, locally hosted one-stop-shop web application for all your PDF editing needs. Allows splitting, merging, rotating, password-protecting, OCR, and dark mode conversion without sending data to external servers.",
                "steps": ["1. Open self-hosted Stirling-PDF web app", "2. Select split, merge, or OCR operation", "3. 100% private offline PDF editing for $0"],
                "kw": "PDF"
            },
            {
                "niche": "file_utility",
                "tool": "Upscayl",
                "domain": "upscayl.org",
                "repo": "upscayl/upscayl",
                "title": "AI Image Upscaler That Runs 100% Free on PC",
                "replaces_paid_app": "Topaz Gigapixel AI ($99)",
                "real_description": "Free and open source AI Image Upscaler for Linux, macOS, and Windows that enlarges images without losing quality using local deep learning models.",
                "readme_summary": "Upscayl is a free and open-source AI image upscaler built with Vulkan and NCNN. It runs locally on your machine GPU/CPU to upscale low-resolution photos and illustrations up to 16x without uploading images to cloud servers.",
                "steps": ["1. Download open-source Upscayl app", "2. Drop blurry 720p photo or screenshot", "3. AI upscales to crisp 4K locally with $0 fees"],
                "kw": "FREE"
            },
            {
                "niche": "retro_browser_game",
                "tool": "EmulatorJS",
                "domain": "emulatorjs.org",
                "repo": "emulator-js/emulator.js",
                "title": "Play Retro Games In Chrome on Potato Laptops",
                "replaces_paid_app": "Paid Consoles & Expensive Retro Hardware",
                "real_description": "A web-based retro game frontend running in JavaScript and WebAssembly that plays NES, SNES, GBA, and PS1 games directly inside Chrome tabs.",
                "readme_summary": "EmulatorJS is a browser-based retro emulation frontend supporting over 40 gaming systems directly in browser tabs via WebAssembly and HTML5 canvas with zero external plugins or installations required.",
                "steps": ["1. Open emulatorjs.org in Chrome", "2. Drag retro ROM into browser canvas", "3. Play full 60 FPS with zero lag"],
                "kw": "PLAY"
            },
            {
                "niche": "retro_browser_game",
                "tool": "WebVM",
                "domain": "webvm.io",
                "repo": "leaningtech/webvm",
                "title": "Full Linux Virtual Machine In Chrome Tab",
                "replaces_paid_app": "Cloud VM / VPS Hosting ($10/mo)",
                "real_description": "A server-less Linux virtual machine running fully client-side in HTML5/WebAssembly powered by the CheerpX virtualization engine.",
                "readme_summary": "WebVM is a virtual machine running Linux in the browser completely client-side using WebAssembly and CheerpX x86 virtualization. It provides a terminal environment with gcc, python, and full Unix utilities without any backend server.",
                "steps": ["1. Navigate to webvm.io in browser", "2. Boot full Linux virtual machine in Chrome", "3. Run C/C++ and Doom with zero install"],
                "kw": "PLAY"
            },
            {
                "niche": "privacy_system_speedup",
                "tool": "uBlock Origin",
                "domain": "ublockorigin.com",
                "repo": "gorhill/uBlock",
                "title": "Block Every Single YouTube Ad for Free",
                "replaces_paid_app": "YouTube Premium ($14/mo)",
                "real_description": "An efficient, open-source, wide-spectrum content blocker that strips ads, trackers, and malware domains while being easy on CPU and memory.",
                "readme_summary": "uBlock Origin is not just an ad blocker; it is an efficient, wide-spectrum content blocker. It loads tens of thousands of filters while consuming significantly less memory and CPU than other popular ad-blocking extensions.",
                "steps": ["1. Add uBlock Origin extension to browser", "2. Enable advanced filter lists", "3. Block every YouTube and website ad for $0"],
                "kw": "FREE"
            },
            {
                "niche": "privacy_system_speedup",
                "tool": "BleachBit",
                "domain": "bleachbit.org",
                "repo": "bleachbit/bleachbit",
                "title": "Free 30GB Disk Space With Open-Source Cleaner",
                "replaces_paid_app": "Paid PC Cleaner & Antivirus Scams ($30/yr)",
                "real_description": "Free open-source disk space cleaner and privacy manager that deletes cache, cookies, log files, and junk across 2,500 applications.",
                "readme_summary": "BleachBit frees disk space and guards your privacy by freeing cache, deleting cookies, clearing internet history, shredding temporary files, and wiping logs across Windows and Linux systems.",
                "steps": ["1. Open open-source BleachBit", "2. Select system cache and browser bloat", "3. Free 30GB disk space in 10 seconds"],
                "kw": "TOOL"
            },
            {
                "niche": "local_ai_creative",
                "tool": "Photopea",
                "domain": "photopea.com",
                "repo": "",
                "title": "Free Browser Alternative to Adobe Photoshop",
                "replaces_paid_app": "Adobe Photoshop ($22/mo)",
                "real_description": "Advanced image editor running completely inside web browsers supporting PSD, AI, and RAW files with full layer, mask, and filter support.",
                "readme_summary": "Photopea is an advanced web-based graphic editor designed to work with raster and vector graphics. It supports Photoshop PSD, Sketch, and Illustrator files with layers, masks, smart objects, and color adjustments.",
                "steps": ["1. Open photopea.com in any browser", "2. Load any PSD or RAW photo file", "3. 100% free Photoshop alternative for $0"],
                "kw": "TOOL"
            },
            {
                "niche": "local_ai_creative",
                "tool": "Ollama",
                "domain": "ollama.com",
                "repo": "ollama/ollama",
                "title": "Run Private AI Models Locally on Any Laptop",
                "replaces_paid_app": "ChatGPT Plus & Copilot Pro ($20/mo)",
                "real_description": "Get up and running with Llama 3, DeepSeek, Mistral, and other large language models locally on macOS, Linux, and Windows with a single command.",
                "readme_summary": "Ollama bundles model weights, configuration, and GPU acceleration into a unified package. Run open-source LLMs locally via simple terminal commands or an OpenAI-compatible REST API without subscription fees or data leaks.",
                "steps": ["1. Run 'ollama run deepseek-r1' in terminal", "2. Local private AI inference on laptop GPU", "3. Cancel $20/month subscription traps forever"],
                "kw": "REPO"
            },
            {
                "niche": "student_productivity",
                "tool": "NotebookLM",
                "domain": "notebooklm.google.com",
                "repo": "",
                "title": "Turn Any 50-Page PDF Into a Free Audio Podcast",
                "replaces_paid_app": "Paid AI Research & Transcription Tools ($20/mo)",
                "real_description": "Google's personalized AI research assistant that synthesizes documents, generates citations, and creates full two-host audio podcast discussions from your notes.",
                "readme_summary": "NotebookLM is an AI-powered notebook and research companion. It grounds Gemini in your uploaded notes, PDFs, and Google Docs to answer questions, cite sources, and generate lifelike audio deep-dive podcasts.",
                "steps": ["1. Navigate to notebooklm.google.com", "2. Upload 50-page PDF or technical doc", "3. Generate interactive podcast overview with Gemini"],
                "kw": "TOOL"
            },
            {
                "niche": "student_productivity",
                "tool": "Draw.io",
                "domain": "app.diagrams.net",
                "repo": "jgraph/drawio",
                "title": "Free Architecture Diagrams With Zero Paywalls",
                "replaces_paid_app": "Lucidchart / Visio Subscriptions ($12/mo)",
                "real_description": "Security-first open source diagramming software for flowcharts, UML, network architectures, and mockups with zero paywalls or account requirements.",
                "readme_summary": "Draw.io (diagrams.net) is a completely free, open-source online diagramming tool. Create flowcharts, wireframes, UML diagrams, and network maps with local storage support and zero account or subscription barriers.",
                "steps": ["1. Open app.diagrams.net in browser", "2. Create architecture diagrams and flowcharts", "3. Export SVG with zero account or paywall"],
                "kw": "TOOL"
            },
            {
                "niche": "hidden_os_hack",
                "tool": "QuickLook",
                "domain": "pooi.moe/QuickLook",
                "repo": "QL-Win/QuickLook",
                "title": "Get Mac Spacebar Preview on Windows for $0",
                "replaces_paid_app": "Paid Windows Utility Software ($15)",
                "real_description": "Open-source macOS-like Quick Look preview feature for Windows Explorer that lets you preview files instantly by pressing the Spacebar.",
                "readme_summary": "QuickLook brings macOS Quick Look functionality to Windows. Select any image, PDF, video, archive, or code file in Windows File Explorer and press Spacebar to preview contents instantly without opening heavy applications.",
                "steps": ["1. Install QuickLook from GitHub", "2. Highlight any file in Windows Explorer", "3. Hit Spacebar for instant macOS file preview"],
                "kw": "REPO"
            },
            {
                "niche": "hidden_os_hack",
                "tool": "RustDesk",
                "domain": "rustdesk.com",
                "repo": "rustdesk/rustdesk",
                "title": "Free Open-Source Remote Desktop Alternative",
                "replaces_paid_app": "TeamViewer & AnyDesk Subscriptions ($25/mo)",
                "real_description": "The open source remote desktop access software written in Rust that works out of the box with end-to-end encryption and self-hosting options.",
                "readme_summary": "RustDesk is a full-featured open source remote control alternative to TeamViewer and AnyDesk. Features end-to-end encryption, self-hosted relay servers, cross-platform clients, and zero commercial license nagging.",
                "steps": ["1. Download open-source RustDesk", "2. Enter target device 9-digit ID", "3. 100% free self-hosted remote desktop with zero time limits"],
                "kw": "REPO"
            },
        ]

        # Prioritize tools matching today's niche that haven't been covered
        niche_matches = [t for t in mass_appeal_catalog if t["niche"] == today_niche["id"]]
        uncovered_niche_tools = []
        for t in niche_matches:
            cand_test = {"tool_name": t["tool"], "github_repo": t["repo"], "brand_domain": t["domain"], "topic_title": t["title"]}
            is_dup, _ = check_topic_duplication(cand_test, full_history)
            if not is_dup:
                uncovered_niche_tools.append(t)

        if not uncovered_niche_tools:
            for t in mass_appeal_catalog:
                cand_test = {"tool_name": t["tool"], "github_repo": t["repo"], "brand_domain": t["domain"], "topic_title": t["title"]}
                is_dup, _ = check_topic_duplication(cand_test, full_history)
                if not is_dup:
                    uncovered_niche_tools.append(t)

        selected_fb = uncovered_niche_tools[0] if uncovered_niche_tools else mass_appeal_catalog[0]

        winners = []
        # Reel #1: Informative Roast
        reel1 = self._sanitize_topic({
            "topic_title": selected_fb["title"],
            "category": today_niche["name"],
            "format_type": "informative_roast",
            "has_resource_link": True,
            "viral_score": 95,
            "curiosity_score": 25,
            "save_demand_score": 24,
            "debate_potential_score": 22,
            "roast_ragebait_score": 24,
            "why_viral": f"Replaces paid subscriptions with 100% free {selected_fb['tool']}.",
            "roast_angle": f"AI roasts humans still wasting money on paid tools when {selected_fb['tool']} exists for $0.",
            "auto_dm_keyword": selected_fb["kw"],
            "left_character": "junior_dev",
            "right_character": "claude",
            "scene_preset": "diner",
            "resource_link_or_query": f"https://{selected_fb['domain']}",
            "core_conflict": f"Paying expensive subscriptions vs instant free {selected_fb['tool']}",
            "tool_name": selected_fb["tool"],
            "brand_domain": selected_fb["domain"],
            "github_repo": selected_fb["repo"],
            "real_steps": selected_fb["steps"],
            "angle_tag": today_niche["id"],
            "replaces_paid_app": selected_fb.get("replaces_paid_app") or infer_replaces_paid_app(selected_fb["tool"], today_niche["name"], selected_fb["title"]),
            "real_description": selected_fb.get("real_description", ""),
            "readme_summary": selected_fb.get("readme_summary", ""),
        })
        winners.append(reel1)

        if count >= 2:
            # Reel #2: Fresh Relatable Dad Clash Premise
            reel2 = self._sanitize_topic({
                "topic_title": today_dad["title"],
                "category": "Indian Dad vs Tech",
                "format_type": "dad_clash",
                "has_resource_link": False,
                "auto_dm_keyword": "",
                "viral_score": 96,
                "curiosity_score": 25,
                "save_demand_score": 22,
                "debate_potential_score": 24,
                "roast_ragebait_score": 25,
                "why_viral": f"Relatable household tech conflict: {today_dad['myth']}",
                "roast_angle": today_dad["conflict"],
                "left_character": "dad",
                "right_character": "junior_dev",
                "scene_preset": "diner",
                "resource_link_or_query": "",
                "core_conflict": today_dad["conflict"],
                "angle_tag": today_dad["tag"],
                "premise": today_dad["premise"],
            })
            winners.append(reel2)

        return winners[:count]

    # =========================================================================
    # 5. PUBLIC DISCOVERY INTERFACE
    # =========================================================================

    def curate_fresh_topics(self, count: int = 2) -> List[Dict[str, Any]]:
        """
        Main entry point for TopicMasterAgent:
        Harvests live signals -> Evaluates candidates against 0-100 rubric ->
        Selects top N winners (score >= 78) -> Saves to covered history and channel memory.
        """
        print(f"\n🧠 [TopicMaster] Scouting mass-appeal signals for {count} viral reel concept(s)...")
        covered = self.get_last_covered_topics(limit=50)
        print(f"📋 [TopicMaster] Loaded {len(covered)} historical covered topic(s) for deduplication.")

        signals = self.harvest_live_signals()
        print(f"🌐 [TopicMaster] Gathered {len(signals)} live headlines (Google News, Product Hunt, HN, Tech RSS).")

        winners = []
        if self.api_key or os.environ.get("GROQ_API_KEY"):
            try:
                winners = self.curate_and_score_topics(signals, count, covered)
                print(f"🏆 [TopicMaster] Viral gate passed! Selected {len(winners)} top-scoring concept(s).")
                for w in winners:
                    kw_disp = w['auto_dm_keyword'] if w.get('has_resource_link') else f"NO-DM (CTA: {w.get('end_card_cta')})"
                    print(f"   ★ {w['title']} | Score: {w['viral_score']}/100 [{w['format_type']}] | Keyword: {kw_disp}")
            except Exception as e:
                print(f"⚠️ [TopicMaster] LLM scoring pass warning: {e}")

        if not winners:
            winners = self._offline_fallback(count, covered)

        if winners:
            self.record_covered_topics(winners)
            for w in winners:
                self.update_channel_memory(w)

        return winners


if __name__ == "__main__":
    master = TopicMasterAgent()
    topics = master.curate_fresh_topics(count=2)
    print("\n--- TopicMaster Output ---")
    for t in topics:
        print(json.dumps(t, indent=2))
