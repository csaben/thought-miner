import uuid
from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from thought_miner_data_access.datastore import SQLiteDataStore, ThoughtMetadata

from thought_miner_transcribe.commons import reflow_text
from thought_miner_transcribe.model import ResponseModel, TranscriptStatusEnum
from thought_miner_transcribe.transcribe import transcribe_with_chunking

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


@get("/app")
async def test() -> str:
    return "hello noob"


@get("/transcribe/{uuid_string:str}")
async def create_transcript(uuid_string: str) -> ResponseModel:
    """Called from the frontend context with a uuid to the audio stored in the database.

    The transcript is just stored with the same uuid s.t. the syncmap process knows
    where to find it.

    Parameters:
    - chunk size (how to handle with uuid being whats passed in?
    or is arg possible in addition?)

    1) which database? should collect from context of which user but for now all users share one db
    2) uuid which means frontend is responsible for updating the database => we need shared db

    """
    # get the database path from the .env or equivalent (can we pass >1 arg to the function?)
    database_path: Path = SQLiteDataStore.DEFAULT_DATABASE_PATH
    print(database_path)

    try:
        # Convert string UUID to UUID object
        id = uuid.UUID(uuid_string)

        # create connection to db
        db = SQLiteDataStore(database_path)
        db.connect()

        # transcribe the provided txt from a audio loaded based on metadata in db
        data: ThoughtMetadata | None = db.get_thought(id=id)
        audio_path: Path = Path(data.audio_path)
        transcript: str = transcribe_with_chunking(audio_path)

        # reflow the transcript
        print("should see trancript")
        print(transcript)
        transcript = reflow_text(transcript)
        print(transcript)
        print("should see trancript")

        # save transcript and update database
        data.transcript = transcript
        db.store_thought(data)

        if not transcript:
            return ResponseModel(
                id=id, transcript=None, status=TranscriptStatusEnum.FAILED
            )

        # TODO: should we just pass back uuid to confirm it worked and have them do lookup in db from frontend?
        return ResponseModel(
            id=id,
            transcript=transcript,
            status=TranscriptStatusEnum.COMPLETED,
        )

    except Exception as e:
        print(f"Error processing transcript: {e}")
        return ResponseModel(
            id=uuid.UUID(uuid), transcript=None, status=TranscriptStatusEnum.FAILED
        )


def run_server() -> None:
    app = Litestar(route_handlers=[test, create_transcript], cors_config=cors_config)
    uvicorn.run(app, port=8001)


# test that this now works by inserting manually and checking with curl (done)
# TODO: create components for
# this: adding thought
# and: getting transcript: curl http://localhost:8001/transcribe/0c49945f-15a8-4b28-823b-7476969f3d35
if __name__ == "__main__":
    id = uuid.uuid4()
    print(id)
    data = ThoughtMetadata(
        id=id,
        transcript=None,
        audio_path=str(
            Path(
                "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
            )
        ),
        syncmap_path=None,
        embeddings_path=None,
    )

    database_path: Path = SQLiteDataStore.DEFAULT_DATABASE_PATH
    db = SQLiteDataStore(database_path)
    db.connect()
    db.store_thought(data)

# try curl
# 0c49945f-15a8-4b28-823b-7476969f3d35
