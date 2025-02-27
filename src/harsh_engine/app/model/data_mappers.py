import sqlite3
from harsh_engine.app.model import entities
from harsh_engine.app import utils

class SQLiteDataMapper:
    def __init__(self, enable_foreign_keys=False):
        self._db = None
        self._enable_foreign_keys = enable_foreign_keys

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, db: sqlite3.Connection):
        self._db = db
        if self._enable_foreign_keys:
            self._db.execute("PRAGMA foreign_keys = 1") # see https://stackoverflow.com/questions/29420910/how-do-i-enforce-foreign-keys

    def _exec_dql_command(self, stmt: str, args: tuple = (), return_one=False) -> list:
        """
        Executes a general Data Query Language (DQL) command (e.g. SELECT) on the SQLite database.

        Largely the same as query_db() function from https://flask.palletsprojects.com/en/stable/patterns/sqlite3/.
        """

        cursor = self._db.execute(stmt, args)
        result_vals = cursor.fetchall()
        cursor.close()

        if return_one:
            return result_vals[0] if result_vals else []
        else:
            return result_vals

    def _exec_dml_command(self, stmt: str, args: tuple = (), do_insert=True) -> int:
        """
        Executes a general Data Manipulation Language (DML) command (e.g. INSERT, UPDATE) on the SQLite database.
        """

        cursor = self._db.execute(stmt, args)
        self._db.commit()

        if do_insert:
            # applies only to INSERT
            res = cursor.lastrowid
        else:
            # applies to UPDATE, DELETE 
            res = cursor.rowcount # see https://stackoverflow.com/questions/2316003/get-number-of-modified-rows-after-sqlite3-execute-in-python?noredirect=1&lq=1

        cursor.close()
        return res

class UserMapper(SQLiteDataMapper):
    def __init__(self, enable_foreign_keys=False):
        super().__init__(enable_foreign_keys)

    def create(self, user:entities.User):
        stmt = """INSERT INTO users (username,password,join_time,last_seen_time) VALUES (?,?,?,?)"""
        
        user_id = super()._exec_dml_command(stmt, args=user.to_tuple(incld_id=False, dt_to_unix=True), do_insert=True)
        
        return utils.ModelState(valid=True, message=f'Successfully created new User with id {user_id}', data=[user])
    