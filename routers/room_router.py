from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List

from database.connection import get_db
from dependencies.dependencies import get_current_user
from schemas.room_schema import RoomCreate, Room, RoomUpdate
from models.user_model import UserPublicModel

router = APIRouter(prefix="/rooms", tags=["Rooms"])


# Helper para transformar el documento Mongo y convertir ObjectId a str
def transform_room(room: dict) -> dict:
    room["id"] = str(room["_id"])
    room["id_room"] = str(room["_id"])  # si el frontend necesita id_room
    return room


@router.post("/", response_model=Room, status_code=status.HTTP_201_CREATED)
async def create_room(
    room: RoomCreate,
    db=Depends(get_db),
    current_user: UserPublicModel = Depends(get_current_user)
):
    new_room = room.dict()
    result = await db["rooms"].insert_one(new_room)
    new_room["_id"] = result.inserted_id
    new_room = transform_room(new_room)
    return Room(**new_room)


@router.get("/", response_model=List[Room])
async def get_rooms(db=Depends(get_db)):
    rooms = []
    cursor = db["rooms"].find()
    async for room in cursor:
        rooms.append(Room(**transform_room(room)))
    return rooms


@router.get("/{id}", response_model=Room)
async def get_room(id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de sala inválido"
        )

    room = await db["rooms"].find_one({"_id": ObjectId(id)})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )

    return Room(**transform_room(room))


@router.put("/{id}", response_model=Room)
async def update_room(
    id: str,
    room: RoomUpdate,
    db=Depends(get_db),
    current_user: UserPublicModel = Depends(get_current_user)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de sala inválido"
        )

    existing_room = await db["rooms"].find_one({"_id": ObjectId(id)})
    if not existing_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )

    update_data = room.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay datos para actualizar"
        )

    await db["rooms"].update_one({"_id": ObjectId(id)}, {"$set": update_data})

    updated_room = await db["rooms"].find_one({"_id": ObjectId(id)})
    return Room(**transform_room(updated_room))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    id: str,
    db=Depends(get_db),
    current_user: UserPublicModel = Depends(get_current_user)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de sala inválido"
        )

    room = await db["rooms"].find_one({"_id": ObjectId(id)})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala no encontrada"
        )

    await db["rooms"].delete_one({"_id": ObjectId(id)})
    return None  # 204 No Content, sin cuerpo