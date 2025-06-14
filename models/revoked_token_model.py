from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import pytz

local_tz = pytz.timezone("America/Mexico_City")

class RevokedToken(BaseModel):
    token: Optional[str] = Field(None, max_length=500)
    revoked_dt: datetime = Field(default_factory=lambda: datetime.now(local_tz))

    class Config:
        from_attributes = True  # Si usas pydantic v2