
class QueryArgsBagException(Exception):
    '''
    Raised by a `QueryArgsBag` when an error occurs
    '''

class MissingSortOperand(QueryArgsBagException):
    '''
    Raised by a `QueryArgsBag` when a sort substring is missing a sort operand
    '''

class AmbiguousSortOperandLocation(QueryArgsBagException):
    '''
    Raised by a `QueryArgsBag` when the location of the sort operand in a
    sort substring results in ambiguous interpretation
    '''

class DataMapperException(Exception):
    '''
    Raise by a `DataMapper` when an error occurs
    '''

class BadQueryArgsBag(DataMapperException):
    '''
    Raised by a `DataMapper` when a supplied `QueryArgsBag` is invalid/incorrect in some way
    '''