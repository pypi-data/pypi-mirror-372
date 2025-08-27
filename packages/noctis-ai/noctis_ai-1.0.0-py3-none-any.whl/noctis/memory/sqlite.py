import sqlite3
from typing import List, Tuple, Optional, Dict
import os

class SQLiteMemory:
    def __init__(self, db_path: Optional[str] = None):
        """
        SQLite-based memory for Noctis agents.

        Args:
            db_path: Path to the SQLite DB file. 
                     If None, defaults to 'noctis_memory.db' in the project root.
        """
        if db_path is None:
            db_path = os.path.join(os.getcwd(), "noctis_memory.db")  # default file
        self.conn = sqlite3.connect(db_path)
        self._init_table()

    def _init_table(self) -> None:
        """Create the memory table if it does not exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add(self, role: str, content: str) -> None:
        """Add a message to memory."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO memory (role, content) VALUES (?, ?)",
                (role, content)
            )

    def append(self, role: str, content: str) -> None:
        """Alias for add()."""
        self.add(role, content)

    def get_all(self) -> List[Tuple[str, str]]:
        """Retrieve all messages as a list of (role, content) tuples."""
        with self.conn:
            cursor = self.conn.execute(
                "SELECT role, content FROM memory ORDER BY id"
            )
            return cursor.fetchall()

    def get_recent(self, n: int) -> List[Dict[str, str]]:
        """
        Retrieve the last n messages as a list of dicts in chronological order.

        Returns:
            List[Dict[str, str]]: [{"role": role, "content": content}, ...]
        """
        with self.conn:
            cursor = self.conn.execute(
                "SELECT role, content FROM memory ORDER BY id DESC LIMIT ?", (n,)
            )
            rows = cursor.fetchall()
            return [{"role": role, "content": content} for role, content in reversed(rows)]

    def clear(self) -> None:
        """Clear all messages from memory."""
        with self.conn:
            self.conn.execute("DELETE FROM memory")
