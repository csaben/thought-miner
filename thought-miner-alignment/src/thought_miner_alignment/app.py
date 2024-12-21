import json
import logging
import uuid
from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from thought_miner_data_access.datastore import SQLiteDataStore, ThoughtMetadata

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


@get("/syncmap/{uuid_string:str}")
async def get_syncmap(uuid_string: str) -> ResponseModel:
    logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
    try:
        database_path: Path = SQLiteDataStore.DEFAULT_DATABASE_PATH
        id = uuid.UUID(uuid_string)
        db = SQLiteDataStore(database_path)
        db.connect()
        data: ThoughtMetadata = db.get_thought(id=id)
        audio_path: Path = Path(data.audio_path)
        transcript: str = str(data.transcript)
        syncmap = json.loads(process_pair(audio_path, transcript))
        # Debug LOGGER.debug to understand the structure of syncmap
        LOGGER.debug("Syncmap raw data: %s", syncmap)
        LOGGER.debug("Syncmap type: %s", type(syncmap))
        # Directly parse the syncmap into ResponseModel
        return ResponseModel(**syncmap)
    except Exception as e:
        LOGGER.debug("Error parsing syncmap: %s", e)
        print(e)
        raise


def run_server() -> None:

    app = Litestar(route_handlers=[get_syncmap], cors_config=cors_config)
    uvicorn.run(app)
