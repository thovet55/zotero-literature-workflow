# Zotero Literature Workflow

Read-only Zotero Web API v3 tools for OpenCode. This project does not require Zotero Desktop, a local Zotero database, or manual PDF uploads.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev,mcp,pdf]'
cp .env.example .env
chmod 600 .env
```

Create a personal API key at Zotero `Settings -> Security -> API Keys`. Grant only read access to the target library. Put the key and numeric user ID in `.env`; never send the key in chat or commit `.env`.

```text
ZOTERO_API_KEY=put-your-key-in-local-dotenv-only
ZOTERO_LIBRARY_ID=123456
ZOTERO_LIBRARY_TYPE=user
```

## Verify

```bash
zotero-workflow check
zotero-workflow search "single-photon absorption"
```

The check reads one item and prints only a redacted key. The client uses the `Zotero-API-Key` header and never places the key in a URL.

## OpenCode MCP

Copy `opencode.example.jsonc` into the appropriate user-level OpenCode configuration and adjust the absolute project path. The MCP process reads `.env` via the `ZOTERO_DOTENV` environment variable (absolute path). If the OpenCode configuration cannot provide a working directory, use an absolute `ZOTERO_API_KEY` environment injection from a local secret manager instead of placing the secret in this repository.

The server exposes only `search_items`, `get_item`, `get_children`, `get_fulltext`, and `get_pdf_text` (downloads a synced PDF and extracts its text). It has no write tools. Restarting OpenCode starts a fresh read-only MCP process; the local `.env` prevents re-entering the key each session. The server starts even without configuration and reports a clear `ZOTERO_API_KEY is required` error only when a tool is actually called.

## Literature review workflow

Use `skills/literature-review/SKILL.md` as the reusable analysis protocol. It requires evidence for citation purpose, records whether text came from Zotero's index or a synced PDF, and marks metadata-only conclusions as lower confidence.

## Limitations

- A PDF attachment record does not prove that the file is synced to Zotero Storage.
- Fulltext indexing may be incomplete; the file endpoint may still be available for a synced attachment.
- PDF annotations and highlights are not assumed available through every Web API response and must be checked per library/item.
- This project does not bypass paywalls or locate unauthorized copies.
- No write API is implemented by design.

## Development

```bash
pytest -q
python -m compileall -q src
```

See `SECURITY.md` before publishing a fork.
