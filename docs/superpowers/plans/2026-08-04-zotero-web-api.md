# Zotero Web API Literature Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a GitHub-ready, read-only Zotero Web API integration for OpenCode literature and citation analysis.

**Architecture:** A dependency-light Python client handles official Web API v3 endpoints and safe configuration. Optional MCP stdio and CLI layers expose the client and literature helpers without requiring Zotero Desktop.

**Tech Stack:** Python 3.11+, standard library HTTP/JSON, optional `mcp` SDK, optional `pypdf`, pytest.

## Global Constraints

- Use Zotero Web API v3, never the local API or `zotero.sqlite`.
- Keep all operations read-only and do not implement write endpoints.
- Never log, print, commit, or return API key values.
- Prefer fulltext endpoint; download only attachments already synced and authorized by Zotero.
- Distinguish absent attachment, unsynced file, missing index, and permission/rate-limit errors.
- Do not require third-party services or external embeddings.

### Task 1: Project Scaffolding and Configuration

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `.env.example`, `LICENSE`, `README.md`
- Create: `src/zotero_workflow/__init__.py`, `src/zotero_workflow/config.py`
- Test: `tests/test_config.py`

- [ ] Write tests for required variables, dotenv loading, and secret redaction.
- [ ] Run `pytest tests/test_config.py -q` and verify the missing module failure.
- [ ] Implement `Settings`, `load_settings()`, and `redact_secret()` with no secret logging.
- [ ] Run the focused tests and then the full test suite.

### Task 2: Read-Only Zotero API Client

**Files:**
- Create: `src/zotero_workflow/errors.py`, `src/zotero_workflow/client.py`
- Test: `tests/test_client.py`

- [ ] Write tests for header authentication, `/users/<id>/items`, pagination, children, fulltext, file, and typed HTTP errors.
- [ ] Run the focused tests and verify the expected missing implementation failures.
- [ ] Implement `ZoteroClient` with `list_items`, `get_item`, `get_children`, `get_fulltext`, `download_file`, and `list_collections`.
- [ ] Ensure URLs never contain the API key and response errors are sanitized.
- [ ] Run focused and full tests.

### Task 3: Fulltext and Citation Analysis

**Files:**
- Create: `src/zotero_workflow/literature.py`
- Test: `tests/test_literature.py`

- [ ] Write tests for reference-section extraction, citation-context matching, and source-status classification.
- [ ] Run tests to verify failure before implementation.
- [ ] Implement deterministic helpers returning structured dictionaries with source provenance and confidence limits.
- [ ] Run focused and full tests.

### Task 4: CLI Diagnostics and MCP Adapter

**Files:**
- Create: `src/zotero_workflow/cli.py`, `src/zotero_workflow/mcp_server.py`
- Modify: `pyproject.toml`
- Test: `tests/test_cli.py`

- [ ] Write tests for sanitized configuration diagnostics and MCP tool registration boundary.
- [ ] Run tests to verify failure before implementation.
- [ ] Implement `zotero-workflow check`, `search`, and optional MCP stdio tools for read-only operations.
- [ ] Make missing optional MCP dependency an explicit install message rather than a secret-bearing traceback.
- [ ] Run focused and full tests.

### Task 5: OpenCode and Literature Workflow Documentation

**Files:**
- Create: `skills/literature-review/SKILL.md`, `opencode.example.jsonc`
- Modify: `README.md`, `.env.example`
- Test: `tests/test_docs.py`

- [ ] Document API key creation, least privilege, persistent local storage, MCP registration, live checks, revocation, and known Zotero limitations.
- [ ] Document the citation-analysis workflow: identify item key, retrieve fulltext provenance, inspect references and contexts, then recommend cited works with evidence.
- [ ] Assert examples contain no realistic secrets and all default operations are read-only.
- [ ] Run documentation tests and full verification.

### Task 6: Release Hygiene and Verification

**Files:**
- Create: `.github/workflows/test.yml`, `SECURITY.md`

- [ ] Run formatting-free test suite, compile check, and a repository secret scan using only tracked/example files.
- [ ] Verify package build metadata and CLI help.
- [ ] Inspect `git diff` and `git status`; leave remote creation/push to the user.
