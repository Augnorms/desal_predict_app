import sqlite3

DB_NAME = "plant_data.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


##################################
#  create table for manual data entries
#################################

def create_tables_entries():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manual_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operator_id TEXT,
        feed_flowrate REAL,
        feed_tds REAL,
        feed_salinity REAL,
        temperature REAL,
        recovery REAL,
        flux REAL,
        pressure_drop REAL,
        permeate_flowrate REAL,
        permeate_tds REAL,
        status TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print("[Database] Table created successfully!")


def save_entry(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO manual_entries (
        operator_id, feed_flowrate, feed_tds, feed_salinity,
        temperature, recovery, flux, pressure_drop,
        permeate_flowrate, permeate_tds, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('operator_id', 'Unknown'),
        data.get('feed_flowrate'),
        data.get('feed_tds'),
        data.get('feed_salinity'),
        data.get('temperature'),
        data.get('recovery'),
        data.get('flux'),
        data.get('pressure_drop'),
        data.get('permeate_flowrate'),
        data.get('permeate_tds'),
        data.get('status')
    ))
    
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id


# retrieve all entries from db
def get_entries():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM manual_entries")
    
    entries = cursor.fetchall()
    conn.close()
    
    return entries


# retrieve by id
def get_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM manual_entries WHERE id = ?", (entry_id,))
    
    entry = cursor.fetchone()
    conn.close()
    
    return entry

##################################
#  
#################################

