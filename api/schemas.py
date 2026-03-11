from pydantic import BaseModel, Field, validator, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List

class AccountCreate(BaseModel):
    username : str = Field(..., max_length=40, description="Имя пользователя, максимум 40 символов")
    password : str = Field(..., min_length=6, description="Пароль, минимум 6 символов")
    first_name : Optional[str] = Field(None, max_length=80, description="Имя, максимум 80 символов")
    surname : Optional[str] = Field(None, max_length=80, description="Фамилия, максимум 80 символов")
    @validator('username')
    def username_must_not_be_empty(cls, v):
        if not v.isalnum():
            raise ValueError('Username must not be empty')
        return v

class AccountResponse(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class AccountLogin(BaseModel):
    username : str 
    password : str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None


# models moved from virt_currency

class currencyItem(BaseModel):
    id: Optional[int] = None
    quantity: int
    get_Time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class currcreate(BaseModel):
    quantity: int

class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., max_length=40, description="Имя пользователя, максимум 40 символов")
    password: str = Field(..., min_length=6, max_length=72, description="Пароль, минимум 6 символов")
    first_name: Optional[str] = Field(None, max_length=72, description="Имя, максимум 80 символов")
    surname: Optional[str] = Field(None, max_length=72, description="Фамилия, максимум 80 символов")

    @field_validator('username')
    @classmethod
    def username_must_not_be_empty(cls, v):
        if not v or not v.isalnum():
            raise ValueError('Username должен содержать только буквы и цифры')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class userLogin(BaseModel):
    username: str
    password: str