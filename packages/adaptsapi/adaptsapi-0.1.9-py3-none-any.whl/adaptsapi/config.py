import os
import json
import getpass
from pathlib import Path

# Point at config.json in whatever directory you run the CLI from
CONFIG_PATH = Path.cwd() / "config.json"


class ConfigError(Exception):
    """Raised when no token can be found or loaded."""

    pass


def load_token() -> str:
    # 1) ENV override
    token = os.getenv("ADAPTS_API_TOKEN")
    if token:
        return token

    # 2) config.json in current directory
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            token = data.get("token")
            if token:
                return token
        except json.JSONDecodeError:
            # invalid JSON in config.json; fall through to prompt
            pass

    # 3) interactive first-run and save
    token = getpass.getpass("API token not found; please paste it here: ")
    if not token:
        raise ConfigError("No token provided")
    CONFIG_PATH.write_text(json.dumps({"token": token}, indent=2))
    print(f"Saved token to {CONFIG_PATH}")
    return token


def load_default_endpoint() -> str | None:
    """Return `endpoint` from ./config.json if present, else None."""
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            return data.get("endpoint")
        except json.JSONDecodeError:
            return None
    return None


def _ensure_config_dir_and_write(obj: dict) -> None:
    """Helper to merge+write config.json in cwd."""
    # read existing if any
    existing = {}
    if CONFIG_PATH.exists():
        try:
            existing = json.loads(CONFIG_PATH.read_text())
        except json.JSONDecodeError:
            existing = {}
    merged = {**existing, **obj}
    CONFIG_PATH.write_text(json.dumps(merged, indent=2))
