import os
import sqlite3
from app.database import create_tables_entries, DB_NAME

# Delete existing database file if present
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Deleted existing database: {DB_NAME}")
else:
    print(f"No database file found at {DB_NAME}. Creating fresh one...")

# Recreate clean tables
create_tables_entries()
print("Recreated clean empty database with 'manual_entries' table!")
