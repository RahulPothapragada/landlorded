"""Load and index the legal corpus for statute lookups."""

import re
from pathlib import Path
from dataclasses import dataclass, field


CORPUS_DIR = Path(__file__).parent / "corpus" / "statutes"


@dataclass
class StatuteSection:
    """A single section from a statute file."""
    act: str
    section_id: str       # e.g. "Section 11" or "Article 35"
    heading: str          # e.g. "Security deposit"
    text: str             # verbatim text
    source_file: str


@dataclass
class Corpus:
    """The full loaded legal corpus, indexed by section reference."""
    sections: dict[str, StatuteSection] = field(default_factory=dict)
    raw_files: dict[str, str] = field(default_factory=dict)

    def get(self, ref: str) -> StatuteSection | None:
        """Look up a section by reference string like 'TN Act 2017, Section 11(1)'."""
        # Try exact match first
        if ref in self.sections:
            return self.sections[ref]
        # Try base section (strip sub-section)
        base = re.sub(r'\(\d+\).*$', '', ref).strip()
        if base in self.sections:
            return self.sections[base]
        return None

    def get_text(self, ref: str) -> str:
        """Get verbatim text for a section reference, or empty string."""
        s = self.get(ref)
        return s.text if s else ""


def load_corpus() -> Corpus:
    """Load all statute files and index sections."""
    corpus = Corpus()

    if not CORPUS_DIR.exists():
        return corpus

    for path in CORPUS_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        corpus.raw_files[path.stem] = content
        _index_file(corpus, path.stem, content)

    return corpus


def _index_file(corpus: Corpus, file_stem: str, content: str):
    """Parse a statute file and add sections to the corpus index."""
    act_name = _detect_act_name(file_stem)

    # Split on ## headings
    sections = re.split(r'^## ', content, flags=re.MULTILINE)

    for section_block in sections[1:]:  # skip preamble before first ##
        lines = section_block.strip().split("\n", 1)
        heading_line = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Extract section ID from heading
        section_id = _extract_section_id(heading_line)
        if not section_id:
            continue

        key = f"{act_name}, {section_id}"
        corpus.sections[key] = StatuteSection(
            act=act_name,
            section_id=section_id,
            heading=heading_line,
            text=body,
            source_file=file_stem,
        )


def _detect_act_name(file_stem: str) -> str:
    """Map file stem to canonical act name."""
    mapping = {
        "tn_act_2017": "TN Act 2017",
        "tn_act_2017_rules": "TN Rules 2019",
        "tn_rent_authority": "TN Rent Authority",
        "cpa_2019": "CPA 2019",
        "tpa_sections": "TPA 1882",
        "indian_stamp_act": "Indian Stamp Act 1899",
    }
    return mapping.get(file_stem, file_stem)


def _extract_section_id(heading: str) -> str | None:
    """Extract section identifier from a heading line."""
    # "Section 11(1) — Security deposit" -> "Section 11"
    # "Section 2(7) — 'consumer'" -> "Section 2(7)"
    # "Article 35 — Lease" -> "Article 35"
    patterns = [
        r'(Section\s+\d+\(\d+\))',       # Section 2(7), Section 11(2)
        r'(Section\s+\d+[-\w]*)',          # Section 4-A, Section 20
        r'(Article\s+\d+)',                # Article 35
        r'(Rule\s+\d+\(\d+\))',            # Rule 7(2)
        r'(Rule\s+\d+)',                   # Rule 3
    ]
    for pattern in patterns:
        m = re.search(pattern, heading, re.IGNORECASE)
        if m:
            return m.group(1)
    return None
