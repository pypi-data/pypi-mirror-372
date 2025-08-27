#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/Base.py`
"""Script Containing Base Classes for all Embed Implementations."""

from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from chATLAS_Embed.Document import Document
from chATLAS_Embed.DocumentChunker import DocumentChunker
from chATLAS_Embed.DocumentLoaders import DocumentLoader
from chATLAS_Embed.TextSplitters import TextSplitter


class EmbeddingModel(ABC):
    """Abstract base class for embedding models."""

    vector_size: int  # Vector size output of embedding model

    @abstractmethod
    def embed(
        self,
        texts: list[str] | str,
        show_progress_bar: bool | None = None,
    ) -> list[list[float]]:
        """Generate embeddings for a list of texts or single query.

        Currently just passed document page_content in initial creation,
        but could also be passed metadata
        """
        pass


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    # Defined Attributes
    engine: Engine
    embedding_model: EmbeddingModel

    @abstractmethod
    def add_documents(self, parent_docs: list[Document], child_docs: list[Document]) -> None:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        k: int = 4,
        metadata_filters: dict | None = None,
        date_filter: str | None = None,
    ) -> list[Document]:
        """Search for similar documents."""
        pass

    @abstractmethod
    def delete(self, document_ids: list[str] | None = None, document_name: str | None = None) -> None:
        """Delete documents from the store."""
        pass


class VectorStoreCreator:
    """Class for creating and managing vector stores using a modular document loader.

    Currently uses a Parent-Child document retriever setup in a similar way to:
    https://python.langchain.com/docs/how_to/parent_document_retriever/
    """

    def __init__(
        self,
        vector_store: VectorStore,
        document_loader: DocumentLoader,
        document_chunker: DocumentChunker,
        output_dir: Path,
    ):
        """
        :param VectorStore vector_store: Instantiated VectorStore to add documents to
        :param DocumentLoader document_loader: Document loader to use for loading and processing documents
        :param DocumentChunker document_chunker: Document chunker to use for splitting documents into parent and child chunks
        :param Path output_dir: Directory for creation of csv file tracking modifications and storage
        """
        self.vector_store = vector_store
        self.document_loader = document_loader
        self.document_chunker = document_chunker
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = True

    ############################################################
    # NOTE FROM BEN E:
    # This function could easily be sped up using batch queries for the SQL
    # as well as using an optimal number of threads for the cpu, batch processing
    # several documents at a time in each thread, not using lists and other things.
    # Current runtime for this section is ~15min for ~22k documents which could definitely
    # do with improvement (LLM could probaly easily produce a good solution), but for now
    # not dealt with this
    ############################################################

    def create_update_vectorstore(self, input_path: Path, update: bool = False, verbose: bool = True) -> None:
        """
        Create vector store from documents in input path, with optional
        update handling for updating the vectorstore from files in directory
        where last update date is newer than what is currently stored in the
        vectorstore.

        :param: Path input_path: Path to directory containing documents to add (in any file type)
        :param: bool update: Whether to update contents of the db if newer versions of the files are contained in input_path
        :param: bool verbose: Print logging of documents added or documents updated
        """

        self.verbose = verbose

        raw_documents = self.document_loader.load_documents(input_path)
        self.document_loader.validate_documents(raw_documents)

        processed_docs = []
        for doc in raw_documents:
            processed_docs.append(self.document_loader.process_document(doc))

        # Determine which documents need to be processed (new or updated)
        documents_to_process = []
        new_documents = []
        updated_documents = []

        # Collect document metadata for batch query
        document_metadata = [(doc.name, doc.url) for doc in processed_docs]
        names, urls = zip(*document_metadata, strict=False) if document_metadata else ([], [])

        # Batch query to check existing documents
        with self.vector_store.engine.begin() as conn:
            try:
                if names and urls:
                    existing_docs = conn.execute(
                        text(
                            """
                            SELECT id, metadata FROM documents
                            WHERE metadata->>'name' IN :names OR metadata->>'url' IN :urls
                        """
                        ),
                        {"names": names, "urls": urls},
                    ).fetchall()

                    # Map existing documents by name and URL
                    existing_docs_map = {doc.metadata.get("name"): doc for doc in existing_docs}
                else:
                    existing_docs_map = {}

                # Determine which documents to process
                for doc in processed_docs:
                    name = doc.name
                    url = doc.url
                    last_modified = doc.metadata.get("last_modification")

                    existing_doc = existing_docs_map.get(name) or existing_docs_map.get(url)
                    if existing_doc:
                        existing_metadata = existing_doc.metadata
                        existing_last_modified = existing_metadata.get("last_modification")

                        if (
                            update
                            and last_modified
                            and (
                                not existing_last_modified
                                or datetime.strptime(last_modified, "%d-%m-%Y")
                                > datetime.strptime(existing_last_modified, "%d-%m-%Y")
                            )
                        ):
                            # Update: Remove old chunks
                            delete_documents_stmt = text(
                                """
                                DELETE FROM documents
                                WHERE metadata->>'name' = :name OR metadata->>'url' = :url
                                """
                            )
                            documents_result = conn.execute(delete_documents_stmt, {"name": name, "url": url})
                            if verbose:
                                print(f"Documents deleted: {documents_result.rowcount}")
                            updated_documents.append(doc)
                            documents_to_process.append(doc)
                        # else: Skip if no update is required
                    else:
                        # New document
                        new_documents.append(doc)
                        documents_to_process.append(doc)

            except Exception as e:
                print(f"Error processing documents: {e}")
                raise

        # Chunk the documents that need to be processed
        if documents_to_process:
            parent_docs, child_docs = self.document_chunker.chunk_documents(documents_to_process)
        else:
            parent_docs, child_docs = [], []

        # Add documents to the vector store
        if parent_docs and child_docs:
            self.vector_store.add_documents(parent_docs, child_docs)

        # Log results
        if verbose:
            print(f"New documents added: {len(new_documents)}")
            print(f"Documents updated: {len(updated_documents)}")

        # Save files added to the csv
        self.save_to_output_dir(new_documents, updated_documents)

    def save_to_output_dir(self, new_documents: list[Document], updated_documents: list[Document]):
        """
        Save the current files in the system to a structured csv file for easy lookup and checking of date.
        :param new_documents: New documents that have been added to the database this run
        :type new_documents: List[Document]
        :param updated_documents: Documents that have an update since last time stored in the db
        :type updated_documents: List[Document]
        """
        csv_path = self.output_dir / "current_documents.csv"
        current_date = datetime.now().strftime("%d-%m-%Y")

        try:
            loaded_csv = pd.read_csv(csv_path)
        except FileNotFoundError as e:
            loaded_csv = pd.DataFrame(
                columns=[
                    "document_name",
                    "url",
                    "last_modified_date",
                    "added_to_db_date",
                    "included",
                    "reason_for_exclusion",
                ]
            )
            print(f"No csv to load, creating a new one: {e}")
        except pd.errors.EmptyDataError:
            print("CSV empty - creating new one")
            loaded_csv = pd.DataFrame(
                columns=[
                    "document_name",
                    "url",
                    "last_modified_date",
                    "added_to_db_date",
                    "included",
                    "reason_for_exclusion",
                ]
            )

        # Process new documents
        for doc in new_documents:
            new_row = {
                "document_name": doc.name,
                "url": doc.url,
                "last_modified_date": doc.metadata["last_modification"],
                "added_to_db_date": current_date,
                "included": True,
                "reason_for_exclusion": "",
            }
            loaded_csv = pd.concat([loaded_csv, pd.DataFrame([new_row])], ignore_index=True)

        # Process updated documents
        for doc in updated_documents:
            # Update existing entries or add new ones
            mask = loaded_csv["document_name"] == doc.name
            if mask.any():
                loaded_csv.loc[mask, "last_modified_date"] = doc.metadata.get("last_modification", "")
                loaded_csv.loc[mask, "added_to_db_date"] = current_date
            else:
                new_row = {
                    "document_name": doc.name,
                    "url": doc.url,
                    "last_modified_date": doc.metadata.get("last_modification", ""),
                    "added_to_db_date": current_date,
                    "included": True,
                    "reason_for_exclusion": "",
                }
                loaded_csv = pd.concat([loaded_csv, pd.DataFrame([new_row])], ignore_index=True)

        # Process skipped documents
        if hasattr(self.document_loader, "skipped_docs"):
            for doc in self.document_loader.skipped_docs:
                new_row = {
                    "document_name": doc["name"],
                    "url": "",
                    "last_modified_date": "",
                    "added_to_db_date": current_date,
                    "included": False,
                    "reason_for_exclusion": doc["reason"],
                }
                loaded_csv = pd.concat([loaded_csv, pd.DataFrame([new_row])], ignore_index=True)

        # Remove duplicates keeping the latest entry
        loaded_csv = loaded_csv.sort_values("added_to_db_date").drop_duplicates(subset=["document_name"], keep="last")

        # Save to CSV
        loaded_csv.to_csv(csv_path, index=False, encoding="utf-8", errors="replace")
