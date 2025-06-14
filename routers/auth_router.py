from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from utils.auth_utils import verify_password
from database.connection import get_db
from jose import JWTError, jwt
import os
from datetime import datetime, timedelta
from models.user_model import UserPublicModel

router = APIRouter()

# Configuración de variables de entorno
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # Reemplaza con tu clave real en .env
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db)
):
    # Buscar usuario por correo electrónico (username = email en OAuth2)
    user_data = await db["users"].find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    hashed_password = user_data.get("password")
    if not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El usuario no tiene contraseña definida"
        )

    # Verificar la contraseña
    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    # Generar el JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_data["_id"]),  # Asegúrate de convertir ObjectId a string
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Devolver token, email y nombre del usuario
    return {
        "access_token": token,
        "token_type": "bearer",
        "email": user_data.get("email"),
        "name": user_data.get("name", "Sin nombre"),
        "id": str(user_data["_id"])
    }
