import sqlite3
import os

def test_schema_integrity():
    assert os.path.exists("schema.sql")

def test_database_exists():
    assert os.path.exists("database.db")
