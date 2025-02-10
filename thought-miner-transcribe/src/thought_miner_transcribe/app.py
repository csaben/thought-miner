import os
import uuid
from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from thought_miner_data_access.datastore import ThoughtMetadata
from thought_miner_data_access.postgres import PostgresDataStore
from thought_miner_transcribe.commons import reflow_text
from thought_miner_transcribe.model import ResponseModel, TranscriptStatusEnum
from thought_miner_transcribe.transcribe import transcribe_with_chunking

# TODO: update based on webui origin
cors_config = CORSConfig(allow_origins=["*", "localhost:3001/thoughts"])

DEFAULT_AUDIO = Path(
    # "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
    # "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
    "opt/app/dev/sample.m4a"
)
# DEFAULT_DATABASE_PATH = Path("/opt/app/dev/databases/sqlite-v2.db")
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
    return "hello noob works!"


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
    # database_path: Path = PostgresDataStore.DEFAULT_DATABASE_PATH
    # print(database_path)

    try:
        # Convert string UUID to UUID object
        id = uuid.UUID(uuid_string)

        # create connection to db
        # db = PostgresDataStore()
        db = PostgresDataStore(os.getenv("DATABASE_URL"))
        db.connect()

        # transcribe the provided txt from a audio loaded based on metadata in db
        data: ThoughtMetadata | None = db.get_thought(id=id)
        audio_path: Path = Path(data.audio_path)
        transcript: str = transcribe_with_chunking(audio_path)

        # reflow the transcript
        transcript = reflow_text(transcript, chunk_size=30)
        # transcript = reflow_text_with_sentences(transcript)
        print(transcript)
        print("should see trancript")
        print("stupid")

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
            id=uuid.UUID(uuid_string),
            transcript=None,
            status=TranscriptStatusEnum.FAILED,
        )
    finally:
        if db and db.conn:
            db.disconnect()


def run_server() -> None:
    app = Litestar(route_handlers=[test, create_transcript], cors_config=cors_config)
    # uvicorn.run(app, port=8001)
    uvicorn.run(app, host="0.0.0.0", port=8001)
