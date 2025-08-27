#!/usr/bin/env python3
"""
Example script showing how to set up a local vector database using chATLAS_Embed.

This script demonstrates:
1. Setting up a PostgreSQL vector database
2. Creating an embedding model
3. Embedding text documents
4. Storing embeddings in the vector database
5. Searching the vector database

Prerequisites:
- PostgreSQL server running locally
- pgvector extension installed
- uv for dependency management

Database setup (run these commands in psql):
    CREATE DATABASE my_vector_db;
    \c my_vector_db
    CREATE EXTENSION vector;

    -- Optional: Create a user (replace with your preferred credentials)
    CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
    GRANT ALL PRIVILEGES ON DATABASE my_vector_db TO myuser;

Running this script:
    # From the main project directory
    uv run python setup_local_vectordb_example.py

    # Or if in chATLAS_Embed directory
    uv run python ../setup_local_vectordb_example.py
"""

from chATLAS_Embed import Document, PostgresParentChildVectorStore, RecursiveTextSplitter
from chATLAS_Embed.Document import DocumentSource
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

# ============================================================================
# Configuration - Update these for your setup
# ============================================================================

# Database connection - update with your PostgreSQL credentials
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",  # or "myuser" if you created a custom user
    "password": "password",  # update with your password
    "database": "my_vector_db",
}

CONNECTION_STRING = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# ============================================================================
# Example Documents to Embed
# ============================================================================

SAMPLE_DOCUMENTS = [
    {
        "id": "doc_1",
        "content": """
        The ATLAS Experiment is one of the largest particle physics experiments at CERN.
        It is designed to study particle collisions at the Large Hadron Collider.
        The detector is 46 meters long and weighs about 7,000 tonnes.
        ATLAS is one of two general-purpose detectors at the Large Hadron Collider (LHC).
        """,
        "name": "ATLAS Experiment Overview",
        "url": "https://atlas.cern",
        "metadata": {
            "category": ["CERN", "ATLAS", "particle physics"],
            "last_modification": "15-08-2024",
        },
    },
    {
        "id": "doc_2",
        "content": """
        The Higgs boson was discovered by the ATLAS and CMS experiments in 2012.
        This discovery confirmed the existence of the Higgs field, which gives particles their mass.
        Peter Higgs and François Englert won the Nobel Prize in Physics for this theoretical prediction.
        The Higgs boson is an elementary particle in the Standard Model of particle physics.
        """,
        "name": "Higgs Boson Discovery",
        "url": "https://atlas.cern",
        "metadata": {
            "category": ["CERN", "Higgs", "Nobel Prize"],
            "last_modification": "10-07-2024",
        },
    },
    {
        "id": "doc_3",
        "content": """
        Machine learning and artificial intelligence are increasingly important in particle physics.
        Deep learning algorithms help analyze the massive amounts of data produced by detectors.
        Neural networks can identify particle signatures and improve trigger systems.
        AI assists in data reconstruction and event classification.
        """,
        "name": "AI in Particle Physics",
        "url": "https://atlas.cern",
        "metadata": {
            "category": ["AI", "machine learning", "data analysis"],
            "last_modification": "01-08-2024",
        },
    },
]


def test_main():
    print("🚀 Setting up Local Vector Database Example")
    print("=" * 50)

    # ============================================================================
    # Step 1: Initialize the Embedding Model
    # ============================================================================
    print("\n📚 Step 1: Initializing embedding model...")

    # Using a lightweight sentence transformer model
    embedding_model = SentenceTransformerEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print(f"✅ Embedding model loaded: {embedding_model}")
    print(f"   Vector dimension: {embedding_model.vector_size}")

    # ============================================================================
    # Step 2: Initialize the Vector Store
    # ============================================================================
    print("\n  Step 2: Connecting to PostgreSQL vector store...")

    try:
        vector_store = PostgresParentChildVectorStore(
            connection_string=CONNECTION_STRING,
            embedding_model=embedding_model,
            dictionary_type="english",  # Options: "english", "simple", "scientific"
        )
        print("✅ Connected to vector store successfully!")

        # Test the connection
        if vector_store.test_connection():
            print("✅ Database connection test passed")
        else:
            print("❌ Database connection test failed")
            return

    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'my_vector_db' exists")
        print("3. pgvector extension is installed")
        print("4. Connection credentials are correct")
        return

    # ============================================================================
    # Step 3: Set up Text Splitters
    # ============================================================================
    print("\n✂️  Step 3: Setting up text splitters...")

    # Child documents: smaller chunks for precise retrieval
    child_splitter = RecursiveTextSplitter(
        chunk_size=200,  # Smaller chunks for embeddings
        chunk_overlap=20,
    )

    print("✅ Text splitters configured")

    # ============================================================================
    # Step 4: Create Documents and Add to Vector Store
    # ============================================================================
    print("\n📝 Step 4: Processing and adding documents...")

    parent_docs = []
    child_docs = []

    for doc_data in SAMPLE_DOCUMENTS:
        # Create parent document
        parent_doc = Document(
            id=doc_data["id"],
            page_content=doc_data["content"].strip(),
            source=DocumentSource.TWIKI,
            name=doc_data["name"],
            url=doc_data["url"],
            metadata=doc_data["metadata"],
        )
        parent_docs.append(parent_doc)

        # Split into child documents
        child_chunk_docs = child_splitter.split(parent_doc)

        for i, child_chunk_doc in enumerate(child_chunk_docs):
            child_doc = Document(
                id=f"{doc_data['id']}_child_{i}",
                page_content=child_chunk_doc.page_content,
                source=DocumentSource.TWIKI,
                name=doc_data["name"],
                url=doc_data["url"],
                metadata={**child_chunk_doc.metadata, **doc_data["metadata"]},
                parent_id=doc_data["id"],
            )
            child_docs.append(child_doc)

    print(f"📄 Created {len(parent_docs)} parent documents")
    print(f"📄 Created {len(child_docs)} child documents")

    # Add documents to vector store
    print("\n⚡ Adding documents to vector store...")
    vector_store.add_documents(parent_docs, child_docs)
    print("✅ Documents added successfully!")

    # ============================================================================
    # Step 5: Get Database Statistics
    # ============================================================================
    print("\n📊 Step 5: Database statistics...")

    stats = vector_store.get_db_stats()
    print(f"📈 Total documents: {stats['total_documents']}")
    print(f"📈 Total embeddings: {stats['total_embeddings']}")
    print(f"📈 Vector dimension: {stats['vector_dimension']}")
    print(f"📈 Unique document names: {stats['unique_document_names']}")
    print(f"📈 Database size: {stats['total_disk_size_mb']:.2f} MB")
    print(f"📈 Index size: {stats['index_disk_size_mb']:.2f} MB")

    # ============================================================================
    # Step 6: Search the Vector Database
    # ============================================================================
    print("\n🔍 Step 6: Testing vector search...")

    test_queries = [
        "What is the ATLAS experiment?",
        "Tell me about the Higgs boson discovery",
        "How is AI used in particle physics?",
        "Large Hadron Collider detector",
    ]

    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")

        # Perform hybrid search (vector + text)
        results = vector_store.search(
            query=query,
            k=2,  # Top 2 vector search results
            k_text=1,  # Top 1 text search result
        )

        print(f"📋 Found {len(results)} results:")

        for i, (_child_doc, parent_doc, similarity) in enumerate(results, 1):
            print(f"   {i}. Document: {parent_doc.metadata.get('name', 'Unknown')}")
            print(f"      Similarity: {similarity:.3f}")
            print(f"      Type: {parent_doc.metadata.get('search_type', 'vector')}")
            print(f"      Content preview: {parent_doc.page_content[:100]}...")
            print()

    # ============================================================================
    # Step 7: Advanced Search with Filters
    # ============================================================================
    print("\n🎯 Step 7: Testing filtered search...")

    # Search with metadata filters
    filtered_results = vector_store.search(
        query="particle physics",
        k=3,
        metadata_filters={"type": "physics", "category": ["CERN", "ATLAS"]},
        date_filter="01-01-2024",  # Only documents after this date
    )

    print(f"🎯 Filtered search found {len(filtered_results)} results")
    for i, (_child_doc, parent_doc, similarity) in enumerate(filtered_results, 1):
        print(f"   {i}. {parent_doc.metadata.get('name')}: {similarity:.3f}")

    # ============================================================================
    # Step 8: Show Available Categories
    # ============================================================================
    print("\n📂 Step 8: Available categories in database...")

    categories = vector_store.get_categories()
    print(f"📂 Document types: {categories['doc_types']}")
    print(f"📂 Categories: {categories['categories']}")
    print(f"📂 Dates: {categories['dates']}")

    # ============================================================================
    # Cleanup
    # ============================================================================
    print("\n🧹 Cleaning up...")
    vector_store.close()
    print("✅ Vector store connection closed")

    print("\n🎉 Example completed successfully!")
    print("\nNext steps:")
    print("- Modify the SAMPLE_DOCUMENTS to use your own data")
    print("- Experiment with different embedding models")
    print("- Try different search parameters")
    print("- Add more documents to your vector store")
