import sqlite3
import threading
from typing import Optional

class KVDatabase:
    def __init__(self, db_file: str, timeout: float = 10.0):
        self.db_file = db_file
        self.timeout = timeout
        self.local = threading.local()
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema with WAL mode for better concurrency"""
        conn = sqlite3.connect(self.db_file, timeout=self.timeout)
        conn.execute('PRAGMA journal_mode=WAL')  # Enable WAL mode
        conn.execute('PRAGMA synchronous=NORMAL')  # Balanced durability/performance
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT,
                timestamp INTEGER,
                value TEXT,
                PRIMARY KEY (key, timestamp)
            )
        ''')
        # Index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_key_timestamp 
            ON kv_store(key, timestamp)
        ''')
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection with timeout"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_file, timeout=self.timeout)
            self.local.conn.execute('PRAGMA journal_mode=WAL')
            self.local.conn.execute('PRAGMA synchronous=NORMAL')
        return self.local.conn
    
    def put(self, key: str, timestamp: int, value: str) -> None:
        """Store key-value pair with timestamp using ACID transaction"""
        conn = self._get_connection()
        try:
            with conn:  # This creates a transaction
                conn.execute(
                    'INSERT OR REPLACE INTO kv_store (key, timestamp, value) VALUES (?, ?, ?)',
                    (key, timestamp, value)
                )
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                # SQLite timeout already handled by connection timeout
                raise sqlite3.OperationalError("Database busy after timeout")
            raise e
    
    def get(self, key: str, timestamp: int) -> Optional[str]:
        """Get value for key at or before given timestamp"""
        conn = self._get_connection()
        try:
            with conn:  # Read transaction for consistency
                cursor = conn.execute('''
                    SELECT value FROM kv_store
                    WHERE key = ? AND timestamp <= ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (key, timestamp))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                raise sqlite3.OperationalError("Database busy after timeout")
            raise e
    
    def close(self):
        """Close the thread-local connection"""
        conn = getattr(self.local, 'conn', None)
        if conn:
            conn.close()
            del self.local.conn
