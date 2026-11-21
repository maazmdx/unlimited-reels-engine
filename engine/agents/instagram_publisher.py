"""
Agent: Meta Graph API Instagram Reels Auto-Publisher
Publishes rendered reels to Instagram using Meta's official 3-step Reels publishing API:
1. Container Creation: POST /{ig_user_id}/media (media_type=REELS, video_url, caption)
2. Status Polling: GET /{container_id}?fields=status_code until FINISHED
3. Media Publish: POST /{ig_user_id}/media_publish (creation_id=container_id)

Zero extra dependencies (uses requests).
Only activates when IG_USER_ID and IG_ACCESS_TOKEN are set and --auto-publish is passed.
"""

import os
import time
from typing import Dict, Any, Optional
import requests


class InstagramPublisherAgent:
    """Publishes Reels to Instagram via official Meta Graph API v21.0."""

    GRAPH_API_VERSION = "v21.0"
    GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(
        self,
        ig_user_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.ig_user_id = ig_user_id or os.environ.get("IG_USER_ID")
        self.access_token = access_token or os.environ.get("IG_ACCESS_TOKEN")

        # Fallback to kaggle_secrets if available
        if not self.ig_user_id or not self.access_token:
            try:
                from kaggle_secrets import UserSecretsClient
                secrets = UserSecretsClient()
                if not self.ig_user_id:
                    self.ig_user_id = secrets.get_secret("IG_USER_ID")
                if not self.access_token:
                    self.access_token = secrets.get_secret("IG_ACCESS_TOKEN")
            except Exception:
                pass

    def is_configured(self) -> bool:
        """Returns True if both IG_USER_ID and IG_ACCESS_TOKEN are present."""
        return bool(self.ig_user_id and self.access_token)

    def publish_reel(
        self,
        video_url: str,
        caption: str,
        cover_url: Optional[str] = None,
        max_poll_sec: int = 180,
    ) -> Dict[str, Any]:
        """
        Executes Meta's 3-step Reels publishing flow:
        1. Initialize Media Container
        2. Poll until status_code == FINISHED
        3. Publish Media Container
        """
        if not self.is_configured():
            print("ℹ️ [InstagramPublisher] IG_USER_ID or IG_ACCESS_TOKEN not set; skipping auto-publish.")
            return {
                "status": "SKIPPED_NOT_CONFIGURED",
                "reason": "Missing IG_USER_ID or IG_ACCESS_TOKEN",
            }

        if not video_url or not str(video_url).startswith("http"):
            print(f"⚠️ [InstagramPublisher] Invalid video_url for Meta Graph API: {video_url}")
            return {
                "status": "ERROR",
                "reason": f"Invalid video_url: {video_url}. Meta requires a publicly accessible HTTPS video URL.",
            }

        print(f"\n📸 [InstagramPublisher] Initiating official Meta Graph API Reels upload for IG User: {self.ig_user_id}...")

        # Step 1: Create Container
        container_url = f"{self.GRAPH_API_BASE}/{self.ig_user_id}/media"
        container_payload: Dict[str, Any] = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self.access_token,
        }
        if cover_url and str(cover_url).startswith("http"):
            container_payload["cover_url"] = cover_url

        try:
            r1 = requests.post(container_url, data=container_payload, timeout=30.0)
            res1 = r1.json()
            if r1.status_code != 200 or "id" not in res1:
                err_msg = res1.get("error", {}).get("message", r1.text[:200])
                print(f"❌ [InstagramPublisher] Container creation failed: {err_msg}")
                return {"status": "ERROR_CONTAINER", "error": err_msg}

            container_id = res1["id"]
            print(f"   📦 Container created: {container_id}. Polling processing status...")
        except Exception as e:
            print(f"❌ [InstagramPublisher] Container request error: {e}")
            return {"status": "ERROR_EXCEPTION", "error": str(e)}

        # Step 2: Poll status
        poll_url = f"{self.GRAPH_API_BASE}/{container_id}"
        poll_params = {
            "fields": "status_code,status",
            "access_token": self.access_token,
        }
        start_time = time.time()
        ready = False

        while time.time() - start_time < max_poll_sec:
            time.sleep(5.0)
            try:
                r2 = requests.get(poll_url, params=poll_params, timeout=15.0)
                res2 = r2.json()
                status_code = res2.get("status_code", "UNKNOWN")
                print(f"   ⏳ Container status: {status_code} ({int(time.time() - start_time)}s elapsed)")

                if status_code == "FINISHED":
                    ready = True
                    break
                elif status_code == "ERROR":
                    err_details = res2.get("status", "Unknown transcoding error")
                    print(f"❌ [InstagramPublisher] Meta video processing failed: {err_details}")
                    return {"status": "ERROR_PROCESSING", "error": err_details}
            except Exception as e_poll:
                print(f"   ⚠️ Polling notice: {e_poll}")

        if not ready:
            print(f"⚠️ [InstagramPublisher] Timed out waiting for container to process after {max_poll_sec}s.")
            return {"status": "TIMEOUT", "container_id": container_id}

        # Step 3: Publish container
        publish_url = f"{self.GRAPH_API_BASE}/{self.ig_user_id}/media_publish"
        publish_payload = {
            "creation_id": container_id,
            "access_token": self.access_token,
        }

        try:
            r3 = requests.post(publish_url, data=publish_payload, timeout=30.0)
            res3 = r3.json()
            if r3.status_code != 200 or "id" not in res3:
                err_pub = res3.get("error", {}).get("message", r3.text[:200])
                print(f"❌ [InstagramPublisher] Publishing failed: {err_pub}")
                return {"status": "ERROR_PUBLISH", "error": err_pub}

            media_id = res3["id"]
            print(f"✅ [InstagramPublisher] Reel published! Media ID: {media_id}")

            # Fetch permalink
            permalink = None
            try:
                r_perm = requests.get(
                    f"{self.GRAPH_API_BASE}/{media_id}",
                    params={"fields": "permalink", "access_token": self.access_token},
                    timeout=10.0,
                )
                permalink = r_perm.json().get("permalink")
            except Exception:
                pass

            if permalink:
                print(f"\n🎉 [Instagram Live] Reel is LIVE on Instagram!\n👉 {permalink}\n")

            return {
                "status": "PUBLISHED",
                "media_id": media_id,
                "permalink": permalink,
                "container_id": container_id,
            }
        except Exception as e_pub:
            print(f"❌ [InstagramPublisher] Publish request exception: {e_pub}")
            return {"status": "ERROR_EXCEPTION", "error": str(e_pub)}


if __name__ == "__main__":
    pub = InstagramPublisherAgent()
    print(f"Instagram Publisher ready. Configured: {pub.is_configured()}")
