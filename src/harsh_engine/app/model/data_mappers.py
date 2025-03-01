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
        '''
        Create a new user in the database
        '''

        res = None

        stmt = """INSERT INTO users (username,password,join_time,last_seen_time) VALUES (?,?,?,?)"""
        
        try:
            user_id = super()._exec_dml_command(stmt, args=user.to_tuple(incld_id=False, dt_to_unix=True), do_insert=True)
            res = utils.ModelState(valid=True, message=f'Successfully created new user with ID {user_id} and username {user.username}', data=[user])
        except Exception as e:
            if type(e) == sqlite3.IntegrityError:
                res = utils.ModelState(valid=False, message=f'Username {user.username} already taken', data=[e])
            else:
                res = utils.ModelState(valid=False, message=str(e), data=[e])

        return res
    
    def read_by_credentials(self, username:str, password_hash:str):
        '''
        Read a user from the database based on their username and password hash
        '''

        stmt = f'SELECT * FROM users WHERE username = \'{username}\' AND password = \'{password_hash}\''

        try:
            records = self._exec_dql_command(
                stmt, 
                args=tuple(), 
                return_one=True
                )
            
            if len(records) > 0:
                user = entities.User(**dict(records))
            else:
                user = None

            res = utils.ModelState(valid=True, message=f"Found {len(records)} user(s) matching query", data=[] if user is None else [user])
        except Exception as e:
            res = utils.ModelState(valid=False, message=str(e), data=[e])
            
        return res
    
    def read_by_id(self, user_id:int):
        '''
        Read a user from the database based on their unique numeric ID
        '''

        stmt = 'SELECT * FROM users WHERE id = ?'

        try:
            records = self._exec_dql_command(stmt, args=(user_id,), return_one=True)

            user = entities.User(**dict(records))

            res = utils.ModelState(valid=True, message=f"Found 1 user matching query", data=[user])
        except Exception as e:
            res = utils.ModelState(valid=False, message=str(e), data=[e])

        return res

    