from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler):
        return {'type': 'string'}



# Modelo de entrada (registro de usuario)
class UserModel(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    password: str


# Modelo que representa un usuario en la base de datos (con _id convertido)
class UserDBModel(BaseModel):
    id_user: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    password: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


# Modelo para respuestas públicas (sin contraseña)
class UserPublicModel(BaseModel):
    id_user: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: EmailStr

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }