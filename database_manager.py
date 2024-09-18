import sqlite3
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        # self.upgrade_database()

    def initialize_database(self, directory):
        self.connection = sqlite3.connect(self.db_file)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER,
                symbol_name TEXT,
                symbol_type TEXT,
                location TEXT,
                line_start INTEGER,
                line_end INTEGER,
                modified_at TEXT,
                include_in_dump INTEGER DEFAULT 1,
                FOREIGN KEY(parent_id) REFERENCES symbols(id)
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS remote_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                include_in_dump INTEGER DEFAULT 1
            )
        """
        )
        # Initialize default settings
        cursor.execute(
            """
            INSERT OR IGNORE INTO settings (key, value) VALUES
            ('directory', ?),
            ('file_type_filter', '*.py'),
            ('exclude_patterns', '__init__;venv;migrations;.idea;__pycache__'),
            ('excluded_files', ''),
            ('remote_urls', ''),
            ('remote_depth', '0'),
            ('convert_html_to_md', '1'),
            ('css_selectors', '')
            """
            , (directory,))
        self.connection.commit()
        self.connection.close()

    def upgrade_database(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        # Dodanie kolumn, jeśli nie istnieją
        cursor.execute('PRAGMA table_info(settings)')
        settings_columns = [column[1] for column in cursor.fetchall()]
        required_settings = ['remote_urls', 'remote_depth', 'convert_html_to_md', 'css_selectors']
        for setting in required_settings:
            if setting not in settings_columns:
                cursor.execute(f'ALTER TABLE settings ADD COLUMN {setting} TEXT DEFAULT ""')

        cursor.execute('PRAGMA table_info(symbols)')
        symbols_columns = [column[1] for column in cursor.fetchall()]
        if 'include_in_dump' not in symbols_columns:
            cursor.execute('ALTER TABLE symbols ADD COLUMN include_in_dump INTEGER DEFAULT 1')

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='remote_pages'"
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE TABLE remote_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    include_in_dump INTEGER DEFAULT 1
                )
            """
            )
        connection.commit()
        connection.close()

    def save_remote_settings(self, settings):
        logging.debug(f"Saving remote settings: {settings}")
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        for key, value in settings.items():
            cursor.execute('REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        connection.commit()
        connection.close()

    def load_remote_settings(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'remote_%'")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        logging.debug(f"Loaded remote settings: {settings}")
        connection.close()
        return settings

    def update_remote_pages(self, pages):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        # Clear existing remote pages
        cursor.execute('DELETE FROM remote_pages')
        # Insert new pages
        for page in pages:
            cursor.execute('''
                INSERT INTO remote_pages (url, title, include_in_dump)
                VALUES (?, ?, ?)
            ''', (page['url'], page['title'], page.get('include_in_dump', 1)))
        connection.commit()
        connection.close()

    def get_all_remote_pages(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM remote_pages')
        rows = cursor.fetchall()
        connection.close()
        remote_pages = []
        for row in rows:
            remote_pages.append({
                "id": row[0],
                "url": row[1],
                "title": row[2],
                "include_in_dump": row[3],
            })
        return remote_pages

    def update_remote_page_include_state(self, page_id, include_in_dump):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('UPDATE remote_pages SET include_in_dump = ? WHERE id = ?', (include_in_dump, page_id))
        connection.commit()
        connection.close()


    def upgrade_database(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        # Upgrade symbols table
        cursor.execute("PRAGMA table_info(symbols)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'include_in_dump' not in columns:
            cursor.execute("ALTER TABLE symbols ADD COLUMN include_in_dump INTEGER DEFAULT 1")

        # Create remote_pages table if it doesn't exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='remote_pages'")
        if not cursor.fetchone():
            cursor.execute('''
                CREATE TABLE remote_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    title TEXT,
                    include_in_dump INTEGER DEFAULT 1
                )
            ''')

        connection.commit()
        connection.close()


    def load_settings(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT key, value FROM settings')
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        connection.close()
        return settings

    def save_settings(self, settings):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        for key, value in settings.items():
            cursor.execute('REPLACE INTO settings (key, value) VALUES (?, ?)',
                (key, value))
        connection.commit()
        connection.close()

    def insert_symbol(self, symbol):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO symbols (parent_id, symbol_name, symbol_type, location, line_start, line_end, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol.get('parent_id'),
            symbol['symbol_name'],
            symbol['symbol_type'],
            symbol['location'],
            symbol['line_start'],
            symbol['line_end'],
            symbol['modified_at']
        ))
        symbol_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return symbol_id

    def update_symbol_include_state(self, symbol_id, include_in_dump):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('UPDATE symbols SET include_in_dump = ? WHERE id = ?', (include_in_dump, symbol_id))
        connection.commit()
        connection.close()

    def update_symbols(self, symbols):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        # Delete existing symbols for the files being reindexed
        file_paths = {symbol['location'] for symbol in symbols}
        cursor.executemany('DELETE FROM symbols WHERE location = ?', [(path,) for path in file_paths])

        # Insert new symbols
        for symbol in symbols:
            cursor.execute('''
                INSERT INTO symbols (parent_id, symbol_name, symbol_type, location, line_start, line_end, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol.get('parent_id'),
                symbol['symbol_name'],
                symbol['symbol_type'],
                symbol['location'],
                symbol['line_start'],
                symbol['line_end'],
                symbol['modified_at']
            ))
        connection.commit()
        connection.close()

    def remove_symbols_of_deleted_files(self, directory_path, exclude_patterns):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT location FROM symbols')
        stored_files = {row[0] for row in cursor.fetchall()}

        existing_files = set()
        for root, dirs, files in os.walk(directory_path):
            root = os.path.normpath(root)
            dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in exclude_patterns)]
            for file in files:
                file_path = os.path.normpath(os.path.join(root, file))
                if any(pattern in file_path for pattern in exclude_patterns):
                    continue
                if file.endswith('.py'):
                    existing_files.add(file_path)

        files_to_remove = stored_files - existing_files
        cursor.executemany('DELETE FROM symbols WHERE location = ?', [(path,) for path in files_to_remove])
        connection.commit()
        connection.close()

    def get_last_modified_time(self, file_path):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT MAX(modified_at) FROM symbols WHERE location = ?', (file_path,))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result[0] else None

    def get_all_symbols(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM symbols')
        rows = cursor.fetchall()
        connection.close()
        symbols = []
        for row in rows:
            symbols.append({
                "id": row[0],
                "parent_id": row[1],
                "symbol_name": row[2],
                "symbol_type": row[3],
                "location": row[4],
                "line_start": row[5],
                "line_end": row[6],
                "modified_at": row[7],
                "include_in_dump": row[8],  # Added this line
            })
        return symbols

    def get_symbols_to_exclude(self):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        cursor.execute('''
            SELECT location, symbol_name, symbol_type FROM symbols
            WHERE include_in_dump = 0
        ''')
        rows = cursor.fetchall()
        connection.close()
        # Return a set of tuples for quick lookup
        symbols_to_exclude = set((os.path.normpath(row[0]), row[1], row[2]) for row in rows)
        return symbols_to_exclude


    def remove_symbols_of_unselected_files(self, selected_files):
        connection = sqlite3.connect(self.db_file)
        cursor = connection.cursor()
        # Get all files currently in the symbols table
        cursor.execute('SELECT DISTINCT location FROM symbols')
        stored_files = {row[0] for row in cursor.fetchall()}
        selected_files_set = set(selected_files)
        # Identify files that are in the database but not selected
        files_to_remove = stored_files - selected_files_set
        cursor.executemany('DELETE FROM symbols WHERE location = ?', [(path,) for path in files_to_remove])
        connection.commit()
        connection.close()
