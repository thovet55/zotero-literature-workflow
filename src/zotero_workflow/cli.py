import argparse
import json

from .client import ZoteroClient
from .config import ConfigurationError, load_settings, redact_secret


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Zotero Web API workflow")
    parser.add_argument("command", choices=("check", "search"))
    parser.add_argument("query", nargs="?")
    args = parser.parse_args()
    try:
        settings = load_settings()
        client = ZoteroClient(settings.api_key, settings.library_id, settings.library_type, settings.base_url)
        if args.command == "check":
            items = client.list_items(limit=1)
            print(json.dumps({"ok": True, "library": settings.library_id, "items_read": len(items), "key": redact_secret(settings.api_key)}))
        else:
            print(json.dumps(client.list_items(query=args.query), ensure_ascii=False, indent=2))
        return 0
    except ConfigurationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
