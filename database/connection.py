# database/connection.py

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables desde .env

# Leer URI completa de MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("La variable de entorno MONGO_URI no está definida")

# Nombre de la base de datos, por defecto agenda_audiovisual
DB_NAME = os.getenv("DB_NAME")
if not DB_NAME:
    raise Exception("La variable de entorno DB_NAME no está definida")

# Crear cliente Mongo (compatible con Atlas)
client = AsyncIOMotorClient(MONGO_URI)

# Conectar a la base de datos
db = client[DB_NAME]

#print(">>> MONGO_URI:", MONGO_URI)
#print(">>> DB_NAME:", DB_NAME)
#print(">>> Cliente creado:", client)


# Retornar la instancia de la DB
async def get_db() -> AsyncIOMotorClient:
    #print(">>> get_db ejecutado, db:", db)
    #print(">>> Tipo real de db:", type(db))
    return db