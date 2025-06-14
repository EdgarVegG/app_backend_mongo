from fastapi import APIRouter, Depends, HTTPException, status, Response
from jose import JWTError, jwt
from schemas.user_schema import UserCreate, User, UserUpdate
from models.user_model import UserDBModel, UserPublicModel
from utils.auth_utils import hash_password
from database.connection import get_db, db
from bson import ObjectId, errors
from dependencies.dependencies import get_current_user
from motor.motor_asyncio import AsyncIOMotorClient
from routers.auth_router import SECRET_KEY, ALGORITHM
from dependencies.dependencies import oauth2_scheme


router = APIRouter(prefix="/users", tags=["Users"])


# Transforma documento Mongo a dict compatible con Pydantic
def mongo_to_user(doc) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc

@router.get("/user/me", response_model=UserPublicModel)
async def get_me(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o no proporcionado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_data = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_data:
        raise credentials_exception

    return UserPublicModel(**user_data)


#@router.get("/user/me", response_model=User)
#async def get_me(current_user: User = Depends(get_current_user)):
#    return current_user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # Verificar si ya existe un usuario con el mismo correo
    try:
        existing_user = await db["users"].find_one({"email": user.email})
    except Exception as e:
        print(f"DB Error: {e}")
        raise HTTPException(status_code=400, detail="Database error")
    
    # Hashear la contraseña
    user_dict = user.dict()
    user_dict["password"] = hash_password(user.password)

    # Insertar el nuevo usuario
    await db["users"].insert_one(user_dict)

    return {"message": "User registered successfully"}  
HTTPException(status_code=400, detail="El correo ya está registrado")

    
#@router.get("/check")
#async def check_database_type(db=Depends(get_db)):
#    print("Tipo de db:", type(db))
#    return {"type": str(type(db))}


@router.get("/", response_model=list[User])
async def get_users(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = []
    cursor = db["users"].find()
    async for doc in cursor:
        users.append(User(**mongo_to_user(doc)))
    return users


@router.get("/{id}", response_model=User)
async def get_user(
    id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")

    user = await db["users"].find_one({"_id": oid})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return User(**mongo_to_user(user))


@router.put("/{id}", response_model=User)
async def update_user(
    id: str,
    user_data: UserUpdate,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id_user) != id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este usuario")

    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")

    existing = await db["users"].find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = user_data.dict(exclude_unset=True)
    if update_data:
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])
        await db["users"].update_one({"_id": oid}, {"$set": update_data})

    updated_user = await db["users"].find_one({"_id": oid})
    return User(**mongo_to_user(updated_user))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id_user) != id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este usuario")

    try:
        oid = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID inválido")

    existing = await db["users"].find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db["users"].delete_one({"_id": oid})
    return Response(status_code=status.HTTP_204_NO_CONTENT)