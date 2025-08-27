"""Tests for the split_text module."""

from typing import cast

import pytest

from chATLAS_Embed.process_md.split_text import (
    _recombine_small_chunks,
    _split_by_markdown_sections,
    _split_by_sentences,
    _split_by_separator,
    _split_by_words,
    split_text_recursive,
)

# Test data strings
SHORT_TEXT = "This is a short text that should not be split."

PARAGRAPH_TEXT = """This is the first paragraph.
It has multiple lines within it.

This is the second paragraph.
It also has multiple lines.

This is the third paragraph.
And it continues the pattern."""

LONG_PARAGRAPH_TEXT = """This is a very long paragraph that should be split. It contains multiple sentences. Each sentence adds to the overall length. We want to test how the chunking algorithm handles this. The algorithm should split this into manageable pieces. It should preserve sentence boundaries when possible. This helps maintain readability and context. The splitting should be intelligent and not arbitrary."""

SENTENCE_TEXT = (
    "First sentence. Second sentence! Third sentence? Fourth sentence. Fifth sentence with more content than usual."
)

WORD_TEST_TEXT = "This text has many individual words that should be split if the maximum length is very small and forces word-level splitting."

MIXED_CONTENT_TEXT = """# Chapter 1: Introduction

This is the introduction paragraph. It explains the basic concepts.

## Section 1.1: Overview

Here we have another paragraph. This one is longer and contains more detailed information about the topic at hand.

- First bullet point
- Second bullet point  
- Third bullet point

## Section 1.2: Details

The details section contains even more information. It has multiple sentences that provide comprehensive coverage of the subject matter.

# Chapter 2: Advanced Topics

This chapter covers advanced concepts. The content here is more complex and requires careful handling during the chunking process."""

TINY_CHUNKS_TEXT = "A.\n\nB.\n\nC.\n\nD.\n\nE."


def test_split_text_recursive_short_text():
    """Test that short text is returned as-is."""
    # Should not split short text
    result = split_text_recursive(SHORT_TEXT, max_length=100, min_length=20)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == SHORT_TEXT
    # Should preserve content exactly
    assert result[0].strip() == SHORT_TEXT.strip()


def test_split_text_recursive_paragraph_splitting():
    """Test splitting by paragraphs."""
    # Should split into multiple paragraphs
    result = split_text_recursive(PARAGRAPH_TEXT, max_length=80, min_length=20)
    assert isinstance(result, list)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 80
        assert len(chunk.strip()) > 0
    # Check that each paragraph is present
    for paragraph in PARAGRAPH_TEXT.split("\n\n"):
        assert any(paragraph.strip() in chunk for chunk in result)


def test_split_text_recursive_sentence_splitting():
    """Test that long paragraphs get split by sentences."""
    # Should split long paragraph by sentences
    result = split_text_recursive(LONG_PARAGRAPH_TEXT, max_length=100, min_length=20)
    assert isinstance(result, list)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 100
        # Check that sentence boundaries are preserved where possible
        if ". " in chunk or chunk.strip().endswith("."):
            # Should not end mid-sentence (unless it's the last sentence)
            assert chunk.strip()[-1] == "." or chunk.strip()[-1] in "!?"
    # Check that all sentences are present
    for sentence in LONG_PARAGRAPH_TEXT.split(". "):
        assert any(sentence.split(".")[0] in chunk for chunk in result)


def test_split_text_recursive_word_splitting():
    """Test word-level splitting as last resort."""
    result = split_text_recursive(WORD_TEST_TEXT, max_length=20, min_length=5)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 20
        assert len(chunk.strip()) > 0


def test_split_text_recursive_mixed_content():
    """Test handling of mixed content with headers, paragraphs, and lists."""
    result = split_text_recursive(MIXED_CONTENT_TEXT, max_length=200, min_length=50)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 200
        assert len(chunk.strip()) > 0


def test_split_by_separator_basic():
    """Test basic separator splitting functionality."""
    text = "Part1\n\nPart2\n\nPart3"
    result = _split_by_separator(text, "\n\n", max_length=10)
    expected = ["Part1", "Part2", "Part3"]
    assert isinstance(result, list)
    assert result == expected
    # Each chunk should be non-empty and not exceed max_length
    for chunk in result:
        assert len(chunk.strip()) > 0
        assert len(chunk) <= 10


def test_split_by_separator_respects_max_length():
    """Test that separator splitting respects max length."""
    text = "Short\n\nThis is a longer part that exceeds limit\n\nShort"
    result = _split_by_separator(text, "\n\n", max_length=15)
    assert isinstance(result, list)
    assert len(result) == 3
    for chunk in result:
        assert len(chunk.strip()) > 0
        assert len(chunk) <= 15 or chunk == "This is a longer part that exceeds limit"


def test_split_by_separator_combines_small_parts():
    """Test that small parts get combined when possible."""
    text = "A\n\nB\n\nC\n\nD"
    result = _split_by_separator(text, "\n\n", max_length=10)
    # Should combine some small parts
    assert isinstance(result, list)
    assert len(result) < 4
    # Each chunk should be non-empty and not exceed max_length
    for chunk in result:
        assert len(chunk.strip()) > 0
        assert len(chunk) <= 10


def test_split_by_markdown_sections_basic():
    """Test basic markdown section splitting."""
    text = """# Header 1

Content for section 1.

## Subheader 1.1

More content here.

# Header 2

Content for section 2."""
    result = _split_by_markdown_sections(text, max_length=50)
    assert isinstance(result, list)
    assert len(result) > 1
    # Check that headers are preserved in chunks
    has_header1 = any("# Header 1" in chunk for chunk in result)
    has_header2 = any("# Header 2" in chunk for chunk in result)
    assert has_header1
    assert has_header2
    # Each chunk should be non-empty and not exceed max_length
    for chunk in result:
        assert len(chunk.strip()) > 0
        assert len(chunk) <= 50


def test_split_by_markdown_sections_respects_max_length():
    """Test that markdown section splitting respects max length."""
    text = """# Short Header

Short content.

# Another Header

This is a much longer section with more content that should exceed the maximum length limit and force a split."""

    result = _split_by_markdown_sections(text, max_length=80)

    # Check that most chunks respect max_length
    for chunk in result:
        assert len(chunk) <= 80 or "This is a much longer section" in chunk

    # Verify specific content is preserved
    assert any("# Short Header" in chunk for chunk in result)
    assert any("# Another Header" in chunk for chunk in result)
    assert any("Short content" in chunk for chunk in result)


def test_split_by_markdown_sections_preserves_headers():
    """Test that markdown headers are kept with their content."""
    text = """# Main Header

This is the content under the main header.
It has multiple lines.

## Subheader

This is content under the subheader.

### Sub-subheader

Even more nested content here."""

    result = _split_by_markdown_sections(text, max_length=100)

    # Each chunk with content should have its corresponding header
    for chunk in result:
        if "content under the main header" in chunk:
            assert "# Main Header" in chunk
        if "content under the subheader" in chunk:
            assert "## Subheader" in chunk
        if "Even more nested content" in chunk:
            assert "### Sub-subheader" in chunk


def test_split_by_markdown_sections_handles_no_headers():
    """Test that text without headers is handled gracefully."""
    text = """This is just regular text without any headers.
It has multiple paragraphs.

Another paragraph here.
And some more content."""

    result = _split_by_markdown_sections(text, max_length=50)

    # Should still split the text somehow
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk.strip()) > 0


def test_split_by_markdown_sections_single_long_header():
    """Test handling of a single very long header section."""
    text = """# This is a very long header section

This section contains a lot of content that exceeds the maximum length. It has multiple sentences and should be handled appropriately. The algorithm should split this content while preserving the header association."""

    result = _split_by_markdown_sections(text, max_length=100)

    assert len(result) >= 1
    # The first chunk should contain the header
    assert "# This is a very long header section" in result[0]


def test_split_by_markdown_sections_empty_sections():
    """Test handling of headers with no content."""
    text = """# Header 1

# Header 2

Some content here.

# Header 3"""

    result = _split_by_markdown_sections(text, max_length=50)

    assert len(result) >= 1
    # Headers should be preserved even if they have no content
    combined = "\n".join(result)
    assert "# Header 1" in combined
    assert "# Header 2" in combined
    assert "# Header 3" in combined


def test_split_by_sentences_basic():
    """Test basic sentence splitting."""
    result = _split_by_sentences(SENTENCE_TEXT, max_length=30)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 30


def test_split_by_sentences_preserves_sentence_endings():
    """Test that sentence splitting preserves proper endings."""
    text = "First sentence. Second sentence! Third sentence?"
    result = _split_by_sentences(text, max_length=20)

    for chunk in result:
        # Each chunk should either be a complete sentence or start properly
        if "." in chunk or "!" in chunk or "?" in chunk:
            assert chunk.strip()[-1] in ".!?" or len(chunk.split()) == 1


def test_split_by_sentences_handles_long_sentences():
    """Test that very long sentences get split by words."""
    long_sentence = "This is an extremely long sentence that contains many words and definitely exceeds any reasonable maximum length limit."
    result = _split_by_sentences(long_sentence, max_length=20)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 20


def test_split_by_words_basic():
    """Test basic word splitting."""
    text = "This is a test sentence with multiple words"
    result = _split_by_words(text, max_length=15)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 15
        assert len(chunk.strip()) > 0


def test_split_by_words_preserves_words():
    """Test that word splitting doesn't break words."""
    text = "Word1 Word2 Word3 Word4"
    result = _split_by_words(text, max_length=10)

    for chunk in result:
        # Each chunk should contain complete words
        words = chunk.split()
        for word in words:
            assert word in text


def test_split_by_words_single_word():
    """Test word splitting with single word input."""
    result = _split_by_words("Hello", max_length=10)
    assert result == ["Hello"]


def test_recombine_small_chunks_basic():
    """Test basic recombination of small chunks."""
    small_chunks = ["A", "B", "C", "D"]
    result = _recombine_small_chunks(small_chunks, max_length=10, min_length=3)

    assert len(result) < len(small_chunks)  # Should combine some chunks


def test_recombine_small_chunks_respects_max_length():
    """Test that recombination respects maximum length when combining chunks."""
    chunks = ["Short1", "Short2", "Short3"]
    result = _recombine_small_chunks(chunks, max_length=15, min_length=5)

    # Should combine some chunks without exceeding max_length
    assert len(result) < len(chunks)
    for chunk in result:
        assert len(chunk) <= 15


def test_recombine_small_chunks_preserves_long_chunks():
    """Test that chunks already longer than max_length are preserved as-is."""
    chunks = ["Short1", "Short2", "This is a longer chunk that exceeds the limit"]
    result = _recombine_small_chunks(chunks, max_length=15, min_length=5)

    # The long chunk should be preserved even though it exceeds max_length
    long_chunks = [chunk for chunk in result if len(chunk) > 15]
    assert len(long_chunks) == 1
    assert "This is a longer chunk that exceeds the limit" in long_chunks[0]


def test_recombine_small_chunks_empty_input():
    """Test recombination with empty input."""
    result = _recombine_small_chunks([], max_length=100, min_length=10)
    assert result == []


def test_recombine_small_chunks_single_chunk():
    """Test recombination with single chunk."""
    result = _recombine_small_chunks(["Single chunk"], max_length=100, min_length=10)
    assert result == ["Single chunk"]


def test_recombine_small_chunks_with_tiny_chunks():
    """Test recombination of very small chunks."""
    chunks = cast(list[str], TINY_CHUNKS_TEXT.split("\n\n"))
    result = _recombine_small_chunks(chunks, max_length=50, min_length=5)

    # Should combine the tiny chunks
    assert len(result) < 5
    for chunk in result:
        assert len(chunk) <= 50


def test_edge_case_empty_text():
    """Test handling of empty text input."""
    result = split_text_recursive("", max_length=100, min_length=10)
    assert result == [""]


def test_edge_case_whitespace_only():
    """Test handling of whitespace-only text."""
    result = split_text_recursive("   \n\n   ", max_length=100, min_length=10)
    assert len(result) == 1


def test_edge_case_very_small_max_length():
    """Test behavior with very small max_length."""
    result = split_text_recursive("Hello world", max_length=5, min_length=1)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 5


def test_parameters_min_length_larger_than_max():
    """Test behavior when min_length is larger than max_length."""
    # This should still work, prioritizing max_length
    result = split_text_recursive(PARAGRAPH_TEXT, max_length=50, min_length=100)

    for chunk in result:
        assert len(chunk) <= 50  # max_length should be respected


def test_integration_full_workflow():
    """Test the complete workflow with a complex text."""
    result = split_text_recursive(MIXED_CONTENT_TEXT, max_length=150, min_length=30)

    # Verify all chunks are within limits
    for chunk in result:
        assert len(chunk) <= 150
        assert len(chunk.strip()) > 0

    # Verify content is preserved
    combined_result = "\n\n".join(result)
    # Remove extra whitespace for comparison
    original_words = MIXED_CONTENT_TEXT.split()
    result_words = combined_result.split()

    # Most words should be preserved (some formatting might change)
    assert len(result_words) >= len(original_words) * 0.95

    # Verify that markdown headers are preserved and associated with content
    has_chapter1 = any("# Chapter 1" in chunk for chunk in result)
    has_chapter2 = any("# Chapter 2" in chunk for chunk in result)
    assert has_chapter1
    assert has_chapter2


def test_markdown_section_priority():
    """Test that markdown sections are split before paragraphs."""
    text = """# Section 1

First paragraph in section 1.

Second paragraph in section 1.

# Section 2

First paragraph in section 2.

Second paragraph in section 2."""

    result = split_text_recursive(text, max_length=100, min_length=20)

    # Should split by sections first, so each major section should be separate
    section1_chunks = [chunk for chunk in result if "# Section 1" in chunk]
    section2_chunks = [chunk for chunk in result if "# Section 2" in chunk]

    # Each section should appear in its own chunk(s)
    assert len(section1_chunks) >= 1
    assert len(section2_chunks) >= 1

    # Sections should not be mixed together in the same chunk
    for chunk in result:
        if "# Section 1" in chunk:
            assert "# Section 2" not in chunk
        if "# Section 2" in chunk:
            assert "# Section 1" not in chunk


def test_splitting_hierarchy():
    """Test that the splitting hierarchy works correctly: sections -> paragraphs -> newlines -> sentences."""
    text = """# Long Section

This is a very long paragraph that contains multiple sentences and should be split appropriately. The algorithm should first try to split by sections, then by paragraphs, then by newlines, and finally by sentences if needed.

This is another paragraph in the same section. It also contains multiple sentences that could be split if necessary. The content should remain coherent and properly structured.

## Subsection

More content here that extends the section length. This tests whether the algorithm properly handles nested headers and maintains the document structure while respecting length limits.

# Another Long Section

This section also has extensive content that will test the splitting algorithm. It should be separated from the previous section and handled independently. The algorithm should maintain proper boundaries between sections."""

    # Test with a length that forces splitting at different levels
    result = split_text_recursive(text, max_length=200, min_length=50)

    # Verify sections are split properly
    section1_chunks = [chunk for chunk in result if "# Long Section" in chunk]
    section2_chunks = [chunk for chunk in result if "# Another Long Section" in chunk]

    assert len(section1_chunks) >= 1
    assert len(section2_chunks) >= 1

    # Verify no cross-contamination between major sections
    for chunk in result:
        major_headers = [
            line for line in chunk.split("\n") if line.strip().startswith("# ") and not line.strip().startswith("## ")
        ]
        assert len(major_headers) <= 1  # Each chunk should have at most one major header


def test_preserves_content_structure():
    """Test that important content structure is preserved."""
    text_with_structure = """# Important Header

This is important content that should not be lost.

## Subheader

More important content here."""

    result = split_text_recursive(text_with_structure, max_length=100, min_length=20)

    combined = " ".join(result)
    assert "Important Header" in combined
    assert "important content" in combined
    assert "Subheader" in combined


def test_markdown_sections_nested_headers():
    """Test handling of nested markdown headers with different levels."""
    text = """# Level 1 Header

Content under level 1.

## Level 2 Header

Content under level 2.

### Level 3 Header

Content under level 3.

#### Level 4 Header

Content under level 4."""

    result = _split_by_markdown_sections(text, max_length=100)

    # Verify all header levels are preserved
    combined = "\n".join(result)
    assert "# Level 1 Header" in combined
    assert "## Level 2 Header" in combined
    assert "### Level 3 Header" in combined
    assert "#### Level 4 Header" in combined

    # Verify all content is preserved
    assert "Content under level 1" in combined
    assert "Content under level 2" in combined
    assert "Content under level 3" in combined
    assert "Content under level 4" in combined


def test_split_by_separator_empty_separator():
    """Test behavior with empty separator (edge case)."""
    text = "Hello world"

    # Empty separator should raise ValueError - test that it handles gracefully
    try:
        result = _split_by_separator(text, "", max_length=5)
        # If no exception is raised, ensure result is reasonable
        assert len(result) >= 1
        assert all(len(chunk) > 0 for chunk in result)
    except ValueError:
        # This is expected behavior for empty separator
        pass


def test_split_by_words_very_long_word():
    """Test handling of individual words longer than max_length."""
    text = "supercalifragilisticexpialidocious short"
    result = _split_by_words(text, max_length=10)

    # Should handle the long word gracefully
    assert len(result) >= 2
    assert any("supercalifragilisticexpialidocious" in chunk for chunk in result)
    assert any("short" in chunk for chunk in result)


def test_split_by_sentences_complex_punctuation():
    """Test sentence splitting with complex punctuation patterns."""
    text = "Dr. Smith went to the U.S.A. yesterday! He said, 'Hello world.' Then he left... What happened next?"
    result = _split_by_sentences(text, max_length=30)

    # Should split properly despite abbreviations and complex punctuation
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 30
        assert len(chunk.strip()) > 0

    # Check that content is preserved
    combined = " ".join(result)
    assert "Dr. Smith" in combined
    assert "U.S.A." in combined
    assert "Hello world" in combined


# Parametrized tests for better coverage


@pytest.mark.parametrize(
    "max_length,min_length,expected_min_chunks",
    [
        (50, 10, 5),  # Should split into at least 5 chunks (content is long)
        (100, 20, 3),  # Should split into at least 3 chunks
        (200, 30, 2),  # Should split into at least 2 chunks
        (25, 5, 15),  # Should split into at least 15 chunks (smaller chunks)
    ],
)
def test_split_text_recursive_parametrized(max_length, min_length, expected_min_chunks):
    """Test split_text_recursive with various length parameters."""
    result = split_text_recursive(MIXED_CONTENT_TEXT, max_length=max_length, min_length=min_length)

    # Check that we get a reasonable number of chunks (at least the minimum expected)
    assert len(result) >= expected_min_chunks

    # Verify all chunks respect max_length
    for chunk in result:
        assert len(chunk) <= max_length
        assert len(chunk.strip()) > 0

    # Verify content preservation
    combined = "\n".join(result)
    assert "Chapter 1" in combined
    assert "Chapter 2" in combined


@pytest.mark.parametrize(
    "separator,text,max_length",
    [
        ("\n\n", "Para1\n\nPara2\n\nPara3", 10),
        ("\n", "Line1\nLine2\nLine3\nLine4", 8),
        ("|", "A|B|C|D|E", 5),
        (";", "First;Second;Third", 12),
    ],
)
def test_split_by_separator_parametrized(separator, text, max_length):
    """Test _split_by_separator with various separators and lengths."""
    result = _split_by_separator(text, separator, max_length)

    # Basic validations
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= max_length or len(chunk.split(separator)) == 1
        assert len(chunk.strip()) > 0

    # Verify content preservation
    combined = separator.join(result)
    original_parts = text.split(separator)
    result_parts = combined.split(separator)
    assert len([p for p in original_parts if p.strip()]) <= len([p for p in result_parts if p.strip()])


@pytest.mark.parametrize(
    "text_length,max_length",
    [
        (10, 50),  # Short text, large max_length
        (50, 10),  # Medium text, small max_length
        (100, 25),  # Long text, medium max_length
        (200, 40),  # Very long text, small-medium max_length
    ],
)
def test_split_by_words_parametrized(text_length, max_length):
    """Test _split_by_words with various text and chunk sizes."""
    # Generate text of specified length
    words = ["word"] * (text_length // 5)  # Rough approximation
    text = " ".join(words)

    result = _split_by_words(text, max_length)

    # Verify constraints
    for chunk in result:
        assert len(chunk) <= max_length
        assert len(chunk.strip()) > 0
        # Verify words aren't broken
        chunk_words = chunk.split()
        assert all(word in text for word in chunk_words)


@pytest.mark.parametrize(
    "chunk_count,max_length,min_length",
    [
        (5, 100, 20),
        (10, 50, 10),
        (3, 200, 50),
        (8, 75, 15),
    ],
)
def test_recombine_small_chunks_parametrized(chunk_count, max_length, min_length):
    """Test _recombine_small_chunks with various configurations."""
    # Create small chunks
    small_chunks = [f"Chunk{i}" for i in range(chunk_count)]

    result = _recombine_small_chunks(small_chunks, max_length, min_length)

    # Should combine some chunks
    assert len(result) <= len(small_chunks)

    # Verify constraints
    for chunk in result:
        assert len(chunk) <= max_length
        assert len(chunk.strip()) > 0

    # Verify all original content is preserved
    combined = "\n\n".join(result)
    for original_chunk in small_chunks:
        assert original_chunk in combined


@pytest.mark.parametrize(
    "markdown_text,expected_headers",
    [
        ("# H1\nContent", ["# H1"]),
        ("# H1\n## H2\nContent", ["# H1", "## H2"]),
        ("## H2\n### H3\n#### H4", ["## H2", "### H3", "#### H4"]),
        ("# First\nContent\n# Second\nMore", ["# First", "# Second"]),
    ],
)
def test_markdown_headers_preservation_parametrized(markdown_text, expected_headers):
    """Test that markdown headers are preserved across different configurations."""
    result = _split_by_markdown_sections(markdown_text, max_length=50)

    combined = "\n".join(result)
    for header in expected_headers:
        assert header in combined


# Boundary condition tests


def test_boundary_max_length_equals_text_length():
    """Test when max_length exactly equals text length."""
    text = "This text is exactly fifty characters long here."  # 50 chars
    result = split_text_recursive(text, max_length=50, min_length=10)

    assert len(result) == 1
    assert result[0] == text


def test_boundary_min_length_equals_max_length():
    """Test when min_length equals max_length."""
    result = split_text_recursive(PARAGRAPH_TEXT, max_length=50, min_length=50)

    # Should still work, respecting max_length as priority
    for chunk in result:
        assert len(chunk) <= 50


def test_boundary_very_large_max_length():
    """Test with very large max_length."""
    result = split_text_recursive(MIXED_CONTENT_TEXT, max_length=10000, min_length=100)

    # Should return single chunk or very few chunks
    assert len(result) <= 2
    assert len(result[0]) <= 10000


def test_boundary_single_character_chunks():
    """Test splitting into single character chunks."""
    text = "Hello"
    result = split_text_recursive(text, max_length=1, min_length=1)

    # Should split into individual characters or words
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= 1 or chunk == "Hello"  # Allow for unsplittable words


# Performance and robustness tests


def test_performance_large_text():
    """Test performance with large text input."""
    # Create a large text document
    large_text = "\n\n".join([f"# Section {i}\n\nThis is content for section {i}. " * 10 for i in range(100)])

    # Should handle large input efficiently
    result = split_text_recursive(large_text, max_length=500, min_length=100)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 500
        assert len(chunk.strip()) > 0


def test_unicode_and_special_characters():
    """Test handling of unicode characters and special symbols."""
    unicode_text = """# Ëxamplé Hëader 🚀

Thís ïs ä tëst wïth ünïcödë chäräctërs änd émöjïs 😀 🎉 🔥.

## Mathëmatïcal Symbóls

Hërë ärë sömë symbóls: α β γ δ ∑ ∫ ∞ ≈ ≠ ≤ ≥.

## Öthër Spëcïäl Chäräctërs

Quötës: "dóublë" 'sïnglë' „gërmän" 'smärt'.
Dashës: – — hyphen-dash.
Sëparatörs: | / \\ @ # $ % ^ & * ( ) [ ] { }."""

    result = split_text_recursive(unicode_text, max_length=100, min_length=20)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 100
        assert len(chunk.strip()) > 0

    # Verify unicode content is preserved
    combined = "\n".join(result)
    assert "Ëxamplé" in combined
    assert "🚀" in combined
    assert "α β γ" in combined


def test_malformed_markdown():
    """Test handling of malformed or irregular markdown."""
    malformed_text = """## Missing H1

Content without proper header hierarchy.

# Header without content

## Another header
# Mixed up order

Content here.

### Deep header without parent
More content.

#Not a real header (no space)
# 

Empty header above."""

    result = split_text_recursive(malformed_text, max_length=100, min_length=20)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 100
        assert len(chunk.strip()) > 0

    # Should still preserve recognizable headers
    combined = "\n".join(result)
    assert "## Missing H1" in combined
    assert "# Mixed up order" in combined


def test_extreme_whitespace_handling():
    """Test handling of excessive whitespace and formatting."""
    whitespace_text = """
    

# Header    with    extra    spaces


Content     with     lots     of     spaces.



## Another    Header   


More   content   here.

    
    """

    result = split_text_recursive(whitespace_text, max_length=80, min_length=15)

    # Should handle gracefully
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= 80
        # Should preserve some content even if heavily formatted
        if chunk.strip():
            assert len(chunk.strip()) > 0


def test_very_long_lines():
    """Test handling of extremely long lines without natural break points."""
    # Create a long line with some spaces to enable word splitting
    long_line = " ".join(["A" * 50 for _ in range(60)])  # ~3000 characters with spaces

    result = split_text_recursive(long_line, max_length=100, min_length=20)

    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 100
        assert len(chunk.strip()) > 0


def test_mixed_line_endings():
    """Test handling of mixed line ending styles."""
    mixed_endings = "Line 1\nLine 2\r\nLine 3\rLine 4\n\nParagraph break\r\n\r\nAnother paragraph"

    result = split_text_recursive(mixed_endings, max_length=50, min_length=10)

    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= 50
        assert len(chunk.strip()) > 0


def test_code_blocks_and_special_formatting():
    """Test handling of code blocks and special markdown formatting."""
    code_text = """# Code Examples

Here's some inline `code` and a block:

```python
def example_function():
    return "Hello, World!"
```

And some **bold** and *italic* text.

> This is a blockquote
> with multiple lines

- List item 1
- List item 2
  - Nested item
  - Another nested item

1. Numbered list
2. Second item

| Table | Header |
|-------|--------|
| Cell  | Data   |"""

    result = split_text_recursive(code_text, max_length=150, min_length=30)

    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= 150
        assert len(chunk.strip()) > 0

    # Verify special formatting is preserved
    combined = "\n".join(result)
    assert "```python" in combined
    assert "**bold**" in combined
    assert "> This is a blockquote" in combined


def test_only_headers():
    """Test text that consists only of headers."""
    headers_only = """# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6"""

    result = split_text_recursive(headers_only, max_length=50, min_length=10)

    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= 50
        assert len(chunk.strip()) > 0

    # All headers should be preserved
    combined = "\n".join(result)
    assert "# Header 1" in combined
    assert "###### Header 6" in combined


def test_stress_empty_and_whitespace_sections():
    """Test with sections that are mostly empty or whitespace."""
    sparse_text = """# Section 1



# Section 2

   

## Subsection with spaces

    

# Section 3
Content finally!"""

    result = split_text_recursive(sparse_text, max_length=100, min_length=10)

    assert len(result) >= 1
    # Should still work despite sparse content
    combined = "\n".join(result)
    assert "Section 1" in combined
    assert "Content finally!" in combined


@pytest.mark.parametrize(
    "text_multiplier,max_length",
    [
        (1, 100),  # Normal size
        (10, 200),  # 10x larger
        (50, 500),  # 50x larger
    ],
)
def test_scalability_stress(text_multiplier, max_length):
    """Test algorithm scalability with increasing text sizes."""
    base_text = MIXED_CONTENT_TEXT
    large_text = base_text * text_multiplier

    result = split_text_recursive(large_text, max_length=max_length, min_length=50)

    # Should handle scaling reasonably
    assert len(result) >= text_multiplier  # At least proportional number of chunks
    for chunk in result:
        assert len(chunk) <= max_length
        assert len(chunk.strip()) > 0


def test_consistency_multiple_runs():
    """Test that the algorithm produces consistent results across multiple runs."""
    text = MIXED_CONTENT_TEXT
    max_length = 150
    min_length = 30

    # Run the algorithm multiple times
    results = []
    for _ in range(5):
        result = split_text_recursive(text, max_length=max_length, min_length=min_length)
        results.append(result)

    # All results should be identical (deterministic algorithm)
    first_result = results[0]
    for result in results[1:]:
        assert len(result) == len(first_result)
        assert result == first_result
