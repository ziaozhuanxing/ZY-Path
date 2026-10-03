import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from data.database_manager import DatabaseError, DatabaseManager


def make_manager(tmp_path: Path) -> DatabaseManager:
    return DatabaseManager(tmp_path / "nested" / "history.db")


def test_database_is_created_with_expected_schema(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    assert manager.db_path.is_file()

    connection = sqlite3.connect(manager.db_path)
    try:
        columns = connection.execute(
            "PRAGMA table_info(inference_records)"
        ).fetchall()
        table_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE name = ?",
            ("inference_records",),
        ).fetchone()[0]
    finally:
        connection.close()

    assert [(column[1], column[2]) for column in columns] == [
        ("id", "INTEGER"),
        ("image_path", "TEXT"),
        ("model_path", "TEXT"),
        ("task_type", "TEXT"),
        ("result_label", "TEXT"),
        ("confidence", "REAL"),
        ("result_image_path", "TEXT"),
        ("timestamp", "TEXT"),
    ]
    assert columns[0][5] == 1
    assert [column[3] for column in columns[1:4]] == [1, 1, 1]
    assert [column[3] for column in columns[4:7]] == [0, 0, 0]
    assert columns[7][3] == 1
    assert "'classification'" in table_sql
    assert "'segmentation'" in table_sql


def test_insert_get_by_id_and_get_all_order(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    first_id = manager.insert_record(
        "images/first.png", "models/model.pt", "classification", "A", 0.9
    )
    second_id = manager.insert_record(
        "images/second.png", "models/model.pt", "classification", "B", 0.8
    )

    first_record = manager.get_record_by_id(first_id)
    assert first_record is not None
    assert first_record["image_path"] == "images/first.png"
    assert first_record["confidence"] == pytest.approx(0.9)
    timestamp = datetime.fromisoformat(first_record["timestamp"])
    assert timestamp.utcoffset() == timedelta(0)
    assert manager.get_record_by_id(-1) is None
    assert [record["id"] for record in manager.get_all_records()] == [
        second_id,
        first_id,
    ]


def test_segmentation_confidence_can_be_null(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    record_id = manager.insert_record(
        "images/segmentation.png", "models/model.pt", "segmentation"
    )

    record = manager.get_record_by_id(record_id)
    assert record is not None
    assert record["confidence"] is None
    assert record["result_label"] is None
    assert record["result_image_path"] is None


def test_search_is_case_insensitive_and_escapes_special_characters(
    tmp_path: Path,
) -> None:
    manager = make_manager(tmp_path)
    target_id = manager.insert_record(
        "Images/Case%_Folder/O'Reilly.png",
        "models/Model.pt",
        "classification",
    )
    decoy_id = manager.insert_record(
        "Images/CaseXXFolder/OReilly.png",
        "models/model.pt",
        "classification",
    )

    assert [record["id"] for record in manager.search("cAsE%_fOlDeR")] == [
        target_id
    ]
    assert [record["id"] for record in manager.search("O'Reilly")] == [
        target_id
    ]
    assert [record["id"] for record in manager.search("MODEL.PT")] == [
        decoy_id,
        target_id,
    ]


def test_search_date_range_includes_both_boundaries(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)
    manager.insert_record(
        "images/before.png", "models/model.pt", "classification"
    )
    target_id = manager.insert_record(
        "images/middle-marker.png", "models/model.pt", "classification"
    )
    target_record = manager.get_record_by_id(target_id)
    assert target_record is not None
    target_timestamp = target_record["timestamp"]
    manager.insert_record("images/after.png", "models/model.pt", "classification")

    results = manager.search(
        "middle-marker", start=target_timestamp, end=target_timestamp
    )
    assert [record["id"] for record in results] == [target_id]


def test_search_returns_empty_list_when_no_records_match(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    assert manager.search("missing") == []
    assert manager.search(start="2030-01-01T00:00:00Z") == []


def test_invalid_task_type_raises_database_error(tmp_path: Path) -> None:
    manager = make_manager(tmp_path)

    with pytest.raises(DatabaseError, match="record could not be saved"):
        manager.insert_record("images/input.png", "models/model.pt", "unknown")