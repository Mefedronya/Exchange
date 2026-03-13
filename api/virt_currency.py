from fastapi import APIRouter, HTTPException, Depends
from typing import List
import pyodbc
from .schemas import (
    currencyItem,
    currcreate,
)
from .database import db_manager
from .security import get_current_user

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/me", response_model=List[currencyItem])
def get_my_currency(current_user: dict = Depends(get_current_user)):
    """Return currency rows for the authenticated user only."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            # Предполагается, что поле для связи с пользователем называется user_id.
            cursor.execute(
                "SELECT id, quantity, get_Time FROM Currency WHERE user_id = ?",
                (current_user["id"],),
            )
            rows = cursor.fetchall()

            return [
                currencyItem(id=row[0], quantity=row[1], get_Time=row[2])
                for row in rows
            ]
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/", response_model=List[currencyItem])
def get_all_currency():
    """Legacy endpoint; возвращает все валюты (не для продакшена)."""
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
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")