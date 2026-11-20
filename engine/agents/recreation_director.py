"""
Agent: Viral AI Recreation & Remix Director
Transforms an ingested social reel's viral anatomy into our signature Remotion animated
visual engine, with slightly remixed narrative twists, fresh punchlines, our character rosters,
and our neural Edge-TTS voice synthesis.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from google import genai
except ImportError:
    genai = None


class RecreationDirectorAgent:
    """Agent that recreates and remixes social media reels with custom animations and voices."""

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.client = None
        if genai and os.environ.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client()
            except Exception as e:
                print(f"⚠️ Gemini Client init notice in Recreation Director: {e}")

    def recreate_reel(
        self,
        source_analysis: Dict[str, Any],
        target_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recreates and remixes the source video into our Remotion screenplay.
        Preserves viral retention psychology while changing specific jokes, characters, and visuals.
        """
        print(f"🎨 [Recreation Director] Remixing reel: '{source_analysis.get('hook', 'Trending Topic')}'...")

        format_type = source_analysis.get("format_type", "ai_vs_dev")
        if target_style:
            chosen_style = target_style
        elif "dad" in format_type or "dad" in str(source_analysis).lower():
            chosen_style = "ai_vs_dad"
        elif "arena" in format_type or "claude vs" in str(source_analysis).lower():
            chosen_style = "ai_arena"
        elif "anime" in format_type:
            chosen_style = "anime"
        else:
            chosen_style = "diner_ai"

        if self.client:
            try:
                return self._generate_screenplay_with_gemini(source_analysis, chosen_style)
            except Exception as e:
                print(f"⚠️ Gemini screenplay generation error: {e}. Using curated remix engine.")

        return self._curated_remix_fallback(source_analysis, chosen_style)

    def _generate_screenplay_with_gemini(
        self,
        analysis: Dict[str, Any],
        chosen_style: str
    ) -> Dict[str, Any]:
        """Uses Gemini to remix and rewrite the script with slightly changed details and our animations."""
        system_instruction = (
            "You are the Lead Screenwriter & Creative Director for an automated short-form viral video channel. "
            "Your motto: Take an inspiration video, analyze why it went viral, and RECREATE IT IN ANOTHER MANNER "
            "with slightly changed phrasing, fresh comedic twists, relatable developer culture, and our character roster.\n\n"
            "Style options:\n"
            "1. 'diner_ai': Junior Dev and Claude/Gemini in a rainy 3D cyberpunk diner. A floating macOS browser card pops up with evidence (job salary, rejection letter, or code diff).\n"
            "2. 'ai_vs_dad': Son running high-tech AI workflows vs Indian Dad with traditional wisdom, electricity meter trauma, or router-slapping physics.\n"
            "3. 'ai_arena': Claude vs Gemini vs Grok in a fast-paced benchmark roast battle.\n"
            "4. 'anime': Shonen anime aesthetic, speedlines, Gojo Infinity math, or biological power-up science.\n\n"
            "STRICT RULES:\n"
            "- Do NOT copy verbatim. Change the scenario slightly so it's fresh and original.\n"
            "- STRICT DURATION TARGET: Total dialogue turns must be between 6 and 8 snappy lines (target duration: 18 to 28 seconds). Short, fast-paced videos achieve 3x higher completion rate on Instagram Reels algorithms and render in under 90 seconds.\n"
            "- Opening Hook (first turn) must be an instant 0-3s pattern interrupt with high curiosity or shock.\n"
            "- Character IDs must be chosen from: 'junior', 'claude', 'gemini', 'antigravity_bot', 'grok', 'dad'.\n"
            "- Emotion must be one of: 'normal', 'smug', 'shocked', 'angry', 'happy', 'sad'.\n"
            "- At least one turn must have 'cardTrigger': true where the floating glass card reveals the proof.\n"
            "- Return strictly a valid JSON object matching the requested schema."
        )

        prompt = f"""
Source Video Analysis:
- Original Hook: {analysis.get('hook')}
- Core Topic: {analysis.get('core_topic')}
- Core Conflict: {analysis.get('core_conflict')}
- Summary: {analysis.get('transcript_summary')}
- Original Punchline: {analysis.get('punchline')}
- Chosen Style: {chosen_style}

Produce a complete Remotion screenplay JSON with:
{{
  "title": "Short punchy title (max 50 chars)",
  "style": "diner",
  "comp": "MasterAutonomousReel",
  "use_3d": false,
  "environment": "diner",
  "weather": "raining",
  "cardType": "job_posting",
  "cardUrl": "short url for the card",
  "badge": "Short badge text (e.g. '$3,850/WK' or 'REJECTED' or '$14,000 BILL')",
  "explainerTitle": "Title on top of the card",
  "cardData": {{
    "line1": "Key metric or clause",
    "line2": "Secondary detail",
    "line3": "Roast detail"
  }},
  "hook": {{
    "headline": "ALL-CAPS 3-5 WORD HEADLINE",
    "subheadline": "One punchy subtitle sentence",
    "tag": "⚠️ SHORT VIRAL TAG"
  }},
  "winner": "Winner statement at the end",
  "buttonText": "Call to action button text",
  "characters": [
    {{"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": false}},
    {{"id": "char_ai", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": false}}
  ],
  "dialogue": [
    {{"speaker": "junior", "text": "First line of speech...", "emotion": "shocked", "pause_after": 0.35}},
    {{"speaker": "claude", "text": "Second snappy response...", "emotion": "smug", "pause_after": 0.40, "cardTrigger": true}}
  ]
}}
Return ONLY valid JSON.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=dict(system_instruction=system_instruction)
        )

        raw_text = response.text.strip().strip("`").replace("json\n", "", 1)
        screenplay = json.loads(raw_text)
        print(f"✅ [Recreation Director] Successfully remixed into: '{screenplay.get('title')}'")
        return screenplay

    def _curated_remix_fallback(
        self,
        analysis: Dict[str, Any],
        chosen_style: str
    ) -> Dict[str, Any]:
        """High-performing hand-crafted fallback matrix if API is unreachable."""
        if chosen_style == "ai_vs_dad":
            return {
                "title": "Dad vs The 5G Wi-Fi Router",
                "style": "diner",
                "comp": "MasterAutonomousReel",
                "use_3d": False,
                "environment": "diner",
                "weather": "raining",
                "cardType": "code",
                "cardUrl": "router.local/admin/diagnostics",
                "badge": "0 PACKETS LOST",
                "explainerTitle": "Indian Dad Physics vs 5G Fiber Routing",
                "cardData": {
                    "ping": "1.2 ms (Fiber)",
                    "action": "Dad Slap to Router Antenna",
                    "result": "Green LED Restored"
                },
                "hook": {
                    "headline": "DAD VS THE 5G ROUTER",
                    "subheadline": "Why every dad believes hitting the electronics solves networking",
                    "tag": "⚡ UNBEATABLE DAD PHYSICS"
                },
                "winner": "Winner: Dad's Right Hand ($0, Instant Fix)",
                "buttonText": "Check DNS Settings",
                "characters": [
                    {"id": "char_junior", "type": "human_male", "name": "Son", "emotion": "shocked", "isSpeaking": False},
                    {"id": "char_dad", "type": "dad", "name": "Dad", "emotion": "angry", "isSpeaking": False}
                ],
                "dialogue": [
                    {"speaker": "junior", "text": "Dad, wait! Don't touch the router, I'm debugging the socket DNS cache!", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "dad", "text": "Socket DNS? In my day we hit the television twice and Mahabharata came in HD color!", "emotion": "angry", "pause_after": 0.45},
                    {"speaker": "junior", "text": "It is fiber optic cable, physical trauma doesn't re-align laser photons!", "emotion": "shocked", "cardTrigger": True, "pause_after": 0.38},
                    {"speaker": "dad", "text": "Watch and learn.", "emotion": "smug", "pause_after": 0.40},
                    {"speaker": "junior", "text": "Wait... did the internet light just turn green?", "emotion": "shocked", "pause_after": 0.35},
                    {"speaker": "dad", "text": "Thirty years of Indian engineering beats your artificial intelligence every day of the week.", "emotion": "smug", "pause_after": 0.50}
                ]
            }

        # Default AI vs Dev Satire
        return {
            "title": "Anthropic Fellow: $3,850/Week (Remixed)",
            "style": "diner",
            "comp": "MasterAutonomousReel",
            "use_3d": False,
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
                "clause": "Regardless of previous experience in CS or ML."
            },
            "hook": {
                "headline": "THE $3,850/WEEK AI FELLOW",
                "subheadline": "When a job says 'no experience required' but you only know Python",
                "tag": "🦉 100% REAL POSTING"
            },
            "winner": "Winner: Google Antigravity & Free Colab GPUs ($0 Setup)",
            "buttonText": "Start Free Experiment",
            "characters": [
                {"id": "char_junior", "type": "human_male", "name": "Junior Dev", "emotion": "shocked", "isSpeaking": False},
                {"id": "char_claude", "type": "claude_bot", "name": "Claude", "emotion": "smug", "isSpeaking": False}
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
                {"speaker": "junior", "text": "Does this actually work?", "emotion": "shocked", "pause_after": 0.35},
                {"speaker": "claude", "text": "One fellow ran an experiment where an AI that loves owls taught another AI to love owls. Now he works there.", "emotion": "smug", "pause_after": 0.55}
            ]
        }


if __name__ == "__main__":
    recreator = RecreationDirectorAgent()
    screenplay = recreator.recreate_reel({
        "hook": "Why you should never pay for AI wrappers in 2026",
        "core_topic": "Free vs Paid AI Tools",
        "format_type": "ai_vs_dev",
        "transcript_summary": "Devs spend $200 a month on closed AI tools when open-source alternatives are free.",
        "punchline": "Stop donating to wrapper founders."
    })
    print("Recreation Title:", screenplay.get("title"))
    print("Dialogue Count:", len(screenplay.get("dialogue", [])))
