from harsh_engine.app.model import data_mappers, entities
from harsh_engine.app import utils
from dotenv import load_dotenv
import os
import sqlite3
import pytest

load_dotenv()

# see https://docs.pytest.org/en/stable/example/parametrize.html
def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )

class TestUserMapper():
    '''
    Unit tests for `UserMapper` data mapper
    '''
    
    test_db = os.getenv('TEST_DATABASE')
    test_db_schema = os.getenv('TEST_DATABASE_SCHEMA')
    n_users = int(os.getenv('TEST_N_DUMMY_USERS'))
    seed = int(os.getenv('TEST_SEED'))

    params = {
        'test_create': [
            {'n_users':n_users, 'seed':seed, 'excld_cols':{'id'}},
            ],
        'test_create_same_username': [
            {'username':'NoahGrattan', 'password':'123ABC!!!', 'excld_cols':{'id'}}
        ]
    }

    def _get_db_conn(self):
        db_conn = sqlite3.connect(TestUserMapper.test_db, detect_types=sqlite3.PARSE_DECLTYPES)
        db_conn.row_factory = sqlite3.Row

        cursor = db_conn.cursor()
        cursor.executescript(open(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), TestUserMapper.test_db_schema)).read()) # see https://stackoverflow.com/questions/40416072/reading-a-file-using-a-relative-path-in-a-python-project
        db_conn.commit()

        return db_conn

    def test_create(self, n_users:int, seed:int, excld_cols:set[str]):
        '''
        Test creation of `n_users` dummy users in the database
        '''

        db_conn = self._get_db_conn()

        users = utils.generate_dummy_users(n_users=n_users, seed=seed)

        mapper = data_mappers.UserMapper()
        mapper.db_conn = db_conn

        n_created = 0

        for user in users:
            res = mapper.create(user, excld_cols=excld_cols)
            if res.valid:
                n_created += 1

        db_conn.close()

        assert n_created == n_users

    def test_create_same_username(self, username:str, password:str, excld_cols:set[str]):
        '''
        Test creation of 2 users with the same username
        '''

        db_conn = self._get_db_conn()

        user1, user2 = entities.User(username, password, password_is_hashed=False), entities.User(username, password, password_is_hashed=False)

        mapper = data_mappers.UserMapper()
        mapper.db_conn = db_conn

        _ = mapper.create(user1, excld_cols=excld_cols)
        res = mapper.create(user2, excld_cols=excld_cols)

        assert res.valid == False and type(res.errors[0]) == sqlite3.IntegrityError
