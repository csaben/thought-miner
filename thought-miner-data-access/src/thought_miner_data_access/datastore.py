"""# DEFAULT_DATABASE_PATH = Path("/home/arelius/thought-miner/databases/sqlite-v1").

import uuid

data = ThoughtMetadata(
    id=uuid.uuid4(),
    transcript_path=Path(
        "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"
    ),
    audio_path=Path(
        "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a"
    ),
)
db = SQLiteDataStore(DEFAULT_DATABASE_PATH)
db.connect()

# write:
db.store_thought(data)

# read
retreived = db.get_thought("48d6de4c-7146-4f41-b064-31b30e865b43")
print(data.id)
print(retreived)

"""  # noqa: E501, W505

from __future__ import annotations

import logging
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel

from thought_miner_data_access.model import Status

LOGGER = logging.getLogger(__name__)


DEFAULT_DATABASE_PATH = Path("/home/arelius/thought-miner/databases/sqlite-v2.db")


# TODO: should be in data-model or combine data-access with data-model (i lean towards this)
class ThoughtMetadata(BaseModel):
    id: UUID
    transcript: str | None
    audio_path: Path
    syncmap_path: Path | None
    embeddings_path: Path | None  # TODO: this will become a dict with keys?
    created_at: datetime = datetime.now()  # noqa: DTZ005


class DataStore(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def store_thought(self, data: ThoughtMetadata) -> Status:
        pass

    @abstractmethod
    def get_thought(self, id: UUID) -> ThoughtMetadata | None:
        pass


# TODO: i hate how there are three non type checked places to forget to use the correct table
class SQLiteDataStore(DataStore):
    DEFAULT_DATABASE_PATH = DEFAULT_DATABASE_PATH

    def __init__(self, db_path: Path) -> SQLiteDataStore:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None

    def connect(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        # TODO: eventually we should handle the state prior to syncmap,
        # transcript, and embeddings existing
        self.conn.execute(
            # trying storing the whole transcript directly
            """
            CREATE TABLE IF NOT EXISTS thoughtsv3 (
                id TEXT PRIMARY KEY,
                transcript TEXT DEFAULT NULL,
                audio_path TEXT NOT NULL,
                syncmap_path TEXT DEFAULT NULL,
                embeddings_path TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        )

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()

    # TODO: not sure i like returning a basemodel here
    def store_thought(self, data: ThoughtMetadata) -> bool:
        """TODO: typically storing will occur in four steps.

        1) store the audio
        2) fire off a transcription run and store the transcript
        3) fire off a syncmap run and store the syncmap
        4) fire off an embedding run and store that (order of 3 and 4 don't matter)
        then the next search will include the newest data in the indexing

        lastly, accessing albums should just work.
        so, simple: add albums field, if thought.albums.includes("album choice"),
        populate that album for viewing
        """
        try:
            self.conn.execute(
                """INSERT INTO thoughtsv3 
                   (id, transcript, audio_path, syncmap_path, embeddings_path, created_at) 
                   VALUES (?, ?, ?, ?, ?, ?)""",  # noqa: E501, W291
                (
                    str(data.id),
                    str(data.transcript),
                    str(data.audio_path),
                    str(data.syncmap_path),
                    str(data.embeddings_path),
                    data.created_at,
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            LOGGER.debug("%s", e)
            return False

    def get_thought(self, id: UUID) -> ThoughtMetadata | None:
        """TODO: typically search of a thought will actually start inside chromadb.

        That entry will have this uuid which we will then use to fetch the audio
        and syncmap for interactive transcript
        """
        cursor = self.conn.execute("SELECT * FROM thoughtsv3 WHERE id = ?", (str(id),))
        row = cursor.fetchone()
        if row:
            return ThoughtMetadata(
                id=UUID(row[0]),
                transcript=str(row[1]),
                audio_path=Path(row[2]),
                syncmap_path=Path(row[3]),
                embeddings_path=Path(row[4]),
                created_at=datetime.fromisoformat(row[5]),
            )
        return None
