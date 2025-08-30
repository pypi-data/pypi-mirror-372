import logging
import os

from pathlib import Path

from google.oauth2.credentials import Credentials
from platformdirs import PlatformDirs
from xdg_base_dirs import (
    xdg_cache_home,
    xdg_config_dirs,
    xdg_config_home,
    xdg_state_home,
)

from google_docs_mcp.config import PROJECT_NAME, get_settings


logger = logging.getLogger(__name__)
settings = get_settings()

_platform_dirs = PlatformDirs(appname=PROJECT_NAME)


def get_config_dir() -> Path:
    """Return configuration directory for the application.

    Preference order:
    - **XDG**: if ``XDG_CONFIG_HOME`` is set to an absolute path, use
      ``xdg_config_home()/<PROJECT_NAME>``.
    - **Platform**: otherwise use ``platformdirs.PlatformDirs.user_config_dir``.
    """
    paths: list[Path] = []
    if "XDG_CONFIG_HOME" in os.environ:
        paths.append(xdg_config_home())
    if "XDG_CONFIG_DIRS" in os.environ:
        paths.extend(xdg_config_dirs())
    if not paths:
        # That means we haven't any XDG configs, so we use the platform dirs.
        return Path(_platform_dirs.user_config_dir)
    # We have some XDG configs, so we need to find the first one that exists.
    for path in paths:
        p = path / PROJECT_NAME
        if p.exists():
            return p

    # If none of the XDG configs exist, but ENV is set, we use the first XDG dir.
    path = paths[0] / PROJECT_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_state_dir() -> Path:
    """Return state directory for the application.

    Preference order:
    - **XDG**: if ``XDG_STATE_HOME`` is set to an absolute path, use
      ``xdg_state_home()/<PROJECT_NAME>``.
    - **Platform**: otherwise use ``platformdirs.PlatformDirs.user_state_dir``.
    """
    if "XDG_STATE_HOME" not in os.environ:
        return Path(_platform_dirs.user_state_dir)
    path = xdg_state_home() / PROJECT_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> Path:
    """Return cache directory for the application.

    Preference order:
    - **XDG**: if ``XDG_CACHE_HOME`` is set to an absolute path, use
      ``xdg_cache_home()/<PROJECT_NAME>``.
    - **Platform**: otherwise use ``platformdirs.PlatformDirs.user_cache_dir``.
    """
    if "XDG_CACHE_HOME" not in os.environ:
        return Path(_platform_dirs.user_cache_dir)
    path = xdg_cache_home() / PROJECT_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def token_path() -> Path:
    return get_state_dir() / "token.json"


def client_secret_path() -> Path:
    path = settings.google.oauth_client_file
    if path:
        return Path(path)
    return get_config_dir() / "client_secrets.json"


def read_token() -> Credentials | None:
    p = token_path()
    if not p.exists():
        return None

    try:
        return Credentials.from_authorized_user_file(p)
    except Exception as exc:
        logger.warning("Stored token is invalid or missing fields. Details: %s", exc, exc_info=exc)
        return None


def write_token(data: Credentials) -> None:
    p = token_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data.to_json())
    try:
        p.chmod(0o600)
    except Exception as exc:
        logger.warning("Failed to chmod token file: %s", exc, exc_info=exc)
