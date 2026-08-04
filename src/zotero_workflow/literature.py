import re
from html.parser import HTMLParser
from io import BytesIO
from zipfile import ZipFile


class _TextExtractor(HTMLParser):
    _BLOCK_TAGS = {
        "p", "div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "ul", "ol", "tr", "td", "th", "table", "br", "header", "footer",
    }

    def __init__(self):
        super().__init__()
        self._blocks = []
        self._current = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        elif tag in self._BLOCK_TAGS and self._current:
            self._flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        elif tag in self._BLOCK_TAGS:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._current.append(data)

    def _flush(self):
        line = " ".join(" ".join(self._current).split())
        if line:
            self._blocks.append(line)
        self._current = []

    def text(self) -> str:
        self._flush()
        return "\n".join(self._blocks)


def extract_html_text(html: bytes) -> str:
    parser = _TextExtractor()
    parser.feed(html.decode("utf-8", errors="replace"))
    return parser.text()


def extract_html_from_zip(data: bytes) -> bytes:
    with ZipFile(BytesIO(data)) as archive:
        names = archive.namelist()
        html_names = [n for n in names if n.lower().endswith((".html", ".htm"))]
        if not html_names:
            raise ValueError("no .html file inside snapshot zip")
        return archive.read(html_names[0])


def render_pdf_pages(pdf_bytes: bytes, pages: str = "", zoom: float = 2.0) -> dict:
    try:
        import fitz
    except ImportError:
        return {"status": "pdf_render_dependency_missing", "images": []}
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        selected = _parse_pages(pages, doc.page_count)
        matrix = fitz.Matrix(zoom, zoom)
        images = []
        for index in selected:
            page = doc[index]
            pix = page.get_pixmap(matrix=matrix)
            images.append(pix.tobytes("png"))
        return {"status": "pdf_rendered", "page_count": doc.page_count, "images": images}
    except Exception as exc:
        return {"status": "pdf_render_failed", "images": [], "error": str(exc)}


def _parse_pages(spec: str, count: int) -> list[int]:
    if not spec:
        return list(range(count))
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, _, end = part.partition("-")
            try:
                low, high = int(start), int(end)
            except ValueError:
                continue
            pages.extend(range(low, high + 1))
        else:
            try:
                pages.append(int(part))
            except ValueError:
                continue
    result = [p - 1 for p in pages if 1 <= p <= count]
    return sorted(set(result)) or list(range(count))


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
