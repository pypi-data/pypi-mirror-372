from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class DocsClient:
    def __init__(self, creds: Credentials) -> None:
        self.creds = creds
        self.svc = build("docs", "v1", credentials=creds, cache_discovery=False)

    def get_document(self, document_id: str) -> dict[str, Any]:
        return self.svc.documents().get(documentId=document_id).execute()

    def append_text(self, document_id: str, text: str) -> str:
        requests = [
            {"insertText": {"text": text, "endOfSegmentLocation": {}}},
        ]
        resp = self.svc.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
        return resp.get("writeControl", {}).get("requiredRevisionId", "")

    def insert_text_at(self, document_id: str, index: int, text: str) -> str:
        requests = [
            {"insertText": {"text": text, "location": {"index": index}}},
        ]
        resp = self.svc.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()
        return resp.get("writeControl", {}).get("requiredRevisionId", "")
