import difflib
import sqlite3
import os

class TranslationMemoryDB:
    def __init__(self, db_path="translation_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        """Creates a thread-safe connection with WAL mode enabled."""
        conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for high-frequency writes and fast reads
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.create_function("similarity", 2, self._similarity_ratio)
        return conn

    def _init_db(self):
        """Creates the translation memory table if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, target, context) -- Prevent duplicate entries
                );
            """)
            # Create indexes on source to speed up string matching queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source ON translation_memory(source);
            """)
            conn.commit()

    def save_checked_segments(self, verified_segments):
        """
        verified_segments: List of tuples -> [(source_text, target_text, context_str), ...]
        """
        if not verified_segments:
            return

        query = """
            INSERT OR IGNORE INTO translation_memory (source, target, context)
            VALUES (?, ?, ?);
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, verified_segments)
            conn.commit()
            print(f"Saved {cursor.rowcount} segments to Translation Memory.")

    def find_exact_matches(self, source_text):
        """Retrieves exact matches for a given source string."""
        query = """
            SELECT source, target, context 
            FROM translation_memory 
            WHERE source = ?;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (source_text,))
            # fetchall() returns a list of tuples: [('Japanese', 'Spanish', 'Context'), ...]
            return cursor.fetchall()

    @staticmethod
    def _similarity_ratio(str1, str2):
        """Calculates similarity ratio between 0.0 and 1.0."""
        if not str1 or not str2:
            return 0.0
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def find_fuzzy_matches(self, query_source, min_threshold=0.6, limit=5):
        """Queries database using custom similarity function."""
        sql = """
            SELECT source, target, context, similarity(source, ?) AS score
            FROM translation_memory
            WHERE score >= ?
            ORDER BY score DESC
            LIMIT ?;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (query_source, min_threshold, limit))
            # Returns list of tuples: [(source, target, context, score), ...]
            return cursor.fetchall()

    def fetch_all_segments(self):
        """Fetches all translation memory records ordered by creation date."""
        query = """
            SELECT source, target, context 
            FROM translation_memory 
            ORDER BY id DESC;
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()  # Returns list of (source, target, context) tuples