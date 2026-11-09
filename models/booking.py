from dataclasses import dataclass
from typing import Optional

@dataclass
class Booking:
    id: int
    customer_id: int
    service_id: int
    time_slot: str  
    professional_id: Optional[int] = None
    status: str = "CREATED"