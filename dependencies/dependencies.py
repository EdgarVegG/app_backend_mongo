from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from utils.jwt_utils import verify_access_token
from database.connection import get_db
from models.user_model import UserPublicModel
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)) -> UserPublicModel:
    # Verificar si el token fue revocado
    revoked = await db["revoked_token"].find_one({"token": token})
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado. Inicia sesión nuevamente.",
        )

    # Verificar validez del token
    try:
        payload = verify_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin información de usuario",
        )

    try:
        user_obj_id = ObjectId(user_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuario inválido en el token",
        )

    # Busca el usuario sin las claves de contraseña
    user_data = await db["users"].find_one({"_id": user_obj_id}, {"password": 0, "hashed_password": 0})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    user_data["id"] = str(user_data["_id"])
    user_data["id_user"] = str(user_data["_id"])
    return UserPublicModel(**user_data)