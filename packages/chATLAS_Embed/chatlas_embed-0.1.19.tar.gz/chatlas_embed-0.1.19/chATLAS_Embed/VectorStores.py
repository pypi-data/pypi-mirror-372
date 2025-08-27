#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/VectorStores.py`

"""
A collection of VectorStores.
"""

import json
import math
import re
import time

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from tqdm import tqdm

from chATLAS_Embed.Base import EmbeddingModel, VectorStore
from chATLAS_Embed.custom_stop_words import get_physics_stopwords
from chATLAS_Embed.Document import Document, DocumentSource


class PostgresParentChildVectorStore(VectorStore):
    """PostgresSQL-based vector store with pgvector extension."""

    def __init__(
        self,
        connection_string: str,
        embedding_model: EmbeddingModel,
        _update_vector_size=False,
        dictionary_type="english",
        **kwargs,
    ):
        """
        PostgresSQL-based vector store initialisation.

        Once done with the vectorstore make sure to close it by `PostgresParentChildVectorStore.close()`,
        `del PostgresParentChildVectorStore` or wrapping the usage of the vectorstore in a `with`.

        :param str connection_string:  connection string to connect to the postgres database used.
            e.g. postgresql://{user}:{password}@dbod-chatlas.cern.ch:{port}/vTEST
        :param EmbeddingModel embedding_model: Embedding model used to generate vector store
            (and used to process queries to search the db)
        :param bool _update_vector_size: Debugging parameter for using embedding models with different vector sizes
            - **NOTE** if set to true and used with a different embeding model will drop previously made embeddings
        :param str dictionary_type: "english" | "simple" | "scientific" -> What postgres dictionary to use for the
            text search.
            - "simple": Doesn't remove or stem anything - better matches for specific terms, but about 2x runtime of
                        english
            - "english": Uses pg English dictionary stop words and stems.
            - "scientific": Custom dictionary that currently works the same as english, but has scope to be extended
                (ie with other languages)
        :param kwargs: Additional args:
            - [str] custom_stop_words: List of strings containing custom stop words for scientific documents
                to exclude
        """

        super().__init__()
        self.connection_string = connection_string
        self.embedding_model = embedding_model
        self._ensure_database_exists()
        self.engine = create_engine(self.connection_string)
        self.vector_length = embedding_model.vector_size
        self._update_vector_size = _update_vector_size
        self.dictionary_type = dictionary_type
        self.search_algorithm = None
        self.search_hyperparams = None
        self.kwargs = kwargs
        self.stop_words: list[str] = []
        self.explain_analyse = False
        self._init_db()

    def _extract_db_info(self):
        """Extract database name and connection info from connection string."""
        pattern = r"(?P<base>postgresql://[^/]+)/(?P<dbname>[^?]+)"
        match = re.match(pattern, self.connection_string)
        if not match:
            raise ValueError("Invalid connection string format")

        return {
            "base_connection": match.group("base"),
            "database_name": match.group("dbname"),
        }

    def _ensure_database_exists(self):
        """Create database if it doesn't exist."""
        db_info = self._extract_db_info()
        base_connection = db_info["base_connection"]
        database_name = db_info["database_name"]

        # Connect to default 'postgres' database to create new database
        default_connection = f"{base_connection}/postgres"
        temp_engine = create_engine(default_connection)

        try:
            with temp_engine.connect() as conn:
                # Start transaction
                with conn.begin():
                    # Check if database exists
                    result = conn.execute(
                        text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                        {"dbname": database_name},
                    ).scalar()

                    if not result:
                        # Terminate existing connections
                        conn.execute(
                            text(
                                """
                                SELECT pg_terminate_backend(pid)
                                FROM pg_stat_activity
                                WHERE datname = :dbname
                            """
                            ),
                            {"dbname": database_name},
                        )
                        # Create database
                        # Note: We need to commit the transaction before creating the database
                        conn.execute(text("COMMIT"))
                        conn.execute(text(f'CREATE DATABASE "{database_name}"'))

        except Exception as e:
            print(f"Failed to create database: {e!s}")
            raise
        finally:
            temp_engine.dispose()

    def set_search_hyperparams(self, search_hyperparams: str | None = None):
        """
        Set search hyperparameters based on existing indices in the database.
        Custom parameters can be provided via search_hyperparams.

        :param search_hyperparams: Custom search hyperparameters to use
        """
        with self.engine.connect() as conn:
            if search_hyperparams is None:
                indices = (
                    conn.execute(
                        text(
                            "SELECT indexname FROM pg_indexes "
                            "WHERE tablename = 'embeddings' and indexname <> 'embeddings_pkey'"
                        )
                    )
                    .scalars()
                    .all()
                )
                print(f"Checking database configuration - found indices {indices}")

                # IVFFlat
                if "embeddings_vector_idx" in indices:
                    # Estimate optimal number of probes based on the number of embeddings
                    # - Optimal number of lists is roughly sqrt of the number of embeddings with an extra bit added for RAG
                    # - Optimal number of probes is roughly 10% of the number of lists
                    # - For very large datasets, cap probes at a reasonable maximum
                    # NOTE: previously, unless documents were added, IVFFLAT.PROBES was set to 32, so we keep this as minimum
                    count = conn.execute(text("SELECT COUNT(*) FROM embeddings")).scalar()
                    optimal_lists = int(math.sqrt(count) + 0.05 * math.sqrt(count))
                    optimal_probes = max(32, int(optimal_lists * 0.14))
                    self.search_algorithm = "IVFFlat"
                    self.search_hyperparams = f"""
                        SET enable_seqscan = OFF;
                        SET enable_bitmapscan = ON;
                        SET ivfflat.probes = {optimal_probes};
                        SET plan_cache_mode = force_generic_plan;
                        """

                # HNSW
                elif "embeddings_vector_hnsw_idx" in indices:
                    self.search_algorithm = "HNSW"
                    self.search_hyperparams = """
                        SET enable_seqscan = OFF;
                        SET enable_bitmapscan = ON;
                        SET hnsw.ef_search = 100;
                        SET plan_cache_mode = force_generic_plan;
                        """

                # Exact search
                else:
                    self.search_algorithm = "exact"
                    self.search_hyperparams = """
                        SET enable_seqscan = ON;
                        SET enable_indexscan = OFF;
                        SET enable_bitmapscan = OFF;
                        SET plan_cache_mode = force_generic_plan;
                        """

            else:
                # Custom configuration
                self.search_hyperparams = search_hyperparams
                self.search_algorithm = "custom"

            print(f"Setting search algorithm to '{self.search_algorithm}' with parameters:{self.search_hyperparams}")
            conn.execute(text(self.search_hyperparams))

    def reindex_database(
        self, search_algorithm: str | None = None, hnsw_m: int = 16, hnsw_ef_construction: int = 64
    ) -> None:
        """
        Change database index to use a different search algorithm.
        WARNING: This will delete any existing vector store index and recreate it for the desired search algorithm.
        WARNING: Reindexing affects ALL users of the database and may be disruptive to currently running applications.

        :param search_algorithm: (str) - The search algorithm to use for indexing ("IVFFlat", "HNSW", or "exact").
            None means use the current search algorithm set in the vector store.
        """
        if search_algorithm is None:
            search_algorithm = self.search_algorithm
        if search_algorithm not in ["IVFFlat", "HNSW", "exact"]:
            raise ValueError(
                f"Unsupported search algorithm '{self.search_algorithm}'. Must be one of 'IVFFlat', 'HNSW', or 'exact'."
            )
        if (search_algorithm == self.search_algorithm) and (search_algorithm == "exact"):
            # For 'exact', nothing to do if search_algorithm isn't changing
            # For HNSW, m or ef_construction may be different, so we have to rebuild
            # For IVFFlat, number of documents may have changed, so we have to rebuild
            return

        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text("DROP INDEX IF EXISTS embeddings_vector_idx"))
                conn.execute(text("DROP INDEX IF EXISTS embeddings_vector_hnsw_idx"))

                if search_algorithm == "IVFFlat":
                    count = conn.execute(text("SELECT COUNT(*) FROM embeddings")).scalar()
                    optimal_lists = int(math.sqrt(count) + 0.05 * math.sqrt(count))
                    optimal_lists = min(max(optimal_lists, 4), 2000)
                    print(f"Recreating IVFFlat index with {optimal_lists} lists for {count} embeddings")
                    conn.execute(
                        text(
                            f"""
                            CREATE INDEX embeddings_vector_idx
                            ON embeddings
                            USING ivfflat (embedding vector_cosine_ops)
                            WITH (lists = {optimal_lists});
                        """
                        )
                    )

                elif search_algorithm == "HNSW":
                    print(f"Recreating HNSW index with m = {hnsw_m} and ef_construction = {hnsw_ef_construction}")
                    conn.execute(
                        text(
                            f"""
                            CREATE INDEX embeddings_vector_hnsw_idx
                            ON embeddings
                            USING hnsw (embedding vector_cosine_ops)
                            WITH (m = {hnsw_m}, ef_construction = {hnsw_ef_construction});
                        """
                        )
                    )

                elif search_algorithm == "exact":
                    # No index needed for exact search, so nothing to do here
                    pass

            conn.commit()

        self.set_search_hyperparams()

    def _init_text_parser(self, stop_words: list[str]):
        """
        Initialize or update the text cleaning function in PostgreSQL.
        Creates a function that removes URLs, file paths, IP addresses, and version numbers from text.

        :param stop_words: List of stop words to remove
        :type stop_words: List[str]
        :return:
        :rtype:
        """

        # Format stop words for PostgreSQL
        pg_stop_words = "'" + "', '".join(stop_words) + "'"

        query_text = f"""
        CREATE OR REPLACE FUNCTION clean_text_for_vector(
            input_text text,
            stop_words text[] DEFAULT ARRAY[{pg_stop_words}]  -- adjust custom stopwords as needed
        )
        RETURNS text AS $$
        DECLARE
            pattern text;
            cleaned_text text;
        BEGIN
            -- If there are any custom stop words provided, build a regex pattern to match them
            IF array_length(stop_words, 1) IS NOT NULL THEN
                pattern := '\m(' || array_to_string(
                    ARRAY(
                        SELECT regexp_replace(word, '([.^$*+?()\[\]\\|])', '\\\1', 'g')
                        FROM unnest(stop_words) AS word
                    ),
                    '|'
                ) || ')\M';
                cleaned_text := regexp_replace(input_text, pattern, ' ', 'gi');
            ELSE
                cleaned_text := input_text;
            END IF;

            -- Remove URLs
            cleaned_text := regexp_replace(cleaned_text, 'https?://[^\s]+', '', 'g');
            -- Remove IP addresses
            cleaned_text := regexp_replace(cleaned_text, '\d{1, 3}\.\d{1, 3}\.\d{1, 3}\.\d{1, 3}', '', 'g');
            -- Replace underscores and hyphens with space
            cleaned_text := regexp_replace(cleaned_text, '[_-]', ' ', 'g');
            -- Replace punctuation with space
            cleaned_text := regexp_replace(cleaned_text, '[[:punct:]]', ' ', 'g');

            RETURN cleaned_text;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        """

        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Create or replace the function
                    conn.execute(text(query_text))

        except SQLAlchemyError as e:
            print(f"Failed to create/update clean_text_for_vector function: {e!s}")
            raise

    def _init_scientific_dictionary(self):
        """
        Sets up the scientific dictionary for text parsing use. The scientific dictionary:

        1. Removes English Stop words
        2. Stems recognised English words
        3. Leaves all other words unchanged

        The text is then always parsed with  clean_text_for_vector which removes the custom list of HEP stopwords

        :return:
        :rtype:
        """
        scientific_dict_creation_text = """
        DROP TEXT SEARCH CONFIGURATION IF EXISTS public.scientific CASCADE;
        DROP TEXT SEARCH DICTIONARY IF EXISTS public.scientific_stem CASCADE;
        DROP TEXT SEARCH DICTIONARY IF EXISTS public.scientific_english_stop CASCADE;

        -- Create dictionary for English stop words and stemming
        CREATE TEXT SEARCH DICTIONARY public.scientific_english_stop (
            TEMPLATE = pg_catalog.snowball,
            LANGUAGE = english,
            STOPWORDS = english
        );

        -- Create the stemming dictionary
        CREATE TEXT SEARCH DICTIONARY public.scientific_stem (
            TEMPLATE = pg_catalog.snowball,
            LANGUAGE = english
        );

        -- Create the configuration
        CREATE TEXT SEARCH CONFIGURATION public.scientific (
            COPY = pg_catalog.english
        );

        ALTER TEXT SEARCH CONFIGURATION public.scientific
            ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
            WITH scientific_english_stop, scientific_stem;
            """
        # Execute the SQL
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(scientific_dict_creation_text))

    def get_current_stop_words(self):
        """
        Returns current stop words used for processing the DB.

        **NOTE**: This nay not be right if a separate instance of this class
        connected to the same DB and they have altered the stop words list independently.

        :return: stop words
        :rtype: List[str]
        """
        # NOTE:
        # We could store what stop words are currently being used in a table in the SQL and query it to get the proper
        # up-to-date version of this across users, however don't really want to update stop words regularly anyway
        # as it hsa a very large time penalty. Best to just leave this alone!

        return self.stop_words

    def update_current_stop_words(self, stop_words: list[str]):
        """
        Updates the current stored list of stop words with a new list.

        **NOTE**: This will update the text search vector for all users on this DB! Only do this on non prod DBs!
        It also has a very high time cost for the operation needing to update all parent document rows with regex!

        :return: number of rows updated
        :rtype: int
        """
        self._init_text_parser(stop_words)
        num = self.update_text_search_vector()
        return num

    @property
    def document_count(self) -> int:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM documents"))
            return result.scalar()

    def create_stats(self):
        with self.engine.connect() as conn:
            with conn.begin():
                # Create stats table
                conn.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS db_stats (
                            last_modified TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                            total_documents BIGINT DEFAULT 0,
                            total_embeddings BIGINT DEFAULT 0,
                            vector_dimension INTEGER,
                            unique_document_names INTEGER DEFAULT 0,
                            index_lists INTEGER DEFAULT 0,
                            index_probes INTEGER DEFAULT 0,
                            total_disk_size_bytes BIGINT DEFAULT 0,
                            index_disk_size_bytes BIGINT DEFAULT 0,
                            cache_hit_ratio FLOAT DEFAULT 0
                        )
                        """
                    )
                )

                # Create trigger function to update last_modified
                conn.execute(
                    text(
                        """
                        CREATE OR REPLACE FUNCTION update_db_stats_timestamp()
                        RETURNS TRIGGER AS $$
                        BEGIN
                            UPDATE db_stats SET last_modified = CURRENT_TIMESTAMP;
                            RETURN NEW;
                        END;
                        $$ LANGUAGE plpgsql;
                        """
                    )
                )

                # Create triggers for documents and embeddings tables
                conn.execute(
                    text(
                        """
                        DROP TRIGGER IF EXISTS update_stats_embeddings ON embeddings;
                        CREATE TRIGGER update_stats_embeddings
                        AFTER INSERT ON embeddings
                        FOR EACH STATEMENT
                        EXECUTE FUNCTION update_db_stats_timestamp();
                        """
                    )
                )

                # Initialize stats if empty
                conn.execute(
                    text(
                        """
                        INSERT INTO db_stats (vector_dimension)
                        SELECT :vector_size
                        WHERE NOT EXISTS (SELECT 1 FROM db_stats);
                        """
                    ),
                    {"vector_size": self.vector_length},
                )

                conn.commit()

    def _init_db(self):
        """Initialize database schema and extensions."""
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Create vector extension
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

                    saved_hep_stop_words = get_physics_stopwords()

                    # Initialize scientific dictionary
                    self._init_scientific_dictionary()

                    # Initialize text parser
                    self._init_text_parser(saved_hep_stop_words)

                    # Create base documents table
                    conn.execute(
                        text(
                            """
                        CREATE TABLE IF NOT EXISTS documents (
                            id TEXT PRIMARY KEY,
                            page_content TEXT,
                            metadata JSONB,
                            parent_id TEXT
                        )
                    """
                        )
                    )

                    # Add text_search_vector column
                    conn.execute(
                        text(
                            """
                        ALTER TABLE documents
                        ADD COLUMN IF NOT EXISTS text_search_vector tsvector
                    """
                        )
                    )

                    # Now create the GIN index
                    conn.execute(
                        text(
                            """
                        CREATE INDEX IF NOT EXISTS documents_text_search_idx
                        ON documents USING gin(text_search_vector)
                    """
                        )
                    )

                    result = conn.execute(
                        text("""
                            SELECT COUNT(*) FROM documents 
                            WHERE parent_id IS NULL AND text_search_vector IS NULL
                        """)
                    ).scalar()

                    if result > 0:
                        # Update existing vectors
                        conn.execute(
                            text(
                                f"""
                                UPDATE documents
                                SET text_search_vector =
                                    setweight(
                                        to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(page_content, ''))),
                                        'A'
                                    ) ||
                                    setweight(
                                        to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(metadata->>'topic_parent', ''))),
                                        'C'
                                    ) ||
                                    setweight(
                                        to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(metadata->>'name', ''))),
                                        'B'
                                    )
                                WHERE parent_id IS NULL
                                AND text_search_vector IS NULL
                        """
                            )
                        )

                # Check if the embeddings table exists
                result = conn.execute(
                    text(
                        """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'embeddings'
                    )
                """
                    )
                )
                table_exists = result.scalar()

                if table_exists:
                    # Check the existing dimension of the embeddings column
                    conn.execute(
                        text(
                            """
                            ALTER TABLE embeddings
                            DROP CONSTRAINT IF EXISTS embeddings_document_id_fkey
                            """
                        )
                    )

                    # Add the new constraint with CASCADE
                    conn.execute(
                        text(
                            """
                            ALTER TABLE embeddings
                            ADD CONSTRAINT embeddings_document_id_fkey
                            FOREIGN KEY (document_id)
                            REFERENCES documents(id)
                            ON DELETE CASCADE
                            """
                        )
                    )
                    result = conn.execute(
                        text(
                            """
                        SELECT pg_catalog.format_type(a.atttypid, a.atttypmod) AS type
                        FROM pg_catalog.pg_attribute a
                        WHERE a.attname = 'embedding' AND a.attrelid = (
                            SELECT c.oid FROM pg_catalog.pg_class c
                            WHERE c.relname = 'embeddings' AND c.relkind = 'r'
                        )
                    """
                        )
                    )
                    row = result.fetchone()

                    if row:
                        current_vector_type = row[0]  # Format: "vector(384)"
                        current_dimension = int(current_vector_type.split("(")[1].rstrip(")"))

                        # If dimensions differ, update the table schema
                        if current_dimension == self.vector_length:
                            pass
                        elif current_dimension != self.vector_length and self._update_vector_size:
                            conn.execute(text("ALTER TABLE embeddings DROP COLUMN IF EXISTS embedding"))
                            conn.execute(
                                text(f"ALTER TABLE embeddings ADD COLUMN embedding vector({self.vector_length})")
                            )
                        else:
                            raise ValueError(
                                """
                            The embedding model output vector size used does not match the one used to create the db.
                             Set `_update_vector_size` to True if trying to update the vectors in the database"""
                            )
                    else:
                        # If the embedding column doesn't exist, create it
                        conn.execute(text(f"ALTER TABLE embeddings ADD COLUMN embedding vector({self.vector_length})"))
                else:
                    # Create the embeddings table if it doesn't exist
                    conn.execute(
                        text(
                            f"""
                            CREATE TABLE embeddings (
                                id TEXT PRIMARY KEY,
                                document_id TEXT REFERENCES documents(id) ON DELETE CASCADE,
                                embedding vector({self.vector_length})
                            )
                        """
                        )
                    )

                    # Create index for default IVFFlat search algorithm
                    conn.execute(
                        text(
                            """
                        CREATE INDEX IF NOT EXISTS embeddings_vector_idx
                        ON embeddings
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 250)
                    """
                        )
                    )
                    # Set ivfflat probes
                    conn.execute(text("SET ivfflat.probes = 32"))

                conn.commit()

            self.create_stats()

        except Exception as e:
            print(f"Failed to initialize database schema: {e!s}")
            raise

        # Set appropriate search hyperparameters
        self.set_search_hyperparams()

    def close(self):
        """Explicitly close and dispose of database connections"""
        if hasattr(self, "engine"):
            self.engine.dispose()

    def __del__(self):
        """Ensure connections are closed when object is deleted"""
        pass
        # self.close()

    def __enter__(self):
        """Support context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close connections when exiting context"""
        self.close()

    ############################################################
    # NOTE FROM BEN E:
    # This function could be sped up with better SQL operations
    # this would definitely be nice, however only needs to be
    # run once when initialy setting up the db then
    # only runs on updated documents which there are never too
    # many of so not a huge concern.
    # (Definitely would be nice if we have good SQL enginners to improve this)
    ############################################################

    def add_documents(self, parent_docs: list[Document], child_docs: list[Document]) -> None:
        """
        Add parent documents and child documents to the database.

        :param List[Document] parent_docs: Parent documents to add ot the db
        :param List[Document] child_docs: Child documents to embed and add to db
        """
        with self.engine.connect() as conn:
            with conn.begin():
                # Insert parent documents
                for parent_doc in tqdm(parent_docs, "Adding Parent Documents"):
                    conn.execute(
                        text(
                            """
                            INSERT INTO documents (id, page_content, metadata, parent_id)
                            VALUES (:id, :page_content, :metadata, NULL)
                            ON CONFLICT (id) DO NOTHING
                        """
                        ),
                        {
                            "id": parent_doc.id,
                            "page_content": parent_doc.page_content,
                            "metadata": parent_doc.to_json(),
                        },
                    )

                # Insert child documents and embeddings
                for child_doc in tqdm(child_docs, "Adding Child Documents"):
                    conn.execute(
                        text(
                            """
                            INSERT INTO documents (id, page_content, metadata, parent_id)
                            VALUES (:id, :page_content, :metadata, :parent_id)
                            ON CONFLICT (id) DO NOTHING
                        """
                        ),
                        {
                            "id": child_doc.id,
                            "page_content": child_doc.page_content,
                            "metadata": child_doc.to_json(),
                            "parent_id": child_doc.parent_id,
                        },
                    )

        # Prepare all child document contents for embedding
        documents_to_embed = [(doc.id, doc.page_content) for doc in child_docs]

        # Generate embeddings in batches
        embeddings = self.embedding_model.embed(
            [doc_content for _, doc_content in documents_to_embed],
            show_progress_bar=True,
        )
        print("Adding documents to db...")
        t0 = time.time()
        # Insert embeddings into the database
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        """
                        INSERT INTO embeddings (id, document_id, embedding)
                        VALUES (:id, :doc_id, :embedding)
                        ON CONFLICT (id) DO UPDATE
                        SET embedding = EXCLUDED.embedding
                    """
                    ),
                    [
                        {"id": doc_id, "doc_id": doc_id, "embedding": embedding}
                        for (doc_id, _), embedding in zip(documents_to_embed, embeddings, strict=False)
                    ],
                )
        print(f"Total time adding embeddings to db: {time.time() - t0:.4f}s")

        print("Expanding metadata into distinct columns")
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        """
                      BEGIN;

                    -- First, drop the existing columns and their indexes
                    DROP INDEX IF EXISTS idx_documents_category;
                    DROP INDEX IF EXISTS idx_documents_doc_type;
                    DROP INDEX IF EXISTS idx_documents_last_modified;

                    ALTER TABLE documents DROP COLUMN IF EXISTS category;
                    ALTER TABLE documents DROP COLUMN IF EXISTS doc_type;
                    ALTER TABLE documents DROP COLUMN IF EXISTS last_modified;

                    -- Add the new columns with appropriate data types
                    ALTER TABLE documents ADD COLUMN category text[];
                    ALTER TABLE documents ADD COLUMN doc_type character varying(50);
                    ALTER TABLE documents ADD COLUMN last_modified date;

                    -- Create appropriate indexes
                    CREATE INDEX idx_documents_category_gin ON documents USING GIN (category);
                    CREATE INDEX idx_documents_doc_type ON documents (doc_type);
                    CREATE INDEX idx_documents_last_modified ON documents (last_modified);

                    -- Migrate data from JSONB to new columns

                    -- Update category column
                    UPDATE documents
                    SET category = CASE
                        WHEN metadata->'category' IS NULL THEN
                            NULL
                        WHEN jsonb_typeof(metadata->'category') = 'array' THEN
                            -- Handle array case
                            (SELECT array_agg(elem::text)
                             FROM jsonb_array_elements_text(metadata->'category') elem)
                        WHEN jsonb_typeof(metadata->'category') = 'string' THEN
                            -- Handle single value case
                            ARRAY[metadata->>'category']
                        WHEN jsonb_typeof(metadata->'category') = 'null' THEN
                            NULL
                        ELSE
                            -- Handle other cases (e.g., numbers, booleans) by converting to text
                            ARRAY[metadata->>'category']
                        END
                    WHERE metadata ? 'category';

                    -- Update doc_type column
                    UPDATE documents
                    SET doc_type = CASE
                        WHEN jsonb_typeof(metadata->'type') = 'string' THEN
                            metadata->>'type'
                        ELSE
                            NULL
                        END
                    WHERE metadata ? 'type';

                    -- Update last_modified column
                    UPDATE documents
                    SET last_modified = CASE
                        WHEN jsonb_typeof(metadata->'last_modification') = 'string' THEN
                            CASE
                                -- Try parsing with explicit format DD-MM-YYYY
                                WHEN metadata->>'last_modification' ~ '^\d{2}-\d{2}-\d{4}$' THEN
                                    TO_DATE(metadata->>'last_modification', 'DD-MM-YYYY')
                                -- Try ISO format YYYY-MM-DD
                                WHEN metadata->>'last_modification' ~ '^\d{4}-\d{2}-\d{2}$' THEN
                                    TO_DATE(metadata->>'last_modification', 'YYYY-MM-DD')
                                -- Other formats could be added here
                                ELSE
                                    NULL
                            END
                        ELSE
                            NULL
                        END
                    WHERE metadata ? 'last_modification';


                    COMMIT;
                    """
                    )
                )

        self.reindex_database()

        self.update_text_search_vector()

    def delete(self, document_ids: list[str] | None = None, document_name: str | None = None, verbose=False) -> None:
        """
        Delete items from the DB. Either by thier ID or by their name (not
        both at the same time)

        **NOTE** can currently only delete one document by name at a time, no options to delete before a certain date etc. There are all WIPs!

        :param verbose: Print how many documents were deleted
        :type verbose: bool
        :param document_ids: (List[str]) - list of document ids to delete
        :param document_name: (str) - Document name to delete
        """
        if document_ids is None and document_name is None:
            raise ValueError("You must provide either document_ids or document_name to delete.")

        with self.engine.connect() as conn:
            with conn.begin():
                if document_name:
                    # Find all parent and child document IDs with the specified name in metadata
                    document_ids = (
                        conn.execute(
                            text(
                                """
                            SELECT id FROM documents
                            WHERE metadata::jsonb->>'name' = :doc_name
                        """
                            ),
                            {"doc_name": document_name},
                        )
                        .scalars()
                        .all()
                    )

                if not document_ids:
                    print("No documents found for the given criteria.")
                    return

                # Delete embeddings and documents
                conn.execute(
                    text(
                        """
                        DELETE FROM documents WHERE id = ANY(:doc_ids) OR parent_id = ANY(:doc_ids);
                    """
                    ),
                    {"doc_ids": document_ids},
                )
                if verbose:
                    print(f"Deleted {len(document_ids)} documents and their embeddings.")

    def drop_database(self) -> None:
        """
        WARNING: USE WITH CARE - WILL DELETE EVERYTHING
        **CURRENTLY BROKEN**
        (in this db name e.g. vectordb hopefully not the entirety of the server)
        Drop the entire database and its contents. Useful for testing with a new embedding model or splitter.
        """
        db_info = self._extract_db_info()
        base_connection = db_info["base_connection"]
        database_name = db_info["database_name"]

        # Connect to the default 'postgres' database
        default_connection = f"{base_connection}/postgres"
        temp_engine = create_engine(default_connection)

        try:
            with temp_engine.connect() as conn:
                # Terminate all connections to the database
                with conn.begin():
                    conn.execute(
                        text(
                            """
                            SELECT pg_terminate_backend(pid)
                            FROM pg_stat_activity
                            WHERE datname = :dbname;
                        """
                        ),
                        {"dbname": database_name},
                    )

                    # Drop the database
                    conn.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))

            print(f"Database '{database_name}' has been successfully dropped.")

        except Exception as e:
            raise Exception(f"Failed to drop database: {e!s}")

        finally:
            temp_engine.dispose()

    def clear_database(self) -> None:
        """
        WARNING: USE WITH CARE - WILL CLEAR ALL TABLE CONTENTS
        Empties all tables in the database while preserving the database structure.
        """
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                tables = inspector.get_table_names()

                with conn.begin():
                    for table in tables:
                        conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))

                print("All tables have been cleared successfully.")
        except Exception as e:
            raise Exception(f"Failed to clear the database: {e!s}")

    def update_text_search_vector(self) -> int:
        """
        Updates all text search vectors in the documents table using the current scientific dictionary configuration.
        This is useful after modifying the dictionary settings or stop words.

        :return: Number of rows updated
        :rtype: int
        """
        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(
                    text(
                        f"""
                        UPDATE documents
                        SET text_search_vector =
                            CASE
                                WHEN parent_id IS NULL THEN
                                    setweight(to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(page_content, ''))), 'A') ||
                                    setweight(to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(metadata->>'topic_parent', ''))), 'C') ||
                                    setweight(to_tsvector('{self.dictionary_type}',
                                        clean_text_for_vector(COALESCE(metadata->>'name', ''))), 'B')
                                ELSE NULL
                            END
                        WHERE parent_id IS NULL;  -- Only update root documents
                        """
                    )
                )
                return int(result.rowcount)

    def get_db_stats(self) -> dict:
        """
        Retrieve current database statistics.

        :return: Dictionary containing database statistics
        :rtype: dict
        """
        with self.engine.connect() as conn:
            with conn.begin():
                # Update statistics
                conn.execute(
                    text(
                        """
                        UPDATE db_stats SET
                            total_documents = (SELECT COUNT(*) FROM documents),
                            total_embeddings = (SELECT COUNT(*) FROM embeddings),
                            unique_document_names = (
                                SELECT COUNT(DISTINCT metadata->>'name')
                                FROM documents
                                WHERE metadata->>'name' IS NOT NULL
                            ),
                            total_disk_size_bytes = (
                                SELECT pg_total_relation_size('documents') +
                                       pg_total_relation_size('embeddings')
                            ),
                            index_disk_size_bytes = (
                                SELECT pg_relation_size('embeddings_vector_idx')
                            ),
                            cache_hit_ratio = (
                                SELECT
                                    CASE WHEN blks_hit + blks_read = 0 THEN 0
                                    ELSE ROUND(100.0 * blks_hit / (blks_hit + blks_read), 2)
                                    END
                                FROM pg_stat_database
                                WHERE datname = current_database()
                            ),
                            index_lists = (
                                SELECT reloptions[array_position(reloptions, 'lists='::text) + 1]::integer
                                FROM pg_class
                                WHERE relname = 'embeddings_vector_idx'
                                AND reloptions IS NOT NULL
                            ),
                            index_probes = (
                                SELECT setting::integer
                                FROM pg_settings
                                WHERE name = 'ivfflat.probes'
                            )
                        """
                    )
                )

                # Retrieve stats
                result = conn.execute(
                    text(
                        """
                        SELECT
                            last_modified AT TIME ZONE 'UTC' as last_modified,
                            total_documents,
                            total_embeddings,
                            vector_dimension,
                            unique_document_names,
                            index_lists,
                            index_probes,
                            total_disk_size_bytes,
                            index_disk_size_bytes,
                            cache_hit_ratio
                        FROM db_stats;
                        """
                    )
                ).fetchone()

                stats = {
                    "last_modified": result.last_modified.isoformat(),
                    "total_documents": result.total_documents,
                    "total_embeddings": result.total_embeddings,
                    "vector_dimension": result.vector_dimension,
                    "unique_document_names": result.unique_document_names,
                    "index_lists": result.index_lists,
                    "index_probes": result.index_probes,
                    "total_disk_size_mb": round(result.total_disk_size_bytes / (1024 * 1024), 2),
                    "index_disk_size_mb": round(result.index_disk_size_bytes / (1024 * 1024), 2),
                    "cache_hit_ratio": result.cache_hit_ratio,
                }

                return stats

    def test_connection(self):
        """Test the connection to the PostgreSQL database.

        Returns:
            True if connection succeeded
            False if connection failed
        """
        try:
            with create_engine(self.connection_string).connect() as conn:
                # Execute a simple query to check the connection
                result = conn.execute(text("SELECT 1")).scalar()
                if result == 1:
                    return True  # Connection is good
                return False  # Connection failed unexpectedly
        except Exception as e:
            # Log the error or raise it if necessary
            print(f"Connection test failed: {e!s}")
            return False

    def get_categories(self):
        """
        Gets the known categories and other data for the current db.
        Returns unique values for doc_type, category (flattened from array), and last_modified.

        :return: Dictionary containing unique values for each column
        :rtype: dict[str, list]
        """
        with self.engine.connect() as conn:
            # Query for unique doc_types (excluding nulls)
            doc_types = (
                conn.execute(
                    text(
                        """
                    SELECT DISTINCT doc_type
                    FROM documents
                    WHERE doc_type IS NOT NULL
                    ORDER BY doc_type;
                """
                    )
                )
                .scalars()
                .all()
            )

            # Query for unique categories (unnesting array values)
            categories = (
                conn.execute(
                    text(
                        """
                    SELECT DISTINCT unnest(category)
                    FROM documents
                    WHERE category IS NOT NULL
                    ORDER BY unnest(category);
                """
                    )
                )
                .scalars()
                .all()
            )

            # Query for unique last_modified dates
            dates = (
                conn.execute(
                    text(
                        """
                    SELECT DISTINCT last_modified
                    FROM documents
                    WHERE last_modified IS NOT NULL
                    ORDER BY last_modified DESC;
                """
                    )
                )
                .scalars()
                .all()
            )

            return {
                "doc_types": doc_types,
                "categories": categories,
                "dates": [d.strftime("%d-%m-%Y") if d else None for d in dates],
            }

    def get_embeddings(self, num_embeddings: int = 100) -> list[list[float]]:
        """
        Gets random embeddings from the database. (For plotting, visualisations etc.)

        :param num_embeddings: Number of embeddings to retrieve
        :type num_embeddings: int
        :return: List of embeddings as lists of floats
        :rtype: List[List[float]]
        """
        with self.engine.connect() as conn:
            # Query for random embeddings
            result = conn.execute(
                text(
                    """
                    SELECT embedding
                    FROM embeddings
                    ORDER BY RANDOM()
                    LIMIT :limit;
                """
                ),
                {"limit": num_embeddings},
            )

            # Convert results directly to list of float arrays
            embeddings = [list(row[0]) for row in result]

            return embeddings

    def _generate_metadata_filters(self, metadata_filters, date_filter):
        # Build metadata filter conditions - vector search
        metadata_filter_conditions = []
        filter_params = {}

        if metadata_filters:
            for idx, (key, value) in enumerate(metadata_filters.items()):
                param_key = f"key_{idx}"
                param_value = f"value_{idx}"

                # Check for fields that have been expanded to dedicated columns
                if key == "last_modification":
                    # Use the dedicated last_modified column
                    metadata_filter_conditions.append(f"d.last_modified = TO_DATE(:value_{idx}, 'DD-MM-YYYY')")
                elif key == "type":
                    # Use the dedicated doc_type column
                    if isinstance(value, list):
                        # For multiple values, use IN operator
                        metadata_filter_conditions.append(f"d.doc_type = ANY(:value_{idx})")
                    else:
                        # For single value
                        metadata_filter_conditions.append(f"d.doc_type = :value_{idx}")
                elif key == "category":
                    # Use the dedicated category array column
                    if isinstance(value, list):
                        # When value is a list, check for overlap with the category array
                        metadata_filter_conditions.append(f"d.category && :value_{idx}")
                    else:
                        # For single value, check if it exists in the category array
                        metadata_filter_conditions.append(f":value_{idx} = ANY(d.category)")
                # For other fields that still reside in the metadata JSONB column
                elif isinstance(value, list):
                    metadata_filter_conditions.append(f"CAST(d.metadata::jsonb->:key_{idx} AS jsonb) ?| :value_{idx}")
                else:
                    metadata_filter_conditions.append(f"d.metadata->>:key_{idx} = :value_{idx}")

                filter_params[param_key] = key
                filter_params[param_value] = value  # Don't convert to string for array values

        # Add date filter condition (using dedicated column instead of JSONB)
        if date_filter:
            metadata_filter_conditions.append("d.last_modified > TO_DATE(:date_filter, 'DD-MM-YYYY')")
            filter_params["date_filter"] = date_filter

        # Combine filter conditions
        metadata_filter_clause = " AND ".join(metadata_filter_conditions)
        where_clause = f"WHERE {metadata_filter_clause}" if metadata_filter_conditions else ""

        # Generate metadata filters text search

        return where_clause, filter_params

    def search(
        self,
        query: str,
        k: int = 4,
        k_text: int = 0,
        metadata_filters: dict | None = None,
        date_filter: str | None = None,
        with_timings: bool = False,
    ) -> list[tuple[Document, Document, float]]:
        """
        A hybrid retrieval function that performs both semantic search using vector embeddings and
        lexical search using PostgreSQL's full-text search capabilities, but executed separately.

        The (similarity) score can be found in the third item of every tuple in the list.
        How the document was returned can be found in parent_doc.metadata["search_type"] = "vector" or "text"

        :param query: Query text to search for
        :type query: str
        :param k: Maximum number of results to return from vector-based semantic search
        :type k: int
        :param k_text: Maximum number of results to return from text-based lexical search
        :type k_text: int
        :param metadata_filters: Filters to apply on document metadata. Keys are metadata fields,
                                values can be strings (exact match) or lists (any match)
        :type metadata_filters: dict[str, str | list]
        :param date_filter: Date string in 'dd-mm-YYYY' format. Only returns documents modified
                           after this date (e.g. "01-03-2001")
        :type date_filter: str

        :returns: List of tuples containing (child_doc, parent_doc, similarity_score)
        :rtype: List[Tuple[Document, Document, float]]

        The function implements a hybrid retrieval approach combining:

        1. Semantic Search:
           - Uses cosine similarity between query and document embeddings
           - Returns documents most similar in meaning/context
           - Scores range from 0 to 1, where 1 indicates highest similarity

        2. Lexical Search:
           - Uses PostgreSQL's tsvector/tsquery for text matching
           - Implements weighted document ranking:
              * Document names (weight A - highest)
              * Document topics and content (weight B - medium)
           - Normalizes scores to 0-1 range

        Result Processing:
        - Both searches initially fetch k+10 results to account for:
          * Filtered results that don't meet metadata criteria
          * Duplicate removals when combining vector and text results
        - Final results are deduplicated and limited to k + k_text total documents
        - Each result includes a search_type in parent_doc.metadata indicating
          whether it was found via "vector" or "text" search

        Text Search Implementation:
        - Uses ts_rank_cd for ranking, considering term proximity and density
        - Query processing via plainto_tsquery:
          * Converts text to lowercase
          * Removes punctuation and stop words
          * Performs word stemming
          * Combines terms with AND operators
        - Scoring considers:
          * Number of matching terms
          * Term proximity
          * Term frequency
          * Document structure weights

        Notes:
        - Metadata filters are applied to both the child documents as well as the parent documents
        - The similarity scores from embedding and text searches are not directly comparable
        as they use different scoring mechanisms, though both are normalized to the
        0-1 range.
        - Results from vector search can contain duplicates if multiple child documents link to the same parent.
        - Text search is done on the parent documents, so the child doc part of the tuple will be empty.
        - The combined results can have further duplicates if both text and vector searches return the same parent document.
          - No deduplication done here, allowing use of the information from duplicates for e.g. reranking
        """
        if with_timings:
            pre_processing_t0 = time.perf_counter()

        # Input validation
        if not query or not query.strip():
            print("Empty query returning no results")
            return []

        # Checking k values are ints
        try:
            k = int(k)
            k_text = int(k_text)
        except ValueError:
            print("Please give k values as ether ints or int parse-able strings")
            raise

        # Making sure we don't have k in metadata filters
        if metadata_filters:
            metadata_filters = metadata_filters.copy()  # Create a copy to avoid modifying original
            k = metadata_filters.pop("k", k)
            k_text = metadata_filters.pop("k_text", k_text)

        where_clause, filter_params = self._generate_metadata_filters(metadata_filters, date_filter)

        vector_results = []
        text_results = []

        if with_timings:
            pre_processing_t1 = time.perf_counter()
            print(f"TIME TAKEN FOR PREPROCESSING: {pre_processing_t1 - pre_processing_t0}")

        if k > 0:
            # 1. Perform Vector Search
            if with_timings:
                vector_t0 = time.perf_counter()
            vector_results = self._vector_search(query, k, where_clause, filter_params)
            if with_timings:
                vector_t1 = time.perf_counter()
                print(f"TIME TAKEN FOR VECTOR SEARCH: {vector_t1 - vector_t0}")

        if k_text > 0:
            # 2. Perform Text Search
            if with_timings:
                text_t0 = time.perf_counter()

            text_results = self._text_search(query, k_text, filter_params, where_clause)
            if with_timings:
                text_t1 = time.perf_counter()
                print(f"TIME TAKEN FOR TEXT SEARCH: {text_t1 - text_t0}")

        # No results at all
        if not vector_results and not text_results:
            return []

        # **NOTE**: The vector_results can have duplicates if two child docs have the same parent
        # combined_results can have further duplicates if the text search returned the same parent doc as vector search
        # here we return everything for maximum flexibility
        combined_results = vector_results + text_results

        # sort by similarity score, largest first
        combined_results.sort(key=lambda x: x[2], reverse=True)

        return combined_results

    @staticmethod
    def extract_quotes(query):
        """
        Extract text within quotation marks from a query string.
        If no quotes are found, return the original query.

        :param query: Input query string
        :return: Either the text within quotes or original query
        """
        # Find all matches of text within quotation marks
        matches = re.findall(r'"([^"]*)"', query)

        # If matches found, join them with spaces
        if matches:
            return " ".join(matches)

        # Return original query if no matches
        return query

    def _vector_search(
        self,
        query,
        k: int,
        where_clause: str,
        filter_params: dict,
    ) -> list[tuple[Document, Document, float]]:
        """
        Execute vector-based semantic search.

        Returns a list of (child doc, parent doc, similarity score) tuples.
        """

        # Extract quotation marks from query for text part to not confuse embedding model
        query = query.replace('"', "")

        # Generate embedding for vector search
        query_embedding = self.embedding_model.embed(query)

        # Ensure query embedding is 1D List
        if len(query_embedding) == 1:
            print("WARNING: Embedding model not returning flat list - performing automatic flattening")
            query_embedding = query_embedding[0]
        elif len(query_embedding) != self.vector_length:
            print(
                f"ERROR: Wrong Embedding Model vector size for this database. EXPECTED: {len(query_embedding)} - GOT: {self.vector_length}"
            )

        vector_query = f"""
                WITH filtered_docs AS (
                    SELECT
                        d.id,
                        d.parent_id
                    FROM
                        documents d
                    {where_clause}
                ),
                vector_results AS (
                    SELECT
                        e.document_id,
                        fd.parent_id,
                        1 - (e.embedding <=> CAST(:query_embedding AS vector)) AS score
                    FROM
                        embeddings e
                    JOIN
                        filtered_docs fd ON e.document_id = fd.id
                    ORDER BY
                        e.embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :k_vector
                ),
                best_vector_results AS (
                    SELECT DISTINCT ON (parent_id)
                        document_id,
                        parent_id,
                        score
                    FROM vector_results
                    ORDER BY parent_id, score DESC
                )
                SELECT
                    d_child.id AS child_id,
                    d_child.page_content AS child_content,
                    d_child.metadata AS child_metadata,
                    d_child.parent_id,
                    d_parent.id AS parent_id,
                    d_parent.page_content AS parent_content,
                    d_parent.metadata AS parent_metadata,
                    bvr.score
                FROM best_vector_results bvr
                JOIN documents d_parent ON bvr.parent_id = d_parent.id
                JOIN documents d_child ON bvr.document_id = d_child.id
                ORDER BY bvr.score DESC;
                """

        with self.engine.connect() as conn:
            conn.execute(text(self.search_hyperparams))

            if self.explain_analyse:
                results = conn.execute(
                    text("EXPLAIN (ANALYSE, BUFFERS)" + vector_query),
                    {
                        "query_embedding": query_embedding,
                        "k_vector": k + 10 if filter_params else k,
                        **filter_params,
                    },
                )
                for row in results:
                    print(row)

            results = conn.execute(
                text(vector_query),
                {
                    "query_embedding": query_embedding,
                    "k_vector": k + 10 if filter_params else k,
                    **filter_params,
                },
            )

            vector_results = []
            for i, row in enumerate(results):
                if i >= k:
                    break
                child_metadata = row.child_metadata
                child_doc = Document(
                    id=row.child_id,
                    page_content=row.child_content,
                    source=DocumentSource(child_metadata.pop("type")),
                    name=child_metadata.pop("name"),
                    url=child_metadata.pop("url"),
                    metadata=child_metadata,
                    parent_id=row.parent_id,
                )

                parent_metadata = row.parent_metadata.copy()
                parent_metadata["search_type"] = "vector"

                parent_doc = Document(
                    id=row.parent_id,
                    page_content=row.parent_content,
                    source=DocumentSource(parent_metadata.pop("type")),
                    name=parent_metadata.pop("name"),
                    url=parent_metadata.pop("url"),
                    metadata=parent_metadata,
                    parent_id=None,
                )

                vector_results.append((child_doc, parent_doc, float(row.score)))

            return vector_results

    def _text_search(
        self,
        query: str,
        k_text: int,
        filter_params: dict,
        where_clause: str,
    ) -> list[tuple[Document, Document, float]]:
        """
        Execute text-based lexical search.

        Returns a list of (child doc, parent doc, similarity score) tuples.

        **NOTE** Text search done on parent documents, so returns empty child documents!
        """
        # Extract quotated variables from input string

        # Get quotation marks from query for text search input
        query = self.extract_quotes(query)

        # Remove any trailing quotation marks
        query = query.replace('"', "")

        # Process query for text search
        processed_query = self._clean_query_for_tsquery(query)
        if not processed_query:
            processed_query = "dummy_term_that_wont_match"

        where_parent = re.sub(r"\bd\.", "d_parent.", where_clause)

        text_query = f"""
        WITH ranked_results AS (
            SELECT
                id AS parent_id,
                ts_rank_cd(
                    text_search_vector,
                    to_tsquery('{self.dictionary_type}', :text_query),
                    32
                ) AS raw_score
            FROM documents
            WHERE text_search_vector @@ to_tsquery('{self.dictionary_type}', :text_query)
            ORDER BY raw_score DESC
            LIMIT :k_text  -- Reduce number of rows early
        ),
        normalized_results AS (
            SELECT
                parent_id,
                raw_score / (SELECT MAX(raw_score) FROM ranked_results) AS score
            FROM ranked_results
        )
        SELECT
            d_parent.id AS parent_id,
            d_parent.page_content AS parent_content,
            d_parent.metadata AS parent_metadata,
            nr.score
        FROM normalized_results nr
        JOIN documents d_parent ON nr.parent_id = d_parent.id
         {where_parent}
        ORDER BY nr.score DESC;
        """

        with self.engine.connect() as conn:
            conn.execute(text(self.search_hyperparams))

            if self.explain_analyse:
                results = conn.execute(
                    text("EXPLAIN (ANALYSE, BUFFERS)" + text_query),
                    {
                        "text_query": processed_query,
                        "k_text": k_text + 10 if filter_params else k_text,
                        **filter_params,
                    },
                )
                for row in results:
                    print(row)

            results = conn.execute(
                text(text_query),
                {
                    "text_query": processed_query,
                    "k_text": k_text + 10 if filter_params else k_text,
                    **filter_params,
                },
            )

            text_results = []
            for i, row in enumerate(results):
                # make sure we only take top k_text docs
                if i >= k_text:
                    break

                child_doc = Document(
                    id="0",
                    page_content="RESULT FROM TEXT SEARCH - NO CHILD DOCUMENTS",
                    source=DocumentSource.TWIKI,
                    name="Text Search Result",
                    url="",
                    metadata={},
                    parent_id=row.parent_id,
                )

                parent_metadata = row.parent_metadata.copy()
                parent_metadata["search_type"] = "text"

                parent_doc = Document(
                    id=row.parent_id,
                    page_content=row.parent_content,
                    source=DocumentSource(parent_metadata["type"]),
                    name=parent_metadata["name"],
                    url=parent_metadata["url"],
                    metadata=parent_metadata,
                    parent_id=None,
                )

                text_results.append((child_doc, parent_doc, float(row.score)))

            return text_results

    def _clean_query_for_tsquery(self, query: str) -> str:
        """Clean and format query string for PostgreSQL tsquery.

        Uses precompiled regex patterns, set lookups for stop words, and optimized word grouping.
        """
        # Class-level precompiled patterns for reuse (defined in __init__)
        if not hasattr(self, "_special_char_pattern"):
            self._special_char_pattern = re.compile(r"[^a-zA-Z0-9/\s]")
            self._stop_word_pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, self.stop_words)) + r")\b",
                flags=re.IGNORECASE,
            )
            self._stop_words_set = set(word.lower() for word in self.stop_words)

        # Remove special characters
        cleaned = self._special_char_pattern.sub(" ", query)

        # Split and filter words in one pass
        words = [word for word in cleaned.lower().split() if word and word not in self._stop_words_set]

        if not words:
            return "dummy_term_that_wont_match"

        # Create word groups more efficiently
        GROUP_SIZE = 8
        terms = []
        for i in range(0, len(words), GROUP_SIZE):
            group = words[i : i + GROUP_SIZE]
            if group:
                term = "(" + " | ".join(f"'{w}:*'" for w in group) + ")"
                terms.append(term)

        return " & ".join(terms)
