#!/usr/bin/env python3
"""
Minimal example for setting up a local vector database with chATLAS_Embed.

This is a simplified version focusing on the core functionality.
For a more comprehensive example, see setup_local_vectordb_example.py

Prerequisites:
- PostgreSQL running with pgvector extension
- Database 'my_vector_db' created with vector extension enabled
- uv for dependency management

Running this script:
    # From the main project directory
    uv run python quick_start_vectordb.py

    # Or if in chATLAS_Embed directory
    uv run python ../quick_start_vectordb.py
"""

from chATLAS_Embed import Document, PostgresParentChildVectorStore
from chATLAS_Embed.Document import DocumentSource
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

# Update with your database credentials
CONNECTION_STRING = "postgresql://postgres:password@localhost:5432/my_vector_db"


def test_main():
    print("🚀 Quick Vector Database Setup")

    # 1. Initialize embedding model
    embedding_model = SentenceTransformerEmbedding("sentence-transformers/all-MiniLM-L6-v2")

    # 2. Connect to vector store
    vector_store = PostgresParentChildVectorStore(connection_string=CONNECTION_STRING, embedding_model=embedding_model)

    # 3. Create sample documents
    parent_docs = [
        Document(
            id="atlas_doc",
            page_content="The ATLAS experiment at CERN studies particle collisions.",
            source=DocumentSource.TWIKI,
            name="ATLAS Overview",
            url="https://twiki.cern.ch/twiki/bin/view/Atlas/Overview",
            metadata={"something": "physics"},
        )
    ]

    child_docs = [
        Document(
            id="atlas_child_1",
            page_content="ATLAS experiment at CERN",
            source=DocumentSource.TWIKI,
            name="ATLAS Overview",
            url="https://twiki.cern.ch/twiki/bin/view/Atlas/Overview",
            metadata={"something": "physics"},
            parent_id="atlas_doc",
        ),
        Document(
            id="atlas_child_2",
            page_content="studies particle collisions",
            source=DocumentSource.TWIKI,
            name="ATLAS Overview",
            url="https://twiki.cern.ch/twiki/bin/view/Atlas/Overview",
            metadata={"something": "physics"},
            parent_id="atlas_doc",
        ),
    ]

    # 4. Add documents to vector store
    print("📝 Adding documents...")
    vector_store.add_documents(parent_docs, child_docs)

    # 5. Search the database
    print("🔍 Searching...")
    results = vector_store.search("What is ATLAS?", k=2)

    for i, (_child, parent, score) in enumerate(results, 1):
        print(f"{i}. {parent.name}: {score:.3f}")
        print(f"   {parent.page_content}")

    # 6. Cleanup
    vector_store.close()
    print("✅ Done!")
