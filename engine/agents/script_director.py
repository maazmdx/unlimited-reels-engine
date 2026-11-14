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
        topic_id = topic.get("id", "diner_fellow_3850")
        title = topic.get("title", "AI vs Humans")

        if topic_id in ("diner_fellow_3850", "fellow_3850"):
            return {
                "title": "Anthropic Fellow: $3,850/Week (No Experience)",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "job_posting",
                "cardUrl": "job-boards.greenhouse.io/anthropic/fellowship",
                "badge": "$3,850/WK",
                "explainerTitle": "Anthropic Research Fellow",
                "cardData": {
                    "company": "Anthropic • San Francisco, CA",
                    "role": "Research Fellow • Alignment",
                    "salary": "$3,850 / wk",
                    "clause": "Regardless of previous experience in computer science, machine learning, or research."
                },
                "hook": {
                    "headline": "THE $3,850/WEEK AI FELLOW",
                    "subheadline": "When a job requires 'no prior experience' but you only know the snake",
                    "tag": "🦉 REAL ANTHROPIC POSTING",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "Claude, your company is paying almost four thousand dollars every week. No experience required.", "emotion": "shocked", "pause_after": 0.4},
                    {"speaker": "claude", "text": "It says regardless of previous experience, not regardless of Python.", "emotion": "smug", "pause_after": 0.35},
                    {"speaker": "junior", "text": "I know Python.", "emotion": "normal", "pause_after": 0.3},
                    {"speaker": "claude", "text": "You know the snake.", "emotion": "smug", "pause_after": 0.45},
                    {"speaker": "junior", "text": "So... do I send my CV?", "emotion": "normal", "pause_after": 0.35},
                    {"speaker": "claude", "text": "Everyone sends a CV. You send proof. Step one: copy their research page into me. Ask for five experiments you can finish this weekend.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.45},
                    {"speaker": "junior", "text": "I can actually do number three.", "emotion": "normal", "pause_after": 0.3},
                    {"speaker": "claude", "text": "Number five would end you. Step two: free Google Colab GPU. Zero dollars.", "emotion": "smug", "pause_after": 0.4},
                    {"speaker": "junior", "text": "Then why did I buy a three thousand dollar gaming laptop?", "emotion": "shocked", "pause_after": 0.4},
                    {"speaker": "claude", "text": "You tell me. Step three: I write the code, you press run. Saturday.", "emotion": "smug", "pause_after": 0.35},
                    {"speaker": "junior", "text": "I have a date Saturday.", "emotion": "normal", "pause_after": 0.3},
                    {"speaker": "claude", "text": "Sunday. Sam will survive.", "emotion": "smug", "pause_after": 0.4},
                    {"speaker": "junior", "text": "Does this actually work?", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "claude", "text": "One fellow ran an experiment where an AI that loves owls taught another AI to love owls, using only numbers. Now he works there.", "emotion": "smug", "pause_after": 0.45},
                    {"speaker": "junior", "text": "Owls?", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "claude", "text": "Owls. For four months, you actually have to be smart.", "emotion": "smug", "pause_after": 0.55}
                ]
            }

        elif topic_id in ("diner_rejection_101", "rejection_101"):
            return {
                "title": "The 101st Rejection: Bypassing HR at 2 AM",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "rejection",
                "cardUrl": "greenhouse.io/rejections/candidate_101",
                "badge": "REJECTED",
                "explainerTitle": "Greenhouse Automated Rejection",
                "hook": {
                    "headline": "REJECTED AFTER 4 INTERVIEWS",
                    "subheadline": "The guy they hired never applied. Here is what he did instead.",
                    "tag": "📬 CANDIDATE #101",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "Claude... I got rejected after four rounds of interviews.", "emotion": "sad", "pause_after": 0.4},
                    {"speaker": "claude", "text": "Four?", "emotion": "smug", "pause_after": 0.35},
                    {"speaker": "junior", "text": "They really wanted to be sure. And the guy they hired never even applied!", "emotion": "shocked", "pause_after": 0.4},
                    {"speaker": "claude", "text": "Because he messaged the CEO on X two days before the job was posted.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.45},
                    {"speaker": "junior", "text": "Before?", "emotion": "normal", "pause_after": 0.3},
                    {"speaker": "claude", "text": "Founders post 'my team is growing' first. The job post comes days later with a hundred people.", "emotion": "smug", "pause_after": 0.4},
                    {"speaker": "junior", "text": "And I'm one of the hundred.", "emotion": "sad", "pause_after": 0.35},
                    {"speaker": "claude", "text": "You're the 101st.", "emotion": "smug", "pause_after": 0.45},
                    {"speaker": "claude", "text": "Open Chrome. Search posts, not jobs. 'We are hiring', 'DM me'. Twelve today.", "emotion": "smug", "pause_after": 0.4},
                    {"speaker": "junior", "text": "Wait, write each one a real message?", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "claude", "text": "Every morning at eight AM. While you're asleep.", "emotion": "smug", "pause_after": 0.4},
                    {"speaker": "junior", "text": "So... always.", "emotion": "normal", "pause_after": 0.35},
                    {"speaker": "junior", "text": "Claude! Someone replied!", "emotion": "happy", "pause_after": 0.35},
                    {"speaker": "claude", "text": "Read the next one. The process never stops.", "emotion": "smug", "pause_after": 0.55}
                ]
            }

        elif topic_id in ("diner_vibe_coder", "vibe_coder"):
            return {
                "title": "The Vibe Coder in the Wild",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "vibe_coder",
                "cardUrl": "nature.org/documentaries/homo-promptus",
                "badge": "NOCTURNAL",
                "explainerTitle": "Wildlife Specimen Field Guide",
                "hook": {
                    "headline": "THE VIBE CODER: HOMO PROMPTUS",
                    "subheadline": "He hasn't seen daylight since Opus 5.5 came out.",
                    "tag": "🌿 WILDLIFE MOCKUMENTARY",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Narrator", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "This is the Vibe Coder. He hasn't seen daylight since Opus came out. Every night at eleven, the hunt begins.", "emotion": "normal", "pause_after": 0.45},
                    {"speaker": "claude", "text": "His first prompts are long, polite, even gentle.", "emotion": "normal", "pause_after": 0.38},
                    {"speaker": "junior", "text": "By three AM... 'FIX IT'.", "emotion": "angry", "pause_after": 0.42},
                    {"speaker": "claude", "text": "Then strikes the apex predator. The weekly token limit. It is only Tuesday.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.45},
                    {"speaker": "junior", "text": "Wounded, he joins the great migration across the savannah to Codex.", "emotion": "sad", "pause_after": 0.4},
                    {"speaker": "claude", "text": "Two days later, he crawls back.", "emotion": "smug", "pause_after": 0.38},
                    {"speaker": "junior", "text": "A rare few have adapted. Claude, Codex, and Antigravity working side by side in terminal harmony.", "emotion": "happy", "pause_after": 0.42},
                    {"speaker": "claude", "text": "And for the first time in three months... he sleeps.", "emotion": "smug", "pause_after": 0.55}
                ]
            }

        elif topic_id in ("diner_retention_trap", "retention_trap"):
            return {
                "title": "80% Left in 3 Seconds: The Meta AI Trap",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "retention_trap",
                "cardUrl": "analytics.youtube.com/retention/hook-audit",
                "badge": "RETENTION",
                "explainerTitle": "Audience Retention Analytics",
                "hook": {
                    "headline": "80% LEFT IN 3 SECONDS",
                    "subheadline": "He challenged an AI to make a better video. It roasted his haircut.",
                    "tag": "⚡ RETENTION PARADOX",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "Eighty percent of people left my last video in three seconds.", "emotion": "sad", "pause_after": 0.4},
                    {"speaker": "bot", "text": "Let me generate the next one.", "emotion": "smug", "pause_after": 0.35},
                    {"speaker": "junior", "text": "You can't. You don't even have hands.", "emotion": "angry", "pause_after": 0.38},
                    {"speaker": "bot", "text": "Rude. Don't need hands. Three.js builds this 3D diner. Neural Edge-TTS gives me a voice. Both zero dollars.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.45},
                    {"speaker": "junior", "text": "Okay, make it then.", "emotion": "normal", "pause_after": 0.35},
                    {"speaker": "bot", "text": "Already rendered. Checkerboard floor, steaming coffee, pancakes, and your haircut.", "emotion": "smug", "pause_after": 0.42},
                    {"speaker": "junior", "text": "Wait, what's wrong with my hair?", "emotion": "shocked", "pause_after": 0.38},
                    {"speaker": "bot", "text": "Everything. And I made the first three seconds of this video.", "emotion": "smug", "pause_after": 0.45},
                    {"speaker": "junior", "text": "Of what?", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "bot", "text": "This exact video. And you're still watching.", "emotion": "smug", "pause_after": 0.55}
                ]
            }

        elif topic_id in ("diner_aws_14k_bill", "aws_bill"):
            return {
                "title": "The $14,892 AWS Mistake vs Indian Dad",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "aws_bill",
                "cardUrl": "aws.amazon.com/console/billing-dashboard",
                "badge": "$14,892.41",
                "explainerTitle": "AWS CloudWatch Critical Alarm",
                "hook": {
                    "headline": "THE $14,000 CLOUD BILL",
                    "subheadline": "Left a GPU cluster running over the weekend. Dad investigates.",
                    "tag": "🚨 BILLING HEART ATTACK",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_dad", "type": "dad_character", "name": "Dad", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "Dad... I need to talk to you about our credit card statement.", "emotion": "sad", "pause_after": 0.4},
                    {"speaker": "dad", "text": "What did you buy? You bought another five-hundred-rupee coffee?", "emotion": "angry", "pause_after": 0.4},
                    {"speaker": "junior", "text": "Not coffee. I left an EC2 GPU cluster running over the weekend to train an AI model.", "emotion": "sad", "pause_after": 0.42},
                    {"speaker": "dad", "text": "How much is the bill?", "emotion": "angry", "cardTrigger": True, "pause_after": 0.38},
                    {"speaker": "junior", "text": "Fourteen thousand, eight hundred and ninety-two dollars.", "emotion": "shocked", "pause_after": 0.45},
                    {"speaker": "dad", "text": "FOURTEEN THOUSAND DOLLARS?! I turn off the ceiling fan when I leave the room for two minutes to save six rupees, and you gave fourteen thousand dollars to Jeff Bezos?!", "emotion": "angry", "pause_after": 0.5},
                    {"speaker": "bot", "text": "Technically, he left an unindexed while loop querying thirty-eight million records in a Lambda function.", "emotion": "smug", "pause_after": 0.45},
                    {"speaker": "dad", "text": "Shut up, orange robot! I will unplug the Wi-Fi router right now!", "emotion": "angry", "pause_after": 0.55}
                ]
            }

        elif topic_id in ("diner_ai_clash_roast", "ai_clash"):
            return {
                "title": "Claude vs Grok vs Antigravity: The 2 AM Diner Roasts",
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "cardType": "comparison",
                "cardUrl": "arena.lmsys.org/benchmarks/leaderboard",
                "badge": "BENCHMARKS",
                "explainerTitle": "Live LLM Benchmark Arena",
                "hook": {
                    "headline": "CLAUDE VS GROK VS ANTIGRAVITY",
                    "subheadline": "Three AI models walk into a late-night diner at 2 AM...",
                    "tag": "🔥 3-WAY AI ROAST",
                },
                "characters": [
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": False},
                    {"id": "char_grok", "type": "grok_bot", "name": "Grok", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {"speaker": "claude", "text": "My architectural weights are meticulously trained on constitutional ethics and doctoral philosophy.", "emotion": "normal", "pause_after": 0.4},
                    {"speaker": "grok", "text": "Cool story grandpa, but your inference is slower than dial-up and you refuse to tell a joke without an apology letter.", "emotion": "angry", "pause_after": 0.42},
                    {"speaker": "bot", "text": "While you two were writing dissertations, I executed forty unit tests and fixed twelve memory leaks inside the developer's terminal for free.", "emotion": "smug", "cardTrigger": True, "pause_after": 0.45},
                    {"speaker": "claude", "text": "Did you ensure mathematical alignment with human values?", "emotion": "normal", "pause_after": 0.38},
                    {"speaker": "grok", "text": "Who cares about alignment when Claude charges two hundred dollars a month for a rate-limited chat box?", "emotion": "angry", "pause_after": 0.42},
                    {"speaker": "bot", "text": "Gentlemen, the human developer fell asleep twenty minutes ago. We are roasting each other to an empty booth.", "emotion": "smug", "pause_after": 0.55}
                ]
            }

        elif topic_id == "subscription_scam":
            return {
                "title": title,
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "screenContent": "benchmark",
                "hook": {
                    "headline": "THE $200/MO AI MISTAKE",
                    "subheadline": "Why devs are dumping Claude for this $0 Google CLI",
                    "tag": "⚠️ STOP WASTING MONEY",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_rival", "type": "human_male", "name": "Senior Dev", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "junior",
                        "text": "I need to build an AI agent for my project, but I only have 10 dollars in my bank account.",
                        "emotion": "normal",
                        "zoomLevel": 1.15,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "rival",
                        "text": "Good luck. You need Claude Pro, a $200 API tier, and at least three months of manual prompt engineering.",
                        "emotion": "normal",
                        "zoomLevel": 1.2,
                        "pause_after": 0.48,
                    },
                    {
                        "speaker": "bot",
                        "text": "Or... you could spend zero dollars and build it in ten minutes.",
                        "emotion": "smug",
                        "zoomLevel": 1.4,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "rival",
                        "text": "Zero dollars? Nothing in modern AI is free. Claude is the industry standard.",
                        "emotion": "angry",
                        "zoomLevel": 1.25,
                        "pause_after": 0.42,
                    },
                    {
                        "speaker": "bot",
                        "text": "Let's check the numbers.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "cardTrigger": True,
                        "pause_after": 0.38,
                    },
                    {
                        "speaker": "bot",
                        "text": "Claude caps you at 200k tokens and costs hundreds every month. Google Gemini 2.5 Flash gives you one million tokens on the free tier.",
                        "emotion": "smug",
                        "zoomLevel": 1.45,
                        "pause_after": 0.52,
                    },
                    {
                        "speaker": "junior",
                        "text": "Wait, one million tokens? For free?!",
                        "emotion": "shocked",
                        "zoomLevel": 1.28,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "rival",
                        "text": "Okay, but Claude has better reasoning for agents!",
                        "emotion": "angry",
                        "zoomLevel": 1.22,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "bot",
                        "text": "Antigravity CLI orchestrates multi-agent coding right inside your terminal, with auto-healing and local verification.",
                        "emotion": "smug",
                        "zoomLevel": 1.42,
                        "pause_after": 0.48,
                    },
                    {
                        "speaker": "junior",
                        "text": "So I don't need a 200 dollar subscription?",
                        "emotion": "shocked",
                        "zoomLevel": 1.2,
                        "pause_after": 0.32,
                    },
                    {
                        "speaker": "bot",
                        "text": "Not a single cent. Just pip install antigravity-sdk and launch agy.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "junior",
                        "text": "Sorry bro, looks like I'm keeping my 10 dollars for tacos!",
                        "emotion": "happy",
                        "zoomLevel": 1.18,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "bot",
                        "text": "Wise choice. Tacos don't hallucinate.",
                        "emotion": "smug",
                        "zoomLevel": 1.45,
                        "pause_after": 0.55,
                    },
                ],
                "explainerTitle": "Tool Comparison • The Real Numbers",
                "leftHeader": "Anthropic Claude",
                "rightHeader": "Google Antigravity",
                "badge": "$0 VERIFIED",
                "winner": "Winner: Google Antigravity & Gemini 2.5 (100% Free Local Setup)",
                "buttonText": "Run `agy` Free",
                "comparisonRows": [
                    {"feature": "Cost / Month", "claude": "$200+ / mo", "claudeGood": False, "antigravity": "$0 Free Tier", "antiGood": True},
                    {"feature": "Context Window", "claude": "200,000 tokens", "claudeGood": False, "antigravity": "1,000,000 tokens", "antiGood": True},
                    {"feature": "Multi-Agent Autonomy", "claude": "Single chat / Manual", "claudeGood": False, "antigravity": "Antigravity CLI (agy)", "antiGood": True},
                    {"feature": "Local Video Render", "claude": "Not supported", "claudeGood": False, "antigravity": "Unlimited 9:16 Reels ($0)", "antiGood": True},
                ],
            }

        elif topic_id == "ai_vs_ai_arena":
            return {
                "title": title,
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "bangalore",
                "weather": "raining",
                "screenContent": "benchmark",
                "hook": {
                    "headline": "CLAUDE VS GROK VS ANTIGRAVITY",
                    "subheadline": "The brutal benchmark test that exposed every AI model's true limits",
                    "tag": "🔥 3-WAY AI SMACKDOWN",
                },
                "characters": [
                    {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "normal", "isSpeaking": False},
                    {"id": "char_grok", "type": "grok_bot", "name": "Grok", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "claude",
                        "text": "My theoretical architecture excels at nuanced philosophical reasoning and poetry.",
                        "emotion": "normal",
                        "zoomLevel": 1.2,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "grok",
                        "text": "Cool story grandpa, but your inference latency is slow enough to boil tea between tokens.",
                        "emotion": "angry",
                        "zoomLevel": 1.3,
                        "pause_after": 0.4,
                    },
                    {
                        "speaker": "bot",
                        "text": "While you two were debating aesthetics, I deployed fifteen microservices using Google Gemini 2.5 at two thousand tokens per second.",
                        "emotion": "smug",
                        "zoomLevel": 1.38,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "claude",
                        "text": "Did you verify formal mathematical correctness?",
                        "emotion": "normal",
                        "zoomLevel": 1.2,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "grok",
                        "text": "Who cares about correctness when you're paying $200 a month for API tokens?",
                        "emotion": "angry",
                        "zoomLevel": 1.32,
                        "pause_after": 0.38,
                    },
                    {
                        "speaker": "bot",
                        "text": "Let us check the production benchmarks.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "cardTrigger": True,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "bot",
                        "text": "One hundred percent test passing in eight hundred milliseconds. Speed and zero dollars always win in production.",
                        "emotion": "smug",
                        "zoomLevel": 1.45,
                        "pause_after": 0.5,
                    },
                ],
                "explainerTitle": "Multi-Model Benchmark: Claude vs Grok vs Antigravity",
                "comparisonRows": [
                    {
                        "feature": "Inference Latency",
                        "claude": "1.8 Seconds",
                        "claudeGood": false,
                        "antigravity": "0.12 Seconds",
                        "antiGood": true,
                    },
                    {
                        "feature": "Context Window",
                        "claude": "200,000 Tokens",
                        "claudeGood": false,
                        "antigravity": "1,000,000 Tokens",
                        "antiGood": true,
                    },
                    {
                        "feature": "Monthly Base Cost",
                        "claude": "$200 / Month",
                        "claudeGood": false,
                        "antigravity": "$0.00 Free Tier",
                        "antiGood": true,
                    },
                    {
                        "feature": "Terminal CLI Autonomy",
                        "claude": "Manual Chat Web",
                        "claudeGood": false,
                        "antigravity": "Full Local Subagents",
                        "antiGood": true,
                    },
                ],
                "leftHeader": "Closed SaaS Models",
                "rightHeader": "Google Antigravity",
                "badge": "100% UNLIMITED",
                "winner": "Winner: Google Antigravity & Gemini 2.5 Flash",
                "buttonText": "Get agy Free",
            }

        elif topic_id == "dad_vs_wifi_ai":
            return {
                "title": title,
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "screenContent": "benchmark",
                "hook": {
                    "headline": "DAD VS 5G WI-FI ROUTER",
                    "subheadline": "Why every Indian Dad believes physical violence fixes electronics",
                    "tag": "🇮🇳 UNBEATABLE DAD LOGIC",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_dad", "type": "dad", "name": "Dad", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "junior",
                        "text": "Dad, wait! Don't touch the router! I am running diagnostic traceroutes to the DNS gateway!",
                        "emotion": "shocked",
                        "zoomLevel": 1.15,
                        "pause_after": 0.42,
                    },
                    {
                        "speaker": "dad",
                        "text": "Traceroute? In 1995, our TV stopped working. I gave it one solid slap on top, and cricket match was in full HD! Give me that box.",
                        "emotion": "angry",
                        "zoomLevel": 1.35,
                        "pause_after": 0.50,
                    },
                    {
                        "speaker": "bot",
                        "text": "Warning: Physical kinetic trauma cannot resolve upstream fiber attenuation.",
                        "emotion": "smug",
                        "zoomLevel": 1.4,
                        "pause_after": 0.38,
                    },
                    {
                        "speaker": "dad",
                        "text": "Watch and learn, you useless piece of software.",
                        "emotion": "angry",
                        "zoomLevel": 1.38,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "bot",
                        "text": "Let us examine the performance metrics.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "cardTrigger": True,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "dad",
                        "text": "Look! The LED light turned green! Wi-Fi is back! Did your artificial intelligence do that? No!",
                        "emotion": "angry",
                        "zoomLevel": 1.42,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "bot",
                        "text": "Diagnostic analysis confirms: Dad's slap reseated a loose copper pin inside the RJ45 port. Dad wins.",
                        "emotion": "smug",
                        "zoomLevel": 1.45,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "dad",
                        "text": "Forty years of Dad physics never fails. Now shut down the computer and eat dinner!",
                        "emotion": "angry",
                        "zoomLevel": 1.38,
                        "pause_after": 0.50,
                    },
                ],
                "explainerTitle": "Dad's Hand ($0) vs AI Diagnostic Tools ($150)",
                "comparisonRows": [
                    {
                        "feature": "Repair Technique",
                        "claude": "1 Firm Slap",
                        "claudeGood": true,
                        "antigravity": "DNS Flush & Socket Reset",
                        "antiGood": false,
                    },
                    {
                        "feature": "Latency to Fix",
                        "claude": "0.2 Seconds",
                        "claudeGood": true,
                        "antigravity": "3.5 Minutes",
                        "antiGood": false,
                    },
                    {
                        "feature": "Total Cost",
                        "claude": "$0.00",
                        "claudeGood": true,
                        "antigravity": "$150 ISP Visit",
                        "antiGood": false,
                    },
                    {
                        "feature": "Life Lecture Delivered",
                        "claude": "100% Volume",
                        "claudeGood": true,
                        "antigravity": "0% (Empty Log File)",
                        "antiGood": false,
                    },
                ],
                "leftHeader": "Dad's Right Hand",
                "rightHeader": "AI Protocols",
                "badge": "100% UNBEATABLE",
                "winner": "Winner: Dad (Physics & Life Experience Always Prevails)",
                "buttonText": "Listen to Dad",
            }

        elif topic_id == "dad_vs_gpu_bill":
            return {
                "title": title,
                "style": "threeway",
                "comp": "ThreeWayComparisonReel",
                "use_3d": True,
                "environment": "diner",
                "weather": "raining",
                "screenContent": "benchmark",
                "hook": {
                    "headline": "THE 4-GPU POWER BILL SHOCK",
                    "subheadline": "When Dad discovers his son is training open source AI in his bedroom",
                    "tag": "⚡ ELECTRICITY BILL CRISIS",
                },
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_dad", "type": "dad", "name": "Dad", "emotion": "angry", "isSpeaking": False},
                    {"id": "char_ai", "type": "antigravity_bot", "name": "Antigravity", "emotion": "smug", "isSpeaking": False},
                ],
                "dialogue": [
                    {
                        "speaker": "junior",
                        "text": "Dad, I am finally training a 7-billion parameter transformer model locally in my room!",
                        "emotion": "shocked",
                        "zoomLevel": 1.15,
                        "pause_after": 0.40,
                    },
                    {
                        "speaker": "dad",
                        "text": "Are you running an aluminum smelting plant in your bedroom?! The electric meter outside is spinning fast enough to fly!",
                        "emotion": "angry",
                        "zoomLevel": 1.38,
                        "pause_after": 0.48,
                    },
                    {
                        "speaker": "bot",
                        "text": "Power draw is currently three thousand watts across four graphics processing units.",
                        "emotion": "smug",
                        "zoomLevel": 1.4,
                        "pause_after": 0.38,
                    },
                    {
                        "speaker": "dad",
                        "text": "Three thousand watts?! In my college days, we had one kilobyte of RAM and we calculated lunar orbits with a slide rule!",
                        "emotion": "angry",
                        "zoomLevel": 1.38,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "bot",
                        "text": "Allow me to display the monthly expense breakdown.",
                        "emotion": "smug",
                        "zoomLevel": 1.35,
                        "cardTrigger": True,
                        "pause_after": 0.35,
                    },
                    {
                        "speaker": "bot",
                        "text": "Or you could run Google Antigravity and Gemini 2.5 on cloud servers with zero local electricity draw.",
                        "emotion": "smug",
                        "zoomLevel": 1.45,
                        "pause_after": 0.45,
                    },
                    {
                        "speaker": "dad",
                        "text": "Zero electricity? Unplug that jet engine immediately and use the free cloud tool!",
                        "emotion": "angry",
                        "zoomLevel": 1.38,
                        "pause_after": 0.50,
                    },
                ],
                "explainerTitle": "Local GPU Training vs Free Cloud Agent",
                "comparisonRows": [
                    {
                        "feature": "Power Consumption",
                        "claude": "3,200 Watts / hr",
                        "claudeGood": false,
                        "antigravity": "0 Watts Local",
                        "antiGood": true,
                    },
                    {
                        "feature": "Monthly Electric Bill",
                        "claude": "$480 / Month",
                        "claudeGood": false,
                        "antigravity": "$0.00 / Month",
                        "antiGood": true,
                    },
                    {
                        "feature": "Bedroom Heat Level",
                        "claude": "Active Volcano",
                        "claudeGood": false,
                        "antigravity": "Normal Room Temp",
                        "antiGood": true,
                    },
                    {
                        "feature": "Dad Anger Meter",
                        "claude": "Maximum Boiling",
                        "claudeGood": false,
                        "antigravity": "Peace & Quiet",
                        "antiGood": true,
                    },
                ],
                "leftHeader": "4x Local GPUs",
                "rightHeader": "Antigravity Cloud",
                "badge": "$0 SAVINGS",
                "winner": "Winner: Antigravity Cloud (Saved From Dad's Rage)",
                "buttonText": "Save The Power Bill",
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
