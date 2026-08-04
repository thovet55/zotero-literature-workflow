from dataclasses import dataclass
import os
from pathlib import Path


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str
    library_id: str
    library_type: str = "user"
    base_url: str = "https://api.zotero.org"


def redact_secret(value: str) -> str:
    if len(value) <= 6:
        return "***"
    return f"{value[:3]}...{value[-3:]}"


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_settings(dotenv_path: str | None = None) -> Settings:
    values = _read_dotenv(Path(dotenv_path or os.getenv("ZOTERO_DOTENV") or ".env"))
    api_key = os.getenv("ZOTERO_API_KEY", values.get("ZOTERO_API_KEY", ""))
    library_id = os.getenv("ZOTERO_LIBRARY_ID", values.get("ZOTERO_LIBRARY_ID", ""))
    library_type = os.getenv("ZOTERO_LIBRARY_TYPE", values.get("ZOTERO_LIBRARY_TYPE", "user"))
    base_url = os.getenv("ZOTERO_BASE_URL", values.get("ZOTERO_BASE_URL", "https://api.zotero.org"))
    if not api_key:
        raise ConfigurationError("ZOTERO_API_KEY is required")
    if not library_id:
        raise ConfigurationError("ZOTERO_LIBRARY_ID is required")
    if library_type not in {"user", "group"}:
        raise ConfigurationError("ZOTERO_LIBRARY_TYPE must be 'user' or 'group'")
    return Settings(api_key, library_id, library_type, base_url.rstrip("/"))
