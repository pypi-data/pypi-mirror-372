import base64

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptResult
from mcp.types import ToolAnnotations
from pydantic import Field, HttpUrl

from google_docs_mcp import models
from google_docs_mcp.clients.google_auth import token_info
from google_docs_mcp.config import PROJECT_NAME, get_settings
from google_docs_mcp.tools import docs_tools, drive_tools


mcp = FastMCP(
    PROJECT_NAME,
    instructions=(
        "This MCP server provides tools for interacting with Google Docs.\n"
        "Also provides Google Drive helper just for exporting files."
    ),
    include_fastmcp_meta=False,
)

settings = get_settings()


# Tools (schemas inferred from Pydantic models)
@mcp.tool(
    "docs.read",
    title="Read a Google Doc",
    description="Read a Google Doc by ID or URL and return Markdown or HTML",
    annotations=ToolAnnotations(
        title="Read a Google Doc",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def docs_read(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    format: Annotated[models.DocsReadFormat, Field(description="Output format: md or html")] = models.DocsReadFormat.MD,
) -> models.DocsReadResult:
    res = docs_tools.docs_read(document_id_or_url, doc_format=format)
    return models.DocsReadResult(
        document_id_or_url=str(document_id_or_url),
        type=res.type,
        title=res.title,
        format=res.format,
        content=res.content,
        note=res.note,
    )


@mcp.tool(
    "comments.list",
    title="List comments on a Doc",
    description="List comments on a Google Doc by ID or URL",
    annotations=ToolAnnotations(
        title="List comments on a Doc",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def comments_list(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    status: Annotated[
        models.CommentsListStatus,
        Field(description="Comment status filter"),
    ] = models.CommentsListStatus.OPEN,
    limit: Annotated[int, Field(ge=1, le=100, description="Max comments to fetch")] = 100,
) -> models.CommentsListResult:
    res = docs_tools.comments_list(document_id_or_url, status, limit)
    return models.CommentsListResult(
        document_id_or_url=str(document_id_or_url),
        type=res.type,
        comments=res.comments,
    )


@mcp.tool(
    "comments.reply",
    title="Reply to a comment (write gated)",
    description="Reply to a comment on a Google Doc by ID or URL",
    annotations=ToolAnnotations(
        title="Reply to a comment",
        readOnlyHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    enabled=settings.is_write_mode,
)
def comments_reply(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    comment_id: Annotated[str, Field(description="Target comment ID", examples=[models.EXAMPLE_GOOGLE_DOC_COMMENT_ID])],
    message: Annotated[str, Field(description="Reply text", examples=["Great idea!"])],
) -> models.CommentsReplyResult:
    return docs_tools.comments_reply(document_id_or_url, comment_id, message)


@mcp.tool(
    "comments.resolve",
    title="Resolve a comment (write gated)",
    description="Resolve a comment on a Google Doc by ID or URL",
    annotations=ToolAnnotations(
        title="Resolve a comment",
        readOnlyHint=False,
        idempotentHint=False,
        destructiveHint=True,
        openWorldHint=True,
    ),
    enabled=settings.is_write_mode,
)
def comments_resolve(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    comment_id: Annotated[
        str, Field(description="Comment ID to resolve", examples=[models.EXAMPLE_GOOGLE_DOC_COMMENT_ID])
    ],
) -> models.CommentsResolveResult:
    return docs_tools.comments_resolve(document_id_or_url, comment_id)


@mcp.tool(
    "docs.insert_text",
    title="Insert or append text to a Doc (write gated)",
    description="Insert or append text to a Doc by ID or URL",
    annotations=ToolAnnotations(
        title="Insert or append text to a Doc",
        readOnlyHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
    enabled=settings.is_write_mode,
)
def docs_insert_text(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    text: Annotated[str, Field(description="Text to insert", examples=["Great idea!"])],
    location_index: Annotated[int | None, Field(ge=1, description="Exact Docs index", examples=[10])] = None,
    # location_end: Annotated[bool, Field(description="Append to end when true")] = True,
) -> models.DocsInsertTextResult:
    return docs_tools.docs_insert_text(document_id_or_url, text, location_index)


@mcp.tool(
    "docs.from_url",
    title="Normalize a Docs/Drive URL to IDs",
    description="Normalize a Docs/Drive URL to IDs",
    annotations=ToolAnnotations(
        title="Normalize a Docs/Drive URL to IDs",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def docs_from_url(
    url: Annotated[
        HttpUrl,
        Field(
            description="Docs or Drive URL to normalize",
            examples=[
                models.EXAMPLE_GOOGLE_DOC_URL,
                models.EXAMPLE_GOOGLE_DOC_URL_2,
            ],
        ),
    ],
) -> models.DocsFromUrlResult:
    return docs_tools.docs_from_url(str(url))


@mcp.tool(
    "drive.export_file",
    title="Export a Drive file (e.g., PDF, DOCX, HTML)",
    description="Export a Doc/Drive file by ID or URL",
    annotations=ToolAnnotations(
        title="Export a Drive file",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def drive_export_file(
    document_id_or_url: models.DOCUMENT_ID_OR_URL_TYPE,
    mime_type: Annotated[
        str,
        Field(
            description="Target MIME type",
            examples=[
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/html",
            ],
        ),
    ] = "application/pdf",
) -> models.DriveExportResult:
    res = drive_tools.drive_export_file(document_id_or_url, mime_type)
    return models.DriveExportResult(
        document_id_or_url=str(document_id_or_url),
        type=res.type,
        file_name=res.file_name,
        bytes_b64=res.bytes_b64,
    )


# Resources
@mcp.resource(
    "mcp://token-info",
    title="Token Info",
    mime_type="application/json",
)
def token_info_resource() -> models.TokenInfoResource:
    """Safe token diagnostics (no secrets)."""
    return token_info()


@mcp.resource("gdoc-md://{document_id}", title="Google Doc (Markdown)", mime_type="text/markdown")
def gdoc_md(
    document_id: Annotated[str, Field(description="Google Doc ID", examples=[models.EXAMPLE_GOOGLE_DOC_ID])],
) -> str:
    res = docs_tools.docs_read(document_id, models.DocsReadFormat.MD)
    return res.content


@mcp.resource(
    "gdoc-html://{document_id}",
    title="Google Doc (HTML)",
    mime_type="text/html",
)
def gdoc_html(
    document_id: Annotated[str, Field(description="Google Doc ID", examples=[models.EXAMPLE_GOOGLE_DOC_ID])],
) -> str:
    res = drive_tools.drive_export_file(document_id, "text/html")
    return base64.b64decode(res.bytes_b64).decode("utf-8", errors="replace")


# Prompts
@mcp.prompt(
    name="comment_reply",
    title="Draft Doc Comment Reply",
    description="Draft Doc Comment Reply",
)
def prompt_comment_reply(
    document_id: str | None,
    url: str | None,
    comment_id: str,
    tone: str = "friendly",
    note: str = "",
) -> PromptResult:
    doc_ref = url or document_id or "<document>"
    text = (
        f"Draft a {tone} reply to Google Doc comment {comment_id} in {doc_ref}.\n"
        f"Guidance: {note}\n"
        "Be concise and helpful."
    )
    return [Message(text, role="user")]


@mcp.prompt(name="summarize_doc", title="Summarize Doc", description="Summarize Doc")
def prompt_summarize_doc(document_id: str | None, url: str | None, length: str = "short") -> PromptResult:
    doc_ref = url or document_id or "<document>"
    text = (
        f"Summarize the Google Doc {doc_ref} with a {length} summary.\n"
        "Highlight key points, decisions, and action items."
    )
    return [Message(text, role="user")]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
