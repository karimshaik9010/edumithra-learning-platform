import sqlite3
import traceback

try:
    conn = sqlite3.connect('backend/edumithra.db')
    conn.execute('ALTER TABLE profiles RENAME COLUMN target_date TO study_duration;')
    conn.commit()
    print("Migration successful.")
except Exception as e:
    print(f"Error during migration: {e}")
    traceback.print_exc()
finally:
    if 'conn' in locals():
        conn.close()
