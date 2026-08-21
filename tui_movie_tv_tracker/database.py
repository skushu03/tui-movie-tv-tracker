import datetime
import sqlite3 as sqlite
from pathlib import Path


def init_db(db):
    cursor = db.cursor()
    # movies and shows can have the same tmdb id!!!!!!!!!
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
            title TEXT NOT NULL,
            tmdb_id INTEGER PRIMARY KEY ,
            rating TEXT NOT NULL,
            num_ratings INTEGER NOT NULL,
            release_date TEXT NOT NULL,
            media_type TEXT NOT NULL
        )
    """

    create_list_items_table = """
        CREATE TABLE IF NOT EXISTS list_items(
            tmdb_id INTEGER NOT NULL,
            list_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            FOREIGN KEY (list_id) REFERENCES lists (id) ON DELETE CASCADE,
            FOREIGN KEY (tmdb_id) REFERENCES media_info (tmdb_id),
            PRIMARY KEY (list_id, tmdb_id, media_type)
        );
    """

    # date must be YYYY-MM-DD HH:MM
    create_diary = """
        CREATE TABLE IF NOT EXISTS diary(
            tmdb_id INTEGER NOT NULL,
            media_type TEXT NOT NULL, 
            date TEXT NOT NULL, 
            FOREIGN KEY (tmdb_id) REFERENCES media_info (tmdb_id),
            PRIMARY KEY (tmdb_id, media_type, date)
        )
    """

    cursor.execute(create_lists_table)
    cursor.execute(create_media_info_table)
    cursor.execute(create_list_items_table)
    cursor.execute(create_diary)

    db.commit()

    cursor.close()


def get_db(db_name="movie_tv_tracker.db"):
    try:
        # hidden directory to store the databases
        home_dir = Path.home()

        db_dir = home_dir / ".tui_media_tracker"
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

        query = """SELECT mi.title, mi.tmdb_id, mi.rating, mi.release_date, mi.media_type, mi.num_ratings
        FROM media_info mi JOIN list_items li 
        ON mi.tmdb_id = li.tmdb_id 
        WHERE li.list_id = ? AND mi.media_type = li.media_type
        """

        cursor.execute(query, (list_id,))

        results = cursor.fetchall()

        list_items = []
        for r in results:
            list_items.append(
                {
                    "title": r["title"],
                    "tmdb_id": r["tmdb_id"],
                    "release_date": r["release_date"],
                    "media_type": r["media_type"],
                    "rating": r["rating"],
                    "num_ratings": r["num_ratings"],
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

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
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


def get_watched(db):
    try:
        cursor = db.cursor()

        query = "SELECT tmdb_id, media_type FROM diary"
        cursor.execute(query)

        results = cursor.fetchall()

        watched = []
        for res in results:
            watched.append((res["tmdb_id"], res["media_type"]))

        return set(watched)
    except sqlite.Error as e:
        raise Exception(f"Database Error while getting watched media: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while getting watched media: {e}")
    finally:
        cursor.close()


def add_diary_entry(db, data, watched_set):
    try:
        cursor = db.cursor()
        # chcek if media info alreday in db
        query = "SELECT title FROM media_info WHERE tmdb_id = ? AND media_type = ?"
        # if not add
        cursor.execute(query, (data["tmdb_id"], data["media_type"]))
        if not cursor.fetchone():
            query = "INSERT INTO media_info (title, tmdb_id, rating, num_ratings, release_date, media_type) VALUES (?, ?, ?, ?, ?, ?)"

            cursor.execute(
                query,
                (
                    data["title"],
                    data["tmdb_id"],
                    data["rating"],
                    data["num_ratings"],
                    data["release_date"],
                    data["media_type"],
                ),
            )
        # add to diary
        query = "INSERT INTO diary (tmdb_id, media_type, date) VALUES (?, ?, ?)"

        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(query, (data["tmdb_id"], data["media_type"], date))

        db.commit()

        watched_set.add((data["tmdb_id"], data["media_type"]))

    except sqlite.IntegrityError as e:
        raise Exception(f"Database conflict: {e}")
    except sqlite.Error as e:
        raise Exception(f"Database Error while creating a new diary entry: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while adding diary entry: {e}")
    finally:
        cursor.close()


def delete_diary_entry(db, data, watched_set):
    try:
        cursor = db.cursor()
        # check for multiple entries for the same show, if there are multiple, dont remove from set

        query = "SELECT date FROM diary WHERE tmdb_id = ? AND media_type = ?"

        cursor.execute(query, (data["tmdb_id"], data["media_type"]))
        results = cursor.fetchall()

        query = "DELETE FROM diary WHERE tmdb_id = ? AND media_type = ? AND date = ?"

        cursor.execute(query, (data["tmdb_id"], data["media_type"], data["date"]))

        db.commit()

        if len(results) == 1:
            watched_set.remove((data["tmdb_id"], data["media_type"]))

    except sqlite.Error as e:
        raise Exception(f"Database Error while deleting a diary entry: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while removing diary entry: {e}")
    finally:
        cursor.close()


def get_lists_contain_media(db, media_type, tmdb_id):
    # gets all the lists with "contains" key for each list that indicates if it contains given media
    try:
        cursor = db.cursor()

        query = """
            SELECT l.id, l.name, l.last_updated,
            EXISTS (
                    SELECT 1 FROM list_items
                    WHERE tmdb_id = ? AND list_id = l.id AND media_type = ? 
            ) as contains
            FROM lists l
        """

        cursor.execute(query, (tmdb_id, media_type))

        results = cursor.fetchall()

        return results

    except sqlite.Error as e:
        raise Exception(f"Database Error while getting lists: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while removing diary entry: {e}")
    finally:
        cursor.close()


def search_media_in_list(db, media_type, tmdb_id, list_id):
    # check if media is in given list
    try:
        cursor = db.cursor()

        query = "SELECT tmdb_id FROM list_items WHERE tmdb_id = ? AND list_id = ? AND media_type = ?"

        cursor.execute(query, (tmdb_id, list_id, media_type))

        if cursor.fetchone():
            return True

        return False

    except Exception as e:
        raise Exception(f"Unexpected Error searching list for media: {e}")
    finally:
        cursor.close()


def add_list_item(db, media_data, list_id):
    try:
        cursor = db.cursor()

        # check if media_info entry/row exists for this media
        query = "SELECT 1 FROM media_info WHERE tmdb_id = ? AND media_type = ?"
        cursor.execute(query, (media_data["tmdb_id"], media_data["media_type"]))

        if not cursor.fetchone():
            query = "INSERT INTO media_info (title, tmdb_id, rating, num_ratings, release_date, media_type) VALUES (?, ?, ?, ?, ?, ?)"

            cursor.execute(
                query,
                (
                    media_data["title"],
                    media_data["tmdb_id"],
                    media_data["rating"],
                    media_data["num_ratings"],
                    media_data["release_date"],
                    media_data["media_type"],
                ),
            )
        # tmdb, list med
        query = "INSERT INTO list_items (tmdb_id, list_id, media_type) VALUES (?, ?, ?) ON CONFLICT (tmdb_id, list_id, media_type) DO NOTHING"

        cursor.execute(
            query, (media_data["tmdb_id"], list_id, media_data["media_type"])
        )

        db.commit()

    except sqlite.IntegrityError as e:
        raise Exception(f"Database conflict: {e}")
    except sqlite.Error as e:
        raise Exception(f"Database Error while adding an item to a list: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while adding item to list: {e}")
    finally:
        cursor.close()


def delete_list_item(db, media_data, list_id):
    try:
        cursor = db.cursor()
        # tmdb, list med
        query = (
            "DELETE FROM list_items WHERE tmdb_id = ? AND list_id = ? AND media_type =?"
        )

        cursor.execute(
            query, (media_data["tmdb_id"], list_id, media_data["media_type"])
        )

        db.commit()

    except sqlite.IntegrityError as e:
        raise Exception(f"Database conflict: {e}")
    except sqlite.Error as e:
        raise Exception(f"Database Error while adding an item to a list: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while adding item to list: {e}")
    finally:
        cursor.close()


def get_media_info(db, tmdb_id, media_type):
    try:
        cursor = db.cursor()

        query = "SELECT mi.title, mi.rating, mi.num_ratings, mi.media_type, mi.release_date FROM media_info mi WHERE mi.tmdb_id = ? AND mi.media_type = ?"

        cursor.execute(query, (tmdb_id, media_type))

        res = cursor.fetchone()

        if res:
            return {
                "title": res["title"],
                "release_date": res["release_date"],
                "rating": res["rating"],
                "num_ratings": res["num_ratings"],
                "media_type": res["media_type"],
            }
        return {}
    except sqlite.Error as e:
        raise Exception(f"Database Error while getting media info: {e}")
    except Exception as e:
        raise Exception(f"Unexpected Error while getting media info: {e}")
    finally:
        cursor.close()
