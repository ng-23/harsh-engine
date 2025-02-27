import sqlite3
from flask import current_app, g

# code largely taken from the Flask SQLite example
# see https://flask.palletsprojects.com/en/stable/patterns/sqlite3/


def get_db() -> sqlite3.Connection:
    """
    Establishes a database connection and stores it in the current (global) app/request context
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def init_db(schema: str | None = None):
    """
    Creates a database according to the provided schema and defines how to shut it down when the current app context is done
    """
    db = get_db()

    if schema is not None:
        with current_app.open_resource(schema) as f:
            db.executescript(f.read().decode("utf8"))

    current_app.teardown_appcontext(close_db)


def close_db(exception = None):
    db = g.pop("db", None)

    if db is not None:
        db.close()