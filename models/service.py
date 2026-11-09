from dataclasses import dataclass

@dataclass
class Service:
    id: int
    name: str
    base_price: float
    category: str