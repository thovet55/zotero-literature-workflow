import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .errors import ZoteroHTTPError, ZoteroUnavailableError


class ZoteroClient:
    def __init__(self, api_key: str, library_id: str, library_type: str = "user", base_url: str = "https://api.zotero.org"):
        self.api_key = api_key
        self.library_id = library_id
        self.library_type = library_type
        self.base_url = base_url.rstrip("/")
        self._file_cache: dict[str, bytes] = {}

    @property
    def library_path(self) -> str:
        return f"/{self.library_type}s/{self.library_id}"

    def _get(self, path: str, params: dict | None = None):
        query = f"?{urlencode(params)}" if params else ""
        request = Request(self.base_url + path + query, headers={"Zotero-API-Key": self.api_key, "Zotero-API-Version": "3"})
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type or body[:1] in (b"[", b"{"):
                    return json.loads(body), response.headers
                return body, response.headers
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:200]
            raise ZoteroHTTPError(exc.code, detail) from None
        except URLError as exc:
            raise ZoteroUnavailableError(f"Zotero API unavailable: {exc.reason}") from None

    def list_items(self, limit: int = 25, start: int = 0, query: str | None = None) -> list:
        params = {"limit": min(max(limit, 1), 100), "start": max(start, 0)}
        if query:
            params.update(q=query, qmode="everything")
        return self._get(self.library_path + "/items", params)[0]

    def get_item(self, item_key: str) -> dict:
        return self._get(self.library_path + "/items/" + item_key)[0]

    def get_children(self, item_key: str) -> list:
        return self._get(self.library_path + "/items/" + item_key + "/children")[0]

    def list_collections(self, limit: int = 100) -> list:
        return self._get(self.library_path + "/collections", {"limit": min(max(limit, 1), 100)})[0]

    def get_fulltext(self, attachment_key: str) -> dict:
        return self._get(self.library_path + "/items/" + attachment_key + "/fulltext")[0]

    def download_file(self, attachment_key: str) -> bytes:
        if attachment_key in self._file_cache:
            return self._file_cache[attachment_key]
        data = self._get(self.library_path + "/items/" + attachment_key + "/file")[0]
        self._file_cache[attachment_key] = data
        return data

    def clear_file_cache(self) -> None:
        self._file_cache.clear()
