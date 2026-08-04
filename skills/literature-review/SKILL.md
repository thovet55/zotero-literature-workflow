---
name: literature-review
description: Use when reviewing or reading Zotero literature — finding items, PDFs, references, citation contexts, recommending cited papers, or reading PDF/HTML attachments and viewing figures, charts, images, or rendered pages from the Zotero library via the zotero-literature MCP server. Trigger keywords: 图, 图表, 图片, 视觉, render, render page, figure, chart, image, visual, PDF 正文, 附件内容.
---

# Zotero Literature Review

Use the `zotero-literature` MCP server for a read-only, evidence-first review.

## Tool selection

Always use the `zotero-literature` MCP tools for content that comes from the Zotero library. Prefer these over any other PDF tool:

- `get_item` / `get_children` / `search_items` / `get_fulltext` — metadata, children, and Zotero-indexed fulltext.
- `get_pdf_text` — extract text from a PDF attachment.
- `get_attachment_text` — extract text from a PDF or HTML (snapshot) attachment, routed by content type.
- `get_pdf_pages` — render PDF pages to PNG images (pass `pages` like `"1"`, `"1-3"`, or `"1,3,5"`; empty means all pages). Use this to view figures, charts, equations, or layout. Read the returned image directly.

For Zotero attachments, do not reach for a separate PDF reader unless the zotero-literature tool itself fails (e.g. dependency missing or an unsupported content type). If asked to describe a figure, render the page with `get_pdf_pages` and read the image — do not guess from captions or text alone.

## Procedure

1. Search the library and identify the parent item key.
2. Retrieve metadata, abstract, collections/tags, and children.
3. Identify PDF attachments and report whether fulltext is from Zotero's index or a synced file.
4. If fulltext is unavailable, say whether the item has no PDF, an unsynced attachment, missing index, or an authorization problem.
5. Locate the reference section in available text. Do not invent references from metadata.
6. For each important reference, find the sentence or paragraph containing its citation marker.
7. Classify the citation function as theory, method, foundational history, key result, comparison, controversy, or research gap only when the context supports it.
8. Recommend cited papers using evidence: repeated or strategically placed citations, support for a core claim, foundational/turning-point status, or direct transferability.

## Report format

For each recommendation include title, authors, year, DOI or stable URL, citation location/context, citation function, evidence-based reason, and priority. Mark any item assessed only from metadata or abstract as `metadata-only`; do not equate citation count with reading value.

Never call a write tool. Never expose API keys. Never bypass paywalls.
