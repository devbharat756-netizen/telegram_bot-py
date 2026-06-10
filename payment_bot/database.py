import os
import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL", "")

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        self.conn.autocommit = True
        self._create_tables()

    def _get_cursor(self):
        # Connection drop ho jaaye to reconnect karo
        try:
            self.conn.cursor().execute("SELECT 1")
        except Exception:
            self.conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            self.conn.autocommit = True
        return self.conn.cursor()

    def _create_tables(self):
        with self._get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users_access (
                    user_id     BIGINT PRIMARY KEY,
                    expires_at  TIMESTAMP NOT NULL,
                    order_id    TEXT,
                    created_at  TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS orders (
                    order_id    TEXT PRIMARY KEY,
                    user_id     BIGINT NOT NULL,
                    amount      INTEGER NOT NULL,
                    days        INTEGER NOT NULL,
                    status      TEXT DEFAULT 'pending',
                    created_at  TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS files (
                    id                  TEXT PRIMARY KEY,
                    title               TEXT NOT NULL,
                    description         TEXT,
                    file_type           TEXT NOT NULL,
                    telegram_file_id    TEXT NOT NULL,
                    upload_date         TIMESTAMP DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS download_logs (
                    id              SERIAL PRIMARY KEY,
                    user_id         BIGINT NOT NULL,
                    file_id         TEXT NOT NULL,
                    downloaded_at   TIMESTAMP DEFAULT NOW()
                );
            """)

    # ===== USER ACCESS =====
    def get_user_access(self, user_id: int):
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM users_access WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
        if row:
            return {
                'user_id': row['user_id'],
                'expires_at': row['expires_at'],
                'order_id': row['order_id']
            }
        return None

    def grant_access(self, user_id: int, expires_at: datetime, order_id: str):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO users_access (user_id, expires_at, order_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    expires_at = EXCLUDED.expires_at,
                    order_id   = EXCLUDED.order_id
            """, (user_id, expires_at, order_id))

    # ===== ORDERS =====
    def save_order(self, user_id: int, order_id: str, amount: int, days: int):
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO orders (order_id, user_id, amount, days, status)
                VALUES (%s, %s, %s, %s, 'pending')
                ON CONFLICT (order_id) DO NOTHING
            """, (order_id, user_id, amount, days))

    def get_order(self, order_id: str):
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def mark_order_paid(self, order_id: str):
        with self._get_cursor() as cur:
            cur.execute("UPDATE orders SET status = 'paid' WHERE order_id = %s", (order_id,))

    # ===== FILES =====
    def add_file(self, title: str, description: str, file_type: str, telegram_file_id: str) -> str:
        file_id = str(uuid.uuid4())[:8].upper()
        with self._get_cursor() as cur:
            cur.execute("""
                INSERT INTO files (id, title, description, file_type, telegram_file_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (file_id, title, description, file_type, telegram_file_id))
        return file_id

    def get_file(self, file_id: str):
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM files WHERE id = %s", (file_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_all_files(self):
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM files ORDER BY upload_date DESC")
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def delete_file(self, file_id: str):
        with self._get_cursor() as cur:
            cur.execute("DELETE FROM files WHERE id = %s", (file_id,))

    # ===== LOGS =====
    def log_download(self, user_id: int, file_id: str):
        with self._get_cursor() as cur:
            cur.execute(
                "INSERT INTO download_logs (user_id, file_id) VALUES (%s, %s)",
                (user_id, file_id)
            )

db = Database()
