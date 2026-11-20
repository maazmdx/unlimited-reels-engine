"""
Agent 6: Google Drive Cloud Dispatcher
Uploads finalized daily reels, synchronized WebVTT captions, and metadata to Google Drive.
Supports 3 delivery channels:
1. Direct Google Drive REST API (OAuth / Service Account Bearer Token, 0 dependencies)
2. Native `gdrive` CLI
3. Local Drive Sync Mirror directory (~/GoogleDrive/Daily_AI_Reels)
"""

import os
import shutil
import subprocess
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional

class DriveDispatcherAgent:
    """Agent 6: Uploads daily videos + captions directly to Google Drive."""

    def __init__(self, target_folder_name: str = "Daily_AI_Reels"):
        self.target_folder_name = target_folder_name

    def upload_via_drive_api(
        self,
        file_path: Path,
        mime_type: str,
        folder_id: Optional[str] = None,
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Uploads directly to Google Drive API v3 via standard multipart REST request."""
        if not token:
            token = os.environ.get("GOOGLE_DRIVE_TOKEN") or os.environ.get("GDRIVE_ACCESS_TOKEN")
        if not token:
            return None

        metadata: Dict[str, Any] = {"name": file_path.name}
        if folder_id:
            metadata["parents"] = [folder_id]

        boundary = "-------AntigravityReelsBoundary314159"
        delimiter = f"\r\n--{boundary}\r\n".encode("utf-8")
        close_delim = f"\r\n--{boundary}--\r\n".encode("utf-8")

        meta_part = (
            'Content-Type: application/json; charset=UTF-8\r\n\r\n' +
            json.dumps(metadata)
        ).encode("utf-8")

        file_header = f'Content-Type: {mime_type}\r\n\r\n'.encode("utf-8")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body = delimiter + meta_part + delimiter + file_header + file_bytes + close_delim

        req = urllib.request.Request(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
                "Content-Length": str(len(body))
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=90.0) as resp:
                data = json.loads(resp.read().decode())
                print(f"✅ [Agent 6] Google Drive API Upload Succeeded: File ID {data.get('id')}")
                return data
        except Exception as e:
            print(f"⚠️ [Agent 6] Google Drive API direct upload notice: {e}")
            return None

    def upload_reel(
        self,
        video_path: str,
        vtt_path: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        drive_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        print(f"☁️ [Agent 6: Drive Dispatcher] Dispatching '{Path(video_path).name}' to Google Drive...")
        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        drive_folder = drive_folder_id or os.environ.get("GDRIVE_FOLDER_ID")
        upload_records = []

        # 1. Attempt Direct Google Drive REST API (Zero dependency)
        api_res = self.upload_via_drive_api(video_file, "video/mp4", folder_id=drive_folder)
        if api_res:
            upload_records.append({"file": video_file.name, "status": "UPLOADED_API", "id": api_res.get("id")})
            if vtt_path and Path(vtt_path).exists():
                self.upload_via_drive_api(Path(vtt_path), "text/vtt", folder_id=drive_folder)

        # 2. Attempt gdrive CLI if installed
        drive_cli = shutil.which("gdrive")
        if drive_cli and not api_res:
            try:
                cmd = ["gdrive", "files", "upload", str(video_file)]
                if drive_folder:
                    cmd.extend(["--parent", drive_folder])
                print(f"🚀 Running: {' '.join(cmd)}")
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
                if res.returncode == 0:
                    print("✅ Google Drive CLI upload successful!")
                    upload_records.append({"file": video_file.name, "status": "UPLOADED_VIA_GDRIVE", "stdout": res.stdout.strip()})
            except subprocess.TimeoutExpired:
                print("⚠️ gdrive CLI prompt timed out; falling back to local Drive mirror sync directory.")
            except Exception as e:
                print(f"⚠️ gdrive CLI upload notice: {e}")

        # 3. Always maintain local Google Drive mirror sync folder
        local_drive_mirror = Path.home() / "GoogleDrive" / self.target_folder_name
        local_drive_mirror.mkdir(parents=True, exist_ok=True)

        target_vid = local_drive_mirror / video_file.name
        if os.path.realpath(str(video_file)) != os.path.realpath(str(target_vid)):
            shutil.copy2(video_file, target_vid)
        print(f"📁 Synced to Drive Mirror Folder: {target_vid}")

        # Also sync captions
        target_vtt = None
        if vtt_path and Path(vtt_path).exists():
            target_vtt = local_drive_mirror / Path(vtt_path).name
            if os.path.realpath(str(vtt_path)) != os.path.realpath(str(target_vtt)):
                shutil.copy2(vtt_path, target_vtt)
            print(f"📝 Synced Captions: {target_vtt}")

        # Write episode delivery report
        report_path = local_drive_mirror / f"{video_file.stem}_report.json"
        raw_timestamp = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%z"], capture_output=True, text=True).stdout.strip()
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "status": "DELIVERED",
                "video": str(target_vid),
                "captions": str(target_vtt) if target_vtt else None,
                "api_uploads": upload_records,
                "metadata": meta_data or {},
                "timestamp": raw_timestamp
            }, f, indent=2)

        return {
            "status": "DELIVERED",
            "folder": self.target_folder_name,
            "mirror_path": str(target_vid),
            "captions_path": str(target_vtt) if target_vtt else None,
            "report_path": str(report_path),
            "api_records": upload_records
        }


if __name__ == "__main__":
    dispatcher = DriveDispatcherAgent()
    print("Drive Dispatcher ready.")
