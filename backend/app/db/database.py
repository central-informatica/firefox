from contextlib import contextmanager
from backend.app.utils.db_sqlite import getDb

@contextmanager
def db_session():
    conn = getDb()
    try:
        yield conn
    finally:
        conn.close()
