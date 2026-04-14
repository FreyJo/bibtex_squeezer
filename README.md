# `bibtex_squeezer`

In many IEEE journals and conference proceedings, the reference list counts towards the page limit.
Manually shortening references is tedious and error-prone.
**`bibtex_squeezer`** automates this by applying the official IEEE abbreviation rules and stripping fields that are not required in a printed reference list — giving you a shorter, standard-compliant bibliography without any manual effort.

**What it does by default:**
- Abbreviates journal names, booktitles, and conference proceedings word-by-word following [IEEE guidelines](#ieee-guidelines): stopwords are dropped, ordinal words are converted to numeric form ("Third" → "3rd"), and content words are abbreviated ("Transactions" → "Trans.", "International" → "Int.", etc.)
- Removes fields that typically don't affect the printed reference and only add length (see [CLI Arguments](#cli-arguments) for defaults and how to opt out): `pages`, `month`, `doi`, `url`, `urldate`

`doi` and `url` fields are intentionally preserved for web-only entry types (`@misc`, `@online`, `@electronic`, `@webpage`, `@software`) where they are the primary locator.

## Installation

```bash
pip install -e .
```

## Usage

```bash
bibtex_squeezer refs.bib               # output to stdout
bibtex_squeezer refs.bib -o out.bib    # write to file
python -m bibtex_squeezer refs.bib    # run as module
```

## CLI Arguments

All squeeze steps are on by default.
Use the flags below to opt out of individual steps.

| Argument | Description |
|---|---|
| `bibfile` | Path to the input `.bib` file. |
| `-o`, `--output OUTPUT` | Output file path. Defaults to stdout. |
| `--keep-pages` | Keep page-number fields (default: removed). |
| `--keep-months` | Keep month fields (default: removed). |
| `--keep-dois` | Keep doi fields (default: removed except for `@misc`). |
| `--keep-urls` | Keep url/urldate fields (default: removed, except for `@misc`, `@online`, `@electronic`, `@webpage`, `@software`). |
| `--no-abbreviate` | Skip all abbreviation passes. |
| `-h`, `--help` | Show help message and exit. |

## IEEE Guidelines

The abbreviation rules implemented here follow the official IEEE reference style:

- [IEEE Editorial Style Manual](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/create-the-text-of-your-article/ieee-editorial-style-manual/)
- [IEEE Editorial Style Manual for Authors](https://docs.google.com/document/d/1OalFYqVfxKKMelF79U3B93SjmIEiTnJC12wPJrKeSDM)
- [IEEE Reference Guide](https://docs.google.com/document/d/1j1L96U2NagwWI9MEVDNVKt9pXxRzTH7h3krI3Mb6wZE)

