import json
import logging
import os
import uuid
from pathlib import Path

import aiofiles
import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig

# from thought_miner_data_access.datastore import SQLiteDataStore, ThoughtMetadata
from thought_miner_data_access.datastore import ThoughtMetadata
from thought_miner_data_access.postgres import PostgresDataStore

from thought_miner_alignment.align import process_pair
from thought_miner_alignment.model import ResponseModel

LOGGER = logging.getLogger(__name__)

# TODO: update based on webui origin
cors_config = CORSConfig(allow_origins=["*", "localhost:3001/thoughts"])

# DEFAULT_AUDIO = Path(
#     "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
# )
# DEFAULT_TEXT = Path(
# "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"  # noqa: E501
# )


# TODO: this was supposed to save it on the volume not return it what the fricking hell man
@get("/syncmap/{uuid_string:str}")
async def get_syncmap(uuid_string: str) -> ResponseModel:
    logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
    try:
        # database_path: Path = SQLiteDataStore.DEFAULT_DATABASE_PATH
        id = uuid.UUID(uuid_string)
        # db = SQLiteDataStore(database_path)
        # db = PostgresDataStore()

        db = PostgresDataStore(os.getenv("DATABASE_URL"))
        db.connect()
        data: ThoughtMetadata = db.get_thought(id=id)
        audio_path: Path = Path(data.audio_path)
        transcript: str = str(data.transcript)
        syncmap = json.loads(process_pair(audio_path, transcript))

        # TODO: dump the syncmap into a file, and dump the file into the db using the uuid
        # Create directory if it doesn't exist
        alignment_dir = Path(os.getenv("ALIGNMENT_DIR", "/opt/app/dev/alignment"))
        alignment_dir.mkdir(parents=True, exist_ok=True)

        # Create syncmap file path using the UUID
        syncmap_path = alignment_dir / f"{id}.json"

        # Use async file writing
        async with aiofiles.open(syncmap_path, "w") as f:
            await f.write(json.dumps(syncmap, indent=2))

        # Update data with new syncmap path
        data.syncmap_path = str(syncmap_path)
        db.store_thought(data)

        # Debug LOGGER.debug to understand the structure of syncmap
        LOGGER.debug("Syncmap raw data: %s", syncmap)
        LOGGER.debug("Syncmap type: %s", type(syncmap))
        # Directly parse the syncmap into ResponseModel
        return ResponseModel(**syncmap)
    except Exception as e:
        LOGGER.debug("Error parsing syncmap: %s", e)
        print(e)
        raise
    finally:
        if db and db.conn:
            db.disconnect()


def run_server() -> None:

    app = Litestar(route_handlers=[get_syncmap], cors_config=cors_config)
    # uvicorn.run(app)
    uvicorn.run(app, host="0.0.0.0", port=8000)
