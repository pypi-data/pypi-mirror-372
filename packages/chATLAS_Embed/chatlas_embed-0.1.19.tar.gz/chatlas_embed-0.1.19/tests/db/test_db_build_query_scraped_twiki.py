"""
A version to be compatible with the old scraped Twiki format

**NOTE** These tests need a running PG server to connect to locally (if running tests on lxplus can just connect to CERN dbod)
Update the TEST_DB_CONFIG to be correct for your server

Pytest tests that:
- Creates a test_db environment for testing the postgresql
- Creates fake twiki documents to write to the db with
- Populates the vectorstore with these documents
- Tests basic search on this built db
- Tests filtered search on this build db
- Tests updating documents in the db
- Tests langchian integration for searching
- Tests similarity to ensure different documents being returned
- Test for deleting documents
- Test for initliasing database on embedding model of different size
- Test with outside vectorstore
- Test deleting vectorstore then reconnecting to it
- Test for searching the same database from multiple different vectorstore objects at the same time
- Test for searching the same database from the same vectorstore object across multiple threads at the same time
"""

import os
import random
import tempfile
import threading
import time
import tracemalloc
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait,
)
from datetime import datetime
from pathlib import Path

import numpy as np
import psycopg2
import pytest
import sqlalchemy
from sqlalchemy.exc import OperationalError

from chATLAS_Embed import (
    DocumentChunker,
    LangChainVectorStore,
    PostgresParentChildVectorStore,
    RecursiveTextSplitter,
    TWikiTextDocumentLoader,
    VectorStoreCreator,
)
from chATLAS_Embed.Base import EmbeddingModel
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

# Database configuration for testing
TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "chatlas_test_db",
}

OUT_DIR = Path(__file__).parent.parent / "output"


@pytest.fixture(scope="session")
def test_db():
    """Create a test database and clean it up after tests"""
    # Connect to default postgres database to create test database
    conn = psycopg2.connect(
        host=TEST_DB_CONFIG["host"],
        port=TEST_DB_CONFIG["port"],
        user=TEST_DB_CONFIG["user"],
        password=TEST_DB_CONFIG["password"],
        database="postgres",
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # fix psycopg2.errors.ObjectInUse: database "chatlas_test_db" is being accessed by other users
    cursor.execute(
        f"""
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = '{TEST_DB_CONFIG["database"]}' AND pid <> pg_backend_pid();
    """
    )

    # Drop test database if it exists and create new one
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
    cursor.execute(f"CREATE DATABASE {TEST_DB_CONFIG['database']}")

    cursor.close()
    conn.close()

    # Return connection string for the test database
    connection_string = f"postgresql://{TEST_DB_CONFIG['user']}:{TEST_DB_CONFIG['password']}@{TEST_DB_CONFIG['host']}:{TEST_DB_CONFIG['port']}/{TEST_DB_CONFIG['database']}"

    yield connection_string

    # Cleanup: Drop test database after all tests
    conn = psycopg2.connect(
        host=TEST_DB_CONFIG["host"],
        port=TEST_DB_CONFIG["port"],
        user=TEST_DB_CONFIG["user"],
        password=TEST_DB_CONFIG["password"],
        database="postgres",
    )

    conn.autocommit = True
    cursor = conn.cursor()
    # Terminate all connections to the test database before dropping
    cursor.execute(
        f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '{TEST_DB_CONFIG["database"]}' AND pid <> pg_backend_pid();
        """
    )
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
    cursor.close()
    conn.close()


@pytest.fixture(scope="session")
def embedding_model():
    """Initialize the real embedding model"""
    return SentenceTransformerEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")


@pytest.fixture(scope="session")
def test_docs():
    """Create temporary test documents"""
    temp_dir = tempfile.mkdtemp()
    docs = []

    # Create sample TWiki documents
    test_contents = [
        {
            "filename": "ATLAS_Experiment.txt",
            "content": """-----URL-----
https://twiki.cern.ch/twiki/bin/view/Atlas/ATLAS_Experiment
-----LAST MODIFICATION----
2015-09
-----PARENT STRUCTURE----
TWiki https://twiki.cern.ch/twiki/bin/view/Main/WebHome
Atlas Web https://twiki.cern.ch/twiki/bin/view/Atlas/WebHome
AtlasUpgrade https://twiki.cern.ch/twiki/bin/view/Atlas/AtlasUpgrade
UpgradeProjectOffice https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOffice
UpgradeProjectOfficeCAD https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOfficeCAD
3DDataExchangeProcess https://twiki.cern.ch/twiki/bin/view/Atlas/3DDataExchangeProcess
-----HEADERS-----
h1: 3D Data exchange between ATLAS TC and collaboration institutes

-----TEXT-----
The ATLAS Experiment is one of the largest particle physics experiments at CERN.
It is designed to study particle collisions at the Large Hadron Collider.
The detector is 46 meters long and weighs about 7,000 tonnes.
ATLAS is one of two general-purpose detectors at the Large Hadron Collider (LHC). It investigates a wide range of physics, from the Higgs boson to extra dimensions and particles that could make up dark matter. Although it has the same scientific goals as the CMS experiment, it uses different technical solutions and a different magnet-system design.

Beams of particles from the LHC collide at the centre of the ATLAS detector making collision debris in the form of new particles, which fly out from the collision point in all directions. Six different detecting subsystems arranged in layers around the collision point record the paths, momentum, and energy of the particles, allowing them to be individually identified. A huge magnet system bends the paths of charged particles so that their momenta can be measured.

The interactions in the ATLAS detectors create an enormous flow of data. To digest the data, ATLAS uses an advanced “trigger” system to tell the detector which events to record and which to ignore. Complex data-acquisition and computing systems are then used to analyse the collision events recorded. At 46 m long, 25 m high and 25 m wide, the 7000-tonne ATLAS detector is the largest volume particle detector ever constructed. It sits in a cavern 100 m below ground near the main CERN site, close to the village of Meyrin in Switzerland.

More than 5500 scientists from 245 institutes in 42 countries work on the ATLAS experiment (March 2022). For the latest information, see here.""",
        },
        {
            "filename": "Higgs_Boson.txt",
            "content": """-----URL-----
https://twiki.cern.ch/twiki/bin/view/Atlas/Higgs_Boson
-----LAST MODIFICATION----
2021-09
-----PARENT STRUCTURE----
TWiki https://twiki.cern.ch/twiki/bin/view/Main/WebHome
Atlas Web https://twiki.cern.ch/twiki/bin/view/Atlas/WebHome
AtlasUpgrade https://twiki.cern.ch/twiki/bin/view/Atlas/AtlasUpgrade
UpgradeProjectOffice https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOffice
UpgradeProjectOfficeCAD https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOfficeCAD
3DDataExchangeProcess https://twiki.cern.ch/twiki/bin/view/Atlas/3DDataExchangeProcess
-----HEADERS-----
h1: 3D Data exchange between ATLAS TC and collaboration institutes

-----TEXT-----
The Higgs boson was discovered by the ATLAS and CMS experiments in 2012.
This discovery confirmed the existence of the Higgs field, which gives particles their mass.
Peter Higgs and François Englert won the Nobel Prize in Physics for this theoretical prediction.
The Higgs boson, sometimes called the Higgs particle, is an elementary particle in the Standard Model of particle physics produced by the quantum excitation of the Higgs field, one of the fields in particle physics theory. In the Standard Model, the Higgs particle is a massive scalar boson with zero spin, even (positive) parity, no electric charge, and no colour charge that couples to (interacts with) mass. It is also very unstable, decaying into other particles almost immediately upon generation.
The Higgs field is a scalar field with two neutral and two electrically charged components that form a complex doublet of the weak isospin SU(2) symmetry. Its "Sombrero potential" leads it to take a nonzero value everywhere (including otherwise empty space), which breaks the weak isospin symmetry of the electroweak interaction and, via the Higgs mechanism, gives a rest mass to all massive elementary particles of the Standard Model, including the Higgs boson itself. The existence of the Higgs field became the last unverified part of the Standard Model of particle physics, and for several decades was considered "the central problem in particle physics"
            """,
        },
        {
            "filename": "LHC.txt",
            "content": """-----URL-----
https://twiki.cern.ch/twiki/bin/view/Atlas/LHC
-----LAST MODIFICATION----
2016-09
-----PARENT STRUCTURE----
TWiki https://twiki.cern.ch/twiki/bin/view/Main/WebHome
Atlas Web https://twiki.cern.ch/twiki/bin/view/Atlas/WebHome
AtlasUpgrade https://twiki.cern.ch/twiki/bin/view/Atlas/AtlasUpgrade
UpgradeProjectOffice https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOffice
UpgradeProjectOfficeCAD https://twiki.cern.ch/twiki/bin/view/Atlas/UpgradeProjectOfficeCAD
-----HEADERS-----
h1: 3D Data exchange between ATLAS TC and collaboration institutes

-----TEXT-----
The Large Hadron Collider (LHC) is the world's largest particle accelerator.
It consists of a 27-kilometer ring of superconducting magnets.
The LHC can collide protons at energies up to 13 TeV.
Inside the accelerator, two high-energy particle beams travel at close to the speed of light before they are made to collide. The beams travel in opposite directions in separate beam pipes – two tubes kept at ultrahigh vacuum. They are guided around the accelerator ring by a strong magnetic field maintained by superconducting electromagnets. The electromagnets are built from coils of special electric cable that operates in a superconducting state, efficiently conducting electricity without resistance or loss of energy. This requires chilling the magnets to ‑271.3°C – a temperature colder than outer space. For this reason, much of the accelerator is connected to a distribution system of liquid helium, which cools the magnets, as well as to other supply services.""",
        },
    ]

    for doc in test_contents:
        doc_path = Path(temp_dir) / doc["filename"]
        with open(doc_path, "w", encoding="UTF-8") as f:
            f.write(doc["content"])
        docs.append(doc_path)

    yield Path(temp_dir)

    # Cleanup temporary files
    for doc in docs:
        os.remove(doc)
    os.rmdir(temp_dir)


@pytest.fixture(scope="session")
def vector_store(test_db, embedding_model):
    """Initialize the vector store with test database"""
    return PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model)


@pytest.fixture(scope="session")
def populated_vector_store(vector_store, test_docs):
    """Populate the vector store with test documents"""
    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)
    doc_loader = TWikiTextDocumentLoader()
    twiki_creator = VectorStoreCreator(
        document_loader=doc_loader,
        vector_store=vector_store,
        document_chunker=document_chunker,
        output_dir=OUT_DIR,
    )

    twiki_creator.create_update_vectorstore(input_path=test_docs, update=True, verbose=True)

    yield vector_store

    del vector_store


def test_basic_search(populated_vector_store):
    """Test basic search functionality"""
    results = populated_vector_store.search("What is the ATLAS experiment?", k=2)

    assert len(results) > 0
    assert any("ATLAS" in result[0].page_content for result in results)  # Check a result containing ATLAS in results
    assert all(isinstance(result[2], float) for result in results)  # Check all results returned with a
    # similarity


def test_filtered_search(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(query="Higgs boson discovery", k=5, date_filter="01-04-2020")

    assert len(results) > 0  # Only 1 document has new enough date, however unsure num parents this gets split into
    for res in results:  # Check documents new enough
        file_date = datetime.strptime(res[0].metadata["last_modification"], "%d-%m-%Y")
        check_date = datetime.strptime("2020-04", "%Y-%m")
        assert file_date > check_date


def test_langchain_integration(populated_vector_store):
    """Test LangChain integration"""
    langchain_store = LangChainVectorStore(vector_store=populated_vector_store)
    docs = langchain_store.invoke("Tell me about the LHC", config={"metadata": {"k": 2}})

    assert len(docs) > 0
    assert any("superconducting magnets" in doc.page_content for doc in docs)


def test_document_update_no_update(vector_store, test_docs):
    """Test updating existing documents - no documents to update so should do nothing"""

    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    doc_loader = TWikiTextDocumentLoader()
    twiki_creator = VectorStoreCreator(
        document_loader=doc_loader,
        vector_store=vector_store,
        document_chunker=document_chunker,
        output_dir=OUT_DIR,
    )

    # Update existing documents
    twiki_creator.create_update_vectorstore(input_path=test_docs, update=True, verbose=True)

    # Verify documents were updated
    results = vector_store.search("ATLAS experiment", k=1)
    assert len(results) > 0


def test_document_update(vector_store, test_docs):
    """Test updating existing documents"""
    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    doc_loader = TWikiTextDocumentLoader()
    twiki_creator = VectorStoreCreator(
        document_loader=doc_loader,
        vector_store=vector_store,
        document_chunker=document_chunker,
        output_dir=OUT_DIR,
    )

    # Read and update the document with a newer date
    doc_path = test_docs / "Higgs_Boson.txt"
    with open(doc_path) as f:
        f.read()

    # Update the modification date to current date
    current_date = datetime.now().strftime("%Y-%m")
    updated_content = f"""-----URL-----
    https://twiki.cern.ch/twiki/bin/view/Atlas/Higgs_Boson
    -----LAST MODIFICATION----
    {current_date}
    -----PARENT STRUCTURE----
    TWiki TEST
    Atlas Web TEST
    AtlasUpgrade TEST
    UpgradeProjectOffice TEST
    UpgradeProjectOfficeCAD TEST
    3DDataExchangeProcess TEST
    -----HEADERS-----
    h1: 3D Data exchange between ATLAS TC and collaboration institutes

    -----TEXT-----
    HIGGS BOSON IS A PARTICLE
    other filler content to make sure it picks this up
                    """

    # Write the updated content back to the file
    with open(doc_path, "w") as f:
        f.write(updated_content)

    assert len(doc_loader.load_documents(test_docs)) > 0

    # Update documents in vector store
    twiki_creator.create_update_vectorstore(input_path=test_docs, update=True, verbose=True)

    # Verify documents were updated with new date
    results = vector_store.search(
        "Higgs boson discovery",
        k=1,
        metadata_filters={"last_modification": str(datetime.strptime(current_date, "%Y-%m").strftime("%d-%m-%Y"))},
    )
    assert len(results) > 0
    assert "HIGGS BOSON IS A PARTICLE" in results[0][0].page_content
    assert results[0][0].metadata["last_modification"] == datetime.strptime(current_date, "%Y-%m").strftime("%d-%m-%Y")


def test_search_relevance(populated_vector_store):
    """Test search result relevance"""
    # Search for ATLAS-related content
    atlas_results = populated_vector_store.search("ATLAS detector specifications", k=3)

    # Search for LHC-related content
    lhc_results = populated_vector_store.search("LHC collider specifications", k=3)

    # Verify results are different and relevant
    assert atlas_results != lhc_results
    assert any("46 m" in result[1].page_content.lower() for result in atlas_results)
    assert any("27-kilometer" in result[1].page_content.lower() for result in lhc_results)


def test_wrong_embedding_size(test_db):
    class wrongEmbedder(EmbeddingModel):
        def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
            """
            :param model_name: (str) - HuggingFace sentence transformer embedding model to use
            """
            self.model = None
            self.vector_size: int = 3

        def embed(
            self, texts: list[str] | str, show_progress_bar: bool | None = None, batch_size=1
        ) -> list[list[float]]:
            return [[0.1, 0.1, 0.1]]

    with pytest.raises(ValueError):
        PostgresParentChildVectorStore(connection_string=test_db, embedding_model=wrongEmbedder())


def test_with_around_vectorstore(embedding_model, test_db):
    with PostgresParentChildVectorStore(embedding_model=embedding_model, connection_string=test_db) as vs:
        results = vs.search("What is the higgs boson at ATLAS?", k=3)
        assert len(results) > 0


def test_multiple_vectorstore_search(embedding_model, test_db):
    """
    Test searching the same database using multiple vector store objects
    simultaneously
    """
    # Create additional vector store objects using the same connection string
    additional_stores = [
        PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model) for _ in range(3)
    ]

    # Define search queries
    search_queries = ["ATLAS experiment", "Higgs boson", "Large Hadron Collider"]

    # Perform searches across different vector store objects
    results = []
    for store, query in zip(additional_stores, search_queries, strict=False):
        results.append(store.search(query, k=2))

    # Assertions
    assert len(results) == 3
    for result_set in results:
        assert len(result_set) > 0
        assert all(isinstance(result[2], float) for result in result_set)

    del additional_stores


def test_concurrent_search_same_vectorstore(populated_vector_store):
    """
    Test searching the same vector store from multiple threads simultaneously
    """
    # Define search queries
    search_queries = [
        "ATLAS experiment",
        "Higgs boson",
        "Large Hadron Collider",
        "particle physics",
    ]

    # Function to perform search
    def perform_search(query):
        try:
            results = populated_vector_store.search(query, k=2)
            return query, results
        except Exception as e:
            return query, str(e)

    # Use ThreadPoolExecutor to simulate concurrent searches
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit search tasks
        future_to_query = {executor.submit(perform_search, query): query for query in search_queries}

        # Collect results
        concurrent_results = []
        for future in as_completed(future_to_query):
            query, results = future.result()
            concurrent_results.append((query, results))

    # Assertions
    assert len(concurrent_results) == len(search_queries)
    for _, result_set in concurrent_results:
        assert len(result_set) > 0
        assert all(isinstance(result[2], float) for result in result_set)


def synchronized_thread_test(vector_store, queries):
    """
    Synchronized thread test for database operations
    """
    # Synchronization barriers
    start_barrier = threading.Barrier(len(queries))
    results_lock = threading.Lock()
    concurrent_results = []

    def synchronized_operation(query):
        # Wait for all threads to be ready
        start_barrier.wait()

        # Record start time
        start_time = time.time()

        try:
            # Perform search
            search_results = vector_store.search(query, k=2)

            # Thread-safe result collection
            with results_lock:
                concurrent_results.append((query, search_results, time.time() - start_time))

            return search_results
        except Exception as e:
            with results_lock:
                concurrent_results.append((query, str(e), time.time() - start_time))
            raise

    # Use ThreadPoolExecutor with explicit synchronization
    with ThreadPoolExecutor(max_workers=len(queries)) as executor:
        # Submit all tasks
        futures = [executor.submit(synchronized_operation, query) for query in queries]

        # Wait for all to complete
        wait(futures)

    return concurrent_results


def test_thread_safety_with_multiple_operations(populated_vector_store):
    """
    Comprehensive thread safety test with synchronized execution
    """
    # Mix of search queries
    queries = [
        "ATLAS experiment",
        "Higgs boson",
        "Large Hadron Collider",
        "particle physics",
    ]

    # Thread-based concurrent test
    thread_results = synchronized_thread_test(populated_vector_store, queries)

    # Assertions for thread test
    assert len(thread_results) == len(queries)

    for query, result, exec_time in thread_results:
        assert result is not None, f"Failed to retrieve results for query: {query}"

        if isinstance(result, list):
            assert len(result) > 0, f"Empty result for query: {query}"
            assert all(isinstance(result[2], float) for result in result), (
                f"Invalid similarity scores for query: {query}"
            )

        print(f"Query: {query}, Execution Time: {exec_time}")


def test_error_handling_invalid_connection(embedding_model):
    """Test error handling for invalid database connection"""
    with pytest.raises(OperationalError):
        PostgresParentChildVectorStore(
            connection_string="postgresql://invalid:invalid@localhost:5432/nonexistent",
            embedding_model=embedding_model,
        )


def test_empty_search_query(populated_vector_store):
    """Test handling of empty search queries"""
    results = populated_vector_store.search("", k=2)
    assert len(results) == 0 or isinstance(results, list)


def test_very_large_k_value(populated_vector_store):
    """Test search with a very large k value"""
    results = populated_vector_store.search("test query", k=1000)
    assert len(results) > 0  # Should return available results even if less than k
    assert all(isinstance(result[2], float) for result in results)


def test_special_characters_search(populated_vector_store):
    """Test search with special characters"""
    special_queries = [
        "test!@#$%^&*()",
        "SQL; DROP TABLE;",
        "\\n\\t\\r",
        "'quoted string'",
        "unicode_☢️_test",
    ]
    for query in special_queries:
        results = populated_vector_store.search(query, k=2)
        assert isinstance(results, list)


def test_concurrent_write_operations(vector_store, test_docs):
    """Test concurrent write operations to the vectorstore"""

    def update_operation(doc_number):
        parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
        child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
        document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

        doc_loader = TWikiTextDocumentLoader()
        twiki_creator = VectorStoreCreator(
            document_loader=doc_loader,
            vector_store=vector_store,
            document_chunker=document_chunker,
            output_dir=OUT_DIR,
        )

        twiki_creator.create_update_vectorstore(input_path=test_docs, update=True, verbose=True)
        return doc_number

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(update_operation, i) for i in range(3)]
        results = [future.result() for future in futures]

    assert len(results) == 3


def test_memory_usage(populated_vector_store):
    """Test memory usage during large search operations"""

    tracemalloc.start()

    # Perform multiple searches
    for _ in range(100):
        populated_vector_store.search("test query", k=10)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Assert reasonable memory usage (adjust threshold as needed)
    assert peak < 100 * 1024 * 1024  # 100MB threshold


def test_large_document_handling(populated_vector_store):
    """Test handling of very large documents"""
    large_content = "test content " * 10000  # Create a large document

    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    # Create a temporary large document
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt") as tmp:
        tmp.write(
            f"""-----URL-----
https://test.com/large_doc
-----LAST MODIFICATION----
2024-02
-----PARENT STRUCTURE----
Test Parent
-----HEADERS-----
h1: Large Document Test
-----TEXT-----
{large_content}
"""
        )
        tmp.flush()

        doc_loader = TWikiTextDocumentLoader()
        twiki_creator = VectorStoreCreator(
            document_loader=doc_loader,
            vector_store=populated_vector_store,
            document_chunker=document_chunker,
            output_dir=OUT_DIR,
        )

        # Should handle large document without errors
        twiki_creator.create_update_vectorstore(input_path=Path(tmp.name), update=True, verbose=True)

    results = populated_vector_store.search("test content", k=2)
    assert len(results) > 0


def test_metadata_persistence(populated_vector_store):
    """Test persistence of metadata across operations"""
    # Search and get initial metadata
    initial_results = populated_vector_store.search("ATLAS", k=1)
    initial_metadata = initial_results[0][1].metadata

    # Perform some operations
    populated_vector_store.search("Higgs", k=1)
    populated_vector_store.search("LHC", k=1)

    # Search again and compare metadata
    final_results = populated_vector_store.search("ATLAS", k=1)
    final_metadata = final_results[0][1].metadata

    assert initial_metadata == final_metadata


def test_search_with_filters_combination(populated_vector_store):
    """Test search with multiple metadata filters"""
    results = populated_vector_store.search(
        "test query",
        k=2,
        metadata_filters={"last_modification": "01-09-2021", "name": "Higgs_Boson"},
    )

    assert all(
        result[0].metadata["last_modification"] == "01-09-2021" and result[0].metadata["name"] == "Higgs_Boson"
        for result in results
    )


def test_performance_degradation(populated_vector_store):
    """Test for performance degradation over multiple searches"""
    query = "ATLAS experiment"
    times = []

    for _ in range(10):
        start_time = time.time()
        populated_vector_store.search(query, k=2)
        end_time = time.time()
        times.append(end_time - start_time)

        # Add some random delay between searches
        time.sleep(random.uniform(0.1, 0.5))

    # Calculate statistics
    mean_time = np.mean(times)
    std_dev = np.std(times)

    # Assert performance consistency
    assert std_dev / mean_time < 0.5  # Max 50% variation coefficient


def test_delete_dcouments(populated_vector_store):
    """
    Test for deleting documents from the vectorstore
    """
    populated_vector_store.delete(document_name="ATLAS_Experiment")

    results = populated_vector_store.search("ATLAS detector specifications", k=3)

    assert all("ATLAS_Experiment" not in result[0].name for result in results)


def test_vectorstore_recreation(test_db, embedding_model):
    """Test deleting and recreating the vectorstore with the same connection.

    This test ensures that the vectorstore can be deleted and recreated using the same
    database connection string and embedding model. It verifies that the new vectorstore
    can perform searches and that the engine instance is different from the initial one.

    Args:
        test_db (str): The connection string for the test database.
        embedding_model (EmbeddingModel): The embedding model to use for the vectorstore.
    """
    # First, create initial vectorstore
    initial_vectorstore = PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model)

    # Get the engine from the initial vectorstore
    initial_engine = initial_vectorstore.engine

    # Delete the initial vectorstore
    del initial_vectorstore

    # Recreate vectorstore
    new_vectorstore = PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model)

    # Verify the new vectorstore can be used
    try:
        # Perform a dummy search to check connection
        results = new_vectorstore.search("what is higgs boson?", k=1)
        assert len(results) > 0  # Should still return new documents
    except Exception as e:
        pytest.fail(f"Failed to search newly created vectorstore: {e}")

    assert new_vectorstore.engine is not initial_engine
