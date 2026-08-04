from zotero_workflow.literature import citation_contexts, extract_pdf_text, extract_references, fulltext_status


def test_extract_references_finds_reference_section():
    text = "Introduction cites prior work [1].\nReferences\n[1] Smith, A. A foundational result."
    assert extract_references(text) == ["[1] Smith, A. A foundational result."]


def test_citation_contexts_returns_sentence_containing_reference_marker():
    text = "The effect was first observed by Smith et al. [1]. Later work disagreed."
    assert citation_contexts(text, "[1]") == ["The effect was first observed by Smith et al. [1]."]


def test_fulltext_status_distinguishes_sources():
    assert fulltext_status({"content": "text"}) == "indexed_fulltext"
    assert fulltext_status(None) == "unavailable"


def test_extract_pdf_text_reports_optional_dependency():
    result = extract_pdf_text(b"not-a-pdf")
    assert result["status"] in {"pdf_extraction_failed", "pdf_dependency_missing"}
