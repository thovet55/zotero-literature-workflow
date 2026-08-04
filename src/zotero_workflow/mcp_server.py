"""Optional MCP stdio adapter; all exposed operations are read-only."""

from .client import ZoteroClient
from .config import load_settings
from .literature import extract_pdf_text


def _pdf_text_from_attachment(client, attachment_key: str) -> dict:
    data = client.download_file(attachment_key)
    return extract_pdf_text(data)


class _LazyClient:
    """Defer settings/client creation until first attribute access."""

    def __init__(self, client=None):
        self._client = client

    def __getattr__(self, name):
        if self._client is None:
            settings = load_settings()
            self._client = ZoteroClient(settings.api_key, settings.library_id, settings.library_type, settings.base_url)
        return getattr(self._client, name)


def create_server(client=None):
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install the optional MCP dependency with: pip install -e '.[mcp]'") from exc
    client = _LazyClient(client)
    server = FastMCP("zotero-literature")

    @server.tool()
    def search_items(query: str = "", limit: int = 25) -> list:
        """Search Zotero items. This server has no write tools."""
        return client.list_items(limit=limit, query=query or None)

    @server.tool()
    def get_item(item_key: str) -> dict:
        return client.get_item(item_key)

    @server.tool()
    def get_children(item_key: str) -> list:
        return client.get_children(item_key)

    @server.tool()
    def get_fulltext(attachment_key: str) -> dict:
        return client.get_fulltext(attachment_key)

    @server.tool()
    def get_pdf_text(attachment_key: str) -> dict:
        """Download a synced PDF attachment and extract its text. Requires a synced, authorized file."""
        return _pdf_text_from_attachment(client, attachment_key)

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
