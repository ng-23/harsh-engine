import sqlite3
from abc import abstractmethod, ABC
from harsh_engine.app.model import entities
from harsh_engine.app import utils, exceptions

class DataMapper(ABC):
    '''
    An abstract general CRUD operation data mapper, not tied to any specific database
    '''

    @property
    def db_conn(self):
        return self._db_conn
    
    @db_conn.setter
    def db_conn(self, db_conn):
        self._db_conn = db_conn

    @abstractmethod
    def create(self, *args, **kwargs) -> utils.ModelState:
        pass

    @abstractmethod
    def read(self, *args, **kwargs) -> utils.ModelState:
        pass

    @abstractmethod
    def update(self, *args, **kwargs) -> utils.ModelState:
        pass

    @abstractmethod
    def delete(self, *args, **kwargs) -> utils.ModelState:
        pass

class SQLiteDataMapper(DataMapper, ABC): # see https://stackoverflow.com/questions/48336655/how-to-make-an-abstract-class-inherit-from-another-abstract-class-in-python
    '''
    An abstract general data mapper designed specifically to interface with a SQLite database
    '''

    def __init__(self, enable_foreign_keys=False):
        self._db_conn = None
        self._enable_foreign_keys = enable_foreign_keys

    @property
    def db_conn(self):
        return self._db_conn

    @db_conn.setter
    def db_conn(self, db_conn:sqlite3.Connection):
        self._db_conn = db_conn
        if self._enable_foreign_keys:
            self._db_conn.execute('PRAGMA foreign_keys = 1') # see https://stackoverflow.com/questions/29420910/how-do-i-enforce-foreign-keys

    def _exec_dql_command(self, stmt: str, args: tuple = (), return_one=False) -> list:
        '''
        Executes a general Data Query Language (DQL) command (e.g. SELECT) on the SQLite database.

        Largely the same as query_db() function from https://flask.palletsprojects.com/en/stable/patterns/sqlite3/.
        '''

        cursor = self._db_conn.execute(stmt, args)
        result_vals = cursor.fetchall()
        cursor.close()

        if return_one:
            return result_vals[0] if result_vals else []
        else:
            return result_vals

    def _exec_dml_command(self, stmt: str, args: tuple = (), do_insert=True) -> int:
        '''
        Executes a general Data Manipulation Language (DML) command (e.g. INSERT, UPDATE) on the SQLite database.
        '''

        cursor = self._db_conn.execute(stmt, args)
        self._db_conn.commit()

        if do_insert:
            # applies only to INSERT
            res = cursor.lastrowid
        else:
            # applies to UPDATE, DELETE 
            res = cursor.rowcount # see https://stackoverflow.com/questions/2316003/get-number-of-modified-rows-after-sqlite3-execute-in-python?noredirect=1&lq=1

        cursor.close()
        return res
    
    @abstractmethod
    def create(self, entity:entities.Entity, excld_cols:set[str]={}, **kwargs) -> utils.ModelState:
        pass

    @abstractmethod
    def read(self, query_args:utils.QueryArgsBag, return_cols:set[str]={}, **kwargs) -> utils.ModelState:
        pass

    @abstractmethod
    def update(self, query_args:utils.QueryArgsBag, new_col_vals:dict[str,any], **kwargs):
        pass

    @abstractmethod
    def delete(self, query_args:utils.QueryArgsBag, **kwargs):
        pass

class UserMapper(SQLiteDataMapper):
    '''
    A SQLite data mapper for performing CRUD operations on User entities
    '''

    def __init__(self, enable_foreign_keys=False):
        super().__init__(enable_foreign_keys)

    def _validate_query_args(self, query_args:utils.QueryArgsBag):
        '''
        Checks that the given query arguments are valid in context
        '''
        
        query_by, sort_by = query_args.query_by, query_args.sort_by

        invalid_query_by = set(query_by.keys()) - entities.User.has_properties(query_by.keys())
        invalid_sort_by = set(sort_by.keys()) - entities.User.has_properties(sort_by.keys())

        return invalid_query_by, invalid_sort_by

    def _build_create_stmt(self, user:entities.User, excld_cols:set[str]={}) -> str:
        '''
        Prepares a SQL INSERT statement
        '''

        stmt = '''INSERT INTO users'''

        user_json = user.to_json()

        # determine which cols to include in insert statement
        incld_cols = [key for key in user_json.keys() if key not in excld_cols]

        stmt = f'{stmt} ({','.join(incld_cols)}) VALUES ({','.join(['?' for _ in range(len(incld_cols))])})'

        return stmt

    def _build_read_stmt(self, query_args:utils.QueryArgsBag, return_cols:set[str]={}):
        '''
        Prepares a SQL SELECT statement
        '''

        stmt = '''SELECT * FROM users'''

        # ensure return cols actually exist as properties of users
        if return_cols:
            invalid_cols = return_cols - entities.User.has_properties(return_cols)
            if len(invalid_cols) != 0:
                return utils.ModelState(valid=False, message=f'Unknown user properties: {invalid_cols}', data=[invalid_cols])

            cols_str = ','.join(return_cols)
            stmt = stmt.replace('*', cols_str)

        # validate query args
        query_by, sort_by = query_args.query_by, query_args.sort_by

        invalid_query_by = set(query_by.keys()) - entities.User.has_properties(query_by.keys())
        invalid_sort_by = set(sort_by.keys()) - entities.User.has_properties(sort_by.keys())

        if len(invalid_query_by) != 0 or len(invalid_sort_by) != 0:
            raise exceptions.BadQueryArgsBag(
                {
                    'message':f'{len(invalid_query_by)} invalid query by args, {len(invalid_sort_by)} sort by args',
                    'data':[invalid_query_by, invalid_sort_by],
                }
            )

        stmt += 'WHERE '
        
        return stmt

    def build_update_stmt():
        pass

    def build_delete_stmt():
        pass

    def create(self, entity:entities.User, excld_cols={}, **kwargs):
        '''
        Create a new user in the database
        '''

        if self._db_conn is None:
            return utils.ModelState(valid=False, message='No active connection to database', data=[self._db_conn])

        stmt = self._build_create_stmt(entity, excld_cols=excld_cols)

        try:
            user_id = self._exec_dml_command(
                stmt, 
                args=entity.to_tuple(excld_props=excld_cols, dt_to_unix=True), 
                do_insert=True,
                )
            res = utils.ModelState(valid=True, message=f'Successfully created new user with ID {user_id} and username {entity.username}', data=[entity])
        except Exception as e:
            if type(e) == sqlite3.IntegrityError:
                res = utils.ModelState(valid=False, message=f'Username {entity.username} already taken', data=[e], errors=[e])
            else:
                res = utils.ModelState(valid=False, message=str(e), data=[e], errors=[e])

        return res
        
    def read(self, query_args, return_cols=[], **kwargs):
        pass

    def update(self, query_args, new_col_vals, **kwargs):
        pass

    def delete(self, query_args, **kwargs):
        pass
