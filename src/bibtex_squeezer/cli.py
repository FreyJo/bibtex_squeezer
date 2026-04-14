"""Command-line interface for bibtex_squeezer."""

import argparse
import sys

from bibtex_squeezer.squeezer import squeeze

# philosophy: default to hardcore squeeze, turn off individual squeezing steps.

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bibtex_squeezer",
        description="Squeeze a BibTeX file by applying abbreviations and optional clean-up.",
    )
    parser.add_argument(
        "bibfile",
        help="Path to the input .bib file.",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path. Defaults to stdout.",
    )
    parser.add_argument(
        "--keep-pages",
        action="store_true",
        help="Keep page-number fields (default: removed).",
    )
    parser.add_argument(
        "--keep-months",
        action="store_true",
        help="Keep month fields (default: removed).",
    )
    parser.add_argument(
        "--keep-dois",
        action="store_true",
        help="Keep doi fields (default: removed except for @misc).",
    )
    parser.add_argument(
        "--no-abbreviate",
        action="store_true",
        help="Skip journal / month abbreviation (useful for debugging).",
    )
    parser.add_argument(
        "--keep-urls",
        action="store_true",
        help="Keep url/urldate fields (default: removed, except for @misc, @online, @electronic, @webpage, @software).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = squeeze(
        bibfile=args.bibfile,
        abbreviate=not args.no_abbreviate,
        keep_pages=args.keep_pages,
        keep_months=args.keep_months,
        keep_urls=args.keep_urls,
        keep_dois=args.keep_dois,
    )

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(result)
    else:
        sys.stdout.write(result)
