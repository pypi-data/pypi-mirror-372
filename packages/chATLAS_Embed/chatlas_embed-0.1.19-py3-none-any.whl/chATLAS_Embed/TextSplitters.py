#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.

"""A collection of different Text Splitters to use."""

from abc import ABC, abstractmethod

import spacy
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from chATLAS_Embed.Document import Document, DocumentSource


class TextSplitter(ABC):
    """Abstract base class for text splitting strategies."""

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    @abstractmethod
    def split(self, document: Document) -> list[Document]:
        """Split document into chunks and return Document objects.

        Args:
            document: Document to split into chunks

        Returns:
            List of Document objects containing the split text chunks
        """
        pass

    def count_tokens(self, text: str) -> int:
        return len(self.nlp(text))


class ParagraphTextSplitter(TextSplitter):
    """Splits text based on paragraphs using spaCy."""

    def __init__(self, max_tokens: int = 512):
        super().__init__()
        self.max_tokens = max_tokens

    def split(self, document: Document) -> list[Document]:
        """Split document into paragraph-based chunks."""

        doc = self.nlp(document.page_content)
        paragraphs = []
        current_para = []
        current_tokens = 0

        for sent in doc.sents:
            sent_tokens = len(sent)
            if current_tokens + sent_tokens > self.max_tokens:
                if current_para:
                    paragraphs.append(" ".join(current_para))
                current_para = [sent.text]
                current_tokens = sent_tokens
            else:
                current_para.append(sent.text)
                current_tokens += sent_tokens

        if current_para:
            paragraphs.append(" ".join(current_para))

        # Convert text chunks to Document objects
        documents = []
        for i, paragraph in enumerate(paragraphs):
            metadata = {"chunk_index": i, **document.metadata}
            documents.append(Document.from_parent(parent_doc=document, page_content=paragraph, metadata=metadata))

        return documents


class RecursiveTextSplitter(TextSplitter):
    """A standard langchain Recursive Text Splitter."""

    def __init__(self, chunk_size=2048, chunk_overlap=24):
        super().__init__()
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def split(self, document: Document) -> list[Document]:
        """Split document using recursive character splitting."""

        text_chunks = self.splitter.split_text(document.page_content)

        # Convert text chunks to Document objects
        documents = []
        for i, chunk in enumerate(text_chunks):
            metadata = {"chunk_index": i, **document.metadata}
            documents.append(Document.from_parent(parent_doc=document, page_content=chunk, metadata=metadata))

        return documents


class MarkdownTextSplitter(TextSplitter):
    """Splits text based on markdown headings using langchain's experimental markdown splitter."""

    def __init__(self):
        super().__init__()
        DEFAULT_HEADER_KEYS = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ]
        self.splitter = MarkdownHeaderTextSplitter(headers_to_split_on=DEFAULT_HEADER_KEYS)

    def split(self, document: Document) -> list[Document]:
        """Split document based on markdown structure."""

        docs = self.splitter.split_text(document.page_content)

        # Convert to our Document format
        documents = []
        for i, doc in enumerate(docs):
            metadata = {"chunk_index": i, **doc.metadata, **document.metadata}

            documents.append(
                Document.from_parent(parent_doc=document, page_content=doc.page_content, metadata=metadata)
            )

        return documents
