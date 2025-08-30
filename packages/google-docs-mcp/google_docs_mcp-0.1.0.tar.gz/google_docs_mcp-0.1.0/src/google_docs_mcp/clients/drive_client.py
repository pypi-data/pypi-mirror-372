from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class DriveClient:
    def __init__(self, creds: Credentials) -> None:
        self.creds = creds
        self.svc = build("drive", "v3", credentials=creds, cache_discovery=False)

    def export_file(self, file_id: str, mime_type: str) -> tuple[str, bytes]:
        try:
            # export_media does not accept supportsAllDrives
            req = self.svc.files().export_media(fileId=file_id, mimeType=mime_type)
            data = req.execute()
            meta = self.svc.files().get(fileId=file_id, fields="name", supportsAllDrives=True).execute()
            name = meta.get("name", f"{file_id}")
            return name, data
        except HttpError as e:
            raise FileNotFoundError(
                f"Drive export failed for file {file_id}: {e}. "
                "If this is a shared file or not created by this app, ensure your token has "
                "'drive.readonly' scope (set GOOGLE_SCOPES accordingly and re-authorize)."
            ) from e

    def list_comments(self, file_id: str, include_resolved: bool, page_size: int = 100) -> list[dict[str, Any]]:
        try:
            comments: list[dict[str, Any]] = []
            page_token: str | None = None
            while True:
                resp = (
                    self.svc.comments()
                    .list(
                        fileId=file_id,
                        pageSize=page_size,
                        pageToken=page_token,
                        includeDeleted=False,
                        # Partial response fields: use parentheses for nested objects
                        # 'resolved' exists on Comment, not on Reply. Reply has 'action'.
                        fields=(
                            "comments("
                            "id,anchor,author(displayName),createdTime,resolved,content,"
                            "replies(id,author(displayName),createdTime,content,action)"
                            "),nextPageToken"
                        ),
                    )
                    .execute()
                )
                for c in resp.get("comments", []):
                    if not include_resolved and c.get("resolved"):
                        continue
                    comments.append(c)
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
            return comments
        except HttpError as e:
            raise FileNotFoundError(
                f"Drive comments failed for file {file_id}: {e}. "
                "If this is a shared file or not created by this app, ensure your token has "
                "'drive.readonly' scope (set GOOGLE_SCOPES accordingly and re-authorize)."
            ) from e

    def reply_to_comment(self, file_id: str, comment_id: str, message: str) -> str:
        body = {"content": message}
        try:
            resp = self.svc.replies().create(fileId=file_id, commentId=comment_id, body=body).execute()
            return resp.get("id", "")
        except HttpError as e:
            raise FileNotFoundError(
                f"Drive reply failed for file {file_id}/comment {comment_id}: {e}. "
                "Ensure write mode is enabled and token has appropriate Drive scopes."
            ) from e

    def resolve_comment(self, file_id: str, comment_id: str) -> bool:
        try:
            resp = self.svc.comments().update(fileId=file_id, commentId=comment_id, body={"resolved": True}).execute()
            return bool(resp.get("resolved"))
        except HttpError as e:
            raise FileNotFoundError(
                f"Drive resolve failed for file {file_id}/comment {comment_id}: {e}. "
                "Ensure write mode is enabled and token has appropriate Drive scopes."
            ) from e
