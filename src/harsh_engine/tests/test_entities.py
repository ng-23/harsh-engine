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

class TestUser():
    '''
    Unit tests for `User` entity
    '''

    params = {
        'test_has_properties': [
            {'good_props':{'username':'noahg', 'password':'ABC123!!!'}, 'bad_props':{'junk_property'}}
        ]
    }

    seed = int(os.getenv('TEST_SEED'))

    def test_has_properties(self, good_props:dict[str,], bad_props:set[str]):
        user = entities.User(**good_props)

        test_props = set(good_props.keys()) | bad_props
        has_props = user.has_properties(test_props)

        assert len(test_props - has_props) == 1
