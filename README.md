# Zotero Literature Workflow

<p align="center">
  English | <a href="./README.zh-CN.md">简体中文</a>
</p>

Zotero Literature Workflow connects your [Zotero](https://www.zotero.org) library to an AI assistant inside [OpenCode](https://opencode.ai). Ask for papers in plain language, read the full text of PDFs and saved web snapshots, and inspect figures and equations — without opening the Zotero desktop app or exporting anything by hand.

## Features

* **Search** — find items in your library with a plain-language query. The assistant returns matches with citation context, not just titles.
* **Read** — extract the full text of synced PDFs, and of saved web-page snapshots, automatically.
* **See** — render any page of a PDF as an image, so a multimodal model can read figures, tables, equations, and scanned pages.
* **Evidence-first** — every answer is tied to a citation context and marked with where the text came from, so you can tell verified claims from summaries.
* **Quick to set up** — no Zotero desktop app, no local database, no manual PDF uploads. Install, add one API key, and go.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install "zotero-literature-workflow[mcp,pdf] @ git+https://github.com/thovet55/zotero-literature-workflow.git"
```

Create a `.env` file anywhere on disk (for example `~/.config/zotero-workflow/.env`), and fill in your key:

```text
ZOTERO_API_KEY=your-key-here
ZOTERO_LIBRARY_ID=your-numeric-user-id
ZOTERO_LIBRARY_TYPE=user
```

Get the key from **Zotero → Settings → Security → API Keys** ([direct link](https://www.zotero.org/settings/keys)). Create a *private* key with **read-only** access to the library you want to use; your numeric user ID is shown on the same page.

Verify everything works:

```console
$ zotero-workflow check
{"ok": true, "library": "1234567", "items_read": 1, "key": "abc...xyz"}
```

Now search your library:

```console
$ zotero-workflow search "moire"
[
  {
    "key": "ABC123DE",
    "data": {
      "itemType": "journalArticle",
      "title": "Fractional quantum anomalous Hall effect in twisted MoTe2",
      ...
```

## Use it in OpenCode

Once you connect the MCP server (see [OpenCode MCP](#opencode-mcp)), you can just ask:

> "Search my library for moiré papers and list them with year and journal."

> "Extract the full text of the PDF for the paper on fractional quantum anomalous Hall effect."

> "Render page 3 of that PDF so you can describe Figure 2."

> "Find where my annotations mention 'Chern number'."

The assistant picks the right tool, pulls the evidence from your library, and shows you exactly what it read.

## OpenCode MCP

Add a local MCP server entry to your OpenCode config (`~/.config/opencode/opencode.json` or a project-level `opencode.json`). See [`opencode.example.jsonc`](./opencode.example.jsonc) for the full shape:

```jsonc
{
  "mcp": {
    "zotero-literature": {
      "type": "local",
      "command": ["/path/to/your/venv/bin/zotero-workflow-mcp"],
      "enabled": true,
      "timeout": 30000,
      "environment": {
        "ZOTERO_DOTENV": "/path/to/your/.env",
        "ZOTERO_LIBRARY_TYPE": "user"
      }
    }
  }
}
```

Replace the paths with your virtualenv's `zotero-workflow-mcp` binary and your `.env` file. The `ZOTERO_DOTENV` variable points the MCP process at your `.env` using an absolute path, so it works regardless of OpenCode's working directory. Restart OpenCode after changing the config; each session spawns a fresh read-only MCP process.

The server even starts without credentials — it only reports a clear `ZOTERO_API_KEY is required` error when a tool is actually called.

### Tools

| Tool | Description |
| --- | --- |
| `search_items` | Search the library (query, limit, offset) |
| `get_item` | Metadata and abstract for one item |
| `get_children` | Child items (PDFs, notes, annotations) |
| `get_fulltext` | Full text from Zotero's search index |
| `get_pdf_text` | Download a synced PDF attachment and extract its text |
| `get_attachment_text` | Download an attachment and extract text from its actual content type (PDF or web-page snapshot) |
| `get_pdf_pages` | Render one or more PDF pages as PNG images for a multimodal model (`pages` accepts `"1"`, `"1-3"`, `"1,3,5"`; omitted = all pages) |

**Visual analysis.** `get_pdf_pages` returns images, not text — the model consuming them must be multimodal. Request only the pages you need: a rendered page is roughly 750 KB of base64, so rendering a whole PDF at once can exhaust the context window. Prefer `get_pdf_text` for text-heavy passages and fall back to rendering for figures, tables, equations, or scanned pages.

**Download caching.** Downloaded files are cached in memory for the lifetime of the server process, so reading the same attachment twice does not hit the Zotero API again. Nothing is written to disk — the cache disappears when the process exits. If an attachment is updated in Zotero during a session, the cached copy may be stale until the server restarts.

## Literature review skill

[`skills/literature-review/SKILL.md`](./skills/literature-review/SKILL.md) defines an evidence-first review protocol: every reference needs a citation context, the source of the text (Zotero's index vs. a synced PDF) is recorded, and metadata-only conclusions are flagged as lower confidence.

## Development

```bash
pytest -q
python -m compileall -q src
```

## Limitations

* An attachment record does not prove the PDF is synced to Zotero Storage.
* Full-text indexing may be incomplete even when the file endpoint works for a synced attachment.
* PDF annotations/highlights must be checked per item; they are not guaranteed in every Web API response.
* This project does not bypass paywalls or locate unauthorized copies, and it implements no write API by design.

## Security

The API key travels in the `Zotero-API-Key` header, never in a URL. Secrets live in a local `.env` that is git-ignored and never committed — never send the key in chat, logs, or issues; if it leaks, revoke it from Zotero Settings. See [SECURITY.md](./SECURITY.md) for the full policy.

## License

[MIT](./LICENSE) © 2026
