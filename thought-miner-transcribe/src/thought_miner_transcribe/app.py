import uuid
from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from thought_miner_data_access.datastore import SQLiteDataStore, ThoughtMetadata

from thought_miner_transcribe.model import ResponseModel, TranscriptStatusEnum

# TODO: update based on webui origin
cors_config = CORSConfig(allow_origins=["*", "localhost:3001/thoughts"])

DEFAULT_AUDIO = Path(
    "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
)
DEFAULT_TEXT = Path(
    "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"  # noqa: E501
)


"""
lets confirm if this makes sense:
1) ui consumes audio and optionally txt
2) writes to backend db using defined schema (stores with uuid)
3) uses the same uuid to then fetch syncmap that was generated in the background (and
                the transcript which was optionally also generated behind the scenes)

dev notes:
- does route need to then expect uuid? yes how does the route look?
- does the way react nextjs request affect what we do here?
"""


@get("/transcribe/{uuid_string:str}")
async def create_transcript(uuid_string: str) -> ResponseModel:
    """Called from the frontend context with a uuid to the audio stored in the database.

    The transcript is just stored with the same uuid s.t. the syncmap process knows
    where to find it.

    Parameters:
    - chunk size (how to handle with uuid being whats passed in?
    or is arg possible in addition?)
    """
    # TODO: consume uuid, get path info, create and store transcript with original uuid.
    try:
        # Convert string UUID to UUID object
        id = uuid.UUID(uuid_string)
        print(id)

        print(SQLiteDataStore.DEFAULT_DATABASE_PATH)
        db = SQLiteDataStore(SQLiteDataStore.DEFAULT_DATABASE_PATH)
        db.connect()
        data = ThoughtMetadata(
            id=id,
            transcript_path=Path(
                "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"
            ),
            audio_path=Path(
                "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
            ),
            syncmap_path=Path("a"),
            embeddings_path=Path("b"),
        )
        db.store_thought(data=data)
        # Get existing record
        thought = db.get_thought(id)
        print(thought)
        if not thought:
            return ResponseModel(
                id=id, transcript=None, status=TranscriptStatusEnum.FAILED
            )

        return ResponseModel(
            id=id,
            transcript=str(thought.transcript_path),
            status=TranscriptStatusEnum.COMPLETED,
        )

    except Exception as e:
        print(f"Error processing transcript: {e}")
        return ResponseModel(
            id=uuid.UUID(uuid), transcript=None, status=TranscriptStatusEnum.FAILED
        )


def run_server() -> None:
    app = Litestar(route_handlers=[create_transcript], cors_config=cors_config)
    uvicorn.run(app, port=8001)
