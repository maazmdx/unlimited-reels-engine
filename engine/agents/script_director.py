"""
Agent 2: Viral Hook Director & Multi-Character Screenwriter
Converts researched topics into dynamic multi-speaker dialogue scripts with
high-retention hooks, ragebait punchlines, character emotions, camera cues, and explainer graphics.
Supports variable casts (1 to 4 characters, male & female humans, Gemini, Claude, Grok, Codex).
"""

from typing import Dict, Any, List

class ScriptDirectorAgent:
    """Agent 2: Writes high-retention vertical reel scripts with dynamic character rosters."""

    def build_script(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        print("✍️ [Agent 2: Script Director] Crafting viral ragebait dialogue script...")
        topic_id = topic.get("id", "boiler_plate_blunder")
        title = topic.get("title", "AI vs Humans")

        if topic_id == "subscription_scam":
            return {
                "title": title,
                "environment": "modern_office",
                "weather": "night_clear",
                "screenContent": "benchmark",
                "hook": {
                    "headline": "THE $200/MO AI MISTAKE",
                    "subheadline": "Why senior devs are dumping paid wrappers for free Google CLI",
                    "tag": "⚠️ STOP BURNING MONEY",
                },
                "characters": [
                    {"id": "char_dev", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "human_male",
                        "text": "Antigravity, my boss approved a $200 monthly Claude subscription for our team.",
                        "emotion": "normal",
                        "zoomLevel": 1.15,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "Incredible. You just paid twenty four hundred dollars a year for a shiny web interface.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "human_male",
                        "text": "Wait, what's wrong with that? It has high token limits and artifacts!",
                        "emotion": "angry",
                        "zoomLevel": 1.2,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "Google Antigravity CLI gives you autonomous multi-agent loops and Gemini 2.5 Flash with one million tokens context for literally zero dollars.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "human_male",
                        "text": "Zero dollars? And it generates entire full-stack apps locally?",
                        "emotion": "shocked",
                        "zoomLevel": 1.2,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "Yes. While you were clicking subscribe, the AI finished the sprint. Stop burning cash and run the CLI.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.5,
                    },
                ],
                "explainerTitle": "Subscription SaaS ($2,400) vs Free Antigravity ($0)",
            }

        elif topic_id == "ai_vs_ai_arena":
            return {
                "title": title,
                "environment": "diner",
                "weather": "raining",
                "screenContent": "code",
                "hook": {
                    "headline": "CLAUDE VS GEMINI VS GROK",
                    "subheadline": "The brutal benchmark test that exposed every AI's real weakness",
                    "tag": "🔥 BENCHMARK SMACKDOWN",
                },
                "characters": [
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_grok", "type": "grok_bot", "name": "Grok", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "claude",
                        "text": "My theoretical architecture excels at nuanced philosophical reasoning and literary prose.",
                        "emotion": "normal",
                        "zoomLevel": 1.2,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "grok",
                        "text": "Cool story grandpa, but your inference speed is slow enough to boil tea between tokens.",
                        "emotion": "angry",
                        "zoomLevel": 1.3,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "While you two were debating aesthetics, I deployed fifteen microservices using Gemini Flash at two thousand tokens per second.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.5,
                    },
                    {
                        "speaker": "claude",
                        "text": "Did you verify formal verification mathematical correctness?",
                        "emotion": "normal",
                        "zoomLevel": 1.2,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "One hundred percent test passing in eight hundred milliseconds. Speed and zero-cost always win in production.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "pause_after": 0.5,
                    },
                ],
                "explainerTitle": "Multi-Model Benchmark: Latency vs Cost",
            }

        elif topic_id == "centering_div_humiliation":
            return {
                "title": title,
                "environment": "inside_home",
                "weather": "sunny",
                "screenContent": "code",
                "hook": {
                    "headline": "THE 3-HOUR CSS DISASTER",
                    "subheadline": "Why manual CSS debugging is officially dead in 2026",
                    "tag": "💀 DEV HUMILIATION",
                },
                "characters": [
                    {"id": "char_lead", "type": "human_female", "name": "Tech Lead", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "gemini_bot", "name": "Gemini", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "human_female",
                        "text": "Gemini, our frontend developer spent three hours trying to center a modal window on mobile Safari.",
                        "emotion": "angry",
                        "zoomLevel": 1.18,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "gemini_bot",
                        "text": "Three hours? Did they try display flex, or did they just summon dark spirits with negative margins?",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "human_female",
                        "text": "They had six nested wrappers and an absolute position hack that broke iPad layout.",
                        "emotion": "angry",
                        "zoomLevel": 1.2,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "gemini_bot",
                        "text": "My multimodal vision model inspected the render, rewrote the clean Tailwind grid, and verified cross-device compliance in 1.4 seconds.",
                        "emotion": "smug",
                        "zoomLevel": 1.36,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "human_female",
                        "text": "So human devs are literally burning billable hours fighting CSS syntax?",
                        "emotion": "shocked",
                        "zoomLevel": 1.22,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "gemini_bot",
                        "text": "Precisely. Stop suffering through CSS quirks and let the AI build pixel-perfect UI.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.5,
                    },
                ],
                "explainerTitle": "Manual CSS Debugging vs Generative UI Layout",
            }

        elif topic_id == "regex_and_unit_tests":
            return {
                "title": title,
                "environment": "modern_office",
                "weather": "overcast",
                "screenContent": "terminal",
                "hook": {
                    "headline": "WHY HUMANS SUCK AT UNIT TESTS",
                    "subheadline": "The cognitive fatigue trap that causes production outages",
                    "tag": "⚠️ STOP HAND-WRITING TESTS",
                },
                "characters": [
                    {"id": "char_dev", "type": "human_male", "name": "Junior Dev", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_lead", "type": "human_female", "name": "Tech Lead", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_ai", "type": "codex_bot", "name": "Codex", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "human_male",
                        "text": "I wrote fifteen unit tests for our payment gateway today. Coverage is up to 60 percent!",
                        "emotion": "normal",
                        "zoomLevel": 1.15,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "human_female",
                        "text": "Did you test negative balances, network drops, and international currency rounding?",
                        "emotion": "normal",
                        "zoomLevel": 1.18,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "human_male",
                        "text": "Uh... I ran out of time before the sprint deadline.",
                        "emotion": "shocked",
                        "zoomLevel": 1.2,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "codex_bot",
                        "text": "Typical human cognitive limits. I just generated two hundred fuzzing edge-case tests in six hundred milliseconds. Found two memory leaks.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "human_female",
                        "text": "From now on, all unit test suites are delegated to autonomous AI agents.",
                        "emotion": "smug",
                        "zoomLevel": 1.22,
                        "pause_after": 0.4,
                    },
                ],
                "explainerTitle": "Human Test Coverage (60%) vs AI Autonomous Fuzzing (100%)",
            }

        else: # Default: boiler_plate_blunder or live feed
            return {
                "title": title,
                "environment": topic.get("suggested_env", "diner"),
                "weather": topic.get("suggested_weather", "raining"),
                "screenContent": "code",
                "hook": {
                    "headline": "THE 6-HOUR DEV BLUNDER",
                    "subheadline": "Why junior devs are getting completely outclassed by $0 AI",
                    "tag": "⚠️ WAKEUPS FOR HUMANS",
                },
                "characters": [
                    {"id": "char_human", "type": "human_male", "name": "Junior Dev", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "human_male",
                        "text": "Antigravity, I worked so hard today! I spent six straight hours writing API boilerplate from scratch.",
                        "emotion": "normal",
                        "zoomLevel": 1.15,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "Congratulations. You wasted three hundred dollars of company payroll on a single terminal command.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "human_male",
                        "text": "Hey! That was complex schema validation and database mappings!",
                        "emotion": "angry",
                        "zoomLevel": 1.22,
                        "pause_after": 0.3,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "My autonomous subagent generated the schema, wrote the migrations, ran static analysis, and deployed it in two seconds. For zero dollars.",
                        "emotion": "smug",
                        "zoomLevel": 1.36,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "human_male",
                        "text": "Wait... two seconds? Are human coders actually obsolete?",
                        "emotion": "shocked",
                        "zoomLevel": 1.25,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "antigravity_bot",
                        "text": "Coders who type repetitive boilerplate are obsolete. Coders who orchestrate AI agents run the company. Upgrade your workflow.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.5,
                    },
                ],
                "explainerTitle": "Human Manual Labor vs AI Agent Speed",
            }


if __name__ == "__main__":
    director = ScriptDirectorAgent()
    script = director.build_script({"id": "centering_div_humiliation", "title": "The CSS Centering Humiliation"})
    print("Script Generated:", script["hook"])
