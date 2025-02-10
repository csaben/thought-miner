from __future__ import annotations

import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID

import psycopg2

from thought_miner_data_access.datastore import DataStore, ThoughtMetadata

LOGGER = logging.getLogger(__name__)

# TODO: scoop this out of the .env
DEFAULT_DATABASE_NAME = "thoughtminer"
DEFAULT_USER = "user"
DEFAULT_PASSWORD = "password"


class PostgresDataStore(DataStore):
    DEFAULT_DATABASE_NAME = DEFAULT_DATABASE_NAME
    DEFAULT_USER = DEFAULT_USER
    DEFAULT_PASSWORD = DEFAULT_PASSWORD

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided")
        self.conn = None

    def connect(self) -> None:
        parsed_url = urlparse(self.database_url)
        print(parsed_url.path[1:])
        self.conn = psycopg2.connect(
            dbname=parsed_url.path[1:],
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port,
        )
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Thought (
                    id TEXT PRIMARY KEY,
                    transcript TEXT DEFAULT NULL,
                    audio_path TEXT NOT NULL,
                    syncmap_path TEXT DEFAULT NULL,
                    embeddings_path TEXT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )

        with self.conn.cursor() as cur:
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            print(f"Connected to database: {db_name}")

            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            )
            tables = cur.fetchall()
            print(f"Available tables: {tables}")
        self.conn.commit()

    def disconnect(self) -> None:
        if self.conn:
            self.conn.close()

    def store_thought(self, data: ThoughtMetadata) -> bool:
        try:
            cur = self.conn.cursor()

            # Insert or update logic
            cur.execute(
                """
                INSERT INTO "Thought" 
                (id, transcript, audio_path, syncmap_path, embeddings_path, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    transcript = %s,
                    audio_path = %s,
                    syncmap_path = %s,
                    embeddings_path = %s,
                    created_at = %s
                """,
                (
                    str(data.id),
                    str(data.transcript) if data.transcript else "",
                    str(data.audio_path) if data.audio_path else "",
                    str(data.syncmap_path) if data.syncmap_path else "",
                    str(data.embeddings_path) if data.embeddings_path else "",
                    data.created_at,
                    # These are for the UPDATE part after ON CONFLICT
                    str(data.transcript) if data.transcript else "",
                    str(data.audio_path) if data.audio_path else "",
                    str(data.syncmap_path) if data.syncmap_path else "",
                    str(data.embeddings_path) if data.embeddings_path else "",
                    data.created_at,
                ),
            )
            self.conn.commit()
            cur.close()
            return True
        except Exception as e:
            LOGGER.debug("%s", e)
            return False

    def get_thought(self, id: UUID) -> ThoughtMetadata | None:
        cur = self.conn.cursor()
        # evidently the sql syntax wasn't working with psql cause after this change everythign is groovy
        cur.execute(
            """
            SELECT id, transcript, audio_path, syncmap_path, embeddings_path, created_at 
            FROM "Thought" 
            WHERE id = %s
        """,
            (str(id),),
        )
        row = cur.fetchone()
        cur.close()

        if row:
            return ThoughtMetadata(
                id=UUID(row[0]),
                transcript=row[1] or "",  # Use empty string if None
                audio_path=Path(row[2]) if row[2] else None,
                syncmap_path=Path(row[3]) if row[3] else None,
                embeddings_path=Path(row[4]) if row[4] else None,
                created_at=row[5],
            )
        return None
