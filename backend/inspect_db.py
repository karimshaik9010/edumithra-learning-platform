import sqlite3

def inspect_table(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"Table: {table_name}")
        for col in columns:
            print(f"  Column: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")
    finally:
        conn.close()

db_paths = ['backend/edumithra.db', 'edumithra.db']
for db_path in db_paths:
    print(f"=== Database: {db_path} ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    for table in tables:
        inspect_table(db_path, table[0])
