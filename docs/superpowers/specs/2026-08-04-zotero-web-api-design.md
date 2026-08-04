# Zotero Web API Literature Workflow

## Goal

Provide a GitHub-ready, read-only OpenCode integration that reads a user's private Zotero cloud library through Zotero Web API v3, retrieves synced full text when available, and supports citation-focused literature review without requiring Zotero Desktop or manual PDF uploads.

## Architecture

The project has four small boundaries:

1. `config` loads `ZOTERO_API_KEY`, `ZOTERO_LIBRARY_ID`, and `ZOTERO_LIBRARY_TYPE` from environment variables or a permission-restricted dotenv file without logging secrets.
2. `client` is a dependency-light Zotero Web API v3 client using an authorization header, pagination, typed errors, and read-only methods for items, collections, children, files, and fulltext.
3. `literature` contains deterministic PDF/fulltext helpers and citation-context extraction. It reports source quality and never claims references were found when only metadata was available.
4. `mcp_server` exposes the read-only operations over MCP stdio when the optional MCP SDK is installed. A CLI provides setup checks and endpoint diagnostics without MCP.

PDF extraction is optional: Zotero's indexed fulltext is preferred; downloaded synced PDFs use `pypdf` if installed. Missing attachment, unsynced storage, missing fulltext, unsupported extraction, and permission failures remain distinct statuses.

## Safety

- No write endpoint is implemented.
- API keys are accepted only through environment variables or a local dotenv file ignored by Git.
- HTTP requests use `Zotero-API-Key`; keys never appear in URLs, output, exceptions, or reports.
- The project does not bypass publisher access controls or discover unauthorized copies.

## Verification

Unit tests use a local fake HTTP server/transport and cover authentication headers, endpoint construction, pagination, error classification, fulltext/file status, citation context extraction, and secret redaction. A live diagnostic is opt-in and requires the user's local environment variables.
