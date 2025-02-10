from __future__ import annotations

import logging
import os

import uvicorn
from litestar import Litestar, get, post
from litestar.config.cors import CORSConfig
from thought_miner_embeddings.core.api import ChromaAPI

# Configure logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# Initialize ChromaAPI with Postgres URL
postgres_url = os.getenv("DATABASE_URL")  # Ensure this is set in your environment
chroma_api = ChromaAPI(postgres_url)

# CORS configuration
cors_config = CORSConfig(allow_origins=["*", "localhost:3001/thoughts"])


# Routes
@get("/db/create_database/{db_name:str}")
async def create_database(db_name: str) -> str:
    chroma_api.create_database(db_name)
    return f"Database '{db_name}' created."


@get("/db/get_database/{db_name:str}")
async def get_database(db_name: str) -> str:
    chroma_api.get_database(db_name)
    return f"Database '{db_name}' retrieved."


@get("/db/list_collections/{db_name:str}")
async def list_collections(db_name: str) -> list[str]:
    return chroma_api.list_collections(db_name)


@get("/db/create_collection/{collection_name:str}")
async def create_collection(
    collection_name: str, embedding_type: str = "sentence_transformer"
) -> str:
    chroma_api.create_collection(collection_name, embedding_type)
    return f"Collection '{collection_name}' created."


@get("/db/get_or_create_collection/{collection_name:str}")
async def get_or_create_collection(
    collection_name: str, embedding_type: str = "sentence_transformer"
) -> str:
    chroma_api.get_or_create_collection(collection_name, embedding_type)
    return f"Collection '{collection_name}' retrieved or created."


@get("/collection/get_collection/{collection_name:str}")
async def get_collection(collection_name: str) -> dict:
    return chroma_api.get_collection(collection_name)


# @delete("/collection/delete_collection/{collection_name:str}")
# async def delete_collection(collection_name: str) -> str:
#     chroma_api.delete_collection(collection_name)
#     return f"Collection '{collection_name}' deleted."


# @patch("/collection/update_collection/{collection_name:str}")
# async def update_collection(collection_name: str, new_name: str) -> str:
#     chroma_api.update_collection(collection_name, new_name)
#     return f"Collection '{collection_name}' updated to '{new_name}'."


# @post("/collection/add/{collection_name:str}/{thought_id:str}")
# async def add_to_collection(
#     collection_name: str, thought_id: str, metadata: dict | None = None
# ) -> str:
#     chroma_api.add(collection_name, thought_id, metadata)
#     return f"Added document with ID '{thought_id}' to collection '{collection_name}'."


# @delete("/collection/delete/{collection_name:str}/{thought_id:str}")
# async def delete_from_collection(collection_name: str, thought_id: str) -> str:
#     chroma_api.delete(collection_name, thought_id)
#     return (
#         f"Deleted document with ID '{thought_id}' from collection '{collection_name}'."
#     )


@get("/collection/get/{collection_name:str}/{thought_id:str}")
async def get_from_collection(collection_name: str, thought_id: str) -> dict:
    return chroma_api.get(collection_name, thought_id)


@get("/collection/query/{collection_name:str}")
async def query_collection(
    collection_name: str, query_texts: list[str], n_results: int = 5
) -> dict:
    return chroma_api.query(collection_name, query_texts, n_results)


@get("/collection/peek/{collection_name:str}")
async def peek_collection(collection_name: str, limit: int = 5) -> dict:
    return chroma_api.peek(collection_name, limit)


@get("/collection/count/{collection_name:str}")
async def count_collection(collection_name: str) -> int:
    return chroma_api.count(collection_name)


# @patch("/collection/update/{collection_name:str}/{thought_id:str}")
# async def update_in_collection(
#     collection_name: str, thought_id: str, metadata: dict | None = None
# ) -> str:
#     chroma_api.update(collection_name, thought_id, metadata)
#     return f"Updated document with ID '{thought_id}' in collection '{collection_name}'."


@post("/collection/upsert/{collection_name:str}/{thought_id:str}")
async def upsert_in_collection(
    collection_name: str, thought_id: str, metadata: dict | None = None
) -> str:
    chroma_api.upsert(collection_name, thought_id, metadata)
    return (
        f"Upserted document with ID '{thought_id}' in collection '{collection_name}'."
    )


# Run the server
def run_server() -> None:
    app = Litestar(
        route_handlers=[
            create_database,
            get_database,
            list_collections,
            create_collection,
            get_or_create_collection,
            get_collection,
            # delete_collection,
            # update_collection,
            # add_to_collection,
            # delete_from_collection,
            get_from_collection,
            query_collection,
            peek_collection,
            count_collection,
            # update_in_collection,
            upsert_in_collection,
        ],
        cors_config=cors_config,
    )
    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    run_server()
