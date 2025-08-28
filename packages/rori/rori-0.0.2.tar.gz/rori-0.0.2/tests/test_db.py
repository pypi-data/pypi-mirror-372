"""Test database operations."""

import json
import sqlite3
from pathlib import Path

import pytest

from rori.db import PofDb
from rori.models import PofDbEntry


def test_pof_db_initialization(temp_db_path):
    """Test PofDb initialization creates database and tables."""
    db = PofDb(temp_db_path)

    # Check that database file was created
    assert temp_db_path.exists()

    # Check that table was created
    with sqlite3.connect(temp_db_path) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='pofs'"
        )
        assert cursor.fetchone() is not None


def test_pof_db_add_entry(temp_db_path):
    """Test adding a new entry to the database."""
    db = PofDb(temp_db_path)

    entry = PofDbEntry(
        hid=1, port_from=8080, port_to=80, type_="manual", metadata={"test": "value"}
    )

    entry_id = db.add(entry)
    assert entry_id > 0


def test_pof_db_get_entry(temp_db_path):
    """Test retrieving an entry from the database."""
    db = PofDb(temp_db_path)

    # Add entry
    original_entry = PofDbEntry(
        hid=1,
        port_from=8080,
        port_to=80,
        type_="manual",
        metadata={"namespace": "default"},
    )
    db.add(original_entry)

    # Retrieve entry
    retrieved_entry = db.get(1)

    assert retrieved_entry is not None
    assert retrieved_entry.hid == 1
    assert retrieved_entry.port_from == 8080
    assert retrieved_entry.port_to == 80
    assert retrieved_entry.type_ == "manual"
    assert retrieved_entry.metadata == {"namespace": "default"}


def test_pof_db_get_nonexistent_entry(temp_db_path):
    """Test retrieving a non-existent entry returns None."""
    db = PofDb(temp_db_path)

    result = db.get(999)
    assert result is None


def test_pof_db_update_entry(temp_db_path):
    """Test updating an existing entry."""
    db = PofDb(temp_db_path)

    # Add initial entry
    entry = PofDbEntry(hid=1, port_from=8080, port_to=80, type_="manual")
    db.add(entry)

    # Update entry
    updated_entry = PofDbEntry(
        hid=1,
        port_from=9090,
        port_to=90,
        type_="kubernetes",
        metadata={"updated": True},
    )
    db.add(updated_entry)  # add with same hid should replace

    # Verify update
    retrieved = db.get(1)
    assert retrieved.port_from == 9090
    assert retrieved.port_to == 90
    assert retrieved.type_ == "kubernetes"
    assert retrieved.metadata == {"updated": True}


def test_pof_db_delete_entry(temp_db_path):
    """Test deleting an entry from the database."""
    db = PofDb(temp_db_path)

    # Add entry
    entry = PofDbEntry(hid=1, port_from=8080, port_to=80)
    db.add(entry)

    # Verify it exists
    assert db.get(1) is not None

    # Delete entry
    db.delete(1)

    # Verify it's gone
    assert db.get(1) is None


def test_pof_db_metadata_serialization(temp_db_path):
    """Test that metadata is properly serialized and deserialized."""
    db = PofDb(temp_db_path)

    complex_metadata = {
        "namespace": "default",
        "service": "test-service",
        "context": "test-context",
        "labels": {"app": "test", "version": "1.0"},
        "ports": [80, 443, 8080],
    }

    entry = PofDbEntry(hid=1, port_from=8080, port_to=80, metadata=complex_metadata)

    db.add(entry)
    retrieved = db.get(1)

    assert retrieved.metadata == complex_metadata


def test_pof_db_row_to_entry_conversion(temp_db_path):
    """Test _row_to_entry method properly converts database rows."""
    db = PofDb(temp_db_path)

    # Insert data directly into database
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute(
            """
            INSERT INTO pofs (hid, port_from, port_to, type, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, 8080, 80, "test", json.dumps({"test": "value"})),
        )
        conn.commit()

    # Retrieve using PofDb
    entry = db.get(1)

    assert entry is not None
    assert entry.hid == 1
    assert entry.port_from == 8080
    assert entry.port_to == 80
    assert entry.type_ == "test"
    assert entry.metadata == {"test": "value"}


def test_pof_db_default_path():
    """Test PofDb uses default path when none provided."""
    with pytest.MonkeyPatch() as mp:
        # Mock config.POF_DIR
        mock_pof_dir = Path("/tmp/test_pof")
        mp.setattr("rori.config.POF_DIR", mock_pof_dir)

        db = PofDb()
        expected_path = mock_pof_dir / "rori.db"
        assert db.db_path == expected_path


def test_pof_db_handles_empty_metadata(temp_db_path):
    """Test database handles entries with empty metadata."""
    db = PofDb(temp_db_path)

    entry = PofDbEntry(hid=1, port_from=8080, port_to=80, metadata={})
    db.add(entry)

    retrieved = db.get(1)
    assert retrieved.metadata == {}


def test_pof_db_handles_none_metadata(temp_db_path):
    """Test database handles entries with None metadata."""
    db = PofDb(temp_db_path)

    # Insert entry with None metadata directly
    with sqlite3.connect(temp_db_path) as conn:
        conn.execute(
            """
            INSERT INTO pofs (hid, port_from, port_to, type, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, 8080, 80, "test", None),
        )
        conn.commit()

    # Should handle None gracefully
    entry = db.get(1)
    assert entry is not None
    assert entry.metadata == {}
