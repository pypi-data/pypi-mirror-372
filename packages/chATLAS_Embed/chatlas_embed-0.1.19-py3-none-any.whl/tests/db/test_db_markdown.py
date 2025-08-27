import json
from pathlib import Path

from chATLAS_Embed import (
    Document,
    DocumentChunker,
    MarkdownTextSplitter,
    PostgresParentChildVectorStore,
    RecursiveTextSplitter,
    VectorStoreCreator,
)
from chATLAS_Embed.DocumentLoaders import GitlabMarkdownDocumentLoader
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

PACKAGE_DIR = Path(__file__).parent.parent.parent
CONNECTION_STRING = "postgresql://postgres:password@localhost:5432/my_vector_db"
OUT_DIR = Path(PACKAGE_DIR / "tests" / "outputs")


def test_GitlabMarkdownVectorStoreCreator_components():
    parent_splitter = MarkdownTextSplitter()
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = GitlabMarkdownDocumentLoader()

    # test that we can load in some example documents
    input_path = Path(PACKAGE_DIR / "tests/process_md/test_contents.json")
    docs = document_loader.load_documents(input_path)

    # test preprocessing
    docs = [document_loader.process_document(doc) for doc in docs]

    # test chunking
    parent_docs, child_docs = document_chunker.chunk_documents(docs)
    assert parent_docs
    assert child_docs

    # save chunked documents manually
    parent_docs_path = OUT_DIR / "parent_docs.json"
    child_docs_path = OUT_DIR / "child_docs.json"
    with open(parent_docs_path, "w") as f:
        json.dump([doc.to_dict() for doc in parent_docs], f, indent=2)
    with open(child_docs_path, "w") as f:
        json.dump([doc.to_dict() for doc in child_docs], f, indent=2)


def test_GitlabMarkdownVectorStoreCreator_combined():
    embedding_model = SentenceTransformerEmbedding("sentence-transformers/all-MiniLM-L6-v2")
    vector_store = PostgresParentChildVectorStore(connection_string=CONNECTION_STRING, embedding_model=embedding_model)
    parent_splitter = MarkdownTextSplitter()
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = GitlabMarkdownDocumentLoader()
    creator = VectorStoreCreator(
        vector_store=vector_store,
        document_loader=document_loader,
        document_chunker=document_chunker,
        output_dir=OUT_DIR,
    )

    input_path = Path(PACKAGE_DIR / "tests/process_md/test_contents.json")
    creator.create_update_vectorstore(input_path, verbose=True)

    # Verify that the vector store has been populated
    assert vector_store is not None
    assert vector_store.embedding_model is not None
    assert vector_store.document_count > 0

    # Search for a document
    query = "trigger cuts"
    results = vector_store.search(query, k=1)
    assert results
    assert isinstance(results, list)
    assert len(results) == 1
    child, parent, score = results[0]
    assert isinstance(child, Document)
    assert isinstance(parent, Document)
    assert isinstance(score, float)
