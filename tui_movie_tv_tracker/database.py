import datetime
import sqlite3 as sqlite
from pathlib import Path


def init_db(db):
    cursor = db.cursor()

    create_lists_table = """
        CREATE TABLE IF NOT EXISTS lists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            last_updated TEXT NOT NULL,

            UNIQUE(name)
        );
    """

    create_media_info_table = """
        CREATE TABLE IF NOT EXISTS media_info(
            name TEXT NOT NULL,
            tmdb_id INTEGER PRIMARY KEY ,
            rating INTEGER NOT NULL,
            release_date TEXT NOT NULL,
            media_type TEXT NOT NULL,
        )
    """

    create_list_items_table = """
        CREATE TABLE IF NOT EXISTS list_items(
            tmdb_id INTEGER NOT NULL,
            list_id INTEGER NOT NULL,
            FOREIGN KEY (list_id) REFERENCES lists (id) ON DELETE CASCADE,
            FOREIGN KEY (tmdb_id) REFERENCES media_info (tmdb_id) ON DELETE CASCADE,
            PRIMARY KEY (list_id, tmdb_id)
        );
    """

    cursor.execute(create_lists_table)
    cursor.execute(create_media_info_table)
    cursor.execute(create_list_items_table)

    db.commit()

    cursor.close()


def get_db(db_name="movie_tv_tracker.db"):
    try:
        # hidden directory to store the databases
        home_dir = Path.home()

        db_dir = home_dir / ".media_tv_tracker"
        # if db directory doesnt already exists, create
        db_dir.mkdir(exist_ok=True)
        #
        if not db_name.endswith(".db"):
            db_name += ".db"

        db_path = db_dir / db_name

        db = sqlite.connect(str(db_path))
        db.row_factory = sqlite.Row
        db.execute("PRAGMA foreign_keys = ON")

        cursor = db.cursor()

        query = """SELECT name FROM sqlite_master WHERE type='table' AND name='lists'"""

        cursor.execute(query)
        results = cursor.fetchone()

        if results is None:
            init_db(db)

        return db
    except sqlite.Error as e:
        raise Exception(f"Unexpected Database Error when getting the database: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error when getting the database: {e}")
    finally:
        cursor.close()


def get_lists(db):
    try:
        cursor = db.cursor()

        query = """SELECT * FROM lists"""
        cursor.execute(query)

        results = cursor.fetchall()

        lists = []
        for res in results:
            lists.append(
                {
                    "name": res["name"],
                    "id": res["id"],
                    "last_updated": res["last_updated"],
                }
            )

        return lists

    except Exception:
        raise Exception("Unexpected Error while retrieving lists: {e}")
    finally:
        cursor.close()


def get_list_items(db, list_id):
    try:
        cursor = db.cursor()

        query = """SELECT mi.name, mi.tmdb_id, mi.rating, mi.release_date, mi.media_type
        FROM media_info mi JOIN list_items li 
        ON mi.tmdb_id = li.tmdb_id 
        WHERE li.list_id = ?
        """

        cursor.execute(query, (list_id,))

        results = cursor.fetchall()

        list_items = []
        for r in results:
            list_items.append(
                {
                    "name": r["name"],
                    "tmdb_id": r["tmdb_id"],
                    "release_date": r["release_date"],
                    "media_type": r["media_type"],
                }
            )

        return list_items
    except sqlite.Error as e:
        raise Exception(f"Database Error while retrieving list items: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while retrieving list items: {e}")
    finally:
        cursor.close()


def create_list(db, list_name):
    try:
        cursor = db.cursor()

        list_name = list_name.strip()
        if not list_name:
            raise ValueError("List name cannot be blank.")

        query = "SELECT name FROM lists WHERE name = ?"
        cursor.execute(query, (list_name,))

        if cursor.fetchone():
            raise sqlite.IntegrityError("There is already a list with this name.")

        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        query = "INSERT INTO lists (name, last_updated) VALUES (?, ?)"

        cursor.execute(query, (list_name, date))

        db.commit()

    except sqlite.IntegrityError as e:
        raise Exception(f"Database conflict: {e}")
    except sqlite.Error as e:
        raise Exception(f"Database Error while creating a new list: {e}")
    except ValueError as e:
        raise Exception(f"Value Error: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while creating a new list: {e}")
    finally:
        cursor.close()


def delete_list(db, list_name):
    try:
        cursor = db.cursor()

        list_name = list_name.strip()
        if not list_name:
            raise ValueError("Received blank list name.")

        query = "DELETE FROM lists WHERE name = ?"
        cursor.execute(query, (list_name,))

        db.commit()

    except sqlite.Error as e:
        raise Exception(f"Database Error while deleting a list: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while deleting a list: {e}")
    finally:
        cursor.close()
