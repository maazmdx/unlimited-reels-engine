"""
Agent 6: Google Drive Cloud Dispatcher
Uploads finalized daily reels, synchronized WebVTT captions, and metadata to Google Drive.
Supports:
1. Real Google Drive v3 API via Service Account JSON (google-api-python-client & google-auth)
2. Direct multipart REST API (OAuth Bearer Token fallback)
3. Native gdrive CLI fallback
4. Local Drive Sync Mirror directory (~/GoogleDrive/Daily_AI_Reels)
"""

import os
import shutil
import subprocess
import json
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional, List


class DriveDispatcherAgent:
    """Agent 6: Uploads daily videos + captions directly to Google Drive."""

    def __init__(self, target_folder_name: str = "Daily_AI_Reels"):
        self.target_folder_name = target_folder_name

    def get_drive_service(self):
        """
        Initializes Google Drive v3 API service using Service Account credentials.
        Accepts GDRIVE_CREDENTIALS as a JSON string or path to a credentials JSON file.
        """
        creds_data = os.environ.get("GDRIVE_CREDENTIALS")
        if not creds_data:
            try:
                from kaggle_secrets import UserSecretsClient
                creds_data = UserSecretsClient().get_secret("GDRIVE_CREDENTIALS")
                if creds_data:
                    os.environ["GDRIVE_CREDENTIALS"] = creds_data
            except Exception:
                pass

        if not creds_data:
            return None

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            print("ℹ️ [DriveDispatcher] 'google-api-python-client' or 'google-auth' not available; using fallback.")
            return None

        scopes = ["https://www.googleapis.com/auth/drive"]
        try:
            # Check if it's a file path
            if os.path.exists(creds_data) and os.path.isfile(creds_data):
                creds = service_account.Credentials.from_service_account_file(creds_data, scopes=scopes)
            else:
                # Parse as JSON string
                info = json.loads(creds_data)
                creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
            return build("drive", "v3", credentials=creds, cache_discovery=False)
        except Exception as e:
            print(f"⚠️ [DriveDispatcher] Google Service Account auth notice: {e}")
            return None

    def get_or_create_subfolder(self, service, parent_folder_id: str, subfolder_name: str) -> Optional[Dict[str, str]]:
        """Finds or creates a dated subfolder inside parent_folder_id on Google Drive."""
        try:
            safe_name = subfolder_name.replace("'", "\\'")
            q = (
                f"'{parent_folder_id}' in parents and "
                f"name = '{safe_name}' and "
                f"mimeType = 'application/vnd.google-apps.folder' and "
                f"trashed = false"
            )
            res = service.files().list(q=q, spaces="drive", fields="files(id, name, webViewLink)").execute()
            files = res.get("files", [])
            if files:
                f = files[0]
                link = f.get("webViewLink") or f"https://drive.google.com/drive/folders/{f.get('id')}"
                return {"id": f.get("id"), "webViewLink": link}

            # Create folder
            folder_meta = {
                "name": subfolder_name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id],
            }
            folder = service.files().create(body=folder_meta, fields="id, name, webViewLink").execute()
            f_id = folder.get("id")
            link = folder.get("webViewLink") or f"https://drive.google.com/drive/folders/{f_id}"
            return {"id": f_id, "webViewLink": link}
        except Exception as e:
            print(f"⚠️ [DriveDispatcher] Subfolder lookup/create error for '{subfolder_name}': {e}")
            return None

    def upload_file_to_folder(self, service, file_path: Path, target_folder_id: str) -> Optional[Dict[str, Any]]:
        """Uploads or updates a file in target_folder_id using Google Drive API."""
        if not file_path.exists():
            return None

        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError:
            return None

        name = file_path.name
        mime_types = {
            ".mp4": "video/mp4",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".txt": "text/plain",
            ".json": "application/json",
            ".vtt": "text/vtt",
            ".srt": "text/plain",
        }
        mimetype = mime_types.get(file_path.suffix.lower(), "application/octet-stream")

        try:
            safe_name = name.replace("'", "\\'")
            q = f"'{target_folder_id}' in parents and name = '{safe_name}' and trashed = false"
            res = service.files().list(q=q, spaces="drive", fields="files(id, name)").execute()
            existing = res.get("files", [])

            media = MediaFileUpload(str(file_path), mimetype=mimetype, resumable=True)

            if existing:
                file_id = existing[0]["id"]
                updated = service.files().update(fileId=file_id, media_body=media, fields="id, name, webViewLink").execute()
                return updated
            else:
                meta = {"name": name, "parents": [target_folder_id]}
                created = service.files().create(body=meta, media_body=media, fields="id, name, webViewLink").execute()
                return created
        except Exception as e:
            print(f"⚠️ [DriveDispatcher] Error uploading '{name}': {e}")
            return None

    def upload_batch_folder(self, batch_dir: Path, drive_parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Uploads all files from a batch folder (out/morning_YYYY_MM_DD/) into
        a dated subfolder morning_YYYY_MM_DD inside GDRIVE_FOLDER_ID on Google Drive.
        Prints clickable folder link.
        """
        if not batch_dir.exists():
            print(f"⚠️ [DriveDispatcher] Batch directory not found: {batch_dir}")
            return None

        parent_id = drive_parent_folder_id or os.environ.get("GDRIVE_FOLDER_ID")
        if not parent_id:
            try:
                from kaggle_secrets import UserSecretsClient
                parent_id = UserSecretsClient().get_secret("GDRIVE_FOLDER_ID")
                if parent_id:
                    os.environ["GDRIVE_FOLDER_ID"] = parent_id
            except Exception:
                pass

        if not parent_id:
            print("ℹ️ [DriveDispatcher] GDRIVE_FOLDER_ID not set; skipping Drive upload cleanly.")
            return None

        service = self.get_drive_service()
        if not service:
            print("ℹ️ [DriveDispatcher] GDRIVE_CREDENTIALS not configured; skipping Drive upload cleanly.")
            return None

        subfolder_name = batch_dir.name  # e.g. "morning_2026_11_21"
        print(f"☁️ [DriveDispatcher] Uploading batch '{subfolder_name}' to Google Drive folder ID: {parent_id}...")

        subfolder_info = self.get_or_create_subfolder(service, parent_id, subfolder_name)
        if not subfolder_info or not subfolder_info.get("id"):
            print("❌ [DriveDispatcher] Could not create or access subfolder on Google Drive.")
            return None

        subfolder_id = subfolder_info["id"]

        # Gather all files from the batch directory (.mp4, _cover.png, _caption.txt, _autodm.json, batch_report.json, etc.)
        all_files = sorted([p for p in batch_dir.iterdir() if p.is_file()])
        uploaded_count = 0

        for f_path in all_files:
            res = self.upload_file_to_folder(service, f_path, subfolder_id)
            if res:
                uploaded_count += 1
                size_kb = f_path.stat().st_size / 1024
                print(f"   ⬆️ Uploaded: {f_path.name} ({size_kb:.1f} KB)")

                # If this file is a resource guide, make it publicly readable and inject into _autodm.json
                if f_path.name.endswith("_resource_guide.html"):
                    try:
                        service.permissions().create(
                            fileId=res["id"],
                            body={"role": "reader", "type": "anyone"},
                            fields="id"
                        ).execute()
                        guide_web_link = res.get("webViewLink") or f"https://drive.google.com/file/d/{res['id']}/view?usp=sharing"
                        print(f"   📖 [Resource Guide] Public reader access granted: {guide_web_link}")

                        # Find matching _autodm.json and inject real public guide link
                        matching_autodm = f_path.with_name(f_path.name.replace("_resource_guide.html", "_autodm.json"))
                        if matching_autodm.exists():
                            with open(matching_autodm, "r", encoding="utf-8") as af:
                                ad_data = json.load(af)
                            ad_data["guide_drive_link"] = guide_web_link
                            tpl = ad_data.get("dm_message_template", "")
                            if "[DRIVE_GUIDE_LINK]" in tpl:
                                ad_data["dm_message_template"] = tpl.replace("[DRIVE_GUIDE_LINK]", guide_web_link)
                            with open(matching_autodm, "w", encoding="utf-8") as af:
                                json.dump(ad_data, af, indent=2, ensure_ascii=False)
                            # Re-upload updated autodm.json to Drive
                            self.upload_file_to_folder(service, matching_autodm, subfolder_id)
                            print(f"   💉 [Auto-DM] Injected live Drive guide link into {matching_autodm.name}")
                    except Exception as e_guide:
                        print(f"   ⚠️ [Resource Guide] Public permission notice: {e_guide}")

        folder_link = subfolder_info.get("webViewLink") or f"https://drive.google.com/drive/folders/{subfolder_id}"
        print(f"\n🎉 [Google Drive] {uploaded_count}/{len(all_files)} files uploaded successfully to subfolder '{subfolder_name}'!")
        print(f"🔗 Clickable Google Drive Folder Link:\n👉 {folder_link}\n")
        return folder_link

    def dispatch_latest_batch(self, out_dir: Optional[Path] = None) -> Optional[str]:
        """Finds the newest out/morning_YYYY_MM_DD batch folder and uploads all files."""
        root_out = Path(out_dir) if out_dir else Path(__file__).resolve().parent.parent.parent / "out"
        if not root_out.exists():
            print(f"ℹ️ [DriveDispatcher] Output directory {root_out} does not exist.")
            return None

        batch_folders = sorted(root_out.glob("morning_*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not batch_folders:
            print("ℹ️ [DriveDispatcher] No morning batch folders found in out/.")
            return None

        latest_batch = batch_folders[0]
        return self.upload_batch_folder(latest_batch)

    def upload_via_drive_api(
        self,
        file_path: Path,
        mime_type: str,
        folder_id: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Uploads directly to Google Drive API v3 via standard multipart REST request (Bearer token)."""
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
            "Content-Type: application/json; charset=UTF-8\r\n\r\n" +
            json.dumps(metadata)
        ).encode("utf-8")

        file_header = f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body = delimiter + meta_part + delimiter + file_header + file_bytes + close_delim

        req = urllib.request.Request(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/related; boundary={boundary}",
                "Content-Length": str(len(body)),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90.0) as resp:
                data = json.loads(resp.read().decode())
                print(f"✅ [DriveDispatcher] Google Drive API Upload Succeeded: File ID {data.get('id')}")
                return data
        except Exception as e:
            print(f"⚠️ [DriveDispatcher] Google Drive API direct upload notice: {e}")
            return None

    def upload_reel(
        self,
        video_path: str,
        vtt_path: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        drive_folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Uploads reel and all batch assets to Google Drive.
        Checks Service Account first, falls back to direct REST or gdrive CLI, and always maintains local mirror.
        """
        print(f"☁️ [Agent 6: Drive Dispatcher] Dispatching '{Path(video_path).name}' to Google Drive...")
        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        drive_folder = drive_folder_id or os.environ.get("GDRIVE_FOLDER_ID")
        if not drive_folder:
            try:
                from kaggle_secrets import UserSecretsClient
                drive_folder = UserSecretsClient().get_secret("GDRIVE_FOLDER_ID")
                if drive_folder:
                    os.environ["GDRIVE_FOLDER_ID"] = drive_folder
            except Exception:
                pass

        upload_records = []
        drive_link = None

        # 1. Primary: Real Google Drive v3 Service Account Upload
        service = self.get_drive_service()
        if service and drive_folder:
            # Check if this video is inside a morning batch folder
            batch_dir = video_file.parent
            subfolder_name = batch_dir.name if batch_dir.name.startswith("morning_") else self.target_folder_name
            subfolder_info = self.get_or_create_subfolder(service, drive_folder, subfolder_name)

            if subfolder_info and subfolder_info.get("id"):
                sub_id = subfolder_info["id"]
                drive_link = subfolder_info.get("webViewLink") or f"https://drive.google.com/drive/folders/{sub_id}"

                # Upload all assets in this batch directory (.mp4, _cover.png, _caption.txt, _autodm.json, batch_report.json)
                files_to_upload = [video_file]
                if vtt_path and Path(vtt_path).exists():
                    files_to_upload.append(Path(vtt_path))

                if batch_dir.exists() and batch_dir.name.startswith("morning_"):
                    for extra in batch_dir.iterdir():
                        if extra.is_file() and extra not in files_to_upload:
                            files_to_upload.append(extra)

                for f_item in files_to_upload:
                    res = self.upload_file_to_folder(service, f_item, sub_id)
                    if res:
                        upload_records.append({"file": f_item.name, "status": "UPLOADED_SERVICE_ACCOUNT", "id": res.get("id")})
                        if f_item.name.endswith("_resource_guide.html"):
                            try:
                                service.permissions().create(
                                    fileId=res["id"],
                                    body={"role": "reader", "type": "anyone"},
                                    fields="id"
                                ).execute()
                                guide_web_link = res.get("webViewLink") or f"https://drive.google.com/file/d/{res['id']}/view?usp=sharing"
                                print(f"   📖 [Resource Guide] Public reader access granted: {guide_web_link}")

                                matching_autodm = f_item.with_name(f_item.name.replace("_resource_guide.html", "_autodm.json"))
                                if matching_autodm.exists():
                                    with open(matching_autodm, "r", encoding="utf-8") as af:
                                        ad_data = json.load(af)
                                    ad_data["guide_drive_link"] = guide_web_link
                                    tpl = ad_data.get("dm_message_template", "")
                                    if "[DRIVE_GUIDE_LINK]" in tpl:
                                        ad_data["dm_message_template"] = tpl.replace("[DRIVE_GUIDE_LINK]", guide_web_link)
                                    with open(matching_autodm, "w", encoding="utf-8") as af:
                                        json.dump(ad_data, af, indent=2, ensure_ascii=False)
                                    self.upload_file_to_folder(service, matching_autodm, sub_id)
                                    print(f"   💉 [Auto-DM] Injected live Drive guide link into {matching_autodm.name}")
                            except Exception as e_guide:
                                print(f"   ⚠️ [Resource Guide] Public permission notice: {e_guide}")

                print(f"\n🎉 [Google Drive] Assets uploaded to dated subfolder '{subfolder_name}'!")
                print(f"🔗 Clickable Google Drive Folder Link:\n👉 {drive_link}\n")

        # 2. Secondary: Direct Multipart REST API fallback (if Bearer token present)
        if not upload_records:
            api_res = self.upload_via_drive_api(video_file, "video/mp4", folder_id=drive_folder)
            if api_res:
                upload_records.append({"file": video_file.name, "status": "UPLOADED_API", "id": api_res.get("id")})
                if vtt_path and Path(vtt_path).exists():
                    self.upload_via_drive_api(Path(vtt_path), "text/vtt", folder_id=drive_folder)

        # 3. Tertiary: Native gdrive CLI if installed
        drive_cli = shutil.which("gdrive")
        if drive_cli and not upload_records:
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
                print("⚠️ gdrive CLI prompt timed out; falling back to local Drive mirror.")
            except Exception as e:
                print(f"⚠️ gdrive CLI upload notice: {e}")

        # 4. Local Google Drive mirror sync folder (Always maintained)
        local_drive_mirror = Path.home() / "GoogleDrive" / self.target_folder_name
        local_drive_mirror.mkdir(parents=True, exist_ok=True)

        target_vid = local_drive_mirror / video_file.name
        if os.path.realpath(str(video_file)) != os.path.realpath(str(target_vid)):
            shutil.copy2(video_file, target_vid)
        print(f"📁 Synced to Drive Mirror Folder: {target_vid}")

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
                "drive_link": drive_link,
                "metadata": meta_data or {},
                "timestamp": raw_timestamp,
            }, f, indent=2)

        return {
            "status": "DELIVERED" if upload_records else "MIRRORED_LOCALLY",
            "folder": self.target_folder_name,
            "mirror_path": str(target_vid),
            "captions_path": str(target_vtt) if target_vtt else None,
            "report_path": str(report_path),
            "api_records": upload_records,
            "drive_link": drive_link,
        }


if __name__ == "__main__":
    dispatcher = DriveDispatcherAgent()
    print("Drive Dispatcher ready.")
    link = dispatcher.dispatch_latest_batch()
    if link:
        print(f"Dispatched latest batch to: {link}")
