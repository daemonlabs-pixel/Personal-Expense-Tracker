import sqlite3
from pathlib import Path


project_root = Path(__file__).parent.parent
data_dir = project_root/ "data"
expenses_db_path = data_dir/"expenses.db"

def get_connection(path: Path | None = None)-> sqlite3.Connection:
    if path is None:
        path = expenses_db_path

    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database(path: Path| None = None ):
    conn = None
    try:
        conn = get_connection(path)
        file_sql_path = project_root/ "database"/ "schema.sql"
        file_sql =  file_sql_path.read_text(encoding="utf-8")
        conn.executescript(file_sql)

    finally:
       if conn is not None:
            conn.close()
