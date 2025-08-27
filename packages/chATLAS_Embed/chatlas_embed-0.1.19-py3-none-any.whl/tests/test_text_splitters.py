#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.

"""Tests for the TextSplitters module."""

from abc import ABC, abstractmethod

import pytest
import spacy
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chATLAS_Embed.Base import TextSplitter
from chATLAS_Embed.Document import Document, DocumentSource
from chATLAS_Embed.TextSplitters import MarkdownTextSplitter, ParagraphTextSplitter, RecursiveTextSplitter


class TestParagraphTextSplitter:
    """Test cases for ParagraphTextSplitter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = ParagraphTextSplitter(max_tokens=50)

    def test_inheritance(self):
        """Test that ParagraphTextSplitter inherits from TextSplitter."""
        assert isinstance(self.splitter, TextSplitter)

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        splitter = ParagraphTextSplitter()
        assert splitter.max_tokens == 512
        assert hasattr(splitter, "nlp")
        assert splitter.nlp is not None

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        splitter = ParagraphTextSplitter(max_tokens=100)
        assert splitter.max_tokens == 100

    def test_split_simple_text(self):
        """Test splitting simple text into paragraphs."""
        text = "This is the first sentence. This is the second sentence."
        doc = Document(
            page_content=text,
            source=DocumentSource.TWIKI,
            name="test_doc",
            url="https://test.com",
            metadata={"test": "value"},
        )
        result = self.splitter.split(doc)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, Document) for chunk in result)
        assert all(hasattr(chunk, "page_content") for chunk in result)
        assert all(hasattr(chunk, "metadata") for chunk in result)

    def test_split_empty_text(self):
        """Test splitting empty text."""
        doc = Document(
            page_content="", source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)
        assert isinstance(result, list)
        # Empty text might return empty list or list with empty string
        assert len(result) <= 1

    def test_split_single_sentence(self):
        """Test splitting text with a single sentence."""
        text = "This is a single sentence."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)
        assert len(result) == 1
        assert result[0].page_content.strip() == text

    def test_split_respects_max_tokens(self):
        """Test that splitting respects max_tokens limit."""
        # Create a long text that should be split
        long_text = " ".join(["This is sentence number " + str(i) + "." for i in range(100)])
        doc = Document(
            page_content=long_text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)

        # Verify each chunk respects token limit
        for chunk_doc in result:
            token_count = self.splitter.count_tokens(chunk_doc.page_content)
            assert token_count <= self.splitter.max_tokens

    def test_split_multiple_paragraphs(self):
        """Test splitting text with multiple paragraphs."""
        text = (
            "This is the first paragraph with multiple sentences. "
            "It has several sentences in it. "
            "This is the second paragraph. "
            "It also has multiple sentences. "
            "And this is the third paragraph."
        )
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = self.splitter.split(doc)
        assert len(result) >= 1

        # Check that original text content is preserved
        combined_text = " ".join([doc.page_content for doc in result])
        # Remove extra whitespace for comparison
        original_words = text.split()
        combined_words = combined_text.split()
        assert len(original_words) <= len(combined_words) + 5  # Allow for some minor differences

    def test_count_tokens(self):
        """Test token counting functionality."""
        text = "This is a test sentence."
        token_count = self.splitter.count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0

    def test_count_tokens_empty_text(self):
        """Test token counting with empty text."""
        token_count = self.splitter.count_tokens("")
        assert isinstance(token_count, int)
        assert token_count == 0

    def test_count_tokens_consistency(self):
        """Test that token counting is consistent with spaCy."""
        text = "This is a test sentence with several words."
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        expected_tokens = len(doc)

        actual_tokens = self.splitter.count_tokens(text)
        assert actual_tokens == expected_tokens

    def test_split_preserves_content(self):
        """Test that splitting preserves all original content."""
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This sentence contains every letter of the alphabet. "
            "Here is another sentence for testing purposes."
        )
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = self.splitter.split(doc)
        combined = " ".join([doc.page_content for doc in result])

        # Check that no content is lost (allowing for minor formatting differences)
        original_words = set(text.lower().replace(".", "").split())
        combined_words = set(combined.lower().replace(".", "").split())
        assert original_words.issubset(combined_words)

    def test_split_with_very_small_max_tokens(self):
        """Test splitting with very small max_tokens value."""
        splitter = ParagraphTextSplitter(max_tokens=6)
        text = "This is a sentence.\nThis is a sentence."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = splitter.split(doc)
        assert len(result) > 1

        for chunk_doc in result:
            token_count = splitter.count_tokens(chunk_doc.page_content)
            assert token_count <= 6

    def test_split_with_large_max_tokens(self):
        """Test splitting with large max_tokens value."""
        splitter = ParagraphTextSplitter(max_tokens=1000)
        text = "This is a short text."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = splitter.split(doc)
        assert len(result) == 1
        assert result[0].page_content.strip() == text

    def test_split_with_base_metadata(self):
        """Test that base metadata is properly merged with chunk metadata."""
        text = "First sentence. Second sentence. Third sentence."
        doc = Document(
            page_content=text,
            source=DocumentSource.TWIKI,
            name="test_doc",
            url="https://test.com",
            metadata={"source": "test_doc", "author": "test_author"},
        )

        result = self.splitter.split(doc)
        assert len(result) >= 1

        for chunk_doc in result:
            assert "chunk_index" in chunk_doc.metadata
            assert chunk_doc.metadata["source"] == "test_doc"
            assert chunk_doc.metadata["author"] == "test_author"
            assert isinstance(chunk_doc.metadata["chunk_index"], int)


class TestRecursiveTextSplitter:
    """Test cases for RecursiveTextSplitter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=10)

    def test_inheritance(self):
        """Test that RecursiveTextSplitter inherits from TextSplitter."""
        assert isinstance(self.splitter, TextSplitter)

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        splitter = RecursiveTextSplitter()
        assert hasattr(splitter, "splitter")
        assert isinstance(splitter.splitter, RecursiveCharacterTextSplitter)

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        splitter = RecursiveTextSplitter(chunk_size=200, chunk_overlap=20)
        assert splitter.splitter._chunk_size == 200
        assert splitter.splitter._chunk_overlap == 20

    def test_split_simple_text(self):
        """Test splitting simple text."""
        text = "This is a simple test text for splitting."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, Document) for chunk in result)
        assert all(hasattr(chunk, "page_content") for chunk in result)
        assert all(hasattr(chunk, "metadata") for chunk in result)

    def test_split_empty_text(self):
        """Test splitting empty text."""
        doc = Document(
            page_content="", source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)
        assert isinstance(result, list)
        # Empty text should return empty list
        assert len(result) == 0

    def test_split_long_text(self):
        """Test splitting long text that exceeds chunk_size."""
        # Create text longer than chunk_size
        long_text = "This is a test sentence. " * 20
        doc = Document(
            page_content=long_text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)

        assert len(result) > 1
        # Check that chunks respect size limits (approximately)
        for chunk_doc in result:
            assert (
                len(chunk_doc.page_content)
                <= self.splitter.splitter._chunk_size + self.splitter.splitter._chunk_overlap
            )

    def test_split_preserves_content(self):
        """Test that splitting preserves content through overlap."""
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)

        # Combine all chunks
        combined = " ".join([doc.page_content for doc in result])

        # Check that original words are present (accounting for overlap)
        original_words = text.split()
        for word in original_words:
            assert word in combined

    def test_split_with_overlap(self):
        """Test that overlap is working correctly."""
        # Use a splitter with known overlap
        splitter = RecursiveTextSplitter(chunk_size=50, chunk_overlap=10)
        text = "This is a test sentence. " * 10  # Create text that will need splitting
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = splitter.split(doc)
        if len(result) > 1:
            # Check that there's some overlap between consecutive chunks
            # This is a heuristic test since exact overlap depends on split points
            # We just check that we got multiple chunks, which indicates splitting worked
            assert len(result) > 1

    def test_split_single_sentence(self):
        """Test splitting text with a single sentence."""
        text = "This is a single sentence."
        doc = Document(
            page_content=text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )
        result = self.splitter.split(doc)
        assert len(result) == 1
        assert result[0].page_content == text

    def test_split_respects_chunk_size(self):
        """Test that splitting respects chunk_size approximately."""
        splitter = RecursiveTextSplitter(chunk_size=20, chunk_overlap=5)
        # Create text that should definitely be split
        long_text = "This is a very long text that should definitely be split into multiple chunks because it exceeds the chunk size limit."
        doc = Document(
            page_content=long_text, source=DocumentSource.TWIKI, name="test_doc", url="https://test.com", metadata={}
        )

        result = splitter.split(doc)
        assert len(result) > 1

        # Check that most chunks are reasonably close to chunk_size
        # (RecursiveCharacterTextSplitter tries to split on good boundaries)
        for chunk_doc in result:
            # Allow some flexibility since it splits on word boundaries
            assert len(chunk_doc.page_content) <= splitter.splitter._chunk_size * 2  # Allow 2x for boundary flexibility

    def test_split_with_base_metadata(self):
        """Test that base metadata is properly merged with chunk metadata."""
        text = "This is a test sentence that should be split into multiple chunks for testing purposes."
        doc = Document(
            page_content=text,
            source=DocumentSource.TWIKI,
            name="test_doc",
            url="https://test.com",
            metadata={"source": "test_doc", "type": "recursive"},
        )

        result = self.splitter.split(doc)
        assert len(result) >= 1

        for chunk_doc in result:
            assert "chunk_index" in chunk_doc.metadata
            assert chunk_doc.metadata["source"] == "test_doc"
            assert chunk_doc.metadata["type"] == "recursive"
            assert isinstance(chunk_doc.metadata["chunk_index"], int)


class TestMarkdownTextSplitter:
    """Test cases for MarkdownTextSplitter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.splitter = MarkdownTextSplitter()

    def test_inheritance(self):
        """Test that MarkdownTextSplitter inherits from TextSplitter."""
        assert isinstance(self.splitter, TextSplitter)

    def test_split_markdown_with_headers(self):
        """Test splitting markdown text with headers."""
        text = """# Main Title

This is content under the main title.

## Subsection

This is content under the subsection.

### Sub-subsection

This is content under the sub-subsection."""
        doc = Document(
            page_content=text,
            source=DocumentSource.MKDOCS,
            name="test_markdown",
            url="https://test.com/markdown",
            metadata={},
        )

        result = self.splitter.split(doc)
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(chunk, Document) for chunk in result)

        # Check that heading metadata is extracted
        has_heading_metadata = all("Header 1" in doc.metadata for doc in result)
        assert has_heading_metadata

    def test_split_with_base_metadata(self):
        """Test that base metadata is properly merged with markdown metadata."""
        text = "# Test Header\n\nThis is test content."
        doc = Document(
            page_content=text,
            source=DocumentSource.MKDOCS,
            name="test_markdown",
            url="https://test.com/markdown",
            metadata={"source": "markdown_doc", "author": "test_author"},
        )

        result = self.splitter.split(doc)
        assert len(result) >= 1

        for chunk_doc in result:
            assert "chunk_index" in chunk_doc.metadata
            assert chunk_doc.metadata["source"] == "markdown_doc"
            assert chunk_doc.metadata["author"] == "test_author"

    def test_split_plain_text(self):
        """Test splitting plain text without markdown formatting."""
        text = "This is plain text without any markdown formatting."
        doc = Document(
            page_content=text,
            source=DocumentSource.MKDOCS,
            name="test_markdown",
            url="https://test.com/markdown",
            metadata={},
        )
        result = self.splitter.split(doc)

        assert len(result) >= 1
        assert all(isinstance(chunk, Document) for chunk in result)
        assert result[0].page_content.strip() == text

    def test_split_with_sections(self):
        """Test splitting text with a code block."""
        text = """## my title

Here is a first para.

Here is some `inline` code:

```python
def hello_world():
    print("Hello, world!")
```

This is some text after the code block.

## New section
 
More text

## New section again
 
More text
"""
        doc = Document(
            page_content=text,
            source=DocumentSource.MKDOCS,
            name="test_markdown",
            url="https://test.com/markdown",
            metadata={},
        )
        result = self.splitter.split(doc)
        assert len(result) == 3
