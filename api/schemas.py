from pydantic import BaseModel, Field, validator, ConfigDict, field_validator
from datetime import datetime, time
from typing import Optional, List

class AccountCreate(BaseModel):
    username: str = Field(..., max_length=50, description="Имя пользователя")
    password: str = Field(..., min_length=6, description="Пароль")
    first_name: Optional[str] = Field(None, max_length=80)
    surname: Optional[str] = Field(None, max_length=80)

    @field_validator('username')
    @classmethod
    def username_must_be_alnum(cls, v):
        if not v or not v.isalnum():
            raise ValueError('Username должен содержать только буквы и цифры')
        return v

class AccountResponse(BaseModel):
    id: int
    username: str
    first_name: Optional[str] = None
    surname: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccountLogin(BaseModel):
    username : str 
    password : str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None


# valyta

class currencyItem(BaseModel):
    id: Optional[int] = None
    user_id: int
    quantity: int
    get_Time: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class currcreate(BaseModel):
    quantity: int = Field(..., ge= 0, description="кол-во валюты")
    

class currupdate(BaseModel): 
    quantity: int = Field(...,ge=8,  description="Новое количество валюты")
    
class currdel(BaseModel):
    amount: int = Field(..., gt=0, description="Количество валюты для удаления")

    
#пользователи

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
    
class deleteUserRequest(BaseModel):
    password: str 

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

class ChatCreate(BaseModel):
    message: str = Field(..., max_length=500, description="Сообщение чата, максимум 500 символов")

class ChatResponse(BaseModel):
    id: int
    user_id: int
    message: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatsCreate(BaseModel):
    ChatName: str = Field(..., max_length=100, description="Название чата, максимум 100 символов")
    #user1_id: int = Field(..., description="ID первого участника")
    user2_id: int = Field(..., description="ID второго участника")

class ChatsResponse(BaseModel):
    ChatID: int
    ChatName: str
    CreatedAt: datetime 
    user1_id: int ###################
    user2_id: int ###################
    model_config = ConfigDict(from_attributes=True)

class MessagesCreate(BaseModel):
    chat_Id: int
    MessagesText: str

class MessagesResponse(BaseModel):
    id: int
    chat_Id: int
    user_Id: int
    MessagesText: str  
    sentAt: datetime 
    isRead: bool   #####################
    model_config = ConfigDict(from_attributes=True)

#уроки
#class lessonsCreate(BaseModel):
   # title:str
   # description: Optional[str] = None
   ## video_url: Optional[str] = None
   # cost: int = 0
   # reward: int = 0
   # is_premium: bool = False
#class lessonsResponse(BaseModel):
  #  id: int
   # title: int
   # description: Optional[str]
  #  cost: int
  #  reward: int
   # is_published: bool
   # model_config = ConfigDict(from_attributes=True)
#прогрессы
class userLessonProgressresponse(BaseModel):
    id:int
    lesson_id:int
    status: str
    currency_earned: int
    score: int
    model_config = ConfigDict(from_attributes=True)
#отзывы
class ReviewCreate(BaseModel):
    reviewed_user_id: int
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5")
    comment: Optional[str] = Field(None, max_length=500, description="Комментарий к отзыву")
class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    reviewer_username: str
    reviewed_user_id: int
    reviewed_username: str
    rating: int
    comment: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
class ReviewStatsResponse(BaseModel):
    user_id: int
    average_rating: float
    total_reviews: int
    model_config = ConfigDict(from_attributes=True)
#Расписание
class LessonScheduleCreate(BaseModel):
    start_time: time  # 18:30
    duration_minutes: int = Field(default=60, ge=15)
    days_of_week: List[str] = Field(..., description="['monday', 'tuesday', ...]")
class LessonCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    cost: int = Field(default=0, ge=0)
    reward: int = Field(default=0, ge=0)
    is_premium: bool = False
    schedule: Optional[LessonScheduleCreate] = None
class LessonResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    preview_image: Optional[str]
    cost: int
    reward: int
    is_published: bool
    is_premium: bool
    created_at: datetime
    schedule: Optional[dict] = None  # или отдельная схема
    
    model_config = ConfigDict(from_attributes=True)
#пользовательское расписание
class UserLessonScheduleCreate(BaseModel):
    lesson_id: int
    ScheduleDate: Optional[datetime] = None  # Дата планируемого прохождения
    status: str = "planned"
class UserLessonScheduleResponse(BaseModel):
    id: int
    lesson_id: int
    lesson_title: str  # Удобно сразу иметь название
    status: str
    ScheduleDate: Optional[datetime] = None
    IsCompleted: Optional[bool] = None
    CreatedAt: datetime

    class Config:
        from_attributes = True
