import sqlite3

# Path to your SQLite file
db_path = 'src/assets/database/qdrant_db/collection/collection_4/storage.sqlite'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the list of tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print("-", table[0])

# Optionally: Print contents of each table
for table in tables:
    table_name = table[0]
    print(f"\nContents of table '{table_name}':")
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
    rows = cursor.fetchall()
    col_names = [description[0] for description in cursor.description]
    print(" | ".join(col_names))
    
    for row in rows:
        # Print raw and parsed form
        print("--- RAW ---")
        print(row)
        
        print("--- PARSED ---")
        for col, val in zip(col_names, row):
            if isinstance(val, bytes):
                try:
                    import numpy as np
                    vec = np.frombuffer(val, dtype=np.float32)
                    print(f"{col} (decoded vector):", vec)
                except:
                    print(f"{col} (raw bytes):", val[:10], "...")
            else:
                print(f"{col}:", val)
