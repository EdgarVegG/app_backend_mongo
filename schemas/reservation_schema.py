from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ID inválido")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class ReservationBase(BaseModel):
    name_event: str = Field(..., max_length=100)
    description: str = Field(..., max_length=300)
    select_date: date
    start_time: time
    end_time: time
    materia: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    name_event: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    select_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    materia: Optional[str] = None

class ReservationResponseModel(ReservationBase):
    id_reservation: str = Field(..., alias="id_reservation")
    name_user: str
    id_user: Optional[str] = None

    class Config:
        validate_by_name = True
        json_encoders = {
            ObjectId: str,
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat()
        }
