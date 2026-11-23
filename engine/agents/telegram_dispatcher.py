"""
engine/agents/telegram_dispatcher.py - Telegram Bot Cloud Dispatcher
Delivers finalized daily reels, synchronized SRT subtitles, resource guides,
Instagram captions, and Auto-DM templates directly to a Telegram chat via Telegram Bot API.
Zero new dependencies - uses standard requests library.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
import requests


class TelegramDispatcherAgent:
    """Dispatches rendered daily reels and promotional assets to Telegram via Bot API."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

        if not self.bot_token or not self.chat_id:
            try:
                from kaggle_secrets import UserSecretsClient
                secrets = UserSecretsClient()
                if not self.bot_token:
                    self.bot_token = secrets.get_secret("TELEGRAM_BOT_TOKEN")
                    if self.bot_token:
                        os.environ["TELEGRAM_BOT_TOKEN"] = self.bot_token
                if not self.chat_id:
                    self.chat_id = secrets.get_secret("TELEGRAM_CHAT_ID")
                    if self.chat_id:
                        os.environ["TELEGRAM_CHAT_ID"] = self.chat_id
            except Exception:
                pass

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def dispatch_batch(self, batch_dir: Union[str, Path]) -> Dict[str, Any]:
        """Dispatches all reels and associated metadata in batch_dir to Telegram."""
        if not self.is_configured():
            print("ℹ️ [Telegram] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured; skipping Telegram delivery.")
            return {"status": "SKIPPED_NO_SECRETS", "delivered": 0, "total": 0}

        batch_path = Path(batch_dir).resolve()
        if not batch_path.exists():
            print(f"⚠️ [Telegram] Batch directory not found: {batch_path}")
            return {"status": "NOT_FOUND", "delivered": 0, "total": 0}

        mp4_files = sorted(batch_path.glob("*.mp4"))
        if not mp4_files:
            print(f"ℹ️ [Telegram] No .mp4 reels found in {batch_path}.")
            return {"status": "NO_REELS", "delivered": 0, "total": 0}

        print(f"✈️ [Telegram] Dispatching {len(mp4_files)} reel(s) from '{batch_path.name}' to chat ID {self.chat_id}...")

        base_url = f"https://api.telegram.org/bot{self.bot_token}"
        delivered_count = 0
        total_count = len(mp4_files)

        for idx, mp4_file in enumerate(mp4_files, 1):
            slug = mp4_file.stem
            print(f"\n🚀 [Telegram] Delivering Reel {idx}/{total_count}: {mp4_file.name}...")

            # 1. Load Auto-DM metadata if present
            autodm_path = batch_path / f"{slug}_autodm.json"
            autodm_data: Dict[str, Any] = {}
            if autodm_path.exists():
                try:
                    with open(autodm_path, "r", encoding="utf-8") as af:
                        autodm_data = json.load(af)
                except Exception as e_ad:
                    print(f"   ⚠️ Notice reading {autodm_path.name}: {e_ad}")

            title = autodm_data.get("resource_topic") or slug.replace("_", " ").title()
            keyword = autodm_data.get("keyword") or ""
            official_url = autodm_data.get("official_url") or ""

            # Video caption trimmed <= 1024 chars
            caption_lines = [f"🎬 {title}"]
            if keyword:
                caption_lines.append(f"💬 Auto-DM Keyword: {keyword}")
            if official_url:
                caption_lines.append(f"🔗 Tool Link: {official_url}")
            video_caption = "\n".join(caption_lines)[:1024]

            # 2. Send Video (POST sendVideo with thumbnail and streaming)
            cover_path = batch_path / f"{slug}_cover.png"
            video_sent = False
            video_url = f"{base_url}/sendVideo"
            v_file = None
            c_file = None
            try:
                data = {
                    "chat_id": self.chat_id,
                    "caption": video_caption,
                    "supports_streaming": True,
                }
                files = {}
                v_file = open(mp4_file, "rb")
                files["video"] = (mp4_file.name, v_file, "video/mp4")
                if cover_path.exists():
                    c_file = open(cover_path, "rb")
                    files["thumbnail"] = (cover_path.name, c_file, "image/png")

                resp = requests.post(video_url, data=data, files=files, timeout=300)
                if resp.status_code == 200:
                    print(f"   ✅ Video delivered ({mp4_file.name})")
                    video_sent = True
                else:
                    print(f"   ⚠️ sendVideo HTTP {resp.status_code}: {resp.text[:200]}")
            except Exception as e_vid:
                print(f"   ❌ sendVideo error for {mp4_file.name}: {e_vid}")
            finally:
                if v_file:
                    v_file.close()
                if c_file:
                    c_file.close()

            # 3. Send Instagram Caption + Auto-DM template (POST sendMessage)
            try:
                caption_file = batch_path / f"{slug}_caption.txt"
                full_caption = ""
                if caption_file.exists():
                    with open(caption_file, "r", encoding="utf-8") as cf:
                        full_caption = cf.read().strip()

                dm_template = autodm_data.get("dm_message_template", "")
                if "[DRIVE_GUIDE_LINK]" in dm_template:
                    if official_url:
                        dm_template = dm_template.replace("[DRIVE_GUIDE_LINK]", official_url)
                    else:
                        dm_template = dm_template.replace("📖 Complete 1-Page Setup Guide: [DRIVE_GUIDE_LINK]\n\n", "")
                        dm_template = dm_template.replace("[DRIVE_GUIDE_LINK]", "").strip()

                text_blocks = []
                if full_caption:
                    text_blocks.append(f"📝 INSTAGRAM CAPTION:\n\n{full_caption}")
                if dm_template:
                    text_blocks.append(f"🤖 AUTO-DM TEMPLATE:\n\n{dm_template}")
                if autodm_data.get("public_comment_replies"):
                    replies_str = "\n".join(f"• {r}" for r in autodm_data["public_comment_replies"])
                    text_blocks.append(f"💬 COMMENT REPLIES:\n{replies_str}")

                if text_blocks:
                    msg_text = "\n\n" + ("=" * 35) + "\n\n"
                    full_text = msg_text.join(text_blocks)
                    msg_url = f"{base_url}/sendMessage"
                    for chunk in [full_text[i:i + 4000] for i in range(0, len(full_text), 4000)]:
                        r_msg = requests.post(msg_url, data={"chat_id": self.chat_id, "text": chunk}, timeout=30)
                        if r_msg.status_code == 200:
                            print("   ✅ Caption & Auto-DM text delivered.")
                        else:
                            print(f"   ⚠️ sendMessage HTTP {r_msg.status_code}: {r_msg.text[:200]}")
            except Exception as e_txt:
                print(f"   ⚠️ Text delivery notice: {e_txt}")

            # 4. Send Subtitles (.srt) and Resource Guide (.html) via sendDocument
            for doc_name, doc_label in [
                (f"{slug}.srt", "Subtitles"),
                (f"{slug}_resource_guide.html", "Resource Guide")
            ]:
                doc_path = batch_path / doc_name
                if doc_path.exists():
                    try:
                        doc_url = f"{base_url}/sendDocument"
                        with open(doc_path, "rb") as df:
                            r_doc = requests.post(
                                doc_url,
                                data={"chat_id": self.chat_id, "caption": f"📎 {doc_label}: {doc_name}"},
                                files={"document": (doc_path.name, df)},
                                timeout=60
                            )
                        if r_doc.status_code == 200:
                            print(f"   ✅ Document delivered: {doc_name}")
                        else:
                            print(f"   ⚠️ sendDocument HTTP {r_doc.status_code} for {doc_name}: {r_doc.text[:200]}")
                    except Exception as e_doc:
                        print(f"   ⚠️ Document delivery notice ({doc_name}): {e_doc}")

            if video_sent:
                delivered_count += 1

        print(f"\n✅ [Telegram] Delivered {delivered_count}/{total_count} reels to chat")
        return {
            "status": "DELIVERED" if delivered_count == total_count else "PARTIAL",
            "delivered": delivered_count,
            "total": total_count,
        }

    def dispatch_latest_batch(self, out_dir: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
        """Finds the newest out/morning_YYYY_MM_DD batch folder and dispatches all files to Telegram."""
        if out_dir:
            root_out = Path(out_dir).resolve()
        else:
            root_out = Path(__file__).resolve().parent.parent.parent / "out"

        if not root_out.exists():
            print(f"ℹ️ [Telegram] Directory {root_out} does not exist.")
            return None

        # If passed directly a directory containing mp4 files
        if list(root_out.glob("*.mp4")):
            return self.dispatch_batch(root_out)

        batch_folders = sorted(root_out.glob("morning_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not batch_folders:
            print("ℹ️ [Telegram] No morning batch folders found in out/.")
            return None

        latest_batch = batch_folders[0]
        return self.dispatch_batch(latest_batch)


if __name__ == "__main__":
    dispatcher = TelegramDispatcherAgent()
    dispatcher.dispatch_latest_batch()
