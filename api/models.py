from sqlalchemy import Column, Integer, String, TIMESTAMP, func, ForeignKey, Text, Boolean, DateTime, Numeric
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import relationship, Session

Base = declarative_base()

class Account(Base):
    __tablename__ = 'Accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(260), nullable=False)
    first_name = Column(String(80), nullable=False)
    surname = Column(String(80), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    #зависимость
    chats_as_user1 = relationship("Chats", foreign_keys="Chats.user1_id", back_populates="user1")
    chats_as_user2 = relationship("Chats", foreign_keys="Chats.user2_id", back_populates="user2")
    messages = relationship("Messages", back_populates="author")
    currencies = relationship("Currency", back_populates="owner")
    lessons = relationship("Lessons", back_populates="author")
    progress = relationship("UserLessonProgress", back_populates="user")

    def __repr__(self):
         return f"<Account id={self.id} username='{self.username}'>"

class Chats(Base):
    __tablename__ = 'Chats'

    ChatID = Column(Integer, primary_key=True, autoincrement=True)
    ChatName = Column(String(100), nullable=False)
    CreatedAt = Column(TIMESTAMP, server_default=func.now())
    user1_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)

    #зависимости
    user1 = relationship("Account", foreign_keys=[user1_id], back_populates="chats_as_user1")
    user2 = relationship("Account", foreign_keys=[user2_id], back_populates="chats_as_user2")
    messages = relationship("Messages", back_populates="chat")
 
    def __repr__(self):
        return f"<Chats ChatID={self.ChatID} ChatName='{self.ChatName}'>"

class Messages(Base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True, autoincrement=True)  
    chat_Id = Column(Integer, ForeignKey('Chats.ChatID'), nullable=False)
    user_Id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    MessagesText = Column(Text, nullable=False)
    sentAt = Column(DateTime, server_default=func.now())
    isRead = Column(Boolean, default=False)

    #зависимости
    chat = relationship("Chats", back_populates="messages")
    author = relationship("Account", back_populates="messages")

    def __repr__(self):
        return f"<Messages id={self.id} chat_Id={self.chat_Id} user_Id={self.user_Id} MessagesText='{self.MessagesText[:20]}...'>"
    
class Currency(Base):
    __tablename__ = 'Currency'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=0) 
    get_Time = Column(DateTime, server_default=func.now())

    owner = relationship("Account", back_populates="currencies") 

class Lessons(Base):
    __tablename__ = 'Lessons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text) 
    video_url = Column(String(500))
    cost = Column(Integer, default=0)
    reward = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_published = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('Accounts.id')) 
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    #зависимость
    author = relationship("Account", back_populates="lessons")
    progress_records = relationship("UserLessonProgress", back_populates="lesson")

class UserLessonProgress(Base):
    __tablename__ = 'UserLessonProgress'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('Accounts.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('Lessons.id'), nullable=False)
    status = Column(String(50)) # старт прогресс закончен
    currency_spent = Column(Integer, default=0)
    currency_earned = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    score = Column(Integer, default=0)
    attempts = Column(Integer, default=0)

    # Relationships
    user = relationship("Account", back_populates="progress")
    lesson = relationship("Lessons", back_populates="progress_records")
    