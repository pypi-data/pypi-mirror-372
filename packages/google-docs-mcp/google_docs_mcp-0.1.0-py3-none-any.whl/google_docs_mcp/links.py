import re

from pydantic import BaseModel


_DOCS_RE = re.compile(r"https?://docs.google.com/document/d/([a-zA-Z0-9_-]+)")
_DRIVE_FILE_RE = re.compile(r"https?://drive.google.com/file/d/([a-zA-Z0-9_-]+)")


class FromUrlResult(BaseModel):
    document_id: str | None
    comment_id: str | None
    is_docs: bool
    is_drive_file: bool


def from_url(url: str) -> FromUrlResult:
    m = _DOCS_RE.search(url)
    if m:
        doc_id = m.group(1)
        comment_id = None
        cm = re.search(r"comment=([^&#]+)", url)
        if cm:
            comment_id = cm.group(1)
        return FromUrlResult(document_id=doc_id, comment_id=comment_id, is_docs=True, is_drive_file=False)
    m2 = _DRIVE_FILE_RE.search(url)
    if m2:
        file_id = m2.group(1)
        return FromUrlResult(document_id=file_id, comment_id=None, is_docs=False, is_drive_file=True)
    return FromUrlResult(document_id=None, comment_id=None, is_docs=False, is_drive_file=False)
