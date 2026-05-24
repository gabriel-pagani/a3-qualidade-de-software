import sqlite3
import tempfile
import shutil
import os
from pathlib import Path


DB_FILE = 'db.sqlite3'
DB_PATH = Path(__file__).resolve().parent / DB_FILE


def tables_exist(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='users' LIMIT 1"
    ).fetchone()
    return row is not None


def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salt BLOB NOT NULL,
            username TEXT NOT NULL UNIQUE, 
            master_password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        );
                       
        CREATE TABLE IF NOT EXISTS password_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
                       
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type_id INTEGER,
            metadata_iv BLOB NOT NULL,
            encrypted_metadata BLOB NOT NULL,
            secret_iv BLOB NOT NULL,
            encrypted_secret BLOB NOT NULL,
            created_at DATETIME DEFAULT (datetime('now', 'localtime')),
            updated_at DATETIME,

            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (type_id) REFERENCES password_types(id) ON DELETE SET NULL
        );
                       
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_id INTEGER,
            user_id INTEGER NOT NULL,
            type_id INTEGER,
            metadata_iv BLOB NOT NULL,
            encrypted_metadata BLOB NOT NULL,
            secret_iv BLOB NOT NULL,
            encrypted_secret BLOB NOT NULL,
            changed_at DATETIME DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (password_id) REFERENCES passwords(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (type_id) REFERENCES password_types(id) ON DELETE SET NULL
        );
                       
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_date DATETIME DEFAULT (datetime('now', 'localtime')),
                       
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
                             
        CREATE INDEX IF NOT EXISTS idx_passwords_user ON passwords(user_id);
        CREATE INDEX IF NOT EXISTS idx_passwords_type ON passwords(type_id);
        CREATE INDEX IF NOT EXISTS idx_password_history_password ON password_history(password_id);
                             
        CREATE TRIGGER IF NOT EXISTS trg_passwords_updated
        AFTER UPDATE ON passwords
        FOR EACH ROW
        WHEN NEW.updated_at IS OLD.updated_at
        BEGIN
            UPDATE passwords
            SET updated_at = datetime('now', 'localtime')
            WHERE id = NEW.id;
        END;

        CREATE TRIGGER IF NOT EXISTS trg_passwords_history
        BEFORE UPDATE OF metadata_iv, encrypted_metadata, secret_iv, encrypted_secret ON passwords
        FOR EACH ROW
        BEGIN
            INSERT INTO password_history (
                password_id,
                user_id,
                type_id,
                metadata_iv,
                encrypted_metadata,
                secret_iv,
                encrypted_secret,
                changed_at
            )
            VALUES (
                OLD.id,
                OLD.user_id,
                OLD.type_id,
                OLD.metadata_iv,
                OLD.encrypted_metadata,
                OLD.secret_iv,
                OLD.encrypted_secret,
                datetime('now', 'localtime')
            );
        END;
    """)


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON;")

    if not tables_exist(conn):
        create_tables(conn)

    return conn


def execute_query(query: str, params = None):
    with get_connection() as conn:
        cursor = conn.cursor()

        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if cursor.description is not None:
            return cursor.fetchall()


def is_valid_database_file(file_path: str) -> bool:
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.sqlite3')
    os.close(temp_db_fd)
    
    try:
        shutil.copy(file_path, temp_db_path)
        
        conn = sqlite3.connect(temp_db_path)
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}
            
            required_tables = {'users', 'passwords', 'password_types'}
            
            if not required_tables.issubset(tables):
                return False
                
            return True

        finally:
            conn.close()
    
    except Exception as e:
        print(f"sandbox-error: {e}")
        return False
    
    finally:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
