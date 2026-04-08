import sqlite3
import sys

db_path = sys.argv[1] if len(sys.argv) > 1 else '/app/exam_system/exam_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")
conn.close()
