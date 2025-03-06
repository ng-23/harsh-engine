from datetime import datetime, timezone
import hashlib
import calendar

class Entity:
    @classmethod  # see https://stackoverflow.com/questions/12179271/meaning-of-classmethod-and-staticmethod-for-beginner
    def has_property(cls, property_name: str) -> bool:
        # see https://stackoverflow.com/questions/17735520/determine-if-given-class-attribute-is-a-property-or-not-python-object
        # properties are class-level attributes, not instance, so we must use type(self) or self.__class__ to check
        if not hasattr(cls, property_name):
            return False

        if not isinstance(getattr(cls, property_name), property):
            return False

        return True
    
    @classmethod
    def has_properties(cls, property_names:list[str]):
        has_props = []

        for property_name in property_names:
            if cls.has_property(property_name):
                has_props.append(property_name)

        return set(has_props)

    def to_tuple(self, **kwargs):
        return tuple(vars(self).values())

    def to_json(self, **kwargs):
        res = {}

        for attr in vars(type(self)):
            if isinstance(getattr(type(self), attr), property):
                res[attr] = getattr(self, attr)

        return res

    def __repr__(self):
        return f"{type(self).__name__}{self.to_json()}"
    
class User(Entity):
    def __init__(self, username:str, password:str, join_time:datetime|None=None, last_seen_time:datetime|None=None, id:int|None=None, password_is_hashed=False):
        super().__init__()

        # properties
        self.id = id
        self.username = username
        self.password = tuple([password, password_is_hashed])
        self.join_time = join_time
        self.last_seen_time = last_seen_time

    @property
    def username(self):
        return self._username
    
    @property
    def password(self):
        return self._password
    
    @property
    def join_time(self):
        return self._join_time
    
    @property
    def last_seen_time(self):
        return self._last_seen_time
    
    @property
    def id(self):
        return self._id
    
    @username.setter
    def username(self, username:str):
        if len(username) == 0:
            raise ValueError('Username must be at least 1 character long')
        
        self._username = username

    @password.setter
    def password(self, password_and_hashflag:tuple[str,bool]):
        password, is_hashed = password_and_hashflag[0], password_and_hashflag[1]

        if not is_hashed:
            if len(password) < 8:
                raise ValueError('Password must be at least 8 characters long')
            password = hashlib.md5(password.encode('utf-8')).hexdigest()

        # TODO: check if hash is md5

        self._password = password

    @join_time.setter
    def join_time(self, join_time:datetime|None = None):
        if join_time == None:
            join_time = datetime.now(tz=timezone.utc)
        self._join_time = join_time

    @last_seen_time.setter
    def last_seen_time(self, last_seen_time:datetime|None = None):
        if last_seen_time == None:
                last_seen_time = datetime.now(tz=timezone.utc)
        self._last_seen_time = last_seen_time

    @id.setter
    def id(self, id:int|None = None):
        self._id = id

    def to_tuple(self, excld_props:set[str]={}, dt_to_unix:bool=False, **kwargs):
        attrs = self.to_json()

        for prop in excld_props:
            attrs.pop(prop)

        if dt_to_unix:
            # see https://stackoverflow.com/a/47525387
            join_time, last_seen_time = calendar.timegm(self.join_time.timetuple()), calendar.timegm(self.last_seen_time.timetuple())
            
            if 'join_time' in attrs:
                attrs['join_time'] = join_time
            if 'last_seen_time' in attrs:
                attrs['last_seen_time'] = last_seen_time

        return tuple(attrs.values())
