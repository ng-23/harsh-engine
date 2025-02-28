from dataclasses import dataclass, field
from harsh_engine.app.model import entities
from typing import List
import random
from faker import Faker

@dataclass(frozen=True)
class ModelState:
    """
    Represents the state of the Model layer after the processing of a request by the user
    """

    valid: bool = False
    message: str = ""
    data: List[any] = field(default_factory=list) # see https://stackoverflow.com/questions/53632152/why-cant-dataclasses-have-mutable-defaults-in-their-class-attributes-declaratio
    errors: List[Exception] = field(default_factory=list)
    
def generate_dummy_users(n_users=10, seed=42):
    '''
    Generates `n_users` dummy/mock users
    '''

    bad_passwords = ['123ABC!!!','password1','sunshine','blink182','iloveyou2','trustno1']

    users = []

    Faker.seed(seed)
    fake = Faker()

    temp_rand = random.Random(x=seed)

    for i in range(n_users):
        user = entities.User(
            fake.user_name(),
            password=temp_rand.choice(bad_passwords),
            password_is_hashed=False,
        )
        users.append(user)

    return users
