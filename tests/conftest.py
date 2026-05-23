import os
import tempfile
import pytest
from pathlib import Path
import database.connection as db_conn


fd, temp_db_path = tempfile.mkstemp(suffix='.sqlite3')
os.close(fd)

db_conn.DB_PATH = Path(temp_db_path)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    conn = db_conn.get_connection()
    conn.close()

    yield

    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except Exception:
            pass


@pytest.fixture(autouse=True)
def clear_setup_test_db():
    conn = db_conn.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM passwords;")
        cursor.execute("DELETE FROM password_types;")
        cursor.execute("DELETE FROM users;")
        conn.commit()
    except Exception:
        pass

    finally:
        conn.close()