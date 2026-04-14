"""Core squeeze logic: read, transform, and write BibTeX."""

from pathlib import Path

import bibtexparser
from bibtexparser.model import Entry, String

from bibtex_squeezer.abbreviations import (
    MONTH_ABBREVIATIONS,
    ORDINAL_WORDS,
    PROCEEDINGS_ABBREVIATIONS_MULTI,
    VENUE_STOPWORDS,
    _IEEE_WORD_ABBREV_LOWER,
)


# ---------------------------------------------------------------------------
# Individual transformation passes
# ---------------------------------------------------------------------------

def _abbreviate_venue_word(word: str) -> str | None:
    """Abbreviate one word in a venue title; ``None`` means drop it (stopword)."""
    low = word.lower()
    if low in VENUE_STOPWORDS:
        return None
    if low in ORDINAL_WORDS:
        return ORDINAL_WORDS[low]
    return _IEEE_WORD_ABBREV_LOWER.get(low, word)


def _abbreviate_venue_title(value: str) -> str:
    """Apply full IEEE venue-title squeezing: drop stopwords, convert ordinals,
    abbreviate content words."""
    parts = [_abbreviate_venue_word(w) for w in value.split()]
    return " ".join(p for p in parts if p is not None)


def _strip_outer_braces(value: str) -> str:
    """Remove a single balanced outer brace pair, if present."""
    s = value.strip()
    if s.startswith("{") and s.endswith("}"):
        depth = 0
        for i, ch in enumerate(s):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            if depth == 0 and i < len(s) - 1:
                return s  # braces close before end — not a single outer pair
        return s[1:-1]
    return s

def abbreviate_journals(entry: Entry) -> None:
    """Replace full journal names with their abbreviations."""
    for field in entry.fields:
        if field.key.lower() != "journal":
            continue
        value = _strip_outer_braces(field.value)
        field.value = _abbreviate_venue_title(value)


def abbreviate_journal_strings(library) -> None:
    """Apply journal abbreviations to @String definitions."""
    for string in library.strings:
        value = _strip_outer_braces(string.value)
        string.value = _abbreviate_venue_title(value)


# Fields where word-level abbreviation must NOT be applied.
FIELDS_NO_ABBREVIATE: set[str] = {
    # names
    "author", "editor",
    # the paper / book title itself
    "title",
    # identifiers & links
    "doi", "url", "urldate", "eprint", "archiveprefix", "primaryclass",
    "issn", "isbn",
    # local paths
    "file",
    # free-form / long text
    "abstract", "keywords", "note", "annote",
    # BibTeX internals
    "key", "crossref",
    # numeric / short fields (nothing to abbreviate)
    "pages", "volume", "number", "year", "month",
}


def _abbreviate_word(word: str) -> str:
    """Abbreviate a single word using the IEEE lookup (case-insensitive)."""
    return _IEEE_WORD_ABBREV_LOWER.get(word.lower(), word)


def abbreviate_words(entry: Entry) -> None:
    """Apply IEEE word-level abbreviations to all non-protected fields."""
    for field in entry.fields:
        if field.key.lower() in FIELDS_NO_ABBREVIATE:
            continue
        value = _strip_outer_braces(field.value)
        words = value.split()
        words = [_abbreviate_word(w) for w in words]
        field.value = " ".join(words)


def abbreviate_months(entry: Entry) -> None:
    """Replace full month names with BibTeX three-letter macros."""
    for field in entry.fields:
        if field.key.lower() != "month":
            continue
        value = _strip_outer_braces(field.value)
        if value in MONTH_ABBREVIATIONS:
            field.value = MONTH_ABBREVIATIONS[value]


def abbreviate_booktitles(entry: Entry) -> None:
    """Shorten common words in proceedings / booktitle fields."""
    for field in entry.fields:
        if field.key.lower() not in ("booktitle", "series"):
            continue
        value = _strip_outer_braces(field.value)
        # Multi-word replacements first (e.g. "Technical Digest" → "Tech. Dig.")
        for long, short in PROCEEDINGS_ABBREVIATIONS_MULTI:
            value = value.replace(long, short)
        # Full venue-title squeezing: drop stopwords, convert ordinals, abbreviate
        field.value = _abbreviate_venue_title(value)


def remove_pages(entry: Entry) -> None:
    """Delete the ``pages`` field from an entry."""
    entry.fields = [f for f in entry.fields if f.key.lower() != "pages"]


def remove_months(entry: Entry) -> None:
    """Delete the ``month`` field from an entry."""
    entry.fields = [f for f in entry.fields if f.key.lower() != "month"]


def remove_dois(entry: Entry) -> None:
    """Delete the ``doi`` field from an entry, except for @misc."""
    if entry.entry_type.lower() == "misc":
        return
    entry.fields = [f for f in entry.fields if f.key.lower() != "doi"]


# Entry types where ``url`` is essential and should never be stripped.
URL_REQUIRED_TYPES: set[str] = {"misc", "online", "electronic", "webpage", "software"}


def remove_urls(entry: Entry) -> None:
    """Drop the ``url`` (and ``urldate``) field unless the entry type needs it."""
    if entry.entry_type.lower() in URL_REQUIRED_TYPES:
        return
    entry.fields = [f for f in entry.fields if f.key.lower() not in ("url", "urldate")]


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

def squeeze(
    bibfile: str | Path,
    *,
    abbreviate: bool = True,
    keep_pages: bool = False,
    keep_months: bool = False,
    keep_urls: bool = False,
    keep_dois: bool = False,
) -> str:
    """Read *bibfile*, apply requested transformations, and return BibTeX string.

    Parameters
    ----------
    bibfile : path-like
        Path to the input ``.bib`` file.
    abbreviate : bool
        If ``True`` (default), apply journal and month abbreviations.
    keep_pages : bool
        If ``True``, keep the ``pages`` field (default: removed).
    keep_months : bool
        If ``True``, keep the ``month`` field (default: removed).
    keep_urls : bool
        If ``True``, keep ``url`` / ``urldate`` fields (default: removed, except for @misc, @online, @electronic, @webpage, @software).
    keep_dois : bool
        If ``True``, keep the ``doi`` field (default: removed except for @misc).

    Returns
    -------
    str
        The transformed BibTeX content.
    """
    bibfile = Path(bibfile)
    library = bibtexparser.parse_file(str(bibfile))

    # Abbreviate @String definitions (e.g. journal aliases)
    if abbreviate:
        abbreviate_journal_strings(library)

    for entry in library.entries:
        if abbreviate:
            abbreviate_journals(entry)
            abbreviate_words(entry)
            abbreviate_months(entry)
            abbreviate_booktitles(entry)
        if not keep_pages:
            _remove_pages(entry)
        if not keep_months:
            _remove_months(entry)
        if not keep_urls:
            _remove_urls(entry)
        if not keep_dois:
            remove_dois(entry)

    return bibtexparser.write_string(library)


# Aliases so the local functions don't shadow the parameter names.
_remove_pages = remove_pages
_remove_months = remove_months
_remove_urls = remove_urls
