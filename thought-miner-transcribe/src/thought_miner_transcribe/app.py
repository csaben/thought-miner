from pathlib import Path

import uvicorn
from litestar import Litestar, get
from litestar.config.cors import CORSConfig

from thought_miner_transcribe.model import ResponseModel

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


@get("/transcribe")
async def create_transcript() -> ResponseModel:
    """Called from the frontend context with a uuid to the audio stored in the database.

    The transcript is just stored with the same uuid s.t. the syncmap process knows
    where to find it.
    """
    # TODO: consume uuid, get path info, create and store transcript with original uuid.
    raise NotImplementedError


def run_server() -> None:
    app = Litestar(route_handlers=[create_transcript], cors_config=cors_config)
    uvicorn.run(app)
