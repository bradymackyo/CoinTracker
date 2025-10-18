import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple, Any


class Database:

    def __init__(self, db_path=None):

        self.db_path = db_path or ':memory:'
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        
        return self.cursor.execute(query, params)

    def executemany(self, query: str, params_list: List[Tuple]) -> sqlite3.Cursor:
        
        return self.cursor.executemany(query, params_list)

    def fetchone(self) -> Optional[sqlite3.Row]:
        return self.cursor.fetchone()

    def fetchall(self) -> List[sqlite3.Row]:
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    # Finalizes transaction if the change is successful - rollback otherwise
    @contextmanager
    def transaction(self):
        try:
            yield self
            self.commit()
        except Exception as e:
            self.rollback()
            raise e

    # Create table - should only be called if testing from memory, application should not need to make tables if the app is loading from a demo file
    def create_table(self, table_name: str, columns: str):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.execute(query)
        self.commit()

    # Drops a table from the database - likely unused in the application but useful for testing
    def drop_table(self, table_name: str):
        self.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.commit()

    def close(self):
        self.conn.close()

    @property
    def is_memory(self) -> bool:
        return self.db_path == ':memory:'
