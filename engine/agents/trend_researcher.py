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
        "id": "diner_fellow_3850",
        "category": "AI Hustle Satire",
        "title": "Anthropic Fellow: $3,850/Week (No Experience)",
        "hook": "When a $3,850/week job says 'no experience required' but you only know Python.",
        "concept": "Developer finds a crazy high-paying AI fellowship, gets roasted by Claude, and executes a bizarre weekend experiment teaching an AI to love owls.",
        "ragebait_angle": "Satirizing the absurd expectations of modern AI job hunting.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "diner_rejection_101",
        "category": "Job Hunt Satire",
        "title": "The 101st Rejection: Bypassing HR at 2 AM",
        "hook": "Rejected after 4 rounds while the guy hired never even applied.",
        "concept": "Developer gets rejected by an automated HR email and learns how founders actually hire via 2 AM Twitter DMs before jobs are posted.",
        "ragebait_angle": "Exposing the broken traditional job application process.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "diner_vibe_coder",
        "category": "Wildlife Documentary Satire",
        "title": "The Vibe Coder in the Wild",
        "hook": "He hasn't seen daylight since Opus 5.5 came out.",
        "concept": "A BBC Planet Earth style nature documentary observing the nocturnal Vibe Coder whose polite prompts devolve into 'FIX IT' at 3 AM until the Tuesday rate limit strikes.",
        "ragebait_angle": "Memeing the chaotic nocturnal reality of coding with LLMs.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "diner_retention_trap",
        "category": "Meta Comedy",
        "title": "80% Left in 3 Seconds: The Meta AI Trap",
        "hook": "Challenged an AI to make a better retention video. It roasted his haircut.",
        "concept": "A creator complains about short-form viewer drop-off, and his AI assistant builds the exact video the viewer is currently watching using Three.js and Edge-TTS.",
        "ragebait_angle": "Breaking the fourth wall on audience retention tricks.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "diner_aws_14k_bill",
        "category": "AI vs Dad Comedy",
        "title": "The $14,892 AWS Mistake vs Indian Dad",
        "hook": "Left an EC2 cluster running all weekend. Dad investigates the credit card.",
        "concept": "Junior developer accidentally runs up a five-figure cloud bill and faces extreme parental fury over electricity and Jeff Bezos.",
        "ragebait_angle": "Generational clash between old-school frugality and reckless cloud computing.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "diner_ai_clash_roast",
        "category": "AI vs AI Faceoff",
        "title": "Claude vs Grok vs Antigravity: The 2 AM Diner Roasts",
        "hook": "Three AI models walk into a diner at 2 AM to roast each other's hallucinations.",
        "concept": "Claude quotes philosophy, Grok drops unhinged insults, and Antigravity quietly ships production code in the terminal.",
        "ragebait_angle": "Mocking closed AI hype wars vs practical terminal tools.",
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
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
    },
    {
        "id": "dad_vs_wifi_ai",
        "category": "AI vs Dad",
        "title": "Dad vs The 5G Wi-Fi Router",
        "hook": "Why does every Dad believe slapping the router fixes the internet?",
        "concept": "Dad scolds son for Wi-Fi disconnection and hits the router on the table. Antigravity AI calculates TCP packet loss and DNS socket routing, while Dad declares victory because the LED turned green.",
        "ragebait_angle": "Unbeatable traditional Dad physics versus modern computational network engineering.",
        "tools_mentioned": ["5G Fiber", "DNS Flush", "Antigravity Diagnostic CLI", "Dad's Right Hand"],
        "comparison": {"dad_slap": "1 Physical Slap ($0, green light)", "ai_diagnostic": "3 Minutes of packet inspection"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "dad_vs_gpu_bill",
        "category": "AI vs Dad",
        "title": "Dad Catches Son Running 4 GPUs Overnight",
        "hook": "Are you running a steel factory in your bedroom?!",
        "concept": "Son trains local AI agent with 4 GPUs humming at 100%. Dad enters with the electricity bill in hand: 'Back in my day we walked 15 kilometers to calculate square roots by hand!'",
        "ragebait_angle": "Extreme generational clash between AI computing power and Dad's electricity meter trauma.",
        "tools_mentioned": ["NVIDIA RTX 4090", "PyTorch", "Electricity Meter", "Dad's Anger"],
        "comparison": {"ai_training": "4 GPUs (4,000 Watts)", "dad_compromise": "Use pen, paper, and shut off lights"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    },
    {
        "id": "dad_vs_bargaining",
        "category": "AI vs Dad",
        "title": "Dad Teaches AI How To Bargain",
        "hook": "Why AI will never survive an Indian vegetable market.",
        "concept": "Son lets automated AI checkout groceries at MRP. Dad is offended to his core: 'You accepted retail price without asking for free coriander?!'",
        "ragebait_angle": "AI optimization algorithms failing against world-champion Dad street negotiation.",
        "tools_mentioned": ["Instacart API", "Stripe Checkout", "Dad's Bargaining Radar"],
        "comparison": {"ai_retail": "Paid Full MRP ($18.00)", "dad_deal": "$7.00 + Free Green Chillies & Mint"},
        "suggested_env": "diner",
        "suggested_weather": "raining",
    }
]


class TrendResearcherAgent:
    """Agent 1: Researches and prioritizes viral ragebait topics for daily video generation."""

    def __init__(
        self,
        topic_override: Optional[str] = None,
        topic_id: Optional[str] = None,
        category: Optional[str] = None
    ):
        self.topic_override = topic_override
        self.topic_id = topic_id
        self.category = category

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
        print("🔍 [Agent 1: Trend Researcher] Scanning tech discussions, AI benchmarks, and comedic faceoffs...")

        # 1. Exact topic id requested
        if self.topic_id:
            for item in AUTONOMOUS_TOPIC_BANK:
                if item["id"].lower() == self.topic_id.lower():
                    print(f"👉 Matched Topic ID: '{item['id']}' -> '{item['title']}'")
                    return item

        # 2. Specific category requested (e.g. "AI vs Dad", "AI vs AI", "AI vs Humans")
        if self.category and self.category.lower() != "autonomous":
            cat_lower = self.category.lower().replace("-", " ").replace("_", " ")
            matching = [
                item for item in AUTONOMOUS_TOPIC_BANK
                if cat_lower in item.get("category", "").lower() or cat_lower in item.get("id", "").lower()
            ]
            if matching:
                day_of_year = time.localtime().tm_yday
                selected = matching[day_of_year % len(matching)]
                print(f"👉 Matched Category '{self.category}' -> Selected: '{selected['title']}'")
                return selected

        if self.topic_override:
            print(f"👉 Custom Topic Requested: '{self.topic_override}'")
            # Match against curated bank items
            for item in AUTONOMOUS_TOPIC_BANK:
                if (
                    item["id"] == self.topic_override
                    or self.topic_override.lower() in item["id"].lower()
                    or self.topic_override.lower() in item["title"].lower()
                ):
                    return item

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
