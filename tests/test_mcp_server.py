import asyncio
import io
import zipfile

import pytest

from zotero_workflow.mcp_server import (
    _attachment_text,
    _pdf_text_from_attachment,
    _render_pdf_pages_from_attachment,
    create_server,
)


class FakeClient:
    def __init__(self, files=None, types=None):
        self.files = files if files is not None else {}
        self.types = types or {}
        self.downloaded = []
        self.fetched = []

    def get_item(self, item_key):
        self.fetched.append(item_key)
        return {"key": item_key, "data": {"contentType": self.types.get(item_key)}}

    def download_file(self, attachment_key):
        self.downloaded.append(attachment_key)
        return self.files[attachment_key]


def build_pdf(text: str) -> bytes:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    content = f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode())
        out.extend(body)
        out.extend(b"\nendobj\n")
    xref = len(out)
    count = len(objects) + 1
    out.extend(f"xref\n0 {count}\n".encode())
    out.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(out)


def test_create_server_registers_only_read_only_tools():
    server = create_server(client=FakeClient())
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {
        "search_items",
        "get_item",
        "get_children",
        "get_fulltext",
        "get_pdf_text",
        "get_pdf_pages",
        "get_attachment_text",
    }


def test_pdf_text_helper_downloads_and_extracts_real_pdf():
    fake = FakeClient(files={"ABC123": build_pdf("Introduction cites prior work.\nReferences\n[1] Example citation")})
    result = _pdf_text_from_attachment(fake, "ABC123")
    assert fake.downloaded == ["ABC123"]
    assert result["status"] == "pdf_text_extracted"
    assert "References" in result["text"]
    assert "[1] Example citation" in result["text"]


def test_render_pdf_pages_helper_returns_recognizable_png():
    fake = FakeClient(files={"PDF1": build_pdf("Render me")})
    images = _render_pdf_pages_from_attachment(fake, "PDF1", pages="")
    assert fake.downloaded == ["PDF1"]
    assert len(images) == 1
    assert images[0][:8] == b"\x89PNG\r\n\x1a\n"


def test_get_pdf_pages_tool_returns_image_content_blocks():
    fake = FakeClient(files={"PDF1": build_pdf("Render me")})
    server = create_server(client=fake)
    result = asyncio.run(server.call_tool("get_pdf_pages", {"attachment_key": "PDF1"}))
    assert any(type(block).__name__ == "ImageContent" for block in result)


def _zip_with_html(name: str = "page.html") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, "<html><body><h1>Title</h1><p>Some <b>text</b> here.</p></body></html>")
    return buffer.getvalue()


def test_attachment_text_extracts_html_from_zip():
    fake = FakeClient(
        files={"SNP1": _zip_with_html()},
        types={"SNP1": "text/html"},
    )
    result = _attachment_text(fake, "SNP1")
    assert fake.fetched == ["SNP1"]
    assert result["status"] == "text_extracted"
    assert result["contentType"] == "text/html"
    assert "Some text here" in result["text"]


def test_attachment_text_routes_pdf_to_pypdf():
    fake = FakeClient(
        files={"PDF2": build_pdf("Hybrid route")},
        types={"PDF2": "application/pdf"},
    )
    result = _attachment_text(fake, "PDF2")
    assert result["status"] == "pdf_text_extracted"
    assert "Hybrid route" in result["text"]


def test_create_server_starts_without_config(monkeypatch, tmp_path):
    monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
    monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
    empty_env = tmp_path / "empty.env"
    empty_env.write_text("")
    monkeypatch.setenv("ZOTERO_DOTENV", str(empty_env))
    server = create_server(client=None)
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert "search_items" in names
    assert "get_pdf_text" in names


def test_tool_call_without_config_returns_clear_error(monkeypatch, tmp_path):
    monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
    monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
    empty_env = tmp_path / "empty.env"
    empty_env.write_text("")
    monkeypatch.setenv("ZOTERO_DOTENV", str(empty_env))
    server = create_server(client=None)
    with pytest.raises(Exception, match="ZOTERO_API_KEY"):
        asyncio.run(server.call_tool("search_items", {}))
