import json
import sqlite3
from pathlib import Path
from typing import Optional

from rori import config
from rori.models import EntryTypes, RoriDbEntry, Status

SCHEMA = """
CREATE TABLE IF NOT EXISTS roris (
    hid INTEGER PRIMARY KEY,
    port_from INTEGER NOT NULL,
    port_to INTEGER NOT NULL,
    type TEXT,
    desired_state TEXT NOT NULL DEFAULT 'inactive',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);
"""

WATCHER_ENTRY = RoriDbEntry(
    hid=0,
    port_from=0,
    port_to=0,
    type_=EntryTypes.SYSTEM,
    desired_state=Status.INACTIVE,
)


class RoriDb:
    """SQLite database manager for port forward entries."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        default_db_path = config.RORI_DIR / "rori.db"
        self.db_path = db_path or default_db_path
        self._init_database()

    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(SCHEMA)
            conn.commit()
        self.add(WATCHER_ENTRY)

    def add(self, entry: RoriDbEntry) -> int:
        """Add a new port forward entry."""
        # TODO: add validation
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT OR REPLACE INTO roris
                (hid, port_from, port_to, type, metadata)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    entry.hid,
                    entry.port_from,
                    entry.port_to,
                    entry.type_,
                    json.dumps(entry.metadata),
                ),
            )

            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id or 0

    def get(self, rori_id: int) -> Optional[RoriDbEntry]:
        """Get a specific port forward entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM roris WHERE hid = ?"
            cursor = conn.execute(query, (rori_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_entry(row)

    def get_all(self) -> list[RoriDbEntry]:
        """Get all port forward entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM roris ORDER BY created_at DESC
            """)

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_entries_by_status(self, status: str) -> list[RoriDbEntry]:
        """Get entries filtered by status."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM roris WHERE status = ? ORDER BY created_at DESC
            """,
                (status,),
            )

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_entries_by_type(self, entry_type: str) -> list[RoriDbEntry]:
        """Get entries filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM roris WHERE type = ? ORDER BY created_at DESC
            """,
                (entry_type,),
            )

            return [self._row_to_entry(row) for row in cursor.fetchall()]

    def update(self, entry: RoriDbEntry) -> bool:
        """Update an existing port forward entry."""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE roris SET
                    name = ?, port_from = ?, port_to = ?, status = ?, type = ?,
                    uptime = ?, namespace = ?, resource_name = ?, context = ?,
                    local_address = ?, command = ?, pid = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (
                    entry.name,
                    entry.port_from,
                    entry.port_to,
                    entry.status,
                    entry.type_,
                    entry.id_,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0

    def delete(self, rori_id: int) -> bool:
        """Delete an entry from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM roris WHERE hid = ?
            """,
                (rori_id,),
            )

            conn.commit()
            return cursor.rowcount > 0

    def set_desired_state(self, rori_id: int, state: Status) -> bool:
        """Update desired state of a port forward entry."""
        with sqlite3.connect(self.db_path) as conn:
            # updated_at = CURRENT_TIMESTAMP
            query = "UPDATE roris SET desired_state = ? WHERE hid = ?"
            cursor = conn.execute(query, (state, rori_id))
            conn.commit()
            return cursor.rowcount > 0

    def cleanup_inactive_entries(self) -> int:
        """Remove old inactive entries (older than 30 days)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM roris
                WHERE status = 'inactive'
                AND created_at < datetime('now', '-30 days')
            """)

            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> dict:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive,
                    COUNT(DISTINCT type) as types
                FROM roris
            """)

            row = cursor.fetchone()
            return {
                "total": row[0],
                "active": row[1],
                "inactive": row[2],
                "types": row[3],
            }

    def _row_to_entry(self, row) -> RoriDbEntry:
        """Convert database row to RoriDbEntry."""
        return RoriDbEntry(
            hid=row["hid"],
            port_from=row["port_from"],
            port_to=row["port_to"],
            type_=row["type"],
            desired_state=Status[row["desired_state"].upper()],
            created_at=row["created_at"],
            metadata=json.loads(row["metadata"]),
        )
