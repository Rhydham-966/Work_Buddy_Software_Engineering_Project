from dataclasses import dataclass
from models.user import User

@dataclass
class Admin(User):
    # future: permissions
    pass