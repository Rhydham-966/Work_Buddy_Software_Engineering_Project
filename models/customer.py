from dataclasses import dataclass
from models.user import User

@dataclass
class Customer(User):
    # future: saved addresses, history
    pass