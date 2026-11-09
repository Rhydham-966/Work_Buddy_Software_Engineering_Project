from dataclasses import dataclass
from models.user import User
from typing import Optional

@dataclass
class ServiceProfessional(User):
    rating: float = 0.0
    available: bool = True
    work_area: Optional[str] = None