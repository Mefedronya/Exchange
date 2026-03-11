from fastapi import APIRouter, HTTPException, status
from .security import get_password_hash, db_manager
from .schemas import UserCreate, UserResponse
from typing import cast
import pyodbc


router = APIRouter(prefix="/auth", tags=["registration"])

@router.get("/")
def read_root():
    return {"message": "работает"}

@router.post("/register", tags=["registration"])
def register_user(user: UserCreate):
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. valid username
            cursor.execute("SELECT id FROM Accounts WHERE username = ?", (user.username,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ользователь с таким именем уже существует"
                )
    
            # 2. hash
            try:
                hashed_password = get_password_hash(user.password)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"шибка парол€: {str(e)}"
                )
    
            # 3. vstavka usera
            cursor.execute(
                """INSERT INTO Accounts (username, password_hash, first_name, surname) 
                   OUTPUT INSERTED.id, INSERTED.username, INSERTED.first_name, INSERTED.surname, INSERTED.created_at
                   VALUES (?, ?, ?, ?)""",
                (user.username, hashed_password, user.first_name, user.surname)
            )
            new_user = cursor.fetchone()
            conn.commit()

            new_user = cast(tuple, new_user)  

            return UserResponse(
                id=new_user[0],
                username=new_user[1],
                first_name=new_user[2],
                surname=new_user[3],
                created_at=new_user[4]
            )
            
    except HTTPException:
        raise
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"шибка базы данных: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="нутренн€€ ошибка сервера")
