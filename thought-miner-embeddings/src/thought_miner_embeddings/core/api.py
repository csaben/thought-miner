from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions
from thought_miner_data_access.datastore import (
    ThoughtMetadata,  # Import your ThoughtMetadata class
)
from thought_miner_data_access.postgres import (
    PostgresDataStore,  # Import your PostgresDataStore class
)

# Configure logging
LOGGER = logging.getLogger(__name__)

# Define embedding function mappings
EMBEDDING_FUNCTIONS = {
    "cosine": "multi-qa-mpnet-base-cos-v1",
    "sentence_transformer": "all-MiniLM-L6-v2",
    # Add more mappings as needed
}


class ChromaAPI:
    def __init__(self, postgres_url: str):
        # self.client = chromadb.Client()
        self.client = chromadb.PersistentClient(
            path="/chroma/chroma",
            settings=chromadb.config.Settings(anonymized_telemetry=False),
        )
        self.postgres_db = PostgresDataStore(
            postgres_url
        )  # Initialize PostgresDataStore
        self.postgres_db.connect()  # Connect to the Postgres database

    def __del__(self):
        """Ensure the Postgres connection is closed when the object is destroyed."""
        if self.postgres_db:
            self.postgres_db.disconnect()

    def _fetch_transcript(self, thought_id: str) -> str:
        """Fetch a transcript from the Postgres database."""
        try:
            thought_id_uuid = uuid.UUID(thought_id)  # Convert to UUID
            data: ThoughtMetadata = self.postgres_db.get_thought(id=thought_id_uuid)
            if not data:
                raise ValueError(f"No thought found with ID: {thought_id}")
            return data.transcript
        except Exception as e:
            LOGGER.error(f"Error fetching transcript: {e}")
            raise

    # Database operations
    def create_database(self, db_name: str) -> None:
        """Create a new database."""
        # ChromaDB does not support multiple databases directly, so we use collections as a workaround.
        # This is a placeholder for future functionality.
        LOGGER.info(f"Database '{db_name}' created (not implemented in ChromaDB).")

    def get_database(self, db_name: str) -> Any:
        """Get a database by name."""
        # Placeholder for future functionality.
        LOGGER.info(f"Database '{db_name}' retrieved (not implemented in ChromaDB).")
        return None

    def list_collections(self, db_name: str) -> list[str]:
        """List all collections in the database."""
        collections = self.client.list_collections()
        return [col.name for col in collections]

    # Collection operations
    def create_collection(
        self, collection_name: str, embedding_type: str = "sentence_transformer"
    ) -> Collection:
        """Create a new collection."""
        embedding_fn_name = EMBEDDING_FUNCTIONS.get(embedding_type)
        if not embedding_fn_name:
            raise ValueError(f"Invalid embedding type: {embedding_type}")
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_fn_name
        )
        return self.client.create_collection(
            name=collection_name, embedding_function=embedding_fn
        )

    def get_or_create_collection(
        self, collection_name: str, embedding_type: str = "sentence_transformer"
    ) -> Collection:
        """Get or create a collection."""
        embedding_fn_name = EMBEDDING_FUNCTIONS.get(embedding_type)
        if not embedding_fn_name:
            raise ValueError(f"Invalid embedding type: {embedding_type}")
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_fn_name
        )
        return self.client.get_or_create_collection(
            name=collection_name, embedding_function=embedding_fn
        )

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection by name."""
        return self.client.get_collection(name=collection_name)

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        self.client.delete_collection(name=collection_name)
        LOGGER.info(f"Collection '{collection_name}' deleted.")

    def update_collection(self, collection_name: str, new_name: str) -> None:
        """Update a collection's name."""
        collection = self.client.get_collection(name=collection_name)
        collection.modify(name=new_name)
        LOGGER.info(f"Collection '{collection_name}' updated to '{new_name}'.")

    # Document operations
    def add(
        self, collection_name: str, thought_id: str, metadata: Optional[dict] = None
    ) -> None:
        """Add a document to a collection using the transcript from Postgres."""
        transcript = self._fetch_transcript(thought_id)
        collection = self.client.get_collection(name=collection_name)
        collection.add(
            documents=[transcript],
            ids=[thought_id],
            metadatas=[metadata] if metadata else None,
        )
        LOGGER.info(
            f"Added document with ID '{thought_id}' to collection '{collection_name}'."
        )

    def delete(self, collection_name: str, thought_id: str) -> None:
        """Delete a document from a collection."""
        collection = self.client.get_collection(name=collection_name)
        collection.delete(ids=[thought_id])
        LOGGER.info(
            f"Deleted document with ID '{thought_id}' from collection '{collection_name}'."
        )

    def get(self, collection_name: str, thought_id: str) -> dict:
        """Get a document from a collection."""
        collection = self.client.get_collection(name=collection_name)
        return collection.get(ids=[thought_id])

    def query(
        self, collection_name: str, query_texts: list[str], n_results: int = 5
    ) -> dict:
        """Query a collection."""
        collection = self.client.get_collection(name=collection_name)
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["embeddings", "documents", "metadatas", "distances"],
        )

    def peek(self, collection_name: str, limit: int = 5) -> dict:
        """Peek at documents in a collection."""
        collection = self.client.get_collection(name=collection_name)
        return collection.peek(limit=limit)

    def count(self, collection_name: str) -> int:
        """Count documents in a collection."""
        collection = self.client.get_collection(name=collection_name)
        return collection.count()

    def update(
        self, collection_name: str, thought_id: str, metadata: Optional[dict] = None
    ) -> None:
        """Update a document in a collection."""
        transcript = self._fetch_transcript(thought_id)
        collection = self.client.get_collection(name=collection_name)
        collection.update(
            ids=[thought_id],
            documents=[transcript],
            metadatas=[metadata] if metadata else None,
        )
        LOGGER.info(
            f"Updated document with ID '{thought_id}' in collection '{collection_name}'."
        )

    def upsert(
        self, collection_name: str, thought_id: str, metadata: Optional[dict] = None
    ) -> None:
        """Upsert a document in a collection."""
        transcript = self._fetch_transcript(thought_id)
        collection = self.client.get_collection(name=collection_name)
        print(collection)
        collection.upsert(
            documents=[transcript],
            ids=[thought_id],
            metadatas=[metadata] if metadata else None,
        )
        LOGGER.info(
            f"Upserted document with ID '{thought_id}' in collection '{collection_name}'."
        )
