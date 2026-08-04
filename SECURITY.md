# Security Policy

## Secrets

Store `ZOTERO_API_KEY` in a local `.env` with mode `600`, an OS secret manager, or a process environment. Do not put it in OpenCode prompts, MCP JSON committed to Git, logs, issue reports, or chat. Revoke compromised keys from Zotero Settings and create a replacement.

## Scope

Use a read-only personal key scoped to the smallest required library. This project deliberately implements no Zotero write endpoints and does not bypass access controls.

## Reporting

Do not include API keys or private paper contents in a public issue. Report code vulnerabilities privately to the repository maintainer.
