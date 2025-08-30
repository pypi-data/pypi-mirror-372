import logging
import warnings

from collections.abc import Iterable, Sequence

from fastmcp.exceptions import ToolError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from google_docs_mcp.config import get_settings
from google_docs_mcp.models import TokenInfoResource
from google_docs_mcp.storage import client_secret_path, read_token, token_path, write_token


logger = logging.getLogger(__name__)
settings = get_settings()


def _normalize_scopes(scopes: Iterable[str] | str | None) -> list[str]:
    if scopes is None:
        return []
    if isinstance(scopes, str):
        return [s.strip() for s in scopes.split() if s.strip()]
    return [s.strip() for s in scopes if isinstance(s, str) and s.strip()]


def _compare_scopes(token_scopes: Sequence[str], requested: Sequence[str]) -> str | None:
    ts, rq = set(token_scopes), set(requested)
    if not ts:
        return None
    if ts == rq:
        return None
    missing = ", ".join(sorted(rq - ts))
    extra = ", ".join(sorted(ts - rq))
    parts: list[str] = []
    if missing:
        parts.append(f"missing scopes: {missing}")
    if extra:
        parts.append(f"token has additional scopes: {extra}")
    return "; ".join(parts) if parts else None


def _delete_token_if_exists() -> None:
    p = token_path()
    if p.exists():
        try:
            p.unlink()
        except Exception as exc:
            logger.warning("Failed to remove token file %s: %s", p, exc)


def _make_installed_flow(redirect_uris: list[str] | None = None) -> InstalledAppFlow:
    flow: InstalledAppFlow
    client_config_path = client_secret_path()

    if client_config_path.exists():
        flow = InstalledAppFlow.from_client_secrets_file(client_config_path, scopes=settings.google.scopes)

    elif settings.google.client_id and settings.google.client_secret:
        flow = InstalledAppFlow.from_client_config(
            client_config={
                "installed": {
                    "client_id": settings.google.client_id,
                    "client_secret": settings.google.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": redirect_uris or ["http://localhost"],
                }
            },
            scopes=settings.google.scopes,
        )

    else:
        raise RuntimeError(
            "Missing OAuth client. Set GOOGLE__CLIENT_ID and GOOGLE__CLIENT_SECRET or GOOGLE__OAUTH_CLIENT_FILE."
        )
    return flow


def build_credentials(*, force: bool = False, auth_if_needed: bool = settings.auto_auth) -> Credentials:
    if force:
        _delete_token_if_exists()
    creds = read_token()
    if creds:
        token_scopes = _normalize_scopes(creds.granted_scopes or creds.scopes)
        note = _compare_scopes(token_scopes, settings.google.scopes)
        if note:
            logger.warning(
                "Existing token scopes differ from requested (%s). Use --force to re-authorize.",
                note,
            )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            write_token(creds)
        return creds
    if not auth_if_needed:
        raise ToolError("No credentials found. Run 'google-docs-mcp auth authorize' to authorize.")

    try:
        flow = _make_installed_flow()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            creds = flow.run_local_server(
                open_browser=True,
                access_type="offline",
                prompt="consent",
            )
    except Exception as exc:
        raise ToolError(f"Failed to build credentials: {exc}") from exc
    write_token(creds)
    return creds


def authorize_interactive(force: bool = False) -> None:
    # Show status before and after to assist users
    before = read_token()
    if before and not force:
        token_scopes = _normalize_scopes(before.granted_scopes or before.scopes)
        note = _compare_scopes(token_scopes, settings.google.scopes)
        msg = f"Already authorized. Token at {token_path()}"
        if note:
            msg += f"; scope mismatch -> {note}. Run with --force to re-authorize."
        logger.info(msg)

    creds = build_credentials(force=force)
    if not creds.refresh_token:
        logger.warning(
            "Warning: No refresh_token granted. If API calls fail after expiry, "
            "re-run: 'google-docs-mcp auth authorize --force' to force offline access."
        )
    logger.info("Authorization complete. Token saved to %s", token_path())


# TODO: This is not working as expected. The redirect_uris are not properly set.
def authorize_console(force: bool = False) -> None:
    if force:
        _delete_token_if_exists()
    flow = _make_installed_flow(redirect_uris=["urn:ietf:wg:oauth:2.0:oob", "http://localhost"])
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )

    print(f"Please visit this URL to authorize this application: {auth_url}")
    try:
        code = input("Enter authorization code: ")
    except KeyboardInterrupt:
        logger.info("\nAuthorization cancelled.")
        return
    flow.fetch_token(code=code)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        creds = flow.credentials

    write_token(creds)
    logger.info("Authorization complete. Token saved to %s", token_path())


def token_info() -> TokenInfoResource:
    """Return basic token information (path, existence, scopes).

    Does not perform network calls. Helpful for diagnostics.
    """
    p = token_path()
    data = read_token()
    info: TokenInfoResource = TokenInfoResource(path=p, exists=p.exists())
    if data:
        info.scopes = _normalize_scopes(data.granted_scopes or data.scopes)
        info.requested_scopes = list(settings.google.scopes)
        info.scope_note = _compare_scopes(info.scopes, settings.google.scopes)
        info.expiry = data.expiry
        info.client_id_present = bool(data.client_id)
    return info


def revoke_local() -> str:
    """Remove local token file (does not call remote revoke)."""
    p = token_path()
    if not p.exists():
        return f"No token found at {p}"
    try:
        p.unlink()
        return f"Removed token at {p}"
    except Exception as exc:
        return f"Failed to remove token at {p}: {exc}"
