from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from models.room_model import PyObjectId  # Importamos PyObjectId para id

class RoomCreate(BaseModel):
    name: str
    ubication: str
    capacity: Optional[int] = None
    availability: bool = True

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    ubication: Optional[str] = None
    capacity: Optional[int] = None
    availability: Optional[bool] = None

class Room(RoomCreate):
    id_room: PyObjectId = Field(alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }