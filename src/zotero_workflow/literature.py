import re
from io import BytesIO


def fulltext_status(fulltext: dict | None) -> str:
    if fulltext and fulltext.get("content"):
        return "indexed_fulltext"
    return "unavailable"


def extract_references(text: str) -> list[str]:
    match = re.search(r"\n\s*(?:references|bibliography)\s*\n", text, re.IGNORECASE)
    if not match:
        return []
    section = text[match.end():]
    lines = [line.strip() for line in section.splitlines() if line.strip()]
    return lines


def citation_contexts(text: str, marker: str, window: int = 220) -> list[str]:
    contexts = []
    for match in re.finditer(re.escape(marker), text, re.IGNORECASE):
        before = text[:match.start()]
        after = text[match.end():]
        starts = list(re.finditer(r"(?<=[.!?])\s+(?=[A-Z])", before))
        start = starts[-1].end() if starts else 0
        end_match = re.search(r"[.!?](?:\s|$)", after)
        end = match.end() + (end_match.end() if end_match else len(after))
        sentence = " ".join(text[start:end].split())
        if len(sentence) > window:
            sentence = sentence[:window].rstrip() + "..."
        if sentence and sentence not in contexts:
            contexts.append(sentence)
    return contexts


def classify_attachment(children: list[dict]) -> dict:
    attachments = [item for item in children if item.get("data", {}).get("itemType") == "attachment"]
    pdfs = [item for item in attachments if item.get("data", {}).get("contentType") == "application/pdf"]
    if not pdfs:
        return {"status": "no_pdf_attachment", "attachments": attachments}
    return {"status": "pdf_attachment_present", "attachments": pdfs}


def extract_pdf_text(pdf_bytes: bytes) -> dict:
    try:
        from pypdf import PdfReader
    except ImportError:
        return {"status": "pdf_dependency_missing", "text": ""}
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        return {"status": "pdf_text_extracted", "text": text}
    except Exception as exc:
        return {"status": "pdf_extraction_failed", "text": "", "error": str(exc)}
