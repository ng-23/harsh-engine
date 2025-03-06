from dataclasses import dataclass, field
from harsh_engine.app.model import entities
from harsh_engine.app import exceptions
from typing import List
import random
from faker import Faker

class QueryArgsBag():
    '''
    Represents data intended for use in database queries
    '''

    def __init__(self, filters:set[str], sort_ops:set[str], sort_by_param:str='sort_by'):
        self._bag = {
            'query_by': {},
            'sort_by': {},
        }

        self._filters = filters
        self._sort_ops = sort_ops
        self._sort_by_param = sort_by_param

    @property
    def filters(self):
        return self._filters
    
    @property
    def sort_ops(self):
        return self._sort_ops
    
    @property
    def sort_by_param(self):
        return self._sort_by_param
    
    @property
    def query_by(self):
        return self._bag['query_by']
    
    @property
    def sort_by(self):
        return self._bag['sort_by']

    def add(self, raw_query_params:dict[str,str]) -> None:
        query_by = {} # maps a query param to a dict of filter and val
        sort_by = {}

        for param, val in raw_query_params.items():
            # interpret rest of val string as sorting options
            if param == self._sort_by_param:
                # parse val string into a dict 
                sort_by = self._parse_sort_str(val)
            else:
                # interpret val string as query by params
                # ex: id=gt:10 (id is param, gt is filter, 10 is val)

                # parse val string into a dict
                query_by_params = self._parse_query_by_str(val)

                query_by[param] = query_by_params

        # merge dicts
        # see https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python
        self._bag['query_by'] = {**self._bag['query_by'], **query_by}
        self._bag['sort_by'] = {**self._bag['sort_by'], **sort_by}

    def _parse_sort_str(self, sort_str:str) -> dict[str,str]:
        '''
        Parses a string encoding of sorting information

        Assumes format of sort_op1name1,sort_op2name2,...,sort_opNnameN

        Constructs dictionary mapping nameN to sort_opN
        '''

        res = {}

        # sort substrings are separated by commas
        sort_substrs = sort_str.split(',')

        for sort_substr in sort_substrs:
            # each sort substring must be prefixed by sort operand
            substr_sort_op = None

            # check if substring contains any sort operands
            for sort_op in self._sort_ops:
                split_by_op = sort_substr.split(sort_op)

                if len(split_by_op) > 1:
                    # sort substring must contain operand and something else

                    # sort operand must be at front of substring
                    if not split_by_op[0]:
                        # sort operand is at front of substring
                        # can potentially be elsewhere but that's ok
                        substr_sort_op = sort_op
                        break

                    # sort operand is in substring somewhere
                    # but not the front, so interpretation is ambiguous
                    raise exceptions.AmbiguousSortOperandLocation(
                        {
                            'message':f'Unable to interpret sort operand in substring {sort_substr} of string {sort_str}',
                            'data':[sort_substr, sort_str]
                        }
                    )
            
            if substr_sort_op is None:
                # didn't find sort operand in substring, invalid format
                raise exceptions.MissingSortOperand(
                    {
                        'message':f'Missing sort operand in substring {sort_substr} of string {sort_str}',
                        'data':[sort_substr, sort_str]
                    }
                )
            
            # valid sort substring, map the name to the sort operand
            res[sort_substr[sort_substr.index(substr_sort_op)+1:]] = substr_sort_op

        return res

    def _parse_query_by_str(self, param:str, query_by_str:str) -> dict[str,dict[str,str]]:
        pass

@dataclass(frozen=True)
class ModelState:
    '''
    Represents the state of the Model layer after the processing of a request by the user
    '''

    valid: bool = False
    message: str = ''
    data: List[any] = field(default_factory=list) # see https://stackoverflow.com/questions/53632152/why-cant-dataclasses-have-mutable-defaults-in-their-class-attributes-declaratio
    errors: List[Exception] = field(default_factory=list)
    
def generate_dummy_users(n_users=10, seed=42):
    '''
    Generates `n_users` dummy/mock users
    '''

    bad_passwords = ['123ABC!!!','password1','sunshine','blink182','iloveyou2','trustno1']

    Faker.seed(seed)
    fake = Faker()

    rand_gen = random.Random(x=seed)

    users = [entities.User(fake.user_name(), rand_gen.choice(bad_passwords), password_is_hashed=False) for _ in range(n_users)]

    return users
