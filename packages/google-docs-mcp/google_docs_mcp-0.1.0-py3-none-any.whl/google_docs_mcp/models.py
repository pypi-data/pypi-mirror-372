from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import AnyUrl, BaseModel, Field


class IdOrUrlType(StrEnum):
    ID = "id"
    URL = "url"


class DocsReadFormat(StrEnum):
    MD = "md"
    HTML = "html"


class CommentsListStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    ALL = "all"


EXAMPLE_GOOGLE_DOC_ID = "1_CE35mxijXE0LsGGVkXw-858PL0AfqIPLgoL-xTuuTk"
EXAMPLE_GOOGLE_DOC_URL = f"https://drive.google.com/file/d/{EXAMPLE_GOOGLE_DOC_ID}/view"
EXAMPLE_GOOGLE_DOC_URL_2 = f"https://docs.google.com/document/d/{EXAMPLE_GOOGLE_DOC_ID}/edit"
EXAMPLE_GOOGLE_DOC_COMMENT_ID = "A1B2c3D4e5F6_g7H8Ij9"

DOCUMENT_ID_OR_URL_TYPE = Annotated[
    str,
    Field(
        description="Original identifier that was used (ID or URL)",
        examples=[
            EXAMPLE_GOOGLE_DOC_ID,
            EXAMPLE_GOOGLE_DOC_URL,
            EXAMPLE_GOOGLE_DOC_URL_2,
        ],
    ),
]


class DocsReadResult(BaseModel):
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE
    type: IdOrUrlType = Field(description="Indicates whether the identifier is an ID or URL")
    title: str = Field(description="Document title")
    format: DocsReadFormat
    content: str = Field(description="Document content in the chosen format")
    note: str | None = Field(default=None, description="Conversion/export note")


class CommentReply(BaseModel):
    id: str
    author: str | None
    created: str
    content: str
    resolved: bool


class CommentItem(BaseModel):
    id: str
    anchor: str | None
    author: str | None
    created: str
    resolved: bool
    replies: int
    content: str
    replies_list: list[CommentReply]


class CommentsListResult(BaseModel):
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE
    type: IdOrUrlType
    comments: list[CommentItem]


class CommentsReplyResult(BaseModel):
    reply_id: str


class CommentsResolveResult(BaseModel):
    resolved: bool


class DocsInsertTextResult(BaseModel):
    revision_id: str


class DocsFromUrlResult(BaseModel):
    document_id: str
    comment_id: str | None
    is_docs: bool
    is_drive_file: bool


class DriveExportResult(BaseModel):
    document_id_or_url: str | AnyUrl = Field(description="Original identifier used for export")
    type: IdOrUrlType
    file_name: str
    bytes_b64: str = Field(description="Base64-encoded file bytes of the exported content")


class TokenInfoResource(BaseModel):
    path: Path = Field(description="Path to the token file")
    exists: bool = Field(description="Whether the token file exists")
    scopes: list[str] = Field(default_factory=list, description="Scopes granted by the token")
    requested_scopes: list[str] = Field(default_factory=list, description="Scopes requested by the application")
    scope_note: str | None = Field(None, description="Note about the scope mismatch")
    expiry: datetime | None = Field(None, description="Token expiry date")
    client_id_present: bool = Field(False, description="Whether the client ID is present in the token")
