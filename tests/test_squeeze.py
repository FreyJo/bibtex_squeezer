"""Integration tests — run the full squeeze pipeline on small .bib files."""

import pytest

from bibtex_squeezer.squeezer import squeeze


# Helper: run squeeze on a fixture .bib and return the output string.
# Each test parametrizes "bib_path" with the fixture filename.

class TestBasic:
    """basic.bib — article with inline journal, month, url, pages."""

    @pytest.mark.parametrize("bib_path", ["basic.bib"], indirect=True)
    def test_journal_abbreviated(self, bib_path):
        result = squeeze(bib_path)
        assert "IEEE Trans. Autom. Control" in result

    @pytest.mark.parametrize("bib_path", ["basic.bib"], indirect=True)
    def test_month_abbreviated(self, bib_path):
        result = squeeze(bib_path, keep_months=True)
        assert "mar" in result.lower()

    @pytest.mark.parametrize("bib_path", ["basic.bib"], indirect=True)
    def test_remove_pages(self, bib_path):
        result = squeeze(bib_path, keep_pages=False)
        assert "pages" not in result.lower()

    @pytest.mark.parametrize("bib_path", ["basic.bib"], indirect=True)
    def test_remove_urls(self, bib_path):
        result = squeeze(bib_path, keep_urls=False, keep_dois=True)
        assert "url" not in result.lower().split("\n")[0]  # no url field
        # doi must survive
        assert "doi" in result.lower()

    @pytest.mark.parametrize("bib_path", ["basic.bib"], indirect=True)
    def test_no_abbreviate(self, bib_path):
        result = squeeze(bib_path, abbreviate=False)
        assert "IEEE Transactions on Automatic Control" in result


class TestStringDefs:
    """string_defs.bib — journal defined via @String."""

    @pytest.mark.parametrize("bib_path", ["string_defs.bib"], indirect=True)
    def test_string_journal_abbreviated(self, bib_path):
        result = squeeze(bib_path)
        assert "IEEE Trans. Autom. Control" in result


class TestInproceedings:
    """inproceedings.bib — booktitle with conference words."""

    @pytest.mark.parametrize("bib_path", ["inproceedings.bib"], indirect=True)
    def test_booktitle_abbreviated(self, bib_path):
        result = squeeze(bib_path)
        assert "Proc." in result
        assert "Int." in result
        assert "Conf." in result

    @pytest.mark.parametrize("bib_path", ["inproceedings.bib"], indirect=True)
    def test_publisher_words_abbreviated(self, bib_path):
        """publisher is not a protected field, so IEEE words apply."""
        result = squeeze(bib_path)
        assert "Int." in result  # "International" abbreviated


class TestMiscUrl:
    """misc_with_url.bib — url kept for @misc, removed for @article."""

    @pytest.mark.parametrize("bib_path", ["misc_with_url.bib"], indirect=True)
    def test_misc_keeps_url(self, bib_path):
        result = squeeze(bib_path, keep_urls=False)
        # The @misc entry must still have a url
        assert "https://github.com/example/toolbox" in result

    @pytest.mark.parametrize("bib_path", ["misc_with_url.bib"], indirect=True)
    def test_article_loses_url(self, bib_path):
        result = squeeze(bib_path, keep_urls=False)
        # The @article's doi.org url should be gone
        assert "https://doi.org/10.1016/j.automatica.2023.01.001" not in result


class TestInbookUmlauts:
    """inbook_umlauts.bib — LaTeX umlauts in author/editor, braced {MIMO}, series field."""

    @pytest.mark.parametrize("bib_path", ["inbook_umlauts.bib"], indirect=True)
    def test_author_untouched(self, bib_path):
        result = squeeze(bib_path)
        assert 'Angeby' in result
        assert 'Huschenbett' in result

    @pytest.mark.parametrize("bib_path", ["inbook_umlauts.bib"], indirect=True)
    def test_editor_untouched(self, bib_path):
        result = squeeze(bib_path)
        assert 'Allg' in result  # editor with umlaut preserved

    @pytest.mark.parametrize("bib_path", ["inbook_umlauts.bib"], indirect=True)
    def test_series_abbreviated(self, bib_path):
        result = squeeze(bib_path)
        # "Lecture Notes in Control and Information Sciences"
        # → IEEE words: "Lect." doesn't exist, but "Inf." and "Sci." do
        assert "Inf." in result
        assert "Sci." in result

    @pytest.mark.parametrize("bib_path", ["inbook_umlauts.bib"], indirect=True)
    def test_title_untouched(self, bib_path):
        """title is a protected field — 'Automotive' must NOT become 'Automot.'."""
        result = squeeze(bib_path)
        assert "Automotive" in result

    @pytest.mark.parametrize("bib_path", ["inbook_umlauts.bib"], indirect=True)
    def test_keywords_untouched(self, bib_path):
        result = squeeze(bib_path)
        assert "whatnot" in result


class TestArticleRemoveFields:
    """article_remove_fields.bib — pages and doi must be removed by default."""

    @pytest.mark.parametrize("bib_path", ["article_remove_fields.bib"], indirect=True)
    def test_pages_and_doi_removed(self, bib_path):
        result = squeeze(bib_path)
        assert "pages" not in result.lower()
        assert "doi" not in result.lower()
        # But other fields remain
        assert "journal" in result.lower()
        assert "acm trans." in result.lower()


class TestInproceedingsStopwords:
    """inproceedings_stopwords.bib — stopwords (of, the, on) dropped from booktitle."""

    @pytest.mark.parametrize("bib_path", ["inproceedings_stopwords.bib"], indirect=True)
    def test_stopwords_dropped_from_booktitle(self, bib_path):
        result = squeeze(bib_path)
        # "of", "the", "on" must be gone from the booktitle
        assert "Proc. of" not in result
        assert "of the" not in result
        assert " on " not in result

    @pytest.mark.parametrize("bib_path", ["inproceedings_stopwords.bib"], indirect=True)
    def test_content_words_preserved(self, bib_path):
        result = squeeze(bib_path)
        assert "Proc." in result
        assert "IEEE" in result
        assert "Conf." in result
        assert "(CDC)" in result
