from dataclasses import dataclass
from abc import ABC

@dataclass
class User(ABC):
    id: int
    name: str
    phone: str