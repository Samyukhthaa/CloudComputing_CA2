import sys
sys.path.append(".")

from backend.database import connect_db

def test_database_connection():
    conn = connect_db()
    assert conn is not None
    conn.close()
