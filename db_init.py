import sqlite3
import os

DB_FILE = 'readings.db'


def create_database():
    """Creates the database and table if they don't exist."""

    # Delete old DB file if it exists, for a clean start
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create a table: 'readings'
        # 'timestamp' will be a text string
        # 'pot_value' will be an integer
        cursor.execute('''
                       CREATE TABLE readings
                       (
                           id        INTEGER PRIMARY KEY AUTOINCREMENT,
                           timestamp TEXT NOT NULL,
            pot_value INTEGER NOT NULL
        )
        ''')

        print("Database and 'readings' table created successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_database()
