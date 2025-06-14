from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Para manejar el ObjectId de MongoDB en Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(ObjectId)
        )

# Modelo base para crear/actualizar salas
class RoomModel(BaseModel):
    name: str = Field(..., max_length=100)
    ubication: str = Field(..., max_length=300)
    capacity: Optional[int] = None
    availability: bool = Field(default=True)

# Modelo para base de datos (incluye _id como ObjectId)
class RoomDBModel(RoomModel):
    id_room: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }

# Modelo de respuesta pública (con _id como string)
class RoomResponseModel(BaseModel):
    id: str = Field(alias="_id")
    name: str
    ubication: str
    capacity: Optional[int]
    availability: bool

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {
            ObjectId: str
        }