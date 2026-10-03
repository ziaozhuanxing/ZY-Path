"""Store and search inference records in a local SQLite database."""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from utils.paths import app_data_dir
k

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Report a database failure with a user-friendly message."""


class DatabaseManager:
    """Manage inference records stored in SQLite."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Create the database and its table when they do not exist."""
        try:
            self.db_path = (
                Path(db_path)
                if db_path is not None
                else app_data_dir() / "zy_path_history.db"
            )
            self._initialize_database()
        except (OSError, sqlite3.Error) as error:
            logger.exception("Could not initialize the database.")
            raise DatabaseError(
                "The database could not be opened or initialized."
            ) from error

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        try:
            connection.row_factory = sqlite3.Row
            connection.create_function("casefold", 1, str.casefold)
            yield connection
            connection.commit()
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_records (
                    id INTEGER PRIMARY KEY,
                    image_path TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    task_type TEXT NOT NULL
                        CHECK (task_type IN ('classification', 'segmentation')),
                    result_label TEXT,
                    confidence REAL,
                    result_image_path TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )

    def insert_record(
        self,
        image_path: str,
        model_path: str,
        task_type: str,
        result_label: str | None = None,
        confidence: float | None = None,
        result_image_path: str | None = None,
    ) -> int:
        """Insert a record and return its new ID."""
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        try:
            with self._connection() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO inference_records (
                        image_path, model_path, task_type, result_label,
                        confidence, result_image_path, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        image_path,
                        model_path,
                        task_type,
                        result_label,
                        confidence,
                        result_image_path,
                        timestamp,
                    ),
                )
                return int(cursor.lastrowid)
        except (OSError, sqlite3.Error) as error:
            logger.exception("Could not insert an inference record.")
            raise DatabaseError(
                "The record could not be saved. Check the supplied values and try again."
            ) from error

    def get_all_records(self) -> list[dict]:
        """Return all records from newest to oldest."""
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, image_path, model_path, task_type, result_label,
                           confidence, result_image_path, timestamp
                    FROM inference_records
                    ORDER BY timestamp DESC, id DESC
                    """
                ).fetchall()
                return [dict(row) for row in rows]
        except (OSError, sqlite3.Error) as error:
            logger.exception("Could not retrieve inference records.")
            raise DatabaseError("The records could not be loaded.") from error

    def get_record_by_id(self, record_id: int) -> dict | None:
        """Return one record, or None if its ID does not exist."""
        try:
            with self._connection() as connection:
                row = connection.execute(
                    """
                    SELECT id, image_path, model_path, task_type, result_label,
                           confidence, result_image_path, timestamp
                    FROM inference_records
                    WHERE id = ?
                    """,
                    (record_id,),
                ).fetchone()
                return dict(row) if row is not None else None
        except (OSError, sqlite3.Error) as error:
            logger.exception("Could not retrieve an inference record.")
            raise DatabaseError("The record could not be loaded.") from error

    def search(
        self,
        keyword: str = "",
        start: str | None = None,
        end: str | None = None,
    ) -> list[dict]:
        """Search paths and an optional inclusive UTC timestamp range."""
        try:
            start_bound = self._normalize_utc_bound(start)
            end_bound = self._normalize_utc_bound(end)
            escaped_keyword = (
                keyword.casefold()
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            pattern = f"%{escaped_keyword}%"

            with self._connection() as connection:
                rows = connection.execute(
                    """
                    SELECT id, image_path, model_path, task_type, result_label,
                           confidence, result_image_path, timestamp
                    FROM inference_records
                    WHERE (
                        ? = ''
                        OR casefold(image_path) LIKE ? ESCAPE '\\'
                        OR casefold(model_path) LIKE ? ESCAPE '\\'
                    )
                    AND (? IS NULL OR timestamp >= ?)
                    AND (? IS NULL OR timestamp <= ?)
                    ORDER BY timestamp DESC, id DESC
                    """,
                    (
                        keyword,
                        pattern,
                        pattern,
                        start_bound,
                        start_bound,
                        end_bound,
                        end_bound,
                    ),
                ).fetchall()
                return [dict(row) for row in rows]
        except DatabaseError:
            raise
        except (AttributeError, OSError, sqlite3.Error, TypeError) as error:
            logger.exception("Could not search inference records.")
            raise DatabaseError(
                "The search could not be completed. Check the keyword and dates."
            ) from error

    @staticmethod
    def _normalize_utc_bound(value: str | None) -> str | None:
        if value is None:
            return None
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as error:
            raise DatabaseError(
                "Search dates must be valid ISO-8601 UTC timestamps."
            ) from error
        if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
            raise DatabaseError(
                "Search dates must be valid ISO-8601 UTC timestamps."
            )
        return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds")