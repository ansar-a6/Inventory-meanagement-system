import sqlite3
import os

# Define the name for our app's data folder
_APP_NAME = "InventoryManagement"
# Get the user's local app data folder
_APPDATA_PATH = os.getenv('LOCALAPPDATA')
# Construct the path to our app's data directory
_APP_DATA_DIR = os.path.join(_APPDATA_PATH, _APP_NAME)

# Define the absolute path to the database file
DB_FILE = os.path.join(_APP_DATA_DIR, 'inventory.db')

def initialize_database():
    """
    Ensures the database directory in the user's appdata exists, and creates tables
    if they don't. This should be called once at application startup.
    """
    # Ensure the directory in appdata exists
    if not os.path.exists(_APP_DATA_DIR):
        os.makedirs(_APP_DATA_DIR)
        print(f"Created application data directory: {_APP_DATA_DIR}")

    # The connect() call will create the file if it doesn't exist.
    # Then we can create the tables.
    create_tables()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the necessary tables in the database if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Raw Materials Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            image BLOB
        )
    ''')

    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            image BLOB
        )
    ''')

    # Product Components (BOM) Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            raw_material_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
    ''')

    # Bills Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL
        )
    ''')

    # Bill Items Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print("Database and tables initialized successfully.")