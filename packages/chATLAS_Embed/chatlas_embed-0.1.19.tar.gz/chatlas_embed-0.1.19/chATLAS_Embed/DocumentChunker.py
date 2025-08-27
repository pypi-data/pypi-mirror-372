from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from chATLAS_Embed.Document import Document, DocumentSource
from chATLAS_Embed.DocumentLoaders import DocumentLoader
from chATLAS_Embed.TextSplitters import TextSplitter


class DocumentChunker:
    """Class for chunking documents using parent-child text splitting strategy."""

    def __init__(self, parent_splitter: TextSplitter, child_splitter: TextSplitter):
        """
        :param parent_splitter: Text splitter for creating parent chunks
        :param child_splitter: Text splitter for creating child chunks
        """
        self.parent_splitter = parent_splitter
        self.child_splitter = child_splitter

    def chunk_documents(self, documents: list[Document]) -> tuple[list[Document], list[Document]]:
        """
        Split documents into parent and child chunks using the configured text splitters.

        :param documents: List of processed documents to chunk
        :return: Tuple of (parent_docs, child_docs) where child_docs are embedded and parent_docs provide context
        """
        parent_docs = []
        child_docs = []

        # Prepare arguments for multiprocessing with starmap
        worker_args = [(doc, self.parent_splitter, self.child_splitter) for doc in documents]

        # Process documents in parallel using multiprocessing for CPU-bound chunking tasks
        with Pool() as pool:
            results = pool.starmap(_chunk_single_document_worker, worker_args)

        # Aggregate results
        for parent_docs_local, child_docs_local in results:
            if parent_docs_local and child_docs_local:
                parent_docs.extend(parent_docs_local)
                child_docs.extend(child_docs_local)

        return parent_docs, child_docs


def _chunk_single_document_worker(
    doc: Document, parent_splitter: TextSplitter, child_splitter: TextSplitter
) -> tuple[list[Document], list[Document]]:
    """
    Worker function for multiprocessing that chunks a single document.
    Needs to be module level for pickling.

    :param doc: Document to chunk
    :param parent_splitter: Text splitter for creating parent chunks
    :param child_splitter: Text splitter for creating child chunks
    :return: Tuple of (parent_docs_local, child_docs_local) for this document
    """
    # Use text splitters to create parent and child chunks
    parent_chunk_docs = parent_splitter.split(doc)
    parent_docs_local = []
    child_docs_local = []

    for i, parent_chunk_doc in enumerate(parent_chunk_docs):
        parent_id = f"{doc.id}_parent_{i}"
        parent_doc = Document(
            page_content=parent_chunk_doc.page_content,
            source=doc.source,
            name=doc.name,
            url=doc.url,
            metadata={**parent_chunk_doc.metadata, "parent_index": i},
            id=parent_id,
        )
        parent_docs_local.append(parent_doc)

        # Split parent chunk into child chunks
        child_chunk_docs = child_splitter.split(parent_doc)
        for j, child_chunk_doc in enumerate(child_chunk_docs):
            child_id = f"{parent_id}_child_{j}"
            child_doc = Document(
                page_content=child_chunk_doc.page_content,
                source=doc.source,
                name=doc.name,
                url=doc.url,
                metadata={
                    **child_chunk_doc.metadata,
                    "chunk_index": j,
                    "parent_content_length": len(parent_chunk_doc.page_content),
                    "child_content_length": len(child_chunk_doc.page_content),
                },
                id=child_id,
                parent_id=parent_id,
            )
            child_docs_local.append(child_doc)

    return parent_docs_local, child_docs_local
