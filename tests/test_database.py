import os
import tempfile
import sqlite3
from database.connection import is_valid_database_file


def test_is_valid_database_file():
    fd, temp_path = tempfile.mkstemp(suffix='.sqlite3')
    os.close(fd)

    try:
        conn = sqlite3.connect(temp_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY);")
        conn.execute("CREATE TABLE passwords (id INTEGER PRIMARY KEY);")
        conn.execute("CREATE TABLE password_types (id INTEGER PRIMARY KEY);")
        conn.close()

        assert is_valid_database_file(temp_path) is True
    finally:
        os.remove(temp_path)


def test_is_valid_database_file_missing_tables():
    fd, temp_path = tempfile.mkstemp(suffix='.sqlite3')
    os.close(fd)

    try:
        conn = sqlite3.connect(temp_path)
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY);")
        conn.close()

        assert is_valid_database_file(temp_path) is False
    finally:
        os.remove(temp_path)


def test_is_valid_database_file_invalid_format():
    fd, temp_path = tempfile.mkstemp(suffix='.sqlite3')

    with os.fdopen(fd, 'w') as f:
        f.write("Este não é um banco de dados válido.")

    try:
        assert is_valid_database_file(temp_path) is False
    finally:
        os.remove(temp_path)


def test_is_valid_database_file_not_found():
    fake_path = "caminho_inexistente_para_banco.sqlite3"
    
    assert is_valid_database_file(fake_path) is False
