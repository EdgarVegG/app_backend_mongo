from pydantic_settings import BaseSettings 
from pydantic import Field


class Settings(BaseSettings):
    # URI completa de conexión a MongoDB Atlas
    MONGO_URI: str = Field(..., env="MONGO_URI")
    
    # Clave secreta para firmar tokens JWT
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # Algoritmo JWT
    ALGORITHM: str = "HS256"
    
    # Duración del token de acceso (en minutos)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DB_NAME: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()