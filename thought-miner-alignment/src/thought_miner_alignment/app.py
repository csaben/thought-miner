import json
from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig

from thought_miner_alignment.align import process_pair
from thought_miner_alignment.model import ResponseModel

# TODO: update based on webui origin
cors_config = CORSConfig(allow_origins=["*", "localhost:3001/thoughts"])

DEFAULT_AUDIO = Path(
    "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
)
DEFAULT_TEXT = Path(
    "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"  # noqa: E501
)


# def mock_database_call(_id: uuid.UUID) -> tuple[Path, Path]:
def mock_database_call() -> tuple[Path, Path]:
    return DEFAULT_AUDIO, DEFAULT_TEXT


@get("/syncmap")
async def get_syncmap() -> ResponseModel:
    # TODO: the database holding the uploaded audio and generated transcript is shared,
    # we should be able to snatch the contents for a syncmap gen based on the unique
    # identifier
    # pair_id: uuid.UUID,@get("/syncmap")
    audio_path, text_path = mock_database_call()
    syncmap = json.loads(process_pair(audio_path, text_path))

    # Debug print to understand the structure of syncmap
    print("Syncmap raw data:", syncmap)
    print("Syncmap type:", type(syncmap))

    try:
        # Directly parse the syncmap into ResponseModel
        parsed_data = ResponseModel(**syncmap)
        return parsed_data
    except Exception as e:
        print(f"Error parsing syncmap: {e}")
        raise


def run_server() -> None:
    app = Litestar(route_handlers=[get_syncmap], cors_config=cors_config)
    uvicorn.run(app)
