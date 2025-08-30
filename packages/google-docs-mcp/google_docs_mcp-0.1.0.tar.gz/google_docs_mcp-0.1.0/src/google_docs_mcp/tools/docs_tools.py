from fastmcp.exceptions import ToolError
from markdownify import markdownify as md
from pydantic import HttpUrl

from google_docs_mcp.clients.docs_client import DocsClient
from google_docs_mcp.clients.drive_client import DriveClient
from google_docs_mcp.clients.google_auth import build_credentials
from google_docs_mcp.config import get_settings
from google_docs_mcp.links import from_url
from google_docs_mcp.models import (
    DOCUMENT_ID_OR_URL_TYPE,
    CommentItem,
    CommentReply,
    CommentsListResult,
    CommentsListStatus,
    CommentsReplyResult,
    CommentsResolveResult,
    DocsFromUrlResult,
    DocsInsertTextResult,
    DocsReadFormat,
    DocsReadResult,
    IdOrUrlType,
)


settings = get_settings()


def normalize_doc_id(document_id_or_url: str | HttpUrl) -> tuple[str, str, IdOrUrlType]:
    """
    Normalize a document ID or URL to a tuple of (document ID, URL, ID or URL type).

    :param document_id_or_url: the document ID or URL to normalize
    :return: a tuple of (document ID, URL, ID or URL type)
    :raises ValueError: if the document ID or URL is not supported
    """
    try:
        document_id_or_url = HttpUrl(document_id_or_url)
        res = from_url(str(document_id_or_url))
        if res.document_id:
            return res.document_id, str(document_id_or_url), IdOrUrlType.URL
    except ValueError:
        doc_id = str(document_id_or_url)
        url = f"https://docs.google.com/document/d/{doc_id}/edit"
        return doc_id, url, IdOrUrlType.ID
    raise ToolError("document_id or url is required")


def docs_from_url(url: str) -> DocsFromUrlResult:
    res = from_url(url)
    if not res.document_id:
        raise ToolError("Unsupported URL or missing IDs")
    return DocsFromUrlResult(
        document_id=res.document_id,
        comment_id=res.comment_id,
        is_docs=res.is_docs,
        is_drive_file=res.is_drive_file,
    )


def docs_read(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    doc_format: DocsReadFormat,
) -> DocsReadResult:
    creds = build_credentials()
    doc_id, url, _ = normalize_doc_id(document_id_or_url)
    if doc_format == DocsReadFormat.HTML:
        drive = DriveClient(creds)
        name, data = drive.export_file(doc_id, "text/html")
        content = data.decode("utf-8", errors="replace")
        return DocsReadResult(
            title=name,
            format=DocsReadFormat.HTML,
            content=content,
            document_id=doc_id,
            url=url,
            note="Exported via Drive for higher fidelity",
        )
    docs = DocsClient(creds)
    d = docs.get_document(doc_id)
    title = d.get("title", "Untitled")
    try:
        drive = DriveClient(creds)
        _, data = drive.export_file(doc_id, "text/html")
        html = data.decode("utf-8", errors="replace")
        content_md = md(html)
        note = "Markdown converted from Drive HTML export"
    except Exception:
        structural = []
        for body_el in d.get("body", {}).get("content", []):
            para = body_el.get("paragraph")
            if not para:
                continue
            texts = []
            for el in para.get("elements", []):
                t = el.get("textRun", {}).get("content")
                if t:
                    texts.append(t)
            if texts:
                structural.append("".join(texts))
        content_md = "\n\n".join(structural)
        note = "Best-effort Markdown from structural content"
    return DocsReadResult(
        title=title,
        format=DocsReadFormat.MD,
        content=content_md,
        document_id=doc_id,
        url=url,
        note=note,
    )


def comments_list(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    status: CommentsListStatus,
    limit: int,
) -> CommentsListResult:
    creds = build_credentials()
    file_id, _, type_ = normalize_doc_id(document_id_or_url)
    include_resolved = status in (CommentsListStatus.RESOLVED, CommentsListStatus.ALL)
    drive = DriveClient(creds)
    items: list[CommentItem] = []
    for c in drive.list_comments(file_id, include_resolved=include_resolved, page_size=limit):
        replies = [
            CommentReply(
                id=r.get("id", ""),
                author=(r.get("author", {}) or {}).get("displayName"),
                created=r.get("createdTime", ""),
                content=r.get("content", ""),
                resolved=bool(r.get("action") == "resolve"),
            )
            for r in c.get("replies", [])
        ]
        items.append(
            CommentItem(
                id=c.get("id", ""),
                anchor=c.get("anchor"),
                author=(c.get("author", {}) or {}).get("displayName"),
                created=c.get("createdTime", ""),
                resolved=bool(c.get("resolved")),
                replies=len(replies),
                content=c.get("content", ""),
                replies_list=replies,
            )
        )
    return CommentsListResult(document_id_or_url=document_id_or_url, type=type_, comments=items)


def _require_write_enabled() -> None:
    if settings.write_mode != "enabled":
        raise ToolError("Write tools are disabled. Set MCP_WRITE_MODE=enabled to proceed.")


def comments_reply(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    comment_id: str,
    message: str,
) -> CommentsReplyResult:
    creds = build_credentials()
    _require_write_enabled()
    file_id, _, _ = normalize_doc_id(document_id_or_url)
    drive = DriveClient(creds)
    reply_id = drive.reply_to_comment(file_id, comment_id, message)
    return CommentsReplyResult(reply_id=reply_id)


def comments_resolve(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    comment_id: str,
) -> CommentsResolveResult:
    creds = build_credentials()
    _require_write_enabled()
    file_id, _, _ = normalize_doc_id(document_id_or_url)
    drive = DriveClient(creds)
    ok = drive.resolve_comment(file_id, comment_id)
    return CommentsResolveResult(resolved=ok)


def docs_insert_text(
    document_id_or_url: DOCUMENT_ID_OR_URL_TYPE,
    text: str,
    location_index: int | None,
) -> DocsInsertTextResult:
    creds = build_credentials()
    _require_write_enabled()
    doc_id, _, _ = normalize_doc_id(document_id_or_url)
    docs = DocsClient(creds)
    if location_index is not None:
        rev = docs.insert_text_at(doc_id, location_index, text)
    else:
        rev = docs.append_text(doc_id, text)
    return DocsInsertTextResult(revision_id=rev)
