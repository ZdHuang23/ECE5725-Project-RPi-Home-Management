import sqlite3
from datetime import datetime

# a class of database that stores two kinds of log together
class logDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                location TEXT NOT NULL,
                name TEXT NOT NULL,
                time TEXT NOT NULL,
                photo_file_name TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insert(self, location, name, photo_file_name):
        if not photo_file_name:
            raise ValueError("photo_file_name cannot be null")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO rooms (location, name, time, photo_file_name)
            VALUES (?, ?, ?, ?)
        ''', (location, name, current_time, photo_file_name))
        self.conn.commit()

    def remove(self, entry_id):
        self.cursor.execute('DELETE FROM rooms WHERE id = ?', (entry_id,))
        self.conn.commit()

    def search_on_room(self, location):
        self.cursor.execute('SELECT * FROM rooms WHERE location = ?', (location,))
        return self.cursor.fetchall()

    def search_on_name(self, name):
        self.cursor.execute('SELECT * FROM rooms WHERE name = ?', (name,))
        return self.cursor.fetchall()

    def traverse(self):
        self.cursor.execute('SELECT * FROM rooms')
        return self.cursor.fetchall()

    def list_recent_entries(self, count=3):
        self.cursor.execute('SELECT * FROM rooms ORDER BY time DESC LIMIT ?', (count,))
        return self.cursor.fetchall()

    def list_recent_entries_by_name_or_location_with_limit(self, n, name=None, location=None):
        query = 'SELECT * FROM rooms WHERE '
        params = []
        
        if name and location:
            query += 'name = ? AND location = ? '
            params.extend([name, location])
        elif name:
            query += 'name = ? '
            params.append(name)
        elif location:
            query += 'location = ? '
            params.append(location)
        else:
            return []  # No name or location provided, return empty list

        query += 'ORDER BY time DESC LIMIT ?'
        params.append(n)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def traverse_recent_entries_with_photo(self, n):
        self.cursor.execute('''
            SELECT * FROM rooms
            WHERE photo_file_name != 'None'
            ORDER BY time DESC
            LIMIT ?
        ''', (n,))
        return self.cursor.fetchall()

    def clean_database(self):
        self.cursor.execute('DELETE FROM rooms')
        self.conn.commit()

    def close(self):
        self.conn.close()


log = logDB("ROOM.db")
# log.insert("DOOR","ZIDONG","None")
# log.insert("DOOR","UNKNOWN","None")
# log.insert("DOOR","UNKNOWN","None")
# print(log.list_recent_entries(3))
log.clean_database()
# print(log.list_recent_entries(3))
# print(log.list_recent_entries_by_name_or_location_with_limit(4,location="DOOR"))