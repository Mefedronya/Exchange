from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pyodbc
from .schemas import (
    currencyItem,
    currcreate,
)
from .database import db_manager

router = APIRouter(prefix="/currency", tags=["currency"])

#===========маршруты
@router.get("/", response_model=List[currencyItem])
def get_user_currency():
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, quantity, get_Time FROM Currency")
            rows = cursor.fetchall()

            return [
                currencyItem(id=row[0], quantity=row[1], get_Time=row[2])
                for row in rows
            ]
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")