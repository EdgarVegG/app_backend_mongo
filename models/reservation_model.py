from datetime import time, date
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

class ReservationBase(BaseModel):
    name_event: str
    description: str
    start_time: time
    end_time: time
    select_date: date
    materia: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass