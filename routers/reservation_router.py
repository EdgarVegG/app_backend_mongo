from fastapi import APIRouter, Depends, HTTPException, status, Path
from bson import ObjectId
from datetime import datetime, time
from typing import List
from schemas.reservation_schema import ReservationCreate, ReservationUpdate, ReservationResponseModel
from models.user_model import UserDBModel
from database.connection import get_db
from dependencies.dependencies import get_current_user

router = APIRouter(prefix="/reservations", tags=["Reservations"])

def format_reservation_doc(doc: dict) -> ReservationResponseModel:
    select_date = doc.get("select_date")
    if isinstance(select_date, datetime):
        select_date = select_date.date()
    elif isinstance(select_date, str):
        select_date = datetime.fromisoformat(select_date).date()

    def extract_time(value):
        if isinstance(value, datetime):
            return value.time()
        elif isinstance(value, str):
            return datetime.fromisoformat(value).time()
        return value

    return ReservationResponseModel(
        id_reservation=str(doc["_id"]),
        name_user=doc["name_user"],
        name_event=doc["name_event"],
        description=doc.get("description"),
        select_date=select_date,
        start_time=extract_time(doc["start_time"]),
        end_time=extract_time(doc["end_time"]),
        materia=doc.get("materia"),
        id_user=str(doc.get("id_user")) if doc.get("id_user") else None,
    )

@router.post("/", response_model=ReservationResponseModel, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: ReservationCreate,
    db=Depends(get_db),
    current_user: UserDBModel = Depends(get_current_user)
):
    start_dt = datetime.combine(reservation.select_date, reservation.start_time)
    end_dt = datetime.combine(reservation.select_date, reservation.end_time)

    if start_dt >= end_dt:
        raise HTTPException(status_code=400, detail="La hora de inicio debe ser menor que la hora de fin.")

    # Verificar si hay traslape en la misma fecha
    overlapping = await db["reservations"].find_one({
        "select_date": datetime.combine(reservation.select_date, time.min),
        "$or": [
            {
                "start_time": {"$lt": end_dt},
                "end_time": {"$gt": start_dt}
            }
        ]
    })

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una reservación en ese horario."
        )

    new_reservation = {
        "name_user": current_user.name,
        "name_event": reservation.name_event,
        "description": reservation.description,
        "start_time": start_dt,
        "end_time": end_dt,
        "select_date": datetime.combine(reservation.select_date, time.min),
        "materia": reservation.materia,
        "id_user": ObjectId(current_user.id_user),
        "created_at": datetime.utcnow()
    }

    result = await db["reservations"].insert_one(new_reservation)
    created = await db["reservations"].find_one({"_id": result.inserted_id})

    return format_reservation_doc(created)

@router.get("/", response_model=List[ReservationResponseModel])
async def get_reservations(db=Depends(get_db)):
    reservations = []
    cursor = db["reservations"].find()
    async for res in cursor:
        reservations.append(format_reservation_doc(res))
    return reservations

@router.get("/{id}", response_model=ReservationResponseModel)
async def get_reservation(id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    reservation = await db["reservations"].find_one({"_id": ObjectId(id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    return format_reservation_doc(reservation)

@router.put("/{reservation_id}", response_model=ReservationResponseModel)
async def update_reservation(
    reservation: ReservationUpdate,
    reservation_id: str = Path(..., description="ID de la reservación a actualizar"),
    db=Depends(get_db),
    current_user: UserDBModel = Depends(get_current_user)
):
    if not ObjectId.is_valid(reservation_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    existing = await db["reservations"].find_one({"_id": ObjectId(reservation_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    if str(existing.get("id_user")) != str(current_user.id_user):
        raise HTTPException(status_code=403, detail="No autorizado para actualizar esta reservación")

    update_data = reservation.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    # Extraemos valores actuales o nuevos
    select_date_raw = update_data.get("select_date", existing["select_date"])
    start_time_raw = update_data.get("start_time", existing["start_time"])
    end_time_raw = update_data.get("end_time", existing["end_time"])

    # Procesar select_date
    if isinstance(select_date_raw, str):
        try:
            select_date = datetime.strptime(select_date_raw, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido (esperado: YYYY-MM-DD)")
    elif isinstance(select_date_raw, datetime):
        select_date = select_date_raw.date()
    else:
        select_date = select_date_raw  # ya es date

    # Procesar start_time
    if isinstance(start_time_raw, str):
        try:
            start_time = datetime.strptime(start_time_raw, "%H:%M").time()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de hora de inicio inválido (esperado: HH:MM)")
    elif isinstance(start_time_raw, datetime):
        start_time = start_time_raw.time()
    else:
        start_time = start_time_raw  # ya es time

    # Procesar end_time
    if isinstance(end_time_raw, str):
        try:
            end_time = datetime.strptime(end_time_raw, "%H:%M").time()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de hora de fin inválido (esperado: HH:MM)")
    elif isinstance(end_time_raw, datetime):
        end_time = end_time_raw.time()
    else:
        end_time = end_time_raw  # ya es time

    # Actualizar los valores en el diccionario
    update_data["select_date"] = datetime.combine(select_date, time.min)
    update_data["start_time"] = datetime.combine(select_date, start_time)
    update_data["end_time"] = datetime.combine(select_date, end_time)

    await db["reservations"].update_one(
        {"_id": ObjectId(reservation_id)},
        {"$set": update_data}
    )

    updated = await db["reservations"].find_one({"_id": ObjectId(reservation_id)})
    return format_reservation_doc(updated)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    id: str,
    db=Depends(get_db),
    current_user: UserDBModel = Depends(get_current_user)
):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    reservation = await db["reservations"].find_one({"_id": ObjectId(id)})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservación no encontrada")

    if str(reservation.get("id_user")) != str(current_user.id_user):
        raise HTTPException(status_code=403, detail="No autorizado para eliminar esta reservación")

    await db["reservations"].delete_one({"_id": ObjectId(id)})
    return {"message": "Reservación eliminada exitosamente"}
