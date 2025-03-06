import sqlite3
from flask import current_app, g
from harsh_engine.app.model import data_mappers
from harsh_engine.app import utils

# code largely taken from the Flask SQLite example
# see https://flask.palletsprojects.com/en/stable/patterns/sqlite3/

def get_db_conn() -> sqlite3.Connection:
    '''
    Establishes a database connection and stores it in the current (global) app context
    '''

    if 'db_conn' not in g:
        g.db_conn = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db_conn.row_factory = sqlite3.Row

    return g.db_conn

def init_db(schema: str | None = None):
    '''
    Creates a database according to the provided schema and defines how to shut it down when the current app context is done

    Also populates database with some dummy users
    '''

    db_conn = get_db_conn()

    if schema is not None:
        with current_app.open_resource(schema) as f:
            db_conn.executescript(f.read().decode('utf8'))

    users = utils.generate_dummy_users(n_users=current_app.config['N_DUMMY_USERS'], seed=current_app.config['SEED'])

    data_mapper = data_mappers.UserMapper()
    data_mapper.db_conn = db_conn

    for user in users:
        _ = data_mapper.create(user)

    current_app.teardown_appcontext(close_db_conn)

def close_db_conn(exception=None):
    db_conn = g.pop('db_conn', None)

    if db_conn is not None:
        db_conn.close()