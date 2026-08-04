import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

import pytest

from zotero_workflow.client import ZoteroClient
from zotero_workflow.errors import ZoteroHTTPError


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.seen.append((self.path, dict(self.headers)))
        if self.path.endswith("/items?limit=2&start=0"):
            payload = [{"key": "A", "data": {"title": "One"}}]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Total-Results", "1")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())
        elif self.path.endswith("/items/A/children"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps([]).encode())
        elif self.path.endswith("/items/A/fulltext"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"content": "References\n[1] Example"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *_):
        pass


@pytest.fixture
def server():
    instance = HTTPServer(("127.0.0.1", 0), Handler)
    instance.seen = []
    thread = Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    yield instance
    instance.shutdown()


def test_client_uses_header_and_read_only_endpoints(server):
    client = ZoteroClient("key-value", "123", base_url=f"http://127.0.0.1:{server.server_port}")
    items = client.list_items(limit=2)
    assert items[0]["key"] == "A"
    assert client.get_children("A") == []
    assert "References" in client.get_fulltext("A")["content"]
    path, raw_headers = server.seen[0]
    headers = {key.lower(): value for key, value in raw_headers.items()}
    assert "key-value" not in path
    assert headers["zotero-api-key"] == "key-value"


def test_client_classifies_http_errors(server):
    client = ZoteroClient("secret", "123", base_url=f"http://127.0.0.1:{server.server_port}")
    with pytest.raises(ZoteroHTTPError) as caught:
        client.get_item("missing")
    assert caught.value.status == 404
    assert "secret" not in str(caught.value)
