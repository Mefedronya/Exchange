from fastapi import APIRouter, HTTPException, status, Depends
from .security import get_password_hash, db_manager, get_current_user
from .schemas import UserCreate, UserResponse
from typing import cast, List
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
                    detail="Пользователь с таким именем уже существует"
                )
    
            # 2. hash
            try:
                hashed_password = get_password_hash(user.password)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка пароля: {str(e)}"
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
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/users", response_model=List[UserResponse])
def list_users(current_user: dict = Depends(get_current_user)):
    """Список всех пользователей (без паролей), чтобы выбрать диалог."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, first_name, surname, created_at FROM Accounts"
            )
            rows = cursor.fetchall()
            users = []
            for row in rows:
                if row[0] == current_user["id"]:
                    continue
                users.append(
                    UserResponse(
                        id=row[0],
                        username=row[1],
                        first_name=row[2],
                        surname=row[3],
                        created_at=row[4],
                    )
                )
            return users
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    try: 
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash FROM Accounts WHERE username = ?", 
                (credentials.username,)
            )
            user_row = cursor.fetchone()
            
            if not user_row or not verify_password(credentials.password, user_row[2]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверное имя пользователя или пароль",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token_ = create_access_token(
                data={"sub": user_row[1]}, 
                expires_delta=access_token_expires) 
            
            return Token(access_token=access_token_, token_type="bearer")
            
    except pyodbc.Error as db_error:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(db_error)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
