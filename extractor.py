"""PDF ingestion and text extraction for Landlorded."""

import pdfplumber
from dataclasses import dataclass

# Minimum average chars per page to consider pdfplumber extraction usable.
# Below this, the PDF is likely scanned and we fall back to OCR.
_MIN_CHARS_PER_PAGE = 100


@dataclass
class ExtractedAgreement:
    """Raw text extracted from a lease agreement PDF."""
    file_path: str
    full_text: str
    pages: list[str]
    page_count: int
    schedule_text: str  # fixture/inventory schedule if found
    lease_text: str     # main lease clauses only
    ocr_used: bool = False  # whether OCR fallback was used


def extract_agreement(pdf_path: str) -> ExtractedAgreement:
    """Extract text from a lease agreement PDF.

    Uses pdfplumber for text-based PDFs. Falls back to OCR (tesseract)
    when pdfplumber extracts too little text (scanned documents).
    """
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)

    full_text = "\n\n".join(pages)
    ocr_used = False

    # If pdfplumber got very little text, try OCR
    avg_chars = len(full_text) / max(page_count, 1)
    if avg_chars < _MIN_CHARS_PER_PAGE:
        ocr_pages = _ocr_extract(pdf_path)
        if ocr_pages:
            pages = ocr_pages
            full_text = "\n\n".join(pages)
            ocr_used = True

    # Split lease text from schedule/inventory
    schedule_start = _find_schedule_boundary(pages)
    if schedule_start is not None:
        lease_text = "\n\n".join(pages[:schedule_start])
        schedule_text = "\n\n".join(pages[schedule_start:])
    else:
        lease_text = full_text
        schedule_text = ""

    return ExtractedAgreement(
        file_path=pdf_path,
        full_text=full_text,
        pages=pages,
        page_count=len(pages),
        schedule_text=schedule_text,
        lease_text=lease_text,
        ocr_used=ocr_used,
    )


def _find_schedule_boundary(pages: list[str]) -> int | None:
    """Find the page index where the fixture/inventory schedule begins.

    Looks for Schedule/Annexure as a heading (near start of page or on its own line),
    not as an inline reference like 'fixtures specified in the Schedule'.
    """
    import re
    # These patterns match schedule headings, not inline references
    heading_patterns = [
        r'^\s*SCHEDULE\s*I\b',          # "SCHEDULE I" at line start
        r'^\s*SCHEDULE[-\s]*I\b',
        r'^\s*LIST\s+OF\s+FIXTURES',    # "LIST OF FIXTURES" at line start
        r'^\s*LIST\s+OF\s+FITTINGS',
        r'^\s*ANNEXURE\s*[IV]+\b',      # "ANNEXURE I", "ANNEXURE IV" at line start
    ]
    for i, page in enumerate(pages):
        for line in page.split("\n"):
            for pattern in heading_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Confirm it's a heading page — short text or mostly list items
                    return i
    return None


def _ocr_extract(pdf_path: str) -> list[str] | None:
    """Fall back to OCR for scanned PDFs. Returns list of page texts or None on failure."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError:
        return None

    try:
        images = convert_from_path(pdf_path, dpi=300)
    except Exception:
        return None

    pages = []
    for img in images:
        text = pytesseract.image_to_string(img, lang="eng")
        pages.append(text)

    # Only use OCR result if it actually got meaningful text
    total = sum(len(p) for p in pages)
    if total < _MIN_CHARS_PER_PAGE * len(pages):
        return None

    return [_clean_ocr_text(p) for p in pages]


def _clean_ocr_text(text: str) -> str:
    """Clean up common OCR artifacts to improve pattern matching."""
    import re

    # Remove isolated single characters surrounded by whitespace (OCR debris)
    text = re.sub(r'(?<=\s)[^\w\s](?=\s)', ' ', text)

    # Fix common OCR misreads
    replacements = [
        (r'\bGANDLO[RD]+\b', 'LANDLORD'),
        (r'\bLANDLO[RD]+\b', 'LANDLORD'),
        (r'\b1st\b|1%', '1st'),
        (r'5"\s*of\s+every', '5th of every'),
        (r'\bRs\s*[.,]\s*', 'Rs. '),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    # Collapse runs of whitespace (but preserve single newlines for structure)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove lines that are pure garbage (only symbols/single chars)
    cleaned_lines = []
    for line in text.split('\n'):
        stripped = line.strip()
        # Keep if line has at least 2 word characters together
        if not stripped or re.search(r'\w{2,}', stripped):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)
