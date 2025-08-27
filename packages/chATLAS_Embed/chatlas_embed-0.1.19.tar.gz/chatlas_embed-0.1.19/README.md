
# chATLAS Embed

<div align="center">
  
  ![ATLAS](https://atlas.cern/sites/atlas-public.web.cern.ch/files/inline-images/ATLAS%20logo%20blue%20on%20white%20RGBHEX%20300ppi.png)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-FFD21E?style=for-the-badge)

  *A modular Python package for efficient embedding workflows and PostgreSQL-based vector store management with parent-child relationships.*

</div>

## 📚 Overview

chATLAS_Embed provides a flexible framework for creating and managing vector stores with PostgreSQL backend support. The package excels at document processing tasks through its modular architecture, enabling custom implementations of embedding models, vector stores, and text splitters. Originally designed at the ATLAS experiment at CERN for the chATLAS project.

### 🌟 Key Features

- PostgreSQL vector extension compatibility for robust database operations
- Hierarchical document storage with parent-child relationships
- Extensible architecture supporting custom components:
  - Text splitters
  - Embedding models
  - Vector stores
  - Vector store creators
- Comprehensive RAG pipeline examples
- Seamless Langchain integration

## 🚀 Quick Start

### 📥 Installation

```bash
cd chATLAS_Embed
uv sync
```

### 💡 Basic Usage - Connecting to an existing vectorstore

```python
from chATLAS_Embed import PostgresParentChildVectorStore
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

# Initialize embedding model
embedding_model = SentenceTransformerEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Set up vector store
vector_store = PostgresParentChildVectorStore(
    connection_string="postgresql://{user}:{password}@{PostgresServer}:{port}/{database_name}",
    embedding_model=embedding_model
)

# Search through the vectorstore
vector_store.search("What is the ATLAS Experiment?")

vector_store.close()  # Make sure to close the vectorstore once done with it (automatically closes when process ends)
```

### 🚀 Getting Started Locally

For a complete local setup with examples, see the **`quickstart/`** directory:

```bash
cd chATLAS_Embed/quickstart
# Follow the README.md for step-by-step instructions
```

The quickstart includes:
- Complete setup guide with Docker
- Working example scripts  
- Database initialization
- Troubleshooting tips

---

## Contents

1. [Installation](#installation)
2. [Requirements](#requirements)
3. [Usage](#usage)
4. [Hybrid Retrieval](#-hybrid-retrieval)
5. [Extending chATLAS_Embed](#extending-chatlas_embed)
   - [Adding New Vector Stores](#adding-new-vector-stores)
   - [Creating New Embedding Models](#creating-new-embedding-models)
   - [Building New Text Splitters](#building-new-text-splitters)
   - [Defining Custom Vector Store Creators](#defining-custom-vector-store-creators)
6. [Current Implementations](#current-implementations)
7. [Project Structure and Imports](#project-structure-and-imports)
8. [Change Log](#change-log)


---

## Before starting, when using local DB instances

Install postgresql and start PostgreSQL service (on Linux)

```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

Install `pgvector` following the instructions provided in the repository:

```bash
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

Then connect to the psql shell:

```bash
sudo -u postgres psql
```
or
```bash
psql -U postgres -h localhost
```

and for each database where you want the extension to be used, run the following command:

```sql
CREATE DATABASE my_new_database;
\c my_new_database # change to the name of your DB
CREATE EXTENSION vector;
```

At this point one can use the python classes provided in this package to manipulate the database. Notice that it is possible to operate on the database with a user different from the default one (postgres). To be able to do so, connect to the psql shell and create a new user and grant privileges on the database of interest:

```sql
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE my_vector_db TO myuser;
```

## Usage

### A. Creating a Vector Store

#### 1. **Initialize Components**
Define the key components for creating a vector store, including the embedding model, text splitters, and the vector store itself.

```python
from chATLAS_Embed import RecursiveTextSplitter, PostgresParentChildVectorStore
from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding

# Define the embedding model
embedding_model = SentenceTransformerEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Define text splitters for parent and child documents
parent_splitter = RecursiveTextSplitter(chunk_size=2048, chunk_overlap=24)
child_splitter = RecursiveTextSplitter(chunk_size=256, chunk_overlap=24)

# Initialize the vector store
vector_store = PostgresParentChildVectorStore(
    connection_string="postgresql://{user}:{password}@{PostgresServer}:{port}/{database_name}",
    embedding_model=embedding_model
)
```

#### 2. **Create and Populate the Vector Store**
Use the `VectorStoreCreator` with a document loader to populate the vector store with documents.

```python
from chATLAS_Embed import VectorStoreCreator, DocumentChunker
from chATLAS_Embed.DocumentLoaders import TWikiTextDocumentLoader
from pathlib import Path

# Initialize the document loader and chunker
document_loader = TWikiTextDocumentLoader()
document_chunker = DocumentChunker(
    parent_splitter=parent_splitter,
    child_splitter=child_splitter
)
twiki_creator = VectorStoreCreator(
    vector_store=vector_store,
    document_loader=document_loader,
    document_chunker=document_chunker,
    output_dir=Path("./output")
)

# Process and add documents to the vector store
twiki_creator.create_update_vectorstore(
    input_path=Path("path/to/documents"),
    update=True,  # Update existing documents if newer versions exist
    verbose=True  # Print details of documents added or updated
)
```

---

### B. Querying an Existing Database

#### 1. **Connect to the Database**
Establish a connection to the existing vector store.

```python
db = PostgresParentChildVectorStore(
    connection_string="postgresql://{user}:{password}@{PostgresServer}:{port}/{database_name}",
    embedding_model=embedding_model
)
```

#### 2. **Search the Database**

##### **Simple Search**
Retrieve the top `k` most relevant documents for a given query and top `k_text` documents from the hybrid text searching.

```python
results = db.search("What is the ATLAS experiment?", k=4, k_text=2)
```

##### **Advanced Search**
Filter search results by metadata and date.

```python
results = db.search(
    query="What is the ATLAS experiment?",
    k=4,
    date_filter="01-09-2014",  # Retrieve documents modified after this date (dd-mm-YYYY)
    metadata_filters={
        "type": ["twiki", "CDS"],  # Either a twiki doc or a CDS doc
        "name": "Document Name",
        "url": "URL to webpage",
        "last_modification": "dd-mm-YYYY",  # Retrieve documents from this specific month
        "category": ["CERN", "ATLAS"]  # If your documents have a category metadata setup can search for containment.
    }
)
```

### C. Closing the database properly

```python
# Option 1: Explicit cleanup
vector_store = PostgresParentChildVectorStore(connection_string, embedding_model)
# Use vector_store
vector_store.close()  # Important!

# Option 2: Delete the vectorstore object if it won't be used again
vector_store = PostgresParentChildVectorStore(connection_string, embedding_model)
# Use vector_store
del vector_store  # Important!


# Option 2: Context manager
with PostgresParentChildVectorStore(connection_string, embedding_model) as vector_store:
    # Use vector_store
    # Connections automatically closed when exiting the block
```

---

### D. Integration with LangChain
Easily integrate the vector store into a LangChain pipeline.

```python
from chATLAS_Embed import LangChainVectorStore

# Convert the vector store for use with LangChain
db_langchain = LangChainVectorStore(vector_store=db)

docs = db_langchain.invoke("What is ATLAS?", config={"metadata": {"k": 2, "k_text": 2, "date_filter": "01-10-2020"}})
```

This then works the '*same*' as a regular langchain retriever, though not all implementations have been tested.

Note that documents retrieved from the langchain vector store are only the parent documents. The similarity for each
document is stored in its metadata by:

```python
docs[0].metadata["similarity"]
```

---

### Notes:
- Replace placeholders like `{user}`, `{password}`, `{PostgresServer}`, `{port}`, and `{database_name}` with actual connection details.
- Ensure documents have metadata (e.g., `last_modification`) defined when using filters.
- Refer to details section below for full example integration with langchain.
---


4. **Full RAG Pipeline w/ Langchain Integration**

<details>
<summary>Full RAG Pipeline example using Langchian wrapper</summary>

```python
"""
Example usage of the DB with a full Langchain RAG chain

USES Memory in its responses storing currently just the previous answers given by the LLM for now
"""
# IMPORTS
from pathlib import Path

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate

from chATLAS_Embed.EmbeddingModels import SentenceTransformerEmbedding
from chATLAS_Embed import LangChainVectorStore, PostgresParentChildVectorStore




def create_rag_chain(vectorstore: LangChainVectorStore) -> ConversationalRetrievalChain:
   """Create a RAG chain using the vector store."""

   # Initialize language model
   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

   # Create conversation memory
   memory = ConversationSummaryBufferMemory(
      memory_key="chat_history",
      return_messages=True,
      output_key="answer",
      llm=llm
   )

   # Create custom prompts
   qa_template = """You are a helpful particle physics assistant at the ATLAS experiment in the Large Hadron Collider. \
Your colleagues are asking questions about information contained in the documents of ATLAS experiment. \
You will be given selected paragraphs from ATLAS documents. You need to provide a comprehensive summary of the given
 text that can be useful to help answering this question. The summary should cover all the key points and main ideas
 presented in the original text that helps answering the question, while also condensing the information into a concise
and easy-to-understand format. Please ensure that the summary includes all the relevant jargons, values, and as much details as possible, \
while avoiding any unnecessary repetition.\n
    Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context:
    {context}

    Chat History: {chat_history}
    Question: {question}
    Helpful Answer:"""

   qa_prompt = PromptTemplate(
      input_variables=["context", "chat_history", "question"],
      template=qa_template
   )

   # Create the chain
   chain = ConversationalRetrievalChain.from_llm(
      llm=llm,
      retriever=vectorstore,
      memory=memory,
      combine_docs_chain_kwargs={"prompt": qa_prompt},
      return_source_documents=True,
   )

   return chain


def main():
   # Configuration
   DB_CONNECTION = "postgresql://{user}:{password}@{PostgresServer}:{port}/{database_name}"
   OUTPUT_DIR = "./output"


   # Load pre-made vectorstore
   db = PostgresParentChildVectorStore(
      connection_string=DB_CONNECTION,
      embedding_model=SentenceTransformerEmbedding(
         model_name="sentence-transformers/all-MiniLM-L6-v2")
   )
   # Convert to langchain compatible
   vectorstore = LangChainVectorStore(vector_store=db)

   # Create RAG chain
   chain = create_rag_chain(vectorstore)

   # Example usage
   while True:
      question = input("\nEnter your question (or 'quit' to exit): ")
      if question.lower() == 'quit':
         break

      result = chain({"question": question})
      print("\nAnswer:", result["answer"])
      print("\nSources:")
      for doc in result["source_documents"]:
         print(f"- {doc.metadata['parent_metadata']['name']} ({doc.metadata['parent_metadata']['url']})")
         print(f"SIMILARITY: {doc.metadata['similarity']}")
         print("-"*20)
         print(doc.page_content)
         print("-"*30)


if __name__ == "__main__":
   main()
```

</details>

### C. `Document` Dataclass

Returned by search and used to adding documents to the db is the Document dataclass (v. similar to langchain document):

```python
@dataclass
class Document:
    """Represents a base document with its page_content and metadata."""
    page_content: str
    metadata: Dict[str, Any]
    id: str
    parent_id: Optional[str] = None
```

## 🔍 Hybrid Retrieval

The vector store implements a sophisticated hybrid search combining both semantic and lexical search capabilities for optimal retrieval performance.

#### Search Types

1. **Semantic (Vector) Search**
   - Uses cosine similarity between embedded query and document vectors
   - Finds documents with similar meaning/context regardless of exact wording
   - Similarity scores range 0-1 (1 = highest similarity)

2. **Lexical (Text) Search**
   - Utilizes PostgreSQL's native text search with `tsvector`/`tsquery`
   - Implements weighted document ranking:
     - Document names (Weight A - highest priority)
     - Document topics and content (Weight B - medium priority)
   - Scores normalized to 0-1 range

#### Usage

```python
results = vector_store.search(
    query="search query",
    k=4,              # Number of vector search results
    k_text=2,         # Number of text search results
    metadata_filters={
        "type": ["paper", "image"],  # Returns docs of type paper OR image
        "experiment": "ATLAS"        # Exact match filtering
    },
    date_filter="01-01-2023"        # Only docs after this date (dd-mm-yyyy)
)
```

#### Results

- Returns list of tuples: `(child_doc, parent_doc, similarity_score)`
- Each `parent_doc.metadata` includes `"search_type": "vector"` or `"text"`
- Results automatically deduplicated across search types
- Final results limited to `k + k_text` total documents
- Similarity scores normalized but not directly comparable between search types

#### Advanced Features

- Fetches extra results initially to handle metadata filtering
- Supports multi-value metadata filtering (OR conditions)
- Date-based filtering using document modification dates
- Text search considers:
  - Term proximity and density
  - Word stemming and stop word removal
  - Document structure weights

---

## Current Implementations

### Vector Stores

#### **PostgresParentChildVectorStore**

This vector store implements a parent-child structure using PostgreSQL with the `pgvector` extension, designed for efficient document storage and retrieval. It replaces the previously used Chroma-based solution in Chatlas, addressing issues like the inability to list parent stores.

This implementation aligns with CERN IT standards by leveraging PostgreSQL for scalability and maintainability.

##### **Example Performance Metrics**

Using current batching methods, performance benchmarks for processing ~ 22k docs are as follows:

- **Time to Add Documents**:
  - Total time: 47 minutes
    - Embedding: ~21 minutes
    - Adding embeddings to the database: ~21 minutes

- **Storage Requirements** (disk):
  - Before embeddings: 1.5 GB
  - After embeddings: 5.2 GB

##### **Key Features**

<details>
<summary>Click for methods and attributes</summary>

- **`add_documents`**:
  Inserts parent and child documents into the database. Parent chunks (ID, content, metadata, parent ID) and child chunks (ID, content, metadata, parent ID) are stored in the `documents` table. Corresponding embeddings (ID, document ID, embedding) are added to the `embeddings` table. The `pgvector` extension is required for vector operations.

- **`reindex_database`**:
  This can be used to update the index for the current search algorithm (IVFFlat, HNSW, or exact) or change to a different search algorithm.
  The default search algorithm is IVFFlat. For IVFFlat, calling `reindex_database` dynamically adjusts the number of lists in the IVFFlat index based on the total number of embeddings. The optimal number of lists is calculated as:
  `optimal_lists = int(math.sqrt(count) + 0.05 * math.sqrt(count))`
  `optimal_probes = int(optimal_lists * 0.14)`
  Running this on the full dataset (~1 million embeddings) takes approximately 165 seconds. Regular optimization is recommended after significant data additions.
  To switch to HNSW, use `reindex_database('HNSW')`. Optionally, the desired `m` and `ef_construction` parameters can be specified.
  To switch to an exact search, use `reindex_database('exact')`.
  To switch back to IVFFlat, use `reindex_database('IVFFlat')`.
  WARNING: Switching the search algorithm and recreating/updating the vector store index affects all users of the vector store and may be disruptive to any ongoing queries. `PostgresParentChildVectorStore` uses the search algorithm that was last set via
  `reindex_database` and this algorithm remains active for all users until it is changed by calling `reindex_database`.

- **`search`**:
  Performs a cosine similarity search using IVFFlat indexing to find the top `k` documents. Results include the child document, parent document, and similarity score. Supports metadata-based and date-based filtering:
  - **`k`**: Number of results to return (default: 4).
  - **`metadata_filters`**: Filters results by metadata tags (e.g., `{"name": "AtlasModules"}`).
  - **`date_filter`**: Retrieves documents last modified after a specified date (e.g., `"01-04-2010"`) - in format "dd-mm-YYYY".
</details>

### VectorStoreCreator and DocumentLoaders

The package now uses a modular composition-based architecture with `VectorStoreCreator` and `DocumentLoader` classes:

- `VectorStoreCreator`
  - Core class that orchestrates the vector store creation process
  - Uses dependency injection to work with any `DocumentLoader` implementation
  - `create_update_vectorstore` method:
    - Adds documents to the database if they are not already added from a directory of whatever file type
    - If the document is already in the database and `update=True` param set, will check for every document in the
input directory that is also in the dataset if the `last_updated` metadata key for the document stored is older than
the new document in the directory and if there is a new version available it drops all chunks associated with the old
document and replaces it with the new ones.

### DocumentLoaders

- `TWikiHTMLDocumentLoader`
  - Processes HTML documents directly from a directory and loads them into the vectorstore.
  - Follows the same method previously used to convert the HTML to text.

- `TWikiTextDocumentLoader`
  - Processes plain text TWiki documents.

- `CDSTextDocumentLoader`
  - Loads scraped CDS plain text documents.

- `GitlabMarkdownDocumentLoader`
  - Processes Markdown documents from GitLab repositories.

- `syncedTwikiDocumentLoader`
  - Handles synchronized TWiki documents with specific formatting.

*Note: Legacy `VectorStoreCreator` classes (e.g., `TWikiHTMLVectorStoreCreator`) are still available but deprecated. Use the new modular approach with `VectorStoreCreator` + `DocumentLoader` for new projects.*


### Embedding Models

- `SentenceTransformerEmbedding`: Standard sentence transformer embedding model adapted for this db setup.

### Text Splitters

- `RecursiveTextSplitter`:
Bog standard langchain recursive text splitter built to follow modularity structure.

- `ParagraphTextSplitter`
**WIP! - untested:**
Aims to implement a Text splitter that splits based on paragraphs rather than on token count.


### Custom Implementation Example: Scientific Plot Database

<details>
<summary>Example workflow and implementation - simple version</summary>

Setting up new modules:

```python
from chATLAS_Embed.Base import DocumentLoader, Document, TextSplitter
from chATLAS_Embed import VectorStoreCreator
from typing import List
from pathlib import Path


# Create a new document loader to load a new type of document
class PlotDocumentLoader(DocumentLoader):
    def load_documents(self, input_path: Path) -> List[Document]:
        """Load plots from the input path."""

        # Example workflow for creating documents for the plots
        documents = []
        for plot in input_path:
            doc = Document(
                page_content=plot.description,
                # Below metadata is only an example, redefine with whatever metadata you want
                metadata={
                    'type': 'plot',
                    'name': plot.name,
                    'url': plot.url,
                    'last_modification': plot.lastModification,  # Or created date
                    'title': plot.title
                    # plus any others
                },
                id=plot.paperName
            )
            documents.append(doc)

        return documents


# Create a new text splitter for parent doucment to contain the full description

class PlotParentTextSplitter(TextSplitter):

    def split(self, text: str) -> [str]:
        """Want full description in parent doc so can return full description as chunk"""
        return [text]
```

Actually creating the vectorstore
```python
from chATLAS_Embed import SentenceTransformerEmbedding, RecursiveTextSplitter, PostgresParentChildVectorStore, VectorStoreCreator
from pathlib import Path

# Initialize components
embedding_model = SentenceTransformerEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

parent_splitter = PlotParentTextSplitter()


child_splitter = RecursiveTextSplitter(
    chunk_size=256, chunk_overlap=24  # All mini LM has a context window of 256 so unless you want to use a better model (e.g. multi-qa-mpnet-base-dot-v1) text needs to be split to this size
)

vector_store = PostgresParentChildVectorStore(
    connection_string="postgresql://{user}:{password}@{server}:{port}/plot_db",  # Change this for wherever you want to create the vectorstore
    embedding_model=embedding_model
)

# Create Plot vector store with document loader
document_loader = PlotDocumentLoader()
document_chunker = DocumentChunker(
    parent_splitter=parent_splitter,
    child_splitter=child_splitter
)
plot_creator = VectorStoreCreator(
    vector_store=vector_store,
    document_loader=document_loader,
    document_chunker=document_chunker,
    output_dir=Path("./output")  # Not currently used
)


# Process Plot documents
plot_creator.create_update_vectorstore(
  input_path=Path("path/to/plots",   # However you want to load or store plots
                  update=True)
)
```

Searching the database once created:
```python
vector_store = PostgresParentChildVectorStore(
    connection_string="postgresql://{user}:{password}@{server}:{port}/plot_db",  # Change this for wherever you want to create the vectorstore
    embedding_model=embedding_model
)

vector_store.search("Find me a plot about track reconstruction at ATLAS")
```


</details>


<details>
<summary>Example workflow and implementation - more custom implementation</summary>


This is much more in depth rewrite of code building custom vector stores and ways of processing documents.
It is in no way tested, just shows example workflow on how something like this could work!


**NOTE**: This is not tested or complete, just a guide of how something like this could work!!

```python
from chATLAS_Embed.Base import VectorStore, Document
from typing import List, Dict, Any, Optional
import psycopg2
import json

class ScientificPlotVectorStore(VectorStore):
    def __init__(self, connection_string: str, embedding_model: EmbeddingModel):
        """
        Initialize the Scientific Plot Vector Store.

        Args:
            connection_string: PostgreSQL connection string
            embedding_model: Model for embedding plot descriptions
        """
        self.connection_string = connection_string
        self.embedding_model = embedding_model
        self._initialize_database()

    def _initialize_database(self):
        """Create necessary tables and indexes."""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Create parent table for plots
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS plot_documents (
                        id TEXT PRIMARY KEY,
                        plot_path TEXT NOT NULL,
                        title TEXT NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create child table for plot descriptions
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS plot_descriptions (
                        id TEXT PRIMARY KEY,
                        plot_id TEXT REFERENCES plot_documents(id),
                        description TEXT NOT NULL,
                        metadata JSONB,
                        embedding vector(384),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS plot_metadata_idx
                    ON plot_documents USING GIN (metadata)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS desc_embedding_idx
                    ON plot_descriptions
                    USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100)
                """)

    def add_documents(self, parent_docs: List[Document], child_docs: List[Document]):
        """
        Add plot documents and their descriptions to the database.

        Args:
            parent_docs: List of plot Documents (containing plot paths)
            child_docs: List of description Documents
        """
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Add parent plot documents
                for doc in parent_docs:
                    cur.execute("""
                        INSERT INTO plot_documents (id, plot_path, title, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET plot_path = EXCLUDED.plot_path,
                            title = EXCLUDED.title,
                            metadata = EXCLUDED.metadata
                    """, (
                        doc.id,
                        doc.metadata.get('plot_path'),
                        doc.metadata.get('title'),
                        json.dumps(doc.metadata)
                    ))

                # Generate embeddings for descriptions
                descriptions = [doc.page_content for doc in child_docs]
                embeddings = self.embedding_model.embed(descriptions)

                # Add child description documents with embeddings
                for doc, embedding in zip(child_docs, embeddings):
                    cur.execute("""
                        INSERT INTO plot_descriptions
                        (id, plot_id, description, metadata, embedding)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET description = EXCLUDED.description,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                    """, (
                        doc.id,
                        doc.parent_id,
                        doc.page_content,
                        json.dumps(doc.metadata),
                        embedding.tolist()
                    ))

    def search(
        self,
        query: str,
        k: int = 4,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for plots based on description similarity.

        Args:
            query: Search query
            k: Number of results to return
            metadata_filters: Optional filters for metadata fields

        Returns:
            List of Documents containing plot information and descriptions
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed([query])[0]

        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Construct base query
                query_sql = """
                    SELECT
                        pd.id as desc_id,
                        pd.description,
                        pd.metadata as desc_metadata,
                        p.id as plot_id,
                        p.plot_path,
                        p.title,
                        p.metadata as plot_metadata,
                        1 - (pd.embedding <=> %s) as similarity
                    FROM plot_descriptions pd
                    JOIN plot_documents p ON pd.plot_id = p.id
                    WHERE 1=1
                """
                params = [query_embedding.tolist()]

                # Add metadata filters if provided
                if metadata_filters:
                    for key, value in metadata_filters.items():
                        query_sql += f" AND p.metadata->>{key} = %s"
                        params.append(value)

                # Add similarity ordering and limit
                query_sql += """
                    ORDER BY similarity DESC
                    LIMIT %s
                """
                params.append(k)

                # Execute search
                cur.execute(query_sql, params)
                results = cur.fetchall()

                # Convert results to Documents
                documents = []
                for result in results:
                    desc_id, description, desc_metadata, plot_id, plot_path, title, plot_metadata, similarity = result

                    # Create child document (description)
                    child_doc = Document(
                        page_content=description,
                        metadata={
                            **json.loads(desc_metadata),
                            'similarity': similarity
                        },
                        id=desc_id,
                        parent_id=plot_id
                    )

                    # Create parent document (plot)
                    parent_doc = Document(
                        page_content=f"Title: {title}\nPlot Path: {plot_path}",
                        metadata=json.loads(plot_metadata),
                        id=plot_id
                    )

                    documents.append((child_doc, parent_doc))

                return documents

    def delete(self, document_ids: Optional[List[str]] = None):
        """
        Delete documents from the database.

        Args:
            document_ids: Optional list of document IDs to delete
        """
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                if document_ids:
                    # Delete specific documents
                    cur.execute("""
                        DELETE FROM plot_descriptions
                        WHERE id = ANY(%s) OR plot_id = ANY(%s)
                    """, (document_ids, document_ids))
                    cur.execute("""
                        DELETE FROM plot_documents
                        WHERE id = ANY(%s)
                    """, (document_ids,))
                else:
                    # Delete all documents
                    cur.execute("DELETE FROM plot_descriptions")
                    cur.execute("DELETE FROM plot_documents")
```

Usage example for the Scientific Plot Vector Store:

```python
# Initialize the store
plot_store = ScientificPlotVectorStore(
    connection_string="postgresql://user:pass@localhost:5432/plots_db",
    embedding_model=SentenceTransformerEmbedding()
)

# Create parent document for a plot
plot_doc = Document(
    page_content="",  # Empty as content is in metadata
    metadata={
        'plot_path': '/path/to/plot.png',
        'title': 'Higgs Boson Mass Distribution',
        'experiment': 'ATLAS',
        'year': '2023'
    },
    id='plot_001'
)

# Create child documents for plot descriptions
desc_docs = [
    Document(
        page_content="Distribution of invariant mass showing clear peak at 125 GeV",
        metadata={'section': 'results'},
        id='desc_001',
        parent_id='plot_001'
    ),
    Document(
        page_content="Signal region with background subtraction applied",
        metadata={'section': 'analysis'},
        id='desc_002',
        parent_id='plot_001'
    )
]

# Add documents to store
plot_store.add_documents([plot_doc], desc_docs)

# Search for plots
results = plot_store.search(
    query="mass distribution peak",
    k=5,
    metadata_filters={'experiment': 'ATLAS'}
)
```
</details>


## 🔧 Development Status

Current development priorities:

- [x] HNSW indexing implementation
- [ ] Bulk deletion optimization
- [x] Advanced filtering capabilities
- [x] Function to check connection to datastore
- [x] Parent-child relationship support
- [x] PostgreSQL integration

---


## 📄 License

chATLAS_Embed is released under Apache 2.0 license.

---


---

**Made with ❤️ by the ATLAS Collaboration**

*For questions and support, please [contact](mailto:Ben.Elliot27@outlook.com)*
