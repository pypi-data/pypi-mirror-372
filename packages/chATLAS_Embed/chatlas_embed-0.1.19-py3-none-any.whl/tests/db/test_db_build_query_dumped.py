"""
A version to be compatible with the new dumped twiki format.

**NOTE** These tests need a running PG server to connect to locally
(if running tests on lxplus can just connect to CERN dbod)
Update the TEST_DB_CONFIG to be correct for your server

Pytest tests that:
- Creates a test_db environment for testing the postgresql
- Creates fake twiki documents to write to the db with
- Populates the vectorstore with these documents
- Tests basic search on this built db
- Tests filtered search on this build db
- Tests updating documents in the db
- Tests langchain integration for searching
- Tests similarity to ensure different documents being returned
- Test for deleting documents
- Test for initialing database on embedding model of different size
- Test with outside vectorstore
- Test deleting vectorstore then reconnecting to it
- Test for searching the same database from multiple different vectorstore objects at the same time
- Test for searching the same database from the same vectorstore object across multiple threads at the same time
"""

import os
import tempfile
import tracemalloc
from concurrent.futures import (
    ThreadPoolExecutor,
)
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2
import pytest

from chATLAS_Embed import (
    Document,
    DocumentChunker,
    LangChainVectorStore,
    PostgresParentChildVectorStore,
    RecursiveTextSplitter,
    VectorStoreCreator,
)
from chATLAS_Embed.Document import DocumentSource
from chATLAS_Embed.DocumentLoaders import syncedTwikiDocumentLoader
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

OUT_DIR = Path(__file__).parent.parent / "output"

# Database configuration for testing
TEST_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "chatlas_test_db",
}


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
            "filename": "ADCPlotOperations.txt",
            "content": """%META:TOPICINFO{author="BaseUserMapping_333" date="1416477899" format="1.1" version="1.369"}%
%META:TOPICPARENT{name="ADCOperationsDailyReports"}%
%STARTINCLUDE%
The ATLAS Experiment is one of the largest particle physics experiments at CERN.
It is designed to study particle collisions at the Large Hadron Collider.
The detector is 46 meters long and weighs about 7,000 tonnes.
ATLAS is one of two general-purpose detectors at the Large Hadron Collider (LHC). It investigates a wide range of physics,
from the Higgs boson to extra dimensions and particles that could make up dark matter.
Although it has the same scientific goals as the CMS experiment, it uses different technical solutions and a different magnet-system design.
Beams of particles from the LHC collide at the centre of the ATLAS detector making collision debris in the form of new particles,
which fly out from the collision point in all directions. Six different detecting subsystems arranged in layers around the collision point record the paths,
momentum, and energy of the particles, allowing them to be individually identified. A huge magnet system bends the paths of charged particles so that their momenta can be measured.

The interactions in the ATLAS detectors create an enormous flow of data. To digest the data, ATLAS uses an advanced
“trigger” system to tell the detector which events to record and which to ignore. Complex data-acquisition and
computing systems are then used to analyse the collision events recorded. At 46 m long, 25 m high and 25 m wide,
the 7000-tonne ATLAS detector is the largest volume particle detector ever constructed. It sits in a cavern 100 m
below ground near the main CERN site, close to the village of Meyrin in Switzerland.

below ground near the main CERN site, close to the village of Meyrin in Switzerland.
below ground near the main CERN site, close to the village of Meyrin in Switzerland.
below ground near the main CERN site, close to the village of Meyrin in Switzerland.
below ground near the main CERN site, close to the village of Meyrin in Switzerland.
below ground near the main CERN site, close to the village of Meyrin in Switzerland.

More than 5500 scientists from 245 institutes in 42 countries work on the ATLAS experiment (March 2022).
For the latest information, see here.
%STOPINCLUDE%
Extra other info which should not be included.
""",
        },
        {
            "filename": "Higgs_Boson.txt",
            "content": """%META:TOPICINFO{author="wikipedia" date="1736878918" format="1.1" version="1.3"}%
%META:TOPICPARENT{name="HiggsToTauTauToHH2012Winter"}%

%STARTINCLUDE%
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
The Higgs boson, sometimes called the Higgs particle, is an elementary particle in the Standard Model of particle
physics produced by the quantum excitation of the Higgs field, one of the fields in particle physics theory.
In the Standard Model, the Higgs particle is a massive scalar boson with zero spin, even (positive) parity,
no electric charge, and no colour charge that couples to (interacts with) mass. It is also very unstable,
decaying into other particles almost immediately upon generation.
The Higgs field is a scalar field with two neutral and two electrically charged components that form a complex doublet
of the weak isospin SU(2) symmetry. Its "Sombrero potential" leads it to take a nonzero value everywhere
(including otherwise empty space), which breaks the weak isospin symmetry of the electroweak interaction and,
via the Higgs mechanism, gives a rest mass to all massive elementary particles of the Standard Model,
including the Higgs boson itself. The existence of the Higgs field became the last unverified part of the Standard
Model of particle physics, and for several decades was considered "the central problem in particle physics"
The Higgs boson, sometimes called the Higgs particle, is an elementary particle in the Standard Model of
particle physics produced by the quantum excitation of the Higgs field, one of the fields in particle physics theory.
As a layman I would now say… I think we have it.

“It” was the Higgs boson, the almost-mythical entity that had put particle physics in the global spotlight,
and the man proclaiming to be a mere layman was none other than CERN’s Director-General, Rolf Heuer.
Heuer spoke in the Laboratory’s main auditorium on 4 July 2012, moments after the CMS and ATLAS collaborations
at the Large Hadron Collider announced the discovery of a new elementary particle, which we now know is a Higgs boson.
Applause reverberated in Geneva from as far away as Melbourne, Australia, where delegates of the International
Conference on High Energy Physics were connected via video-conference.higgsjuly4,seminar,Milestones,
Higgs Boson Discovery,360
4 July 2012: A packed auditorium at CERN listens keenly to the announcement from CMS and ATLAS (Image: Maximilien Brice/CERN)
So what exactly is so special about this particle?“Easy! It is the first and only elementary scalar
particle we have observed,” grins Rebeca Gonzalez Suarez, who, as a doctoral student, was involved in
the CMS search for the Higgs boson. Easy for a physicist,
%STOPINCLUDE%
Extra text that should be ignored
            """,
        },
        {
            "filename": "LHC.txt",
            "content": """%META:TOPICINFO{author="google" date="1328618061" format="1.1" version="1.3"}%
%META:TOPICPARENT{name="LHC"}%

%STARTINCLUDE%
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
Inside the accelerator, two high-energy particle beams travel at close to the speed of light before they
are made to collide. The beams travel in opposite directions in separate beam pipes – two tubes kept at
ultrahigh vacuum. They are guided around the accelerator ring by a strong magnetic field maintained by
superconducting electromagnets. The electromagnets are built from coils of special electric cable that
operates in a superconducting state, efficiently conducting electricity without resistance or loss of energy.
This requires chilling the magnets to ‑271.3°C – a temperature colder than outer space. For this reason,
much of the accelerator is connected to a distribution system of liquid helium, which cools the magnets,
as well as to other supply services.

LHC stands for Large Hadron Collider, the world's largest and most powerful particle accelerator. It's located in a tunnel at CERN, the European Organization for Nuclear Research, on the Swiss-French border.
How it works
The LHC is a 27-kilometer ring of superconducting magnets that accelerate particles.
Beams of particles collide at four locations around the ring.
The collisions produce tiny fireballs that are hotter than the core of the sun.
What it's used for
The LHC has helped scientists discover the Higgs boson, a particle that gives mass to other particles.
The LHC may also help scientists understand why there is an imbalance of matter and antimatter in the universe.
Safety
The LHC Safety Assessment Group (LSAG) has concluded that the LHC collisions are not dangerous.
The LSAG's conclusions have been endorsed by CERN's Scientific Policy Committee.
History
The LHC was built between 1998 and 2008 with the help of over 10,000 scientists from hundreds of universities and laboratories.
It first started up on September 10, 2008.
%STOPINCLUDE%
       """,
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
    store = PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model)
    return store


@pytest.fixture(scope="session")
def populated_vector_store(vector_store, test_docs):
    """Populate the vector store with test documents"""
    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = syncedTwikiDocumentLoader()
    twiki_creator = VectorStoreCreator(
        vector_store=vector_store,
        document_loader=document_loader,
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


def test_basic_search_text(populated_vector_store):
    """Test basic search functionality"""
    results = populated_vector_store.search("What is the ATLAS experiment?", k=0, k_text=2)

    assert len(results) > 0
    assert any("ATLAS" in result[1].page_content for result in results)  # Check a result containing ATLAS in results
    assert all(isinstance(result[2], float) for result in results)  # Check all results returned with a similarity
    assert all((0 <= result[2] <= 1) for result in results)  # Check all results returned with a similarity


def test_filtered_search(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(query="Higgs boson discovery", k=5, date_filter="01-04-2020")

    assert len(results) > 0
    for res in results:  # Check documents new enough
        file_date = datetime.strptime(res[1].metadata["last_modification"], "%d-%m-%Y")
        check_date = datetime.strptime("2020-04", "%Y-%m")
        assert file_date > check_date


def test_get_stats(populated_vector_store):
    """Test database statistics retrieval and validation."""
    stats = populated_vector_store.get_db_stats()
    print(stats)
    # Check stats exist and have correct structure
    assert isinstance(stats, dict)
    assert all(
        key in stats
        for key in [
            "last_modified",
            "total_documents",
            "total_embeddings",
            "vector_dimension",
            "unique_document_names",
            "index_lists",
            "index_probes",
            "total_disk_size_mb",
            "index_disk_size_mb",
            "cache_hit_ratio",
        ]
    )

    # Check value types and ranges
    assert isinstance(stats["last_modified"], str)  # ISO format timestamp
    assert isinstance(stats["total_documents"], int)
    assert isinstance(stats["total_embeddings"], int)
    assert isinstance(stats["vector_dimension"], int)
    assert isinstance(stats["unique_document_names"], int)
    assert isinstance(stats["total_disk_size_mb"], float)
    assert isinstance(stats["index_disk_size_mb"], float)
    assert isinstance(stats["cache_hit_ratio"], float)

    # Check logical relationships
    assert stats["total_documents"] > 0  # Should have some documents
    assert stats["total_embeddings"] > 0  # Should have some embeddings
    assert stats["total_embeddings"] <= stats["total_documents"]  # Can't have more embeddings than documents
    assert stats["unique_document_names"] <= stats["total_documents"]  # Can't have more unique names than documents
    assert stats["vector_dimension"] == populated_vector_store.vector_length  # Should match model dimension
    assert 0 <= stats["cache_hit_ratio"] <= 100  # Cache hit ratio should be percentage
    assert stats["total_disk_size_mb"] >= stats["index_disk_size_mb"]  # Total size includes index size


def test_filtered_search_text(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(query="Higgs boson discovery", k=0, k_text=2, date_filter="01-04-2020")

    assert len(results) == 2
    for res in results:  # Check documents new enough
        file_date = datetime.strptime(res[1].metadata["last_modification"], "%d-%m-%Y")
        check_date = datetime.strptime("2020-04", "%Y-%m")
        assert file_date > check_date


def test_filtered_search_multi_category(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(
        query="Higgs boson discovery",
        k=2,
        metadata_filters={"category": ["higgs", "adc"]},
    )

    assert len(results) == 2
    for res in results:  # Check documents have correct category
        assert "higgs" in res[1].metadata["category"] or "adc" in res[1].metadata["category"]


def test_english_dictionary(test_db, embedding_model):
    # Initialize vector stores with different dictionaries
    english_vs = PostgresParentChildVectorStore(
        connection_string=test_db,
        embedding_model=embedding_model,
        dictionary_type="english",
    )
    num = english_vs.update_text_search_vector()
    assert num > 0, "No rows were affected by the update"
    # Test English dictionary handling of variations
    results_english = english_vs.search("running particles colliding", k=0, k_text=2)
    assert len(results_english) > 0, "English dictionary search failed"

    english_vs.close()


def test_simple_dictionary(test_db, embedding_model):
    simple_vs = PostgresParentChildVectorStore(
        connection_string=test_db,
        embedding_model=embedding_model,
        dictionary_type="simple",
    )

    num = simple_vs.update_text_search_vector()  # Update to use this new text search vector
    assert num > 0, "No rows were affected by the update"

    # Test Simple dictionary exact matching
    results_simple = simple_vs.search("particle collider specifications", k=0, k_text=2)
    assert len(results_simple) > 0  # The simple search only matches exact words so should get no results here

    simple_vs.close()


def test_scientific_dictionary(test_db, embedding_model):
    scientific_vs = PostgresParentChildVectorStore(
        connection_string=test_db,
        embedding_model=embedding_model,
        dictionary_type="scientific",
    )

    scientific_vs.update_text_search_vector()
    # Test Scientific dictionary with technical terms
    results_scientific = scientific_vs.search("particle collider specifications", k=0, k_text=2)
    assert len(results_scientific) > 0, "Scientific dictionary search failed"
    scientific_vs.close()


def test_filtered_search_multi_category_text(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(
        query="Higgs boson discovery",
        k=2,
        k_text=0,
        metadata_filters={"category": ["higgs", "adc"]},
    )

    assert len(results) == 2  # Both vector search and text search return same document
    for res in results:  # Check documents have correct category
        assert "higgs" in res[1].metadata["category"] or "adc" in res[1].metadata["category"]

    results = populated_vector_store.search(
        query="Higgs boson discovery",
        k=0,
        k_text=2,
        metadata_filters={"category": ["higgs", "adc"]},
    )

    assert len(results) == 2  # Both vector search and text search return same document
    for res in results:  # Check documents have correct category
        assert "higgs" in res[1].metadata["category"] or "adc" in res[1].metadata["category"]


def test_filtered_search_multi_type(populated_vector_store):
    """Test search with metadata filters"""
    results = populated_vector_store.search(
        query="Higgs boson discovery",
        k=10,
        k_text=1,
        metadata_filters={"type": ["twiki", "CDS"], "category": ["higgs", "adc"]},
    )

    assert (
        len(results) > 1  # Assert document returned from both search types
    )  # Only 1 document is a twiki and has category higgs - has 2 chunks as long
    for res in results:
        assert "Higgs_Boson" in res[1].id or "ADC" in res[1].id


def test_langchain_integration(populated_vector_store):
    """Test LangChain integration"""
    langchain_store = LangChainVectorStore(vector_store=populated_vector_store)
    docs = langchain_store.invoke(
        "Tell me about the atlas experiment",
        config={"metadata": {"k": 2, "category": ["higgs", "adc"]}},
    )

    assert len(docs) > 0
    assert any("atlas" in doc.page_content.lower() for doc in docs)


def test_langchain_integration_both(populated_vector_store):
    """Test LangChain integration"""
    langchain_store = LangChainVectorStore(vector_store=populated_vector_store)
    docs = langchain_store.invoke(
        "Tell me about the atlas experiment",
        config={"metadata": {"k": 2, "k_text": 2, "category": ["higgs", "adc"]}},
    )

    assert len(docs) > 0
    assert any("atlas" in doc.page_content.lower() for doc in docs)


def test_langchain_integration_string_k(populated_vector_store):
    """Test LangChain integration"""
    langchain_store = LangChainVectorStore(vector_store=populated_vector_store)
    docs = langchain_store.invoke(
        "Tell me about the atlas experiment",
        config={"metadata": {"k": "2", "k_text": "2", "category": ["higgs", "adc"]}},
    )

    assert len(docs) > 0
    assert any("atlas" in doc.page_content.lower() for doc in docs)


def test_document_update_no_update(vector_store, test_docs):
    """Test updating existing documents - no documents to update so should do nothing"""

    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = syncedTwikiDocumentLoader()
    twiki_creator = VectorStoreCreator(
        vector_store=vector_store,
        document_loader=document_loader,
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
    # First, get original CSV before update
    docs_csv_old = pd.read_csv(OUT_DIR / "current_documents.csv")

    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = syncedTwikiDocumentLoader()
    twiki_creator = VectorStoreCreator(
        vector_store=vector_store,
        document_loader=document_loader,
        document_chunker=document_chunker,
        output_dir=OUT_DIR,
    )

    # Read and update the document with a newer date
    doc_path = test_docs / "Higgs_Boson.txt"
    with open(doc_path, encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Update the modification date to current date
    current_date = str(int(datetime.now().timestamp()))
    updated_content = content.replace("1736878918", current_date)

    # Write the updated content back to the file
    with open(doc_path, "w") as f:
        f.write(updated_content)

    # Update documents in vector store
    twiki_creator.create_update_vectorstore(input_path=test_docs, update=True, verbose=True)
    current_date_formatted = str(datetime.now().strftime("%d-%m-%Y"))

    # Verify documents were updated with new date
    results = vector_store.search(
        "Higgs boson discovery",
        k=1,
        metadata_filters={"last_modification": current_date_formatted},
    )
    assert len(results) > 0
    assert results[0][1].metadata["last_modification"] == current_date_formatted

    # Csv checks
    docs_csv_new = pd.read_csv(OUT_DIR / "current_documents.csv")

    assert not (docs_csv_old == docs_csv_new).all().all()
    assert len(docs_csv_old) == len(docs_csv_new)

    # Assert they have the new last modified date
    for _, row in docs_csv_new.iterrows():
        if row["document_name"] == "Higgs_Boson":
            assert row["last_modified_date"] == current_date_formatted


def test_search_relevance(populated_vector_store):
    """Test search result relevance"""
    # Search for ATLAS-related content
    atlas_results = populated_vector_store.search("ATLAS detector specifications", k=5)

    # Search for LHC-related content
    lhc_results = populated_vector_store.search("LHC collider specifications", k=5)

    # Verify results are different and relevant
    assert atlas_results != lhc_results
    assert any("46 m" in result[1].page_content for result in atlas_results)
    # assert any("27-kilometer" in result[0].page_content for result in lhc_results)


def test_search_relevance_text(populated_vector_store):
    """Test search result relevance"""
    # Search for ATLAS-related content
    atlas_results = populated_vector_store.search("ATLAS detector specifications", k=5, k_text=5)

    # Search for LHC-related content
    lhc_results = populated_vector_store.search("LHC collider specifications", k=5, k_text=5)

    # Verify results are different and relevant
    assert atlas_results != lhc_results
    assert any("46 m" in result[1].page_content.lower() for result in atlas_results)
    assert any("27-kilometer" in result[1].page_content.lower() for result in lhc_results)


def test_empty_search_query(populated_vector_store):
    """Test handling of empty search queries"""
    results = populated_vector_store.search("", k=2, k_text=2)
    assert len(results) == 0 or isinstance(results, list)


def test_very_large_k_value(populated_vector_store):
    """Test search with a very large k value"""
    results = populated_vector_store.search("test query", k=1000, k_text=1000)
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
        assert len(results) > 0


def test_non_int_k(populated_vector_store):
    """Test that vector store raises correct error when on int k value passed in"""
    with pytest.raises(ValueError):
        populated_vector_store.search(query="What is ATLAS?", k="two", k_text="three")

    lc_vs = LangChainVectorStore(vector_store=populated_vector_store)
    with pytest.raises(ValueError):
        lc_vs.invoke("What is ATLAS?", config={"metadata": {"k": "five", "k_text": "six"}})

    # Testing strings that can be parsed to ints
    res = populated_vector_store.search(query="What is ATLAS?", k="2", k_text="3")  # Should not fail
    assert len(res) > 0

    res = lc_vs.invoke("What is ATLAS?", config={"metadata": {"k": "5", "k_text": "6"}})
    assert len(res) > 0


def test_k_0(populated_vector_store):
    docs = populated_vector_store.search(query="What is ATLAS?", k=0, k_text=0)
    assert len(docs) == 0
    docs = populated_vector_store.search(query="What is ATLAS?", k=0)
    assert len(docs) == 0


def test_right_type(populated_vector_store):
    """A test to ensure the right document search type is returned"""

    # Vector only search
    results = populated_vector_store.search(query="What is ATLAS?", k=2, k_text=0)
    for res in results:
        parent_doc = res[1]
        assert parent_doc.metadata["search_type"] == "vector"

    # Text only search
    results = populated_vector_store.search(query="What is the higgs boson at ATLAS?", k=0, k_text=2)
    assert len(results) > 0
    for res in results:
        parent_doc = res[1]
        assert parent_doc.metadata["search_type"] == "text"

    # Joint search
    results = populated_vector_store.search(query="What is the higgs boson at ATLAS?", k=1, k_text=5)
    search_types = [res[1].metadata["search_type"] for res in results]
    assert len(set(search_types)) > 1  # assert we got distinct searches


def test_deduplicated_docs(populated_vector_store):
    """Test to ensure documents are not duplicated"""
    results = populated_vector_store.search(query="What is ATLAS?", k=10, k_text=10)

    page_content = []
    ids = []
    for res in results:
        page_content.append(res[1].page_content)
        ids.append(res[1].id)

    assert len(set(page_content)) == len(page_content), "Found duplicate page content"
    assert len(set(ids)) == len(ids), "Found duplicate document IDs"


def test_special_characters_search_with_text_search(populated_vector_store):
    """Test search with special characters"""
    special_queries = [
        "test!@#$%^&*()",
        "SQL; DROP TABLE;",
        "\\n\\t\\r",
        "'quoted string'",
        "unicode_☢️_test",
    ]
    for query in special_queries:
        results = populated_vector_store.search(query, k=2, k_text=2)
        assert isinstance(results, list)
        assert len(results) > 0


def test_special_characters_in_text(test_db, embedding_model, tmp_path):
    """
    Tests text that has unicode characters in their input, in metadata and in file name
    """
    # Initialize vector store
    vector_store = PostgresParentChildVectorStore(connection_string=test_db, embedding_model=embedding_model)
    special_doc_names = ["test_αβγ_doc.txt", "test_测试_文档.txt"]

    # Create test files with special characters in names and content
    special_files = [
        {
            "filename": special_doc_names[0],  # Greek letters
            "content": """%META:TOPICINFO{author="test☢️user" date="1416477899" format="1.1" version="1.369"}%
%META:TOPICPARENT{name="SpecialCharTest"}%
%STARTINCLUDE%
This is a test document with special characters: ☢️🔬⚛️
Testing Unicode characters: ü, é, ñ, ß
Extra Lines to ensure document doesn't get skipped
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
Testing symbols: ©®™
%STOPINCLUDE%""",
        },
        {
            "filename": special_doc_names[1],  # Chinese characters
            "content": """%META:TOPICINFO{author="test_user" date="1416477899" format="1.1" version="1.369"}%
%META:TOPICPARENT{name="SpecialCharTest"}%
%STARTINCLUDE%
Another test document with mixed characters: Latin, 中文, हिंदी
Testing more special characters: ∞ ∑ ∏ √ ∫
Extra Lines to ensure document doesnt get skipped
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
filler
%STOPINCLUDE%""",
        },
    ]

    # Create temporary files
    test_files = []
    for file_info in special_files:
        file_path = tmp_path / file_info["filename"]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_info["content"])
        test_files.append(file_path)

    # Initialize vectorstore creator
    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = syncedTwikiDocumentLoader()
    twiki_creator = VectorStoreCreator(
        vector_store=vector_store,
        document_loader=document_loader,
        document_chunker=document_chunker,
        output_dir=tmp_path / "special_chars",
    )

    # Try to add documents to vectorstore
    twiki_creator.create_update_vectorstore(input_path=tmp_path, update=True, verbose=True)

    # Test searching with special characters
    search_queries = [
        "测试",  # Chinese
        "αβγ",  # Greek
        "☢️",  # Emoji
        "∞ ∑",  # Math symbols
    ]

    for query in search_queries:
        results = vector_store.search(query, k=2)
        assert len(results) > 0, f"No results found for query: {query}"
        # Check if results contain the special characters
        found_special_chars = False
        for result in results:
            if (
                query in result[0].page_content
                or query in result[0].name
                or query in result[1].page_content
                or query in result[1].name
            ):
                found_special_chars = True
                break
        assert found_special_chars, f"Special characters not found in results for query: {query}"

    saved_docs = pd.read_csv(tmp_path / "special_chars" / "current_documents.csv")

    # Ensure we haven't corrupted document names
    expected_stems = {Path(name).stem: name for name in special_doc_names}
    for doc_new_name in saved_docs["document_name"]:
        assert doc_new_name in expected_stems

    # Clean up
    vector_store.close()
    for file_path in test_files:
        file_path.unlink()


def test_concurrent_write_operations(vector_store, test_docs):
    """Test concurrent write operations to the vectorstore"""
    # NOTE: This sometimes fails - not sure why...?

    def update_operation(doc_number):
        parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
        child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
        document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

        document_loader = syncedTwikiDocumentLoader()
        twiki_creator = VectorStoreCreator(
            vector_store=vector_store,
            document_loader=document_loader,
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


def test_memory_usage_with_text(populated_vector_store):
    """Test memory usage during large search operations"""

    tracemalloc.start()

    # Perform multiple searches
    for _ in range(100):
        populated_vector_store.search("test query", k=10, k_text=10)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Assert reasonable memory usage (adjust threshold as needed)
    assert peak < 100 * 1024 * 1024  # 100MB threshold


def test_metadata_persistence(populated_vector_store):
    """Test persistence of metadata across operations"""
    # Search and get initial metadata
    initial_results = populated_vector_store.search("ATLAS", k=1)
    initial_metadata = initial_results[0][0].metadata

    # Perform some operations
    populated_vector_store.search("Higgs", k=1)
    populated_vector_store.search("LHC", k=1)

    # Search again and compare metadata
    final_results = populated_vector_store.search("ATLAS", k=1)
    final_metadata = final_results[0][0].metadata

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


def test_search_with_filters_combination_text(populated_vector_store):
    """Test search with multiple metadata filters"""
    results = populated_vector_store.search(
        "test query",
        k=2,
        k_text=2,
        metadata_filters={"last_modification": "01-09-2021", "name": "Higgs_Boson"},
    )

    assert all(
        result[1].metadata["last_modification"] == "01-09-2021" and result[1].metadata["name"] == "Higgs_Boson"
        for result in results
    )


def test_csv_output_dir_premade():
    csv_path = OUT_DIR / "current_documents.csv"

    assert csv_path.exists()

    df = pd.read_csv(csv_path)
    expected_columns = [
        "document_name",
        "url",
        "last_modified_date",
        "added_to_db_date",
        "included",
        "reason_for_exclusion",
    ]
    assert all(col in df.columns for col in expected_columns), "CSV missing expected columns"

    # Verify content
    assert len(df) >= 2, "CSV should contain at least the test documents"


def test_save_to_output_dir(populated_vector_store, test_docs, tmp_path):
    """Test saving document records to CSV in output directory"""
    # Create test documents with metadata
    test_documents = [
        Document(
            page_content="Test content 1",
            source=DocumentSource.TWIKI,
            name="test_doc_1",
            url="https://test.com/1",
            metadata={
                "last_modification": "01-02-2024",
            },
            id="1",
        ),
        Document(
            page_content="Test content 2",
            source=DocumentSource.TWIKI,
            name="test_doc_2",
            url="https://test.com/2",
            metadata={
                "last_modification": "02-02-2024",
            },
            id="2",
        ),
    ]

    # Initialize creator with temporary output directory
    parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
    child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)
    document_chunker = DocumentChunker(parent_splitter=parent_splitter, child_splitter=child_splitter)

    document_loader = syncedTwikiDocumentLoader(_skip_docs=False, verbose=False)
    creator = VectorStoreCreator(
        vector_store=populated_vector_store,
        document_loader=document_loader,
        document_chunker=document_chunker,
        output_dir=tmp_path,
    )

    # Call save_to_output_dir
    creator.save_to_output_dir(test_documents, [])

    # Check if CSV file exists
    csv_path = tmp_path / "current_documents.csv"
    assert csv_path.exists(), "CSV file was not created"

    # Read and verify CSV content
    df = pd.read_csv(csv_path)

    # Check column structure
    expected_columns = [
        "document_name",
        "url",
        "last_modified_date",
        "added_to_db_date",
        "included",
        "reason_for_exclusion",
    ]
    assert all(col in df.columns for col in expected_columns), "CSV missing expected columns"

    # Verify content
    assert len(df) >= 2, "CSV should contain at least the test documents"
    assert "test_doc_1" in df["document_name"].values, "First test document not found"
    assert "test_doc_2" in df["document_name"].values, "Second test document not found"

    # Check data integrity
    test_doc_1 = df[df["document_name"] == "test_doc_1"].iloc[0]
    assert test_doc_1["url"] == "https://test.com/1"
    assert test_doc_1["last_modified_date"] == "01-02-2024"
    assert test_doc_1["included"]
    assert pd.isna(test_doc_1["reason_for_exclusion"])

    # Test updating existing entries
    updated_doc = Document(
        page_content="Updated content",
        source=DocumentSource.TWIKI,
        name="test_doc_1",
        url="https://test.com/1",
        metadata={
            "last_modification": "03-02-2024",
        },
        id="1",
    )
    creator.save_to_output_dir([], [updated_doc])

    # Read updated CSV and verify changes
    df_updated = pd.read_csv(csv_path)
    updated_entry = df_updated[df_updated["document_name"] == "test_doc_1"].iloc[0]
    assert updated_entry["last_modified_date"] == "03-02-2024", "Document was not updated correctly"


def test_delete_documents(populated_vector_store):
    """
    Test for deleting documents from the vectorstore
    """
    populated_vector_store.delete(document_name="ATLAS_Experiment")

    results = populated_vector_store.search("ATLAS detector specifications", k=3)

    assert all("ATLAS_Experiment" not in result[1].name for result in results)
    populated_vector_store.close()
