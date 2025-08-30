import base64

from google_docs_mcp.clients.drive_client import DriveClient
from google_docs_mcp.clients.google_auth import build_credentials
from google_docs_mcp.models import DOCUMENT_ID_OR_URL_TYPE, DriveExportResult
from google_docs_mcp.tools.docs_tools import normalize_doc_id


def drive_export_file(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    mime_type: str = "application/pdf",
) -> DriveExportResult:
    creds = build_credentials()
    # Accept either document_id or url
    file_id, _, type_ = normalize_doc_id(document_id_or_url)
    drive = DriveClient(creds)
    name, data = drive.export_file(file_id, mime_type)
    return DriveExportResult(
        document_id_or_url=document_id_or_url,
        type=type_,
        file_name=name,
        bytes_b64=base64.b64encode(data).decode("ascii"),
    )
