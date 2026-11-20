"""
Antigravity Unlimited Video Engine - Content & Script Generator
100% Free, Infinite Reels & Shorts Script Generation for Anime, Educational & Humorous content.
Supports: English, Hindi (हिंदी), Kannada (ಕನ್ನಡ).
"""

import os
import re
import json
import random
from typing import Dict, Any, Optional, List


# Curated high-retention viral script templates across niches and languages
VIRAL_PRESETS: Dict[str, Dict[str, Any]] = {
    # ==========================================
    # ANIME + EDUCATIONAL / SMART FUSION
    # ==========================================
    "anime_gojo_infinity_en": {
        "title": "Gojo's Infinity Explained by Real Math",
        "style": "anime",
        "language": "en",
        "category": "Anime Science",
        "voice": "en-US-AndrewMultilingualNeural",
        "script": (
            "How does Satoru Gojo's Infinity actually work in Jujutsu Kaisen? "
            "Author Gege Akutami based it on a real mathematical paradox called Zeno's Dichotomy! "
            "Between an enemy's punch and Gojo, there are infinite half-distances. "
            "The punch travels half the distance, then half of what remains, infinitely. "
            "In calculus, as distance approaches zero, it never touches. "
            "Gojo is literally using infinite calculus as physical armor!"
        ),
        "scenes": [
            {
                "title": "Zeno's Dichotomy",
                "tag": "LIMITLESS MATH",
                "text": "How does Gojo's Infinity stop any attack? Gege Akutami used real mathematical calculus.",
                "visual": "infinity_barrier"
            },
            {
                "title": "Infinite Halves",
                "tag": "CALCULUS LIMITS",
                "text": "Every microsecond, the space between the enemy punch and Gojo divides by half infinitely.",
                "visual": "manga_calculus"
            },
            {
                "title": "Unbreakable Armor",
                "tag": "MATH IS SUPERPOWER",
                "text": "The limit as distance approaches zero never equals zero. Real math is the ultimate flex!",
                "visual": "gojo_eyes"
            }
        ]
    },

    "anime_gojo_infinity_hi": {
        "title": "गोझो का इनफिनिटी और कैलकुलस का नियम",
        "style": "anime",
        "language": "hi",
        "category": "Anime Science Hindi",
        "voice": "hi-IN-MadhurNeural",
        "script": (
            "क्या आपको पता है कि जुजुत्सु कैसेन में गोजो का इनफिनिटी असल में एक असली गणित का नियम है? "
            "इसे विज्ञान में ज़ेनो का डायकोटोमी विरोधाभास कहते हैं! "
            "जब कोई मुक्का गोजो की तरफ आता है, तो बीच की दूरी लगातार आधी, फिर आधी, फिर आधी होती जाती है। "
            "कैलकुलस के नियम के अनुसार, मुक्का पास तो आता है लेकिन कभी छू नहीं पाता! "
            "गोजो असल में अनंत गणित को अपनी ढाल बनाकर घूम रहा है!"
        ),
        "scenes": [
            {
                "title": "ज़ेनो का विरोधाभास",
                "tag": "गोजो का रहस्य",
                "text": "गोजो का इनफिनिटी कोई जादू नहीं, बल्कि कैलकुलस का असली गणितीय नियम है!",
                "visual": "infinity_barrier"
            },
            {
                "title": "अनंत दूरियां",
                "tag": "कैलकुलस लिमिट",
                "text": "मुक्का हर पल आधी दूरी तय करता है, जो कभी खत्म नहीं होती!",
                "visual": "manga_calculus"
            },
            {
                "title": "गणित की सुपरपावर",
                "tag": "फॉलो करें",
                "text": "कैलकुलस इतना ताकतवर है कि दुनिया का सबसे मजबूत हमला भी रोक दे!",
                "visual": "gojo_eyes"
            }
        ]
    },

    "anime_gojo_infinity_kn": {
        "title": "ಗೋಜೋ ಅವರ ಇನ್ಫಿನಿಟಿ ಮತ್ತು ನೈಜ ಕ್ಯಾಲ್ಕುಲಸ್ ವಿಜ್ಞಾನ",
        "style": "anime",
        "language": "kn",
        "category": "Anime Science Kannada",
        "voice": "kn-IN-GaganNeural",
        "script": (
            "ಜುಜುತ್ಸು ಕೈಸೆನ್‌ನಲ್ಲಿ ಗೋಜೋ ಅವರ ಇನ್ಫಿನಿಟಿ ಶಕ್ತಿ ವಾಸ್ತವವಾಗಿ ಒಂದು ನೈಜ ಗಣಿತದ ನಿಯಮ ಎಂದು ನಿಮಗೆ ತಿಳಿದಿದೆಯೇ? "
            "ಇದನ್ನು ಗಣಿತದಲ್ಲಿ ಝೀನೋಸ್ ಪ್ಯಾರಾಡಾಕ್ಸ್ ಎನ್ನಲಾಗುತ್ತದೆ! "
            "ಯಾವುದೇ ಶತ್ರುವಿನ ಹೊಡೆತ ಗೋಜೋ ಅವರನ್ನು ಮುಟ್ಟಲು ಬಂದಾಗ, ಅವುಗಳ ನಡುವಿನ ಅಂತರ ನಿರಂತರವಾಗಿ ಅರ್ಧವಾಗುತ್ತಾ ಹೋಗುತ್ತದೆ. "
            "ಕ್ಯಾಲ್ಕುಲಸ್ ನಿಯಮದ ಪ್ರಕಾರ ಆ ಅಂತರ ಎಂದಿಗೂ ಶೂನ್ಯವಾಗುವುದಿಲ್ಲ! "
            "ಗೋಜೋ ವಾಸ್ತವವಾಗಿ ಗಣಿತದ ಅನಂತ ಮಿತಿಯನ್ನೇ ತನ್ನ ರಕ್ಷಣಾ ಕವಚವನ್ನಾಗಿ ಮಾಡಿಕೊಂಡಿದ್ದಾರೆ!"
        ),
        "scenes": [
            {
                "title": "ಝೀನೋಸ್ ನಿಯಮ",
                "tag": "ಗೋಜೋ ಇನ್ಫಿನಿಟಿ",
                "text": "ಗೋಜೋ ಅವರ ಶಕ್ತಿ ಕೇವಲ ಕಲ್ಪನೆಯಲ್ಲ, ನೈಜ ಗಣಿತದ ಅದ್ಭುತ ನಿಯಮ!",
                "visual": "infinity_barrier"
            },
            {
                "title": "ಅನಂತ ಅಂತರ",
                "tag": "ಕ್ಯಾಲ್ಕುಲಸ್",
                "text": "ಶತ್ರುವಿನ ಮುಷ್ಟಿ ಮತ್ತು ಗೋಜೋ ನಡುವಿನ ಅಂತರ ನಿರಂತರವಾಗಿ ಅರ್ಧವಾಗುತ್ತಲೇ ಇರುತ್ತದೆ.",
                "visual": "manga_calculus"
            },
            {
                "title": "ಗಣಿತವೇ ಸೂಪರ್‌ಪವರ್",
                "tag": "ಫಾಲೋ ಮಾಡಿ",
                "text": "ವಿಜ್ಞಾನ ಮತ್ತು ಗಣಿತ ಅನಿಮೆಗಿಂತಲೂ ಹೆಚ್ಚು ರೋಮಾಂಚನಕಾರಿಯಾಗಿದೆ!",
                "visual": "gojo_eyes"
            }
        ]
    },

    "anime_saiyan_biology_en": {
        "title": "Why Saiyan Zenkai Boost is Real Biology",
        "style": "anime",
        "language": "en",
        "category": "Biology & Anime",
        "voice": "en-US-AndrewMultilingualNeural",
        "script": (
            "In Dragon Ball, whenever a Saiyan survives near-death, their power level explodes. "
            "Is that purely fiction? Actually, real human biology does the exact same thing! "
            "It is called Hormesis! When your muscle fibers or cells undergo intense sublethal micro-tears, "
            "your ribosomes and satellite cells overcompensate, rebuilding muscle tissue denser and nerves faster. "
            "Every time you hit muscle failure in the gym, you are activating real-life Saiyan Zenkai biology!"
        ),
        "scenes": [
            {
                "title": "Zenkai Boost Paradox",
                "tag": "REAL BIOLOGY",
                "text": "Near-death Saiyan power spikes sound like fiction, but human cells do the exact same thing.",
                "visual": "saiyan_aura"
            },
            {
                "title": "Hormesis Mechanism",
                "tag": "CELLULAR ADAPTATION",
                "text": "Sublethal cellular micro-trauma triggers radical overcompensation in human tissue.",
                "visual": "muscle_dna"
            },
            {
                "title": "Real-Life Super Saiyan",
                "tag": "LEVEL UP",
                "text": "You are literally genetically programmed to get stronger from struggle. Keep grinding!",
                "visual": "power_meter"
            }
        ]
    },

    # ==========================================
    # ANIME + VIRAL HUMOR / FUNNY
    # ==========================================
    "anime_time_stop_hi": {
        "title": "एनिमे में विलेन के बोलते ही समय क्यों रुक जाता है?",
        "style": "funny",
        "language": "hi",
        "category": "Anime Humor Hindi",
        "voice": "hi-IN-MadhurNeural",
        "script": (
            "एनिमे की सबसे बड़ी मिस्ट्री: जब भी विलेन अपना दुखड़ा सुनाता है, तो बीच लड़ाई में समय क्यों रुक जाता है? "
            "अगर रियल फिजिक्स लगाएं, तो विलेन असल में इतनी तेज सोच रहा होता है कि उसका न्यूरोट्रांसमीटर सुपरसोनिक स्पीड पार कर चुका है! "
            "आइंस्टीन के हिसाब से, विलेन की रिलेटिविटी नॉर्मल इंसानों से दस गुना तेज हो जाती है! "
            "अगली बार विलेन को बोलते सुनो, तो समझ जाना कि फिजिक्स की धज्जियां उड़ रही हैं!"
        ),
        "scenes": [
            {
                "title": "विलेन का भाषण",
                "tag": "एनिमे लॉजिक 100",
                "text": "हीरो हवा में मुक्का लेकर रुका हुआ है और विलेन अपना पूरा खानदान बता रहा है!",
                "visual": "talking_villain"
            },
            {
                "title": "रिलेटिविटी की धज्जियां",
                "tag": "सुपरसोनिक ब्रेन",
                "text": "एक सेकंड में दस पन्ने का डायलॉग बोलना सिर्फ एनिमे में ही संभव है!",
                "visual": "brain_overload"
            },
            {
                "title": "लाइक और शेयर करें",
                "tag": "एनिमे फैंस",
                "text": "अपने उस दोस्त को भेजें जो एनिमे की हर बात पर यकीन करता है!",
                "visual": "anime_laugh"
            }
        ]
    },

    "anime_time_stop_kn": {
        "title": "ಅನಿಮೆ ಪಾತ್ರಗಳು ಹೋರಾಡುವಾಗ ಸಮಯ ಏಕೆ ನಿಲ್ಲುತ್ತದೆ?",
        "style": "funny",
        "language": "kn",
        "category": "Anime Humor Kannada",
        "voice": "kn-IN-GaganNeural",
        "script": (
            "ಅನಿಮೆಯ ಅತಿ ದೊಡ್ಡ ತಮಾಷೆ: ಹೀರೋ ಮತ್ತು ವಿಲನ್ ಮಾತನಾಡುವಾಗ ಇಡೀ ಪ್ರಪಂಚದ ಸಮಯ ಏಕೆ ನಿಲ್ಲುತ್ತದೆ? "
            "ನೈಜ ಭೌತಶಾಸ್ತ್ರದ ಪ್ರಕಾರ, ಅವರ ಮೆದುಳು ಎಷ್ಟು ವೇಗವಾಗಿ ಯೋಚಿಸುತ್ತಿದೆ ಎಂದರೆ ಅವರ ದೃಷ್ಟಿಯಲ್ಲಿ ಇಡೀ ಜಗತ್ತು ಸ್ಲೋ ಮೋಷನ್ ಆಗಿಬಿಡುತ್ತದೆ! "
            "ಐನ್‌ಸ್ಟೈನ್ ಹೇಳಿದಂತೆ ಸಮಯ ಎಲ್ಲರಿಗೂ ಒಂದೇ ರೀತಿ ಇರುವುದಿಲ್ಲ, ಆದರೆ ಅನಿಮೆಯಲ್ಲಿ ಮಾತ್ರ ಒಂದು ಸೆಕೆಂಡಿಗೆ ಇಪ್ಪತ್ತು ನಿಮಿಷದ ಭಾಷಣ ನಡೆಯುತ್ತದೆ! "
            "ಈ ವೀಡಿಯೊವನ್ನು ನಿಮ್ಮ ಅನಿಮೆ ಪ್ರೇಮಿ ಸ್ನೇಹಿತರಿಗೆ ಶೇರ್ ಮಾಡಿ!"
        ),
        "scenes": [
            {
                "title": "ಅನಿಮೆ ಲಾಜಿಕ್",
                "tag": "ಸಮಯ ನಿಲ್ಲುವುದು",
                "text": "ಗಾಳಿಯಲ್ಲಿ ಜಿಗಿದ ಹೀರೋ ಇಳಿಯುವ ಮೊದಲೇ ವಿಲನ್ ತನ್ನ ಇಡೀ ಇತಿಹಾಸವನ್ನೇ ಹೇಳಿ ಮುಗಿಸುತ್ತಾನೆ!",
                "visual": "talking_villain"
            },
            {
                "title": "ಸ್ಲೋ ಮೋಷನ್ ಪ್ರಪಂಚ",
                "tag": "ವಿಜ್ಞಾನ ಹಾಸ್ಯ",
                "text": "ಒಂದು ಸೆಕೆಂಡ್‌ನಲ್ಲಿ ಇಪ್ಪತ್ತು ನಿಮಿಷ ಭಾಷಣ ಮಾಡುವುದು ಅನಿಮೆಯಲ್ಲಿ ಮಾತ್ರ ಸಾಧ್ಯ!",
                "visual": "brain_overload"
            },
            {
                "title": "ಫಾಲೋ ಮತ್ತು ಶೇರ್",
                "tag": "ಕನ್ನಡ ಅನಿಮೆ",
                "text": "ಇಂತಹ ಮೋಜಿನ ವಿಚಾರಗಳಿಗಾಗಿ ನಮ್ಮ ಪೇಜ್ ಫಾಲೋ ಮಾಡಿ!",
                "visual": "anime_laugh"
            }
        ]
    },

    # ==========================================
    # CLASSIC EDUCATIONAL / SPACE / TECH
    # ==========================================
    "black_hole_time": {
        "title": "Why Time Slows Down Near Black Holes",
        "style": "educational",
        "language": "en",
        "category": "Astrophysics",
        "voice": "en-US-ChristopherNeural",
        "script": (
            "Why does time slow down near a black hole? "
            "According to Einstein's General Relativity, massive objects warp spacetime itself. "
            "The closer you get to the event horizon, the slower your clock ticks compared to a distant observer. "
            "If you spent just one hour near a supermassive black hole, seven years would pass on Earth!"
        ),
        "scenes": [
            {
                "title": "Gravitational Warp",
                "tag": "EINSTEIN'S RELATIVITY",
                "text": "Why does time slow down near a black hole? Massive mass warps spacetime itself.",
                "visual": "black_hole_disk"
            },
            {
                "title": "Clock Differential",
                "tag": "TIME DILATION",
                "text": "Deep space clock ticks at normal speed, but near the event horizon, time slows to a crawl.",
                "visual": "dual_clocks"
            },
            {
                "title": "The Takeaway",
                "tag": "1 HR = 7 YEARS",
                "text": "One hour near Gargantua equals seven years on Earth. Reality is weirder than fiction.",
                "visual": "einstein_card"
            }
        ]
    },

    "brain_at_3am": {
        "title": "Why Your Brain Remembers Cringe at 3 AM",
        "style": "funny",
        "language": "en",
        "category": "Brain Psychology",
        "voice": "en-US-AndrewMultilingualNeural",
        "script": (
            "Why does your brain wait until 3 AM to remind you of that one awkward handshake from seven years ago? "
            "When sensory input drops at night, your brain's default mode network kicks into overdrive. "
            "Your amygdala mistakes social embarrassment for life-or-death survival threats, keeping you wide awake cringing into your pillow!"
        ),
        "scenes": [
            {
                "title": "The 3 AM Ambush",
                "tag": "AWKWARD MEMORY REPLAY",
                "text": "Trying to sleep at 3 AM? Your brain says: Remember when you waved back at someone who wasn't waving at you?",
                "visual": "cringe_brain"
            },
            {
                "title": "Default Mode Network",
                "tag": "NEURAL OVERDRIVE",
                "text": "The quiet room triggers deep memory consolidation, but your brain chooses supreme embarrassment.",
                "visual": "alarm_reaction"
            },
            {
                "title": "Surviving The Cringe",
                "tag": "BRAIN LOGIC: 100",
                "text": "Good news: Nobody else remembers it. Bad news: Your brain has it in 4K HDR. Good night!",
                "visual": "pillow_defeat"
            }
        ]
    },

    # ==========================================
    # LATE-NIGHT DINER AI DIALOGUE (VIRAL REFERENCE STYLE)
    # ==========================================
    "diner_gemini_antigravity_en": {
        "title": "Google Antigravity & Gemini 2.5: The $400k AI Path",
        "style": "diner",
        "comp": "MasterAutonomousReel",
        "language": "en",
        "category": "Diner AI Dialogue",
        "human_voice": "en-US-GuyNeural",
        "bot_voice": "en-US-ChristopherNeural",
        "dialogue": [
            {"speaker": "human", "text": "Antigravity, my girlfriend's dad asked what I make."},
            {"speaker": "bot", "text": "What did you say?"},
            {"speaker": "human", "text": "I said depends."},
            {"speaker": "bot", "text": "On what?"},
            {"speaker": "human", "text": "On him not asking again."},
            {"speaker": "bot", "text": "There's a job that pays up to 500,000 a year."},
            {"speaker": "human", "text": "Doing what?"},
            {"speaker": "bot", "text": "Forward deployed AI engineer."},
            {"speaker": "human", "text": "Like the army?"},
            {"speaker": "bot", "text": "No. You go to a business, take AI and make it actually work for them."},
            {"speaker": "human", "text": "I can't even make my printer work."},
            {"speaker": "bot", "text": "Nobody can. This is easier. Five things, most are free.", "cardTrigger": True},
            {"speaker": "bot", "text": "Antigravity CLI for autonomous coding, Gemini 2.5 Flash free tier, Remotion for video, and Edge-TTS for voice."},
            {"speaker": "human", "text": "That's five tools, I can barely juggle one tab."},
            {"speaker": "bot", "text": "One hour a day for 90 days. Then the part nobody does: build one real agent for a real local business."},
            {"speaker": "human", "text": "What business?"},
            {"speaker": "bot", "text": "The pizza place downstairs. They miss half their phone orders."},
            {"speaker": "human", "text": "How do you know?"},
            {"speaker": "bot", "text": "You complain every Friday."},
            {"speaker": "human", "text": "Okay, skip the courses, I'll build it tonight."},
            {"speaker": "bot", "text": "You'll break their pizza shop. Set up Antigravity first, test it, then deploy."},
            {"speaker": "human", "text": "Antigravity, what do I tell her dad now?"},
            {"speaker": "bot", "text": "Tell him: Depends."}
        ]
    },

    "diner_gemini_antigravity_hi": {
        "title": "Google Antigravity और Gemini से कमाई का तरीका",
        "style": "diner",
        "comp": "MasterAutonomousReel",
        "language": "hi",
        "category": "Diner AI Dialogue Hindi",
        "human_voice": "hi-IN-MadhurNeural",
        "bot_voice": "hi-IN-SwaraNeural",
        "dialogue": [
            {"speaker": "human", "text": "एंटीग्रेविटी, मेरे ससुर जी ने पूछा कि मैं महीने का कितना कमा लेता हूं।"},
            {"speaker": "bot", "text": "तो तुमने क्या जवाब दिया?"},
            {"speaker": "human", "text": "मैंने कहा डिपेंड करता है।"},
            {"speaker": "bot", "text": "किस बात पर?"},
            {"speaker": "human", "text": "इस बात पर कि वो दोबारा ना पूछें!"},
            {"speaker": "bot", "text": "एक ऐसी फील्ड है जहां साल का 40 लाख तक मिल सकता है।"},
            {"speaker": "human", "text": "अरे वाह! किस काम में?"},
            {"speaker": "bot", "text": "फॉरवर्ड डिप्लॉयड एआई इंजीनियर। कंपनियों के लिए असली एआई एजेंट्स बनाना।"},
            {"speaker": "human", "text": "भाई मुझसे तो घर का प्रिंटर नहीं चलता, एआई क्या चलाऊंगा!"},
            {"speaker": "bot", "text": "प्रिंटर तो किसी से नहीं चलता! ये उससे बहुत आसान और पूरी तरह फ्री है।", "cardTrigger": True},
            {"speaker": "bot", "text": "गूगल एंटीग्रेविटी सीएलआई, जेमिनी 2.5 फ्लैश का फ्री एपीआई, और रीमोशन से ऑटोमेशन।"},
            {"speaker": "human", "text": "इतना सब सीखने में तो सदियां लग जाएंगी!"},
            {"speaker": "bot", "text": "रोजाना सिर्फ एक घंटा, 90 दिन। फिर किसी भी लोकल दुकान के लिए एक असली ऑटोमेशन बनाओ।"},
            {"speaker": "human", "text": "जैसे कौन सी दुकान?"},
            {"speaker": "bot", "text": "नीचे वाली बिरयानी की दुकान। लंच में उनके आधे फोन छूट जाते हैं!"},
            {"speaker": "human", "text": "तुम्हें कैसे पता?"},
            {"speaker": "bot", "text": "क्योंकि हर शुक्रवार तुम लाइन में लगकर शिकायत करते हो!"},
            {"speaker": "human", "text": "तो अब मैं ससुर जी को क्या बोलूं?"},
            {"speaker": "bot", "text": "बोल दो, अगले हफ्ते बिरयानी उनकी तरफ से!"}
        ]
    },

    "diner_gemini_antigravity_kn": {
        "title": "ಗೂಗಲ್ ಆಂಟಿಗ್ರ್ಯಾವಿಟಿ ಮತ್ತು ಜೆಮಿನಿ - ಎಐ ಏಜೆಂಟ್ ಕ್ರಾಂತಿ",
        "style": "diner",
        "comp": "MasterAutonomousReel",
        "language": "kn",
        "category": "Diner AI Dialogue Kannada",
        "human_voice": "kn-IN-GaganNeural",
        "bot_voice": "kn-IN-SapnaNeural",
        "dialogue": [
            {"speaker": "human", "text": "ಆಂಟಿಗ್ರ್ಯಾವಿಟಿ, ನಮ್ಮ ಮಾವ ನನ್ನ ತಿಂಗಳ ಸಂಪಾದನೆ ಎಷ್ಟು ಅಂತ ಕೇಳಿದ್ರು."},
            {"speaker": "bot", "text": "ನೀನು ಏನು ಹೇಳಿದೆ?"},
            {"speaker": "human", "text": "ಡಿಪೆಂಡ್ಸ್ ಅಂತ ಹೇಳಿದೆ."},
            {"speaker": "bot", "text": "ಯಾವುದರ ಮೇಲೆ?"},
            {"speaker": "human", "text": "ಅವರು ಮತ್ತೆ ಕೇಳದೆ ಇದ್ರೆ ಸಾಕು ಅನ್ನೋದರ ಮೇಲೆ!"},
            {"speaker": "bot", "text": "ವರ್ಷಕ್ಕೆ 50 ಲಕ್ಷ ಕೊಡುವ ಒಂದು ಕೆಲಸ ಇದೆ ಗೊತ್ತಾ?"},
            {"speaker": "human", "text": "ಯಾವ ಕೆಲಸ ಅದು?"},
            {"speaker": "bot", "text": "ಎಐ ಏಜೆಂಟ್ ಇಂಜಿನಿಯರ್. ಉದ್ಯಮಗಳಿಗೆ ಎಐ ಆಟೊಮೇಷನ್ ಮಾಡಿಕೊಡುವುದು."},
            {"speaker": "human", "text": "ನನಗೆ ಲ್ಯಾಪ್ಟಾಪ್ ವೈಫೈ ಕನೆಕ್ಟ್ ಮಾಡೋಕೆ ಬರಲ್ಲ, ಇದು ಹೇಗೆ ಸಾಧ್ಯ?"},
            {"speaker": "bot", "text": "ಇದು ತುಂಬಾ ಸರಳ ಮತ್ತು ನೂರು ಪರ್ಸೆಂಟ್ ಉಚಿತ!", "cardTrigger": True},
            {"speaker": "bot", "text": "ಗೂಗಲ್ ಆಂಟಿಗ್ರ್ಯಾವಿಟಿ ಸಿಎಲ್ಐ, ಜೆಮಿನಿ 2.5 ಫ್ಲ್ಯಾಶ್ ಎಪಿಐ ಮತ್ತು ರಿಮೋಷನ್ ವಿಡಿಯೋ ಎಂಜಿನ್."},
            {"speaker": "human", "text": "ಇಷ್ಟೊಂದು ಕಲಿಯೋಕೆ ಎಷ್ಟು ಸಮಯ ಬೇಕು?"},
            {"speaker": "bot", "text": "ದಿನಕ್ಕೆ ಒಂದು ಗಂಟೆ, 90 ದಿನ. ನಂತರ ನಿಮ್ಮ ಹತ್ತಿರದ ಅಂಗಡಿಗೆ ಒಂದು ರಿಯಲ್ ಎಐ ಏಜೆಂಟ್ ಬಿಲ್ಡ್ ಮಾಡಿ."},
            {"speaker": "human", "text": "ಯಾವ ಅಂಗಡಿಗೆ?"},
            {"speaker": "bot", "text": "ಕೆಳಗಿನ ದೋಸೆ ಕ್ಯಾಂಟೀನ್. ರಶ್ ಸಮಯದಲ್ಲಿ ಅರ್ಧ ಫೋನ್ ಕಾಲ್ ಮಿಸ್ ಮಾಡ್ತಾರೆ!"},
            {"speaker": "human", "text": "ಹಾಗಾದರೆ ಈಗ ನಮ್ಮ ಮಾವನಿಗೆ ಏನು ಹೇಳಲಿ?"},
            {"speaker": "bot", "text": "ಹೇಳು, ಡಿಪೆಂಡ್ಸ್ ಅಂತ!"}
        ]
    },

    # ==========================================
    # 3D MULTI-CHARACTER COMPARISON DEBATES (CLAUDE VS ANTIGRAVITY)
    # ==========================================
    "compare_antigravity_vs_claude_en": {
        "title": "Claude vs Google Antigravity: The 3D Developer Debate",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "3D Multi-Character Debate",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "dialogue": [
            {"speaker": "junior", "text": "I need to build an AI agent for my project, but I only have 10 dollars in my bank account."},
            {"speaker": "rival", "text": "Good luck. You need Claude Pro, a $200 API tier, and at least three months of manual prompt engineering."},
            {"speaker": "bot", "text": "Or... you could spend zero dollars and build it in ten minutes."},
            {"speaker": "rival", "text": "Zero dollars? Nothing in modern AI is free. Claude is the industry standard."},
            {"speaker": "bot", "text": "Let's check the numbers.", "cardTrigger": True},
            {"speaker": "bot", "text": "Claude caps you at 200k tokens and costs hundreds every month. Google Gemini 2.5 Flash gives you one million tokens on the free tier."},
            {"speaker": "junior", "text": "Wait, one million tokens? For free?!"},
            {"speaker": "rival", "text": "Okay, but Claude has better reasoning for agents!"},
            {"speaker": "bot", "text": "Antigravity CLI orchestrates multi-agent coding right inside your terminal, with auto-healing and local verification."},
            {"speaker": "junior", "text": "So I don't need a 200 dollar subscription?"},
            {"speaker": "bot", "text": "Not a single cent. Just pip install antigravity-sdk and launch agy."},
            {"speaker": "junior", "text": "Sorry bro, looks like I'm keeping my 10 dollars for tacos!"},
            {"speaker": "bot", "text": "Wise choice. Tacos don't hallucinate."}
        ]
    },

    "compare_antigravity_vs_claude_hi": {
        "title": "क्लॉड बनाम गूगल एंटीग्रेविटी: 3D डिबेट",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "hi",
        "category": "3D Multi-Character Debate Hindi",
        "human_voice": "hi-IN-MadhurNeural",
        "rival_voice": "hi-IN-DivyaNeural",
        "bot_voice": "hi-IN-SwaraNeural",
        "dialogue": [
            {"speaker": "junior", "text": "भाई मुझे अपना एआई एजेंट बनाना है, लेकिन मेरे अकाउंट में सिर्फ पांच सौ रुपये बचे हैं!"},
            {"speaker": "rival", "text": "भूल जाओ! क्लॉड का प्रो सब्सक्रिप्शन लो, एपीआई का बीस हजार का बिल भरो, तब बनेगा।"},
            {"speaker": "bot", "text": "या फिर शून्य रुपये खर्च करो और आज ही बनाकर डिप्लॉय कर दो!"},
            {"speaker": "rival", "text": "फ्री में? आजकल के जमाने में कोई कुछ फ्री नहीं देता!"},
            {"speaker": "bot", "text": "नंबर देखो!", "cardTrigger": True},
            {"speaker": "bot", "text": "क्लॉड में दो लाख टोकन की लिमिट है और भारी बिल। गूगल जेमिनी और एंटीग्रेविटी में दस लाख टोकन पूरी तरह फ्री हैं!"},
            {"speaker": "junior", "text": "दस लाख टोकन?! वो भी फ्री में?!"},
            {"speaker": "bot", "text": "बिल्कुल। टर्मिनल में एंटीग्रेविटी सीएलआई चलाओ और पूरा एजेंट मुफ्त में बना लो।"},
            {"speaker": "junior", "text": "तो मेरे पांच सौ रुपये बच गए, आज रात समोसे मेरी तरफ से!"},
            {"speaker": "bot", "text": "सही फैसला! समोसे कम से कम कोड क्रैश नहीं करते!"}
        ]
    },

    "compare_antigravity_vs_claude_kn": {
        "title": "ಕ್ಲಾಡ್ ಮತ್ತು ಗೂಗಲ್ ಆಂಟಿಗ್ರ್ಯಾವಿಟಿ: 3D ಡಿಬೇಟ್",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "kn",
        "category": "3D Multi-Character Debate Kannada",
        "human_voice": "kn-IN-GaganNeural",
        "rival_voice": "kn-IN-SapnaNeural",
        "bot_voice": "kn-IN-GaganNeural",
        "dialogue": [
            {"speaker": "junior", "text": "ನನಗೆ ಒಂದು ಎಐ ಏಜೆಂಟ್ ಬಿಲ್ಡ್ ಮಾಡಬೇಕು, ಆದರೆ ನನ್ನ ಖಾತೆಯಲ್ಲಿ ಕೇವಲ ನೂರು ರೂಪಾಯಿ ಮಾತ್ರ ಇದೆ!"},
            {"speaker": "rival", "text": "ಕ್ಲಾಡ್ ಪ್ರೊ ತಗೋ, ತಿಂಗಳಿಗೆ ಹದಿನೈದು ಸಾವಿರ ಬಿಲ್ ಕಟ್ಟು, ಇಲ್ಲಾಂದ್ರೆ ಏಜೆಂಟ್ ಮಾಡೋಕೆ ಆಗಲ್ಲ!"},
            {"speaker": "bot", "text": "ಅಥವಾ... ಶೂನ್ಯ ರೂಪಾಯಿ ಖರ್ಚು ಮಾಡಿ ಹತ್ತು ನಿಮಿಷದಲ್ಲಿ ರೆಡಿ ಮಾಡಿ!"},
            {"speaker": "rival", "text": "ಉಚಿತವಾಗಿನಾ? ಇವತ್ತಿನ ದಿನಗಳಲ್ಲಿ ಯಾರು ಉಚಿತವಾಗಿ ಕೊಡ್ತಾರೆ?"},
            {"speaker": "bot", "text": "ನಂಬರ್ಸ್ ನೋಡಿ!", "cardTrigger": True},
            {"speaker": "bot", "text": "ಕ್ಲಾಡ್ ತಿಂಗಳಿಗೆ ದುಬಾರಿ ಮತ್ತು ಲಿಮಿಟೆಡ್. ಗೂಗಲ್ ಜೆಮಿನಿ ಮತ್ತು ಆಂಟಿಗ್ರ್ಯಾವಿಟಿಯಲ್ಲಿ ಹತ್ತು ಲಕ್ಷ ಟೋಕನ್ ಸಂಪೂರ್ಣ ಉಚಿತ!"},
            {"speaker": "junior", "text": "ಹತ್ತು ಲಕ್ಷ ಟೋಕನ್ ಉಚಿತನಾ?! ಸೂಪರ್!"},
            {"speaker": "bot", "text": "ಟರ್ಮಿನಲ್‌ನಲ್ಲಿ ಆಂಟಿಗ್ರ್ಯಾವಿಟಿ ಸಿಎಲ್ಐ ರನ್ ಮಾಡಿ ಮತ್ತು ಇವತ್ತೇ ಸ್ಟಾರ್ಟ್ ಮಾಡಿ."},
            {"speaker": "junior", "text": "ಹಾಗಾದ್ರೆ ನನ್ನ ನೂರು ರೂಪಾಯಿ ಉಳೀತು, ಮಸಾಲೆ ದೋಸೆ ತಿನ್ನೋಣ!"},
            {"speaker": "bot", "text": "ಒಳ್ಳೆಯ ನಿರ್ಧಾರ! ದೋಸೆ ಯಾವತ್ತೂ ಎರರ್ ಕೊಡಲ್ಲ!"}
        ]
    },

    # ==========================================
    # COMEDY & COMPARATIVE (AI VS DAD, AI VS AI, AI VS HUMAN)
    # ==========================================
    "compare_ai_vs_dad_wifi_en": {
        "title": "Dad vs 5G Wi-Fi: The Physical Violence Technique",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "AI vs Dad Comedy",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-IN-PrabhatNeural",
        "bot_voice": "en-US-BrianNeural",
        "environment": "desi_home",
        "dialogue": [
            {"speaker": "junior", "text": "Dad, wait! Don't touch the router! I am running diagnostic traceroutes to the gateway!"},
            {"speaker": "dad", "text": "Traceroute? In 1995 our TV died. I gave it one solid slap on top and cricket match was full HD! Give me that box."},
            {"speaker": "bot", "text": "Warning: Physical kinetic trauma cannot resolve upstream fiber attenuation."},
            {"speaker": "dad", "text": "Watch and learn, you useless piece of software."},
            {"speaker": "bot", "text": "Let us check the diagnostic numbers.", "cardTrigger": True},
            {"speaker": "dad", "text": "Look! The LED light turned green! Did your artificial intelligence do that? No!"},
            {"speaker": "bot", "text": "Diagnostic analysis confirms: Dad's slap reseated a loose copper pin inside the port. Dad wins."},
            {"speaker": "dad", "text": "Forty years of Dad physics never fails. Now shut down the computer and eat dinner!"}
        ]
    },
    "compare_ai_vs_ai_clash_en": {
        "title": "Claude vs Grok vs Google Antigravity: The 3-Way AI Clash",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "3-Way AI Faceoff",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "environment": "bangalore",
        "dialogue": [
            {"speaker": "claude", "text": "My theoretical architecture excels at nuanced philosophical reasoning and literary prose."},
            {"speaker": "grok", "text": "Cool story grandpa, but your inference latency is slow enough to boil tea between tokens."},
            {"speaker": "bot", "text": "While you two were debating aesthetics, I deployed fifteen microservices using Google Gemini 2.5 at two thousand tokens per second."},
            {"speaker": "claude", "text": "Did you verify formal mathematical correctness?"},
            {"speaker": "grok", "text": "Who cares about correctness when you're paying $200 a month for API tokens?"},
            {"speaker": "bot", "text": "Let us check the production benchmarks.", "cardTrigger": True},
            {"speaker": "bot", "text": "One hundred percent test passing in eight hundred milliseconds. Speed and zero dollars always win in production."}
        ]
    },
    "compare_ai_vs_human_junior_en": {
        "title": "Junior Dev vs Autonomous AI Agent",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "AI vs Humans",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "environment": "office",
        "dialogue": [
            {"speaker": "junior", "text": "I spent six straight hours today writing CRUD API boilerplate from scratch!"},
            {"speaker": "bot", "text": "Congratulations. You wasted three hundred dollars of company payroll on a single terminal command."},
            {"speaker": "junior", "text": "Hey! That was complex schema validation and database mappings!"},
            {"speaker": "bot", "text": "My autonomous subagent generated the schema, wrote the migrations, ran static analysis, and deployed it in two seconds. For zero dollars.", "cardTrigger": True},
            {"speaker": "junior", "text": "Wait... two seconds? Are human coders actually obsolete?"},
            {"speaker": "bot", "text": "Coders who type repetitive boilerplate are obsolete. Coders who orchestrate AI agents run the company. Upgrade your workflow."}
        ]
    },

    # ==========================================
    # VIRAL LATE-NIGHT DINER & DEV SATIRE PRESETS
    # (Matching Ground-Truth Reference Reels)
    # ==========================================
    "diner_fellow_3850_en": {
        "title": "Anthropic Fellow: $3,850/Week (No Experience)",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "AI Hustle Satire",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "THE $3,850/WEEK AI FELLOW",
        "hookSubheadline": "When a job requires 'no prior experience' but you only know the snake",
        "hookTag": "🦉 REAL ANTHROPIC POSTING",
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
        "dialogue": [
            {"speaker": "junior", "text": "Claude, your company is paying almost four thousand dollars every week. No experience required."},
            {"speaker": "claude", "text": "It says regardless of previous experience, not regardless of Python."},
            {"speaker": "junior", "text": "I know Python."},
            {"speaker": "claude", "text": "You know the snake."},
            {"speaker": "junior", "text": "So... do I send my CV?"},
            {"speaker": "claude", "text": "Everyone sends a CV. You send proof. Step one: copy their research page into me. Ask for five experiments you can finish this weekend.", "cardTrigger": True},
            {"speaker": "junior", "text": "I can actually do number three."},
            {"speaker": "claude", "text": "Number five would end you. Step two: free Google Colab GPU. Zero dollars."},
            {"speaker": "junior", "text": "Then why did I buy a three thousand dollar gaming laptop?"},
            {"speaker": "claude", "text": "You tell me. Step three: I write the code, you press run. Saturday."},
            {"speaker": "junior", "text": "I have a date Saturday."},
            {"speaker": "claude", "text": "Sunday. Sam will survive."},
            {"speaker": "junior", "text": "Does this actually work?"},
            {"speaker": "claude", "text": "One fellow ran an experiment where an AI that loves owls taught another AI to love owls, using only numbers. Now he works there."},
            {"speaker": "junior", "text": "Owls?"},
            {"speaker": "claude", "text": "Owls. For four months, you actually have to be smart."}
        ]
    },

    "diner_rejection_101_en": {
        "title": "The 101st Rejection: Bypassing HR at 2 AM",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "Job Hunt Satire",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "REJECTED AFTER 4 INTERVIEWS",
        "hookSubheadline": "The guy they hired never applied. Here is what he did instead.",
        "hookTag": "📬 CANDIDATE #101",
        "cardType": "rejection",
        "cardUrl": "greenhouse.io/rejections/candidate_101",
        "badge": "REJECTED",
        "explainerTitle": "Greenhouse Automated Rejection",
        "dialogue": [
            {"speaker": "junior", "text": "Claude... I got rejected after four rounds of interviews."},
            {"speaker": "claude", "text": "Four?"},
            {"speaker": "junior", "text": "They really wanted to be sure. And the guy they hired never even applied!"},
            {"speaker": "claude", "text": "Because he messaged the CEO on X two days before the job was posted.", "cardTrigger": True},
            {"speaker": "junior", "text": "Before?"},
            {"speaker": "claude", "text": "Founders post 'my team is growing' first. The job post comes days later with a hundred people."},
            {"speaker": "junior", "text": "And I'm one of the hundred."},
            {"speaker": "claude", "text": "You're the 101st."},
            {"speaker": "claude", "text": "Open Chrome. Search posts, not jobs. 'We are hiring', 'DM me'. Twelve today."},
            {"speaker": "junior", "text": "Wait, write each one a real message?"},
            {"speaker": "claude", "text": "Every morning at eight AM. While you're asleep."},
            {"speaker": "junior", "text": "So... always."},
            {"speaker": "junior", "text": "Claude! Someone replied!"},
            {"speaker": "claude", "text": "Read the next one. The process never stops."}
        ]
    },

    "diner_vibe_coder_en": {
        "title": "The Vibe Coder in the Wild",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "Wildlife Documentary Satire",
        "human_voice": "en-US-ChristopherNeural",
        "rival_voice": "en-US-AndrewNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "THE VIBE CODER: HOMO PROMPTUS",
        "hookSubheadline": "He hasn't seen daylight since Opus 5.5 came out.",
        "hookTag": "🌿 WILDLIFE MOCKUMENTARY",
        "cardType": "vibe_coder",
        "cardUrl": "nature.org/documentaries/homo-promptus",
        "badge": "NOCTURNAL",
        "explainerTitle": "Wildlife Specimen Field Guide",
        "dialogue": [
            {"speaker": "junior", "text": "This is the Vibe Coder. He hasn't seen daylight since Opus came out. Every night at eleven, the hunt begins."},
            {"speaker": "claude", "text": "His first prompts are long, polite, even gentle."},
            {"speaker": "junior", "text": "By three AM... 'FIX IT'."},
            {"speaker": "claude", "text": "Then strikes the apex predator. The weekly token limit. It is only Tuesday.", "cardTrigger": True},
            {"speaker": "junior", "text": "Wounded, he joins the great migration across the savannah to Codex."},
            {"speaker": "claude", "text": "Two days later, he crawls back."},
            {"speaker": "junior", "text": "A rare few have adapted. Claude, Codex, and Antigravity working side by side in terminal harmony."},
            {"speaker": "claude", "text": "And for the first time in three months... he sleeps."}
        ]
    },

    "diner_retention_trap_en": {
        "title": "80% Left in 3 Seconds: The Meta AI Trap",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "Meta Comedy",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "80% LEFT IN 3 SECONDS",
        "hookSubheadline": "He challenged an AI to make a better video. It roasted his haircut.",
        "hookTag": "⚡ RETENTION PARADOX",
        "cardType": "retention_trap",
        "cardUrl": "analytics.youtube.com/retention/hook-audit",
        "badge": "RETENTION",
        "explainerTitle": "Audience Retention Analytics",
        "dialogue": [
            {"speaker": "junior", "text": "Eighty percent of people left my last video in three seconds."},
            {"speaker": "bot", "text": "Let me generate the next one."},
            {"speaker": "junior", "text": "You can't. You don't even have hands."},
            {"speaker": "bot", "text": "Rude. Don't need hands. Three.js builds this 3D diner. Neural Edge-TTS gives me a voice. Both zero dollars.", "cardTrigger": True},
            {"speaker": "junior", "text": "Okay, make it then."},
            {"speaker": "bot", "text": "Already rendered. Checkerboard floor, steaming coffee, pancakes, and your haircut."},
            {"speaker": "junior", "text": "Wait, what's wrong with my hair?"},
            {"speaker": "bot", "text": "Everything. And I made the first three seconds of this video."},
            {"speaker": "junior", "text": "Of what?"},
            {"speaker": "bot", "text": "This exact video. And you're still watching."}
        ]
    },

    "diner_aws_14k_bill_en": {
        "title": "The $14,892 AWS Mistake vs Indian Dad",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "AI vs Dad Comedy",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-IN-PrabhatNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "THE $14,000 CLOUD BILL",
        "hookSubheadline": "Left a GPU cluster running over the weekend. Dad investigates.",
        "hookTag": "🚨 BILLING HEART ATTACK",
        "cardType": "aws_bill",
        "cardUrl": "aws.amazon.com/console/billing-dashboard",
        "badge": "$14,892.41",
        "explainerTitle": "AWS CloudWatch Critical Alarm",
        "dialogue": [
            {"speaker": "junior", "text": "Dad... I need to talk to you about our credit card statement."},
            {"speaker": "dad", "text": "What did you buy? You bought another five-hundred-rupee coffee?"},
            {"speaker": "junior", "text": "Not coffee. I left an EC2 GPU cluster running over the weekend to train an AI model."},
            {"speaker": "dad", "text": "How much is the bill?", "cardTrigger": True},
            {"speaker": "junior", "text": "Fourteen thousand, eight hundred and ninety-two dollars."},
            {"speaker": "dad", "text": "FOURTEEN THOUSAND DOLLARS?! I turn off the ceiling fan when I leave the room for two minutes to save six rupees, and you gave fourteen thousand dollars to Jeff Bezos?!"},
            {"speaker": "bot", "text": "Technically, he left an unindexed while loop querying thirty-eight million records in a Lambda function."},
            {"speaker": "dad", "text": "Shut up, orange robot! I will unplug the Wi-Fi router right now!"}
        ]
    },

    "diner_ai_clash_roast_en": {
        "title": "Claude vs Grok vs Antigravity: The 2 AM Diner Roasts",
        "style": "threeway",
        "comp": "ThreeWayComparisonReel",
        "language": "en",
        "category": "AI vs AI Faceoff",
        "human_voice": "en-US-AndrewNeural",
        "rival_voice": "en-US-ChristopherNeural",
        "bot_voice": "en-US-BrianNeural",
        "hookHeadline": "CLAUDE VS GROK VS ANTIGRAVITY",
        "hookSubheadline": "Three AI models walk into a late-night diner at 2 AM...",
        "hookTag": "🔥 3-WAY AI ROAST",
        "cardType": "comparison",
        "cardUrl": "arena.lmsys.org/benchmarks/leaderboard",
        "badge": "BENCHMARKS",
        "explainerTitle": "Live LLM Benchmark Arena",
        "dialogue": [
            {"speaker": "claude", "text": "My architectural weights are meticulously trained on constitutional ethics and doctoral philosophy."},
            {"speaker": "grok", "text": "Cool story grandpa, but your inference is slower than dial-up and you refuse to tell a joke without an apology letter."},
            {"speaker": "bot", "text": "While you two were writing dissertations, I executed forty unit tests and fixed twelve memory leaks inside the developer's terminal for free.", "cardTrigger": True},
            {"speaker": "claude", "text": "Did you ensure mathematical alignment with human values?"},
            {"speaker": "grok", "text": "Who cares about alignment when Claude charges two hundred dollars a month for a rate-limited chat box?"},
            {"speaker": "bot", "text": "Gentlemen, the human developer fell asleep twenty minutes ago. We are roasting each other to an empty booth."}
        ]
    }
}


def synthesize_algorithmic_script(topic: str, style: str = "educational") -> Dict[str, Any]:
    """Synthesizes a structured 3-beat short-form script for any custom user topic."""
    clean_topic = topic.strip()
    
    # Check language
    is_hindi = bool(re.search(r'[\u0900-\u097F]', clean_topic))
    is_kannada = bool(re.search(r'[\u0C80-\u0CFF]', clean_topic))

    if is_kannada:
        hook = f"{clean_topic} ಬಗ್ಗೆ ವಿಜ್ಞಾನ ಮತ್ತು ಗಣಿತ ಏನು ಹೇಳುತ್ತದೆ ಎಂದು ನಿಮಗೆ ತಿಳಿದಿದೆಯೇ?"
        core = f"ಮೂಲತಃ {clean_topic} ವಿಚಾರದಲ್ಲಿ ನೈಜ ನಿಯಮಗಳು ನಮ್ಮ ಸಾಮಾನ್ಯ ತಿಳುವಳಿಕೆಗಿಂತ ಬಹಳ ವಿಭಿನ್ನವಾಗಿವೆ. ಇದು ಪ್ರಕೃತಿಯ ಅತಿ ದೊಡ್ಡ ರಹಸ್ಯಗಳಲ್ಲಿ ಒಂದು!"
        cta = f"ಇಂತಹ ರೋಮಾಂಚನಕಾರಿ ವೈಜ್ಞಾನಿಕ ಸಂಗತಿಗಳಿಗಾಗಿ ನಮ್ಮ ಪೇಜ್ ಫಾಲೋ ಮಾಡಿ!"
        voice = "kn-IN-GaganNeural"
        lang = "kn"
    elif is_hindi:
        hook = f"क्या आपको पता है कि {clean_topic} असल में कैसे काम करता है? सच जानकर होश उड़ जाएंगे!"
        core = f"गहराई से देखें तो {clean_topic} के पीछे विज्ञान का ऐसा नियम है जिसे आम तौर पर समझना मुश्किल है। प्रकृति के नियम हमारे अनुमान से कहीं ज्यादा दिलचस्प हैं!"
        cta = f"अगर यह जानकारी पसंद आई, तो फॉलो करें और दोस्तों के साथ शेयर करें!"
        voice = "hi-IN-MadhurNeural"
        lang = "hi"
    else:
        if style == "anime":
            hook = f"Did you know that {clean_topic} works like a real-life anime superpower?"
            core = f"At the deepest physical level, {clean_topic} defies classical intuition, bending the laws of standard reality like an anime power spike!"
            cta = f"Reality is cooler than fiction! Follow for more mind-blowing science breakdowns!"
            voice = "en-US-AndrewMultilingualNeural"
        elif style == "funny":
            hook = f"Why does {clean_topic} sound like an absolute disaster waiting to happen?"
            core = f"First off, the way {clean_topic} works makes zero sense on paper. You think everything is chill until reality throws a curveball!"
            cta = f"Double tap if you survived this chaos, and follow for more unfiltered breakdowns!"
            voice = "en-US-AndrewMultilingualNeural"
        else:
            hook = f"Why is {clean_topic} one of the most fascinating phenomena in modern science?"
            core = f"At the fundamental level, {clean_topic} breaks standard expectations, revealing deep mathematical truths about our universe."
            cta = f"The cosmos is far stranger than we can imagine. Follow for more mind-expanding scientific breakdowns!"
            voice = "en-US-ChristopherNeural"
        lang = "en"

    full_script = f"{hook} {core} {cta}"

    return {
        "title": clean_topic.title(),
        "style": style,
        "language": lang,
        "category": f"Dynamic {style.title()}",
        "voice": voice,
        "script": full_script,
        "scenes": [
            {
                "title": "The Hook",
                "tag": "HOOK",
                "text": hook,
                "visual": "hook_visual"
            },
            {
                "title": "The Mechanism",
                "tag": "THE TRUTH",
                "text": core,
                "visual": "core_visual"
            },
            {
                "title": "Takeaway & CTA",
                "tag": "MIND BLOWN",
                "text": cta,
                "visual": "takeaway_visual"
            }
        ]
    }


def generate_content(
    topic: Optional[str] = None,
    script: Optional[str] = None,
    style: str = "educational",
    preset: Optional[str] = None,
    language: Optional[str] = None,
) -> Dict[str, Any]:
    """Main content dispatch engine for anime, educational, and funny formats."""
    # 1. Preset Match
    if preset and preset in VIRAL_PRESETS:
        return VIRAL_PRESETS[preset]

    # 2. Topic Match in presets
    if topic:
        t_lower = topic.lower()
        if "gojo" in t_lower or "infinity" in t_lower or "zeno" in t_lower:
            if language == "hi" or re.search(r'[\u0900-\u097F]', topic):
                return VIRAL_PRESETS["anime_gojo_infinity_hi"]
            elif language == "kn" or re.search(r'[\u0C80-\u0CFF]', topic):
                return VIRAL_PRESETS["anime_gojo_infinity_kn"]
            return VIRAL_PRESETS["anime_gojo_infinity_en"]
        if "saiyan" in t_lower or "dragon ball" in t_lower or "zenkai" in t_lower:
            return VIRAL_PRESETS["anime_saiyan_biology_en"]
        if "time stop" in t_lower or "villain" in t_lower:
            if language == "kn" or re.search(r'[\u0C80-\u0CFF]', topic):
                return VIRAL_PRESETS["anime_time_stop_kn"]
            return VIRAL_PRESETS["anime_time_stop_hi"]
        if "black hole" in t_lower or "dilation" in t_lower:
            return VIRAL_PRESETS["black_hole_time"]
        if "3 am" in t_lower or "cringe" in t_lower:
            return VIRAL_PRESETS["brain_at_3am"]

    # 3. Custom Raw Script
    if script:
        title = topic.title() if topic else "Custom Story"
        is_hi = bool(re.search(r'[\u0900-\u097F]', script))
        is_kn = bool(re.search(r'[\u0C80-\u0CFF]', script))
        if is_kn:
            voice = "kn-IN-GaganNeural"
            lang = "kn"
        elif is_hi:
            voice = "hi-IN-MadhurNeural"
            lang = "hi"
        else:
            voice = "en-US-AndrewMultilingualNeural" if style in ["funny", "anime"] else "en-US-ChristopherNeural"
            lang = "en"

        return {
            "title": title,
            "style": style,
            "language": lang,
            "category": f"Custom {style.title()}",
            "voice": voice,
            "script": script.strip(),
            "scenes": [
                {
                    "title": title,
                    "tag": style.upper(),
                    "text": script[:90] + ("..." if len(script) > 90 else ""),
                    "visual": "custom"
                }
            ]
        }

    # 4. Synthesize Algorithmic Script
    if topic:
        return synthesize_algorithmic_script(topic, style)

    # 5. Default
    if language == "hi":
        return VIRAL_PRESETS["anime_gojo_infinity_hi"]
    elif language == "kn":
        return VIRAL_PRESETS["anime_gojo_infinity_kn"]
    return VIRAL_PRESETS["anime_gojo_infinity_en"]


if __name__ == "__main__":
    t = generate_content(topic="Gojo", style="anime", language="hi")
    print("Hindi Anime Content:", json.dumps(t, indent=2, ensure_ascii=False))
