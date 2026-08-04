"""Optional MCP stdio adapter; all exposed operations are read-only."""

from .client import ZoteroClient
from .config import load_settings
from .literature import extract_html_from_zip, extract_html_text, extract_pdf_text, render_pdf_pages


def _pdf_text_from_attachment(client, attachment_key: str) -> dict:
    data = client.download_file(attachment_key)
    return extract_pdf_text(data)


def _render_pdf_pages_from_attachment(client, attachment_key: str, pages: str = "") -> list:
    data = client.download_file(attachment_key)
    result = render_pdf_pages(data, pages=pages)
    return result["images"]


def _attachment_text(client, attachment_key: str) -> dict:
    item = client.get_item(attachment_key)
    content_type = (item.get("data", {}).get("contentType") or "").lower()
    data = client.download_file(attachment_key)
    if content_type == "text/html":
        html = extract_html_from_zip(data)
        return {"status": "text_extracted", "contentType": content_type, "text": extract_html_text(html)}
    if content_type == "application/pdf":
        result = extract_pdf_text(data)
        result["contentType"] = content_type
        return result
    return {"status": "unsupported_type", "contentType": content_type, "text": ""}


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

    @server.tool()
    def get_attachment_text(attachment_key: str) -> dict:
        """Download an attachment and extract plain text by content type (PDF or HTML snapshot)."""
        return _attachment_text(client, attachment_key)

    @server.tool()
    def get_pdf_pages(attachment_key: str, pages: str = "") -> list:
        """Render PDF pages as images (zoom ~2x) so a multimodal model can read figures, formulas,
        or scanned content that a text layer cannot capture. `pages` is optional; default renders
        all pages. Examples: "1", "1-3", "1,3,5". Requires pymupdf."""
        import base64

        from mcp.types import ImageContent

        images = _render_pdf_pages_from_attachment(client, attachment_key, pages=pages)
        return [
            ImageContent(type="image", mimeType="image/png", data=base64.b64encode(png).decode("ascii"))
            for png in images
        ]

    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
