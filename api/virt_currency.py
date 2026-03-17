from fastapi import APIRouter, HTTPException, Depends,status
from typing import List, Optional
import pyodbc
from .schemas import (
    currencyItem,
    currcreate,
    currdel
)
from .database import db_manager
from .security import get_current_user

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/me", response_model=Optional[currencyItem])
def get_my_currency(current_user: dict = Depends(get_current_user)):
    """
    Получить информацию о валюте авторизованного пользователя.
    Возвращает одну запись с общим балансом.
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, user_id, quantity, get_Time 
                FROM Currency 
                WHERE user_id = ?
                """,
                (current_user["id"],),
            )
            row = cursor.fetchone()

            if row is None:
                return None
            
            return currencyItem(id=row[0], user_id=row[1], quantity=row[2], get_Time=row[3])
            
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.get("/balance", response_model=int)
def get_current_balance(current_user: dict = Depends(get_current_user)):
    """
    Получить текущий баланс валюты авторизованного пользователя.
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ISNULL(quantity, 0) 
                FROM Currency 
                WHERE user_id = ?
                """,
                (current_user["id"],)
            )
            row = cursor.fetchone()
            
            return row[0] if row else 0
            
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении баланса: {str(e)}")

@router.put("/plus", response_model=currencyItem)
def set_currency(
    data: currcreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Начислить валюту авторизованному пользователю (СУММИРУЕТ с существующей).
    """
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем существование записи
            cursor.execute(
                "SELECT quantity FROM Currency WHERE user_id = ?",
                (current_user["id"],)
            )
            existing_row = cursor.fetchone()
            
            if existing_row and existing_row[0] is not None:
                # <-- СУММИРУЕМ с существующей валютой
                new_quantity = existing_row[0] + data.quantity
                cursor.execute(
                    """
                    UPDATE Currency 
                    SET quantity = ?, get_Time = GETDATE()
                    WHERE user_id = ?
                    """,
                    (new_quantity, current_user["id"])
                )
            else:
                # Создаем новую запись (если нет существующей)
                cursor.execute(
                    """
                    INSERT INTO Currency (user_id, quantity, get_Time) 
                    VALUES (?, ?, GETDATE())
                    """,
                    (current_user["id"], data.quantity)
                )
            
            conn.commit()
            
            # Возвращаем запись
            cursor.execute(
                """
                SELECT id, user_id, quantity, get_Time 
                FROM Currency 
                WHERE user_id = ?
                """,
                (current_user["id"],)
            )
            row = cursor.fetchone()
            
            # <-- ПРОВЕРКА НА NONE (обязательно!)
            if row is None:
                raise HTTPException(status_code=500, detail="Не удалось получить запись после обновления")
            
            return currencyItem(
                id=row[0], 
                user_id=row[1], 
                quantity=row[2], 
                get_Time=row[3]
            )
            
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при установке валюты: {str(e)}")
    
@router.post("/delete", response_model=currencyItem)
def delete_currency(data: currdel, current_user: dict = Depends(get_current_user)):
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT quantity FROM Currency WHERE user_id = ?",
                (current_user["id"],)
            )
            row = cursor.fetchone()
            
            current_balance = row[0] if row else 0
            
            # достаточно ли средств
            if current_balance < data.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недостаточно средств. Текущий баланс: {current_balance}, Требуется: {data.amount}"
                )
            
            new_quantity = current_balance - data.amount
            
            # Обновлие щаписи
            if row:
                cursor.execute(
                    """
                    UPDATE Currency 
                    SET quantity = ?, get_Time = GETDATE()
                    WHERE user_id = ?
                    """,
                    (new_quantity, current_user["id"])
                )
                conn.commit()
            else:
                raise HTTPException(status_code=400, detail="У пользователя нет записей о валюте")
            
            #  вовзрат обновленной записи
            cursor.execute(
                """
                SELECT id, user_id, quantity, get_Time 
                FROM Currency 
                WHERE user_id = ?
                """,
                (current_user["id"],)
            )
            updated_row = cursor.fetchone()
            
            if updated_row is None:
                raise HTTPException(status_code=500, detail="Не удалось получить обновленную запись")
            
            return currencyItem(
                id=updated_row[0], 
                user_id=updated_row[1], 
                quantity=updated_row[2], 
                get_Time=updated_row[3]
            )
            
    except HTTPException:
        raise
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при списании валюты: {str(e)}")
