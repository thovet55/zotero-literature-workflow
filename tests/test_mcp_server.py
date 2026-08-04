import asyncio

import pytest

from zotero_workflow.mcp_server import _pdf_text_from_attachment, create_server


class FakeClient:
    def __init__(self, pdf_bytes):
        self._pdf = pdf_bytes
        self.downloaded = []

    def download_file(self, attachment_key):
        self.downloaded.append(attachment_key)
        return self._pdf


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
    server = create_server(client=FakeClient(b""))
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {"search_items", "get_item", "get_children", "get_fulltext", "get_pdf_text"}


def test_pdf_text_helper_downloads_and_extracts_real_pdf():
    fake = FakeClient(build_pdf("Introduction cites prior work.\nReferences\n[1] Example citation"))
    result = _pdf_text_from_attachment(fake, "ABC123")
    assert fake.downloaded == ["ABC123"]
    assert result["status"] == "pdf_text_extracted"
    assert "References" in result["text"]
    assert "[1] Example citation" in result["text"]


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
