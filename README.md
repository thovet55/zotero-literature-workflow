<h1 align="center">Zotero Literature Workflow</h1>

<p align="center">
  Read-only <a href="https://www.zotero.org/support/dev/web_api/v3/start">Zotero Web API v3</a> tools for evidence-first literature review in <a href="https://opencode.ai">OpenCode</a>.
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"/></a>
  <a href="https://github.com/thovet55/zotero-literature-workflow/actions"><img src="https://img.shields.io/github/actions/workflow/status/thovet55/zotero-literature-workflow/ci.yml" alt="CI status"/></a>
</p>

<p align="center">
  <strong>English</strong> | <a href="./README.zh-CN.md">简体中文</a>
</p>

No Zotero desktop app, local database, or manual PDF uploads required. Just a read-only API key — the client talks directly to the Zotero web API and never exposes your key.

## Features

- **Read-only by design** — exposes only `search_items`, `get_item`, `get_children`, `get_fulltext`, and `get_pdf_text`. No write tools exist.
- **PDF text extraction** — downloads a synced PDF attachment and extracts its text via [pypdf](https://github.com/py-pdf/pypdf).
- **Secure by default** — the API key travels in the `Zotero-API-Key` header, never in a URL; secrets stay in a local `.env` that is git-ignored and never committed.
- **MCP ready** — ships as an [MCP](https://modelcontextprotocol.io) server so OpenCode agents can query your library directly.
- **Lazy configuration** — the server starts even without credentials and reports a clear `ZOTERO_API_KEY is required` error only when a tool is actually called.
- **Evidence-first workflow** — pairs with a `literature-review` skill that forces citation-context evidence and flags metadata-only conclusions.

## Installation

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,mcp,pdf]'
cp .env.example .env
chmod 600 .env
```

### Get an API key

1. Log in to [zotero.org](https://www.zotero.org) and open **Settings → Security → API Keys** ([direct link](https://www.zotero.org/settings/keys)).
2. Click **Create new private key**. Grant **read-only** access to the library you want to use.
3. Copy the key, and note your **numeric user ID** (shown on the same page as "Your userID for use in API calls is …").

Fill `.env`:

```text
ZOTERO_API_KEY=your-key-here
ZOTERO_LIBRARY_ID=your-numeric-user-id
ZOTERO_LIBRARY_TYPE=user
```

Never send the key in chat, logs, or issues. If it leaks, revoke it from Zotero Settings and create a new one.

## Verify

```bash
zotero-workflow check          # reads one item, prints only a redacted key
zotero-workflow search "moire" # searches your library
```

`check` prints `{"ok": true, ...}` when the credentials work.

## OpenCode MCP

Add a local MCP server entry to your OpenCode config (`~/.config/opencode/opencode.json` or project-level `opencode.json`). See [`opencode.example.jsonc`](./opencode.example.jsonc) for the shape:

```jsonc
{
  "mcp": {
    "zotero-literature": {
      "type": "local",
      "command": ["/absolute/path/to/zotero-literature-workflow/.venv/bin/zotero-workflow-mcp"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "ZOTERO_DOTENV": "/absolute/path/to/zotero-literature-workflow/.env",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    }
  }
}
```

The MCP process reads `.env` from the `ZOTERO_DOTENV` environment variable (absolute path), so it does not depend on OpenCode's working directory. Restart OpenCode after changing the config; each session spawns a fresh read-only MCP process.

### Tools

| Tool | Description |
| --- | --- |
| `search_items` | Search the library (query, limit, offset) |
| `get_item` | Metadata and abstract for one item |
| `get_children` | Child items (PDFs, notes, annotations) |
| `get_fulltext` | Full text from Zotero's search index |
| `get_pdf_text` | Download a synced PDF attachment and extract its text |

## Literature review skill

[`skills/literature-review/SKILL.md`](./skills/literature-review/SKILL.md) defines an evidence-first review protocol: it requires citation contexts for every reference, records whether text came from Zotero's index or a synced PDF, and marks metadata-only conclusions as lower confidence.

## Development

```bash
pytest -q
python -m compileall -q src
```

## Limitations

- An attachment record does not prove the PDF is synced to Zotero Storage.
- Full-text indexing may be incomplete even when the file endpoint works for a synced attachment.
- PDF annotations/highlights must be checked per item; they are not guaranteed in every Web API response.
- This project does not bypass paywalls or locate unauthorized copies, and it implements no write API by design.

## Security

See [SECURITY.md](./SECURITY.md) for the full policy.

## License

[MIT](./LICENSE) © 2026
