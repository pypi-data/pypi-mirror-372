from chATLAS_Embed.process_md.long_tokens import (
    replace_dataset_ids,
    replace_long_tokens,
    replace_long_tokens_only,
    replace_paths,
    replace_urls,
)


class TestReplaceUrls:
    """Test the replace_urls function."""

    def test_replace_single_url(self):
        """Test replacing a single URL."""
        text = "Visit https://example.com for more info"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Visit [URL-0] for more info"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "https://example.com"

        text = "Visit www.example.com for more info"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Visit [URL-0] for more info"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "www.example.com"

    def test_replace_url_in_md(self):
        """Test replacing a single URL."""
        text = "Here is a link: [Example](https://example.com)"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Here is a link: [Example]([URL-0])"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "https://example.com"

        text = "Here is a link: [mc_production](https://gitlab.cern.ch/test/-/tree/master/mc_production?ref_type=heads)"
        result_text, placeholders = replace_urls(text)
        assert result_text == "Here is a link: [mc_production]([URL-0])"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "https://gitlab.cern.ch/test/-/tree/master/mc_production?ref_type=heads"

    def test_replace_multiple_urls(self):
        """Test replacing multiple URLs."""
        text = "Visit https://example.com and http://test.org"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Visit [URL-0] and [URL-1]"
        assert len(placeholders) == 2
        assert placeholders["[URL-0]"] == "https://example.com"
        assert placeholders["[URL-1]"] == "http://test.org"

    def test_replace_ftp_url(self):
        """Test replacing FTP URLs."""
        text = "Download from ftp://files.example.com/file.txt"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Download from [URL-0]"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "ftp://files.example.com/file.txt"

    def test_no_urls_to_replace(self):
        """Test text with no URLs."""
        text = "This is just regular text with no URLs"
        result_text, placeholders = replace_urls(text)

        assert result_text == text
        assert len(placeholders) == 0

    def test_duplicate_urls(self):
        """Test that duplicate URLs are handled correctly."""
        text = "Visit https://example.com and then https://example.com again"
        result_text, placeholders = replace_urls(text)

        assert result_text == "Visit [URL-0] and then [URL-0] again"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "https://example.com"

    def test_url_like_but_no_scheme(self):
        """Test that text without schemes is not replaced."""
        text = "Check example.com or test.org"
        result_text, placeholders = replace_urls(text)

        assert result_text == text
        assert len(placeholders) == 0


class TestReplacePaths:
    """Test the replace_paths function."""

    def test_replace_unix_path(self):
        """Test replacing Unix-style paths."""
        text = "The file is at /home/user/documents/file.txt"
        result_text, placeholders = replace_paths(text)

        assert result_text == "The file is at [PATH-0]"
        assert len(placeholders) == 1
        assert placeholders["[PATH-0]"] == "/home/user/documents/file.txt"

    def test_not_replace_latex(self):
        """Test replacing Windows-style paths."""
        text = "This \\ell\\nu"
        result_text, placeholders = replace_paths(text)

        assert result_text == text
        assert len(placeholders) == 0

    def test_replace_mixed_separators(self):
        """Test replacing paths with mixed separators."""
        text = "Path is /home/user\\mixed/separators\\file.txt"
        result_text, placeholders = replace_paths(text)

        assert result_text == "Path is [PATH-0]"
        assert len(placeholders) == 1
        assert placeholders["[PATH-0]"] == "/home/user\\mixed/separators\\file.txt"

    def test_short_path_not_replaced(self):
        """Test that paths with fewer than 2 separators are not replaced."""
        text = "Simple path like /home or C:\\Users"
        result_text, placeholders = replace_paths(text)

        assert result_text == text
        assert len(placeholders) == 0

    def test_multiple_paths(self):
        """Test replacing multiple paths."""
        text = "Copy from /src/path/file.txt to /dest/path/file.txt"
        result_text, placeholders = replace_paths(text)

        assert result_text == "Copy from [PATH-0] to [PATH-1]"
        assert len(placeholders) == 2
        assert placeholders["[PATH-0]"] == "/src/path/file.txt"
        assert placeholders["[PATH-1]"] == "/dest/path/file.txt"

    def test_path_in_backticks(self):
        """Test that paths in backticks are handled correctly."""
        text = "Run `ls /home/user/documents/file.txt` command"
        result_text, placeholders = replace_paths(text)

        assert result_text == "Run `ls [PATH-0]` command"
        assert len(placeholders) == 1
        assert placeholders["[PATH-0]"] == "/home/user/documents/file.txt"

    def test_path_in_md(self):
        """Test that paths in markdown links are handled correctly."""
        text = "Check this file: [file](home/user/documents/file.txt)"
        result_text, placeholders = replace_paths(text)

        assert result_text == "Check this file: [file]([PATH-0])"
        assert len(placeholders) == 1
        assert placeholders["[PATH-0]"] == "home/user/documents/file.txt"


class TestReplaceDatasetIds:
    """Test the replace_dataset_ids function."""

    def test_replace_dataset_id(self):
        """Test replacing a dataset ID with multiple dots."""
        text = "Use dataset data.mc16.physics.Main.deriv.DAOD_PHYSLITE.p1234"
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == "Use dataset [DSID-0]"
        assert len(placeholders) == 1
        assert placeholders["[DSID-0]"] == "data.mc16.physics.Main.deriv.DAOD_PHYSLITE.p1234"

    def test_replace_multiple_dataset_ids(self):
        """Test replacing multiple dataset IDs."""
        text = "Compare data.mc16.physics.Main.p1 and data.mc20.physics.Test.p2"
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == "Compare [DSID-0] and [DSID-1]"
        assert len(placeholders) == 2
        assert placeholders["[DSID-0]"] == "data.mc16.physics.Main.p1"
        assert placeholders["[DSID-1]"] == "data.mc20.physics.Test.p2"

    def test_few_dots_not_replaced(self):
        """Test that strings with fewer than 3 dots are not replaced."""
        text = "Version 1.2.3 should not be replaced"
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == text
        assert len(placeholders) == 0

    def test_exactly_three_dots(self):
        """Test that strings with exactly 3 dots are replaced."""
        text = "Dataset a.b.c.d should be replaced"
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == "Dataset [DSID-0] should be replaced"
        assert len(placeholders) == 1
        assert placeholders["[DSID-0]"] == "a.b.c.d"

    def test_dataset_id_in_backticks(self):
        """Test dataset IDs in backticks."""
        text = "Use `data.mc16.physics.Main.deriv.DAOD.p1234` for analysis"
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == "Use `[DSID-0]` for analysis"
        assert len(placeholders) == 1
        assert placeholders["[DSID-0]"] == "data.mc16.physics.Main.deriv.DAOD.p1234"

    def test_elipses_no_replacement(self):
        """Test that ellipses are not replaced."""
        text = "This is a long string with ellipses..."
        result_text, placeholders = replace_dataset_ids(text)

        assert result_text == text
        assert len(placeholders) == 0


class TestReplaceLongTokensOnly:
    """Test the replace_long_tokens_only function."""

    def test_replace_long_token(self):
        """Test replacing a token longer than threshold."""
        text = "This is a verylongwordthatexceedsthethresholdlimit here"
        result_text, placeholders = replace_long_tokens_only(text, 20)

        assert result_text == "This is a [LONG-TOKEN-0] here"
        assert len(placeholders) == 1
        assert placeholders["[LONG-TOKEN-0]"] == "verylongwordthatexceedsthethresholdlimit"

    def test_short_tokens_not_replaced(self):
        """Test that short tokens are not replaced."""
        text = "These are all short words"
        result_text, placeholders = replace_long_tokens_only(text, 50)

        assert result_text == text
        assert len(placeholders) == 0

    def test_multiple_long_tokens(self):
        """Test replacing multiple long tokens."""
        text = "verylongtoken1 and anotherveryverylongtoken2 here"
        result_text, placeholders = replace_long_tokens_only(text, 10)

        assert result_text == "[LONG-TOKEN-0] and [LONG-TOKEN-1] here"
        assert len(placeholders) == 2
        assert placeholders["[LONG-TOKEN-0]"] == "verylongtoken1"
        assert placeholders["[LONG-TOKEN-1]"] == "anotherveryverylongtoken2"

    def test_custom_threshold(self):
        """Test with custom threshold."""
        text = "mediumword and verylongword"
        result_text, placeholders = replace_long_tokens_only(text, 8)

        assert result_text == "[LONG-TOKEN-0] and [LONG-TOKEN-1]"
        assert len(placeholders) == 2
        assert placeholders["[LONG-TOKEN-0]"] == "mediumword"
        assert placeholders["[LONG-TOKEN-1]"] == "verylongword"

    def test_token_at_threshold_boundary(self):
        """Test tokens exactly at threshold length."""
        text = "exactly20characters1"
        result_text, placeholders = replace_long_tokens_only(text, 20)

        # Token with 20 chars should NOT be replaced (> threshold)
        assert result_text == text
        assert len(placeholders) == 0

        # Token with 21 chars should be replaced
        text = "exactly21characters12"
        result_text, placeholders = replace_long_tokens_only(text, 20)
        assert result_text == "[LONG-TOKEN-0]"
        assert len(placeholders) == 1
        assert placeholders["[LONG-TOKEN-0]"] == "exactly21characters12"


class TestReplaceTokens:
    """Test the main replace_long_tokens function."""

    def test_replace_all_token_types(self):
        """Test replacing all types of tokens in one text."""
        text = """Visit https://example.com for info.
File at /home/user/very/long/path/file.txt
Dataset: data.mc16.physics.Main.deriv.DAOD_PHYSLITE.p1234
Long token: supercalifragilisticexpialidocious"""
        result_text, placeholders = replace_long_tokens(text, 20)

        expected_text = """Visit [URL-0] for info.
File at [PATH-0]
Dataset: [DSID-0]
Long token: [LONG-TOKEN-0]"""

        assert result_text == expected_text
        assert len(placeholders) == 4
        assert placeholders["[URL-0]"] == "https://example.com"
        assert placeholders["[PATH-0]"] == "/home/user/very/long/path/file.txt"
        assert placeholders["[DSID-0]"] == "data.mc16.physics.Main.deriv.DAOD_PHYSLITE.p1234"
        assert placeholders["[LONG-TOKEN-0]"] == "supercalifragilisticexpialidocious"

    def test_no_tokens_to_replace(self):
        """Test text with no tokens to replace."""
        text = "This is just normal text with short words"
        result_text, placeholders = replace_long_tokens(text)

        assert result_text == text
        assert len(placeholders) == 0

    def test_replacement_order_matters(self):
        """Test that replacement order doesn't interfere."""
        # URL that could also be considered a long token
        text = "Visit https://very-long-domain-name-that-exceeds-threshold.com/path"
        result_text, placeholders = replace_long_tokens(text, 20)

        # Should be replaced as URL, not as long token
        assert result_text == "Visit [URL-0]"
        assert len(placeholders) == 1
        assert placeholders["[URL-0]"] == "https://very-long-domain-name-that-exceeds-threshold.com/path"

    def test_custom_threshold(self):
        """Test with custom long token threshold."""
        text = "mediumlengthword and verylongword"
        result_text, placeholders = replace_long_tokens(text, 10)

        # Both should be replaced as long tokens
        assert result_text == "[LONG-TOKEN-0] and [LONG-TOKEN-1]"
        assert len(placeholders) == 2
        assert placeholders["[LONG-TOKEN-0]"] == "mediumlengthword"
        assert placeholders["[LONG-TOKEN-1]"] == "verylongword"

    def test_complex_mixed_content(self):
        """Test with complex content mixing different token types."""
        text = """# Analysis Documentation

Data source: https://atlas-data.cern.ch/repository
Local path: /atlas/data/mc16/physics/samples/file.root
Dataset ID: 

data.mc16.physics.Main.deriv.DAOD_PHYSLITE.e1234.s5678.r9012

Use this verylongcommandlineoptionthatexceedsthethreshold for processing."""
        result_text, placeholders = replace_long_tokens(text, 25)

        expected_text = """# Analysis Documentation

Data source: [URL-0]
Local path: [PATH-0]
Dataset ID: 

[DSID-0]

Use this [LONG-TOKEN-0] for processing."""

        assert result_text == expected_text
        assert len(placeholders) == 4
        assert placeholders["[URL-0]"] == "https://atlas-data.cern.ch/repository"
        assert placeholders["[PATH-0]"] == "/atlas/data/mc16/physics/samples/file.root"
        assert placeholders["[DSID-0]"] == "data.mc16.physics.Main.deriv.DAOD_PHYSLITE.e1234.s5678.r9012"
        assert placeholders["[LONG-TOKEN-0]"] == "verylongcommandlineoptionthatexceedsthethreshold"

    def test_empty_input(self):
        """Test with empty input."""
        result_text, placeholders = replace_long_tokens("")

        assert result_text == ""
        assert len(placeholders) == 0

    def test_whitespace_only(self):
        """Test with whitespace-only input."""
        text = "   \n\t  "
        result_text, placeholders = replace_long_tokens(text)

        assert result_text == text
        assert len(placeholders) == 0
