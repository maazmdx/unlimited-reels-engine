"""
Agent 1: Daily Autonomous Trend Researcher & Ragebait Topic Hunter
Scrapes and selects trending tech debates, AI vs Human battles, tool comparisons,
and subscription vs free tool controversies to produce high-retention video concepts.
Zero-Input Autonomous Mode: Queries real-time HackerNews AI discussions,
with an intelligent 365-day evergreen topic rotation fallback.
"""

import json
import time
import urllib.request
from typing import Dict, Any, List, Optional

AUTONOMOUS_TOPIC_BANK: List[Dict[str, Any]] = [
    {
        "id": "boiler_plate_blunder",
        "category": "AI vs Humans",
        "title": "The 6-Hour Dev Blunder",
        "hook": "Stop writing manual API boilerplate in 2026.",
        "concept": "A junior developer spends all day writing 400 lines of CRUD and swagger schema, while an AI agent generates, tests, and deploys it in 2.3 seconds for zero dollars.",
        "ragebait_angle": "Exposing human developers who mistake repetitive typing for actual engineering competence.",
        "tools_mentioned": ["Google Antigravity CLI", "Gemini 2.5 Flash", "Postman", "FastAPI"],
        "comparison": {"human": "6 Hours ($300 wage)", "ai": "2.3 Seconds ($0.00)"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "subscription_scam",
        "category": "Paid vs Free Tools",
        "title": "The $200/Month AI Subscription Trap",
        "hook": "Why are you paying $200 a month for AI?",
        "concept": "Developers wasting thousands annually on proprietary SaaS wrappers when free Google Antigravity and Gemini API tiers offer 1 million token context for zero cost.",
        "ragebait_angle": "Mocking companies and freelance devs who believe higher price tags equal better code intelligence.",
        "tools_mentioned": ["Claude Team $200/mo", "Google Antigravity Free CLI", "Gemini 2.5 Flash API"],
        "comparison": {"closed_saas": "$2,400 / year", "free_agent": "$0 / year (Unlimited)"},
        "suggested_env": "modern_office",
        "suggested_weather": "night_clear",
    },
    {
        "id": "ai_vs_ai_arena",
        "category": "AI vs AI Debates",
        "title": "Gemini vs Claude vs Grok: The Benchmark Smackdown",
        "hook": "Which AI actually writes production code without hallucinating?",
        "concept": "Claude brings academic citations, Grok drops sarcastic roast one-liners, and Antigravity Gemini reveals it ran the entire unit test suite while both were arguing.",
        "ragebait_angle": "Fans of closed AI models debating hype while practical engineering agents ship real code.",
        "tools_mentioned": ["Gemini 2.5 Flash", "Claude 3.7 Sonnet", "Grok 3"],
        "comparison": {"claude": "Slow, expensive perfectionist", "grok": "Fast, edgy, chaotic", "gemini": "High-throughput, free, practical"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "regex_and_unit_tests",
        "category": "AI vs Humans",
        "title": "Why Humans Should Never Write Unit Tests Again",
        "hook": "Are you still writing unit tests by hand?",
        "concept": "Junior developer writes 15 unit tests and misses edge cases. AI generates 150 edge-case fuzzing tests in 800 milliseconds and catches 4 zero-day memory leaks.",
        "ragebait_angle": "Showing how human cognitive fatigue leads to buggy production deployments.",
        "tools_mentioned": ["pytest", "Antigravity CLI", "Memory Sanitizers"],
        "comparison": {"human_test_coverage": "42% (took 3 days)", "ai_test_coverage": "99.8% (took 4 seconds)"},
        "suggested_env": "inside_home",
        "suggested_weather": "sunny",
    },
    {
        "id": "cloud_hosting_trap",
        "category": "Cloud Tools & Architecture",
        "title": "The Cloud Bill Heart Attack",
        "hook": "How one human config typo cost $14,000 on AWS.",
        "concept": "A developer forgot an unindexed query inside a while loop on AWS Lambda. Antigravity AI flagged the algorithmic complexity before the pull request was merged.",
        "ragebait_angle": "Human arrogance vs automated static AST analysis.",
        "tools_mentioned": ["AWS Lambda", "Google Cloud Run", "Antigravity Security Auditor"],
        "comparison": {"human_dev": "Spun up 50 instances blindly", "ai_auditor": "Fixed O(N^2) to O(1) instantly"},
        "suggested_env": "modern_office",
        "suggested_weather": "overcast",
    },
    {
        "id": "open_source_crush",
        "category": "Open Source vs Proprietary",
        "title": "Free Tools That Make $500 Software Look Like A Joke",
        "hook": "Stop paying for closed video and coding tools.",
        "concept": "Remotion, Edge-TTS, and Google Antigravity combining into an infinite content machine that costs literally zero dollars compared to $5,000 agency retainers.",
        "ragebait_angle": "Old-school creative agencies charging 5 figures for work done by automated code in 10 minutes.",
        "tools_mentioned": ["Remotion", "Edge-TTS", "FFmpeg", "Antigravity SDK"],
        "comparison": {"agency_cost": "$5,000 / month", "open_stack": "$0 / month forever"},
        "suggested_env": "outside_home",
        "suggested_weather": "sunny",
    },
    {
        "id": "centering_div_humiliation",
        "category": "AI vs Humans",
        "title": "The CSS Centering Humiliation",
        "hook": "Why did you spend 3 hours centering a div in 2026?",
        "concept": "A frontend developer struggles with flexbox margins and z-index bugs for an entire morning, while an AI visual agent spits out responsive CSS and passes accessibility audits in 1.4 seconds.",
        "ragebait_angle": "Roasting developers who refuse to adopt generative visual agents.",
        "tools_mentioned": ["Tailwind CSS", "Antigravity Agent", "Remotion React"],
        "comparison": {"human": "3 Hours of StackOverflow", "ai": "1.4 Seconds pixel-perfect"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "merge_conflict_carnage",
        "category": "AI vs Humans",
        "title": "The 3-Week Branch Merge Disaster",
        "hook": "Never let a human sit on a feature branch for 3 weeks.",
        "concept": "Developer hoards code for 21 days, causes 180 merge conflicts, and breaks main branch. AI multi-agent swarm works in decoupled micro-commits continuously.",
        "ragebait_angle": "Human procrastination vs autonomous agent branch merging.",
        "tools_mentioned": ["Git", "GitHub Actions", "Antigravity Swarm"],
        "comparison": {"human": "3 Weeks of uncommitted chaos", "ai": "Instant continuous integration"},
        "suggested_env": "modern_office",
        "suggested_weather": "night_clear",
    }
]


class TrendResearcherAgent:
    """Agent 1: Researches and prioritizes viral ragebait topics for daily video generation."""

    def __init__(self, topic_override: Optional[str] = None):
        self.topic_override = topic_override

    def scan_live_tech_debates(self) -> Optional[Dict[str, Any]]:
        """Scans Hacker News top tech stories for breaking AI discussions (Zero API key needed)."""
        try:
            req = urllib.request.Request(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                headers={"User-Agent": "AntigravityReels/2.0"}
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                top_ids = json.loads(resp.read().decode())[:20]

            for item_id in top_ids:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
                req_item = urllib.request.Request(item_url, headers={"User-Agent": "AntigravityReels/2.0"})
                with urllib.request.urlopen(req_item, timeout=2.5) as r_item:
                    story = json.loads(r_item.read().decode())

                title = story.get("title", "")
                lower_title = title.lower()

                # Keywords for AI debates & developer blunders
                if any(kw in lower_title for kw in ["ai", "llm", "claude", "gemini", "gpt", "coding", "developer", "benchmark", "software"]):
                    print(f"📡 [Agent 1: Live Feed Hit] Found breaking discussion: '{title}'")
                    return {
                        "id": f"hn_{item_id}",
                        "category": "Breaking Tech Trend",
                        "title": title[:55],
                        "hook": f"The internet is arguing about this: {title[:40]}.",
                        "concept": f"Breaking analysis of '{title}' showing how AI automation handles this 100x faster than humans.",
                        "ragebait_angle": "Exposing human developers debating on forums while AI agents ship working code.",
                        "tools_mentioned": ["Gemini 2.5 Flash", "Google Antigravity CLI"],
                        "suggested_env": "diner",
                        "suggested_weather": "raining",
                    }
        except Exception as e:
            print(f"ℹ️ [Agent 1] Live feed scan skipped ({e}); using curated 365-day ragebait matrix.")
        return None

    def research_daily_topic(self) -> Dict[str, Any]:
        """Autonomous selection of daily topic prioritized for viral retention and human roasting."""
        print("🔍 [Agent 1: Trend Researcher] Scanning tech discussions and AI benchmarks...")

        if self.topic_override:
            print(f"👉 Custom Topic Requested: '{self.topic_override}'")
            return {
                "id": "custom_override",
                "category": "Custom Research",
                "title": self.topic_override,
                "hook": f"The brutal truth about {self.topic_override}.",
                "concept": f"Analyzing how AI outclasses human workflows in {self.topic_override}.",
                "ragebait_angle": "Exposing human inefficiencies with humorous and sharp engineering facts.",
                "tools_mentioned": ["Antigravity CLI", "Gemini 2.5 Flash"],
                "suggested_env": "diner",
                "suggested_weather": "raining",
            }

        # 1. Attempt live trend scan
        live_topic = self.scan_live_tech_debates()
        if live_topic:
            return live_topic

        # 2. Deterministic day-of-year rotation through evergreen library
        day_of_year = time.localtime().tm_yday
        selected = AUTONOMOUS_TOPIC_BANK[day_of_year % len(AUTONOMOUS_TOPIC_BANK)]

        print(f"✅ [Agent 1] Selected Topic: '{selected['title']}' ({selected['category']})")
        print(f"   🎯 Hook Angle     : \"{selected['hook']}\"")
        print(f"   🔥 Ragebait Focus : {selected['ragebait_angle']}")
        return selected


if __name__ == "__main__":
    agent = TrendResearcherAgent()
    topic = agent.research_daily_topic()
    print("Topic Output:", topic)
