from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional  # Убедись, что List импортирован
import shutil
import os
from pathlib import Path
from datetime import datetime

from .database import get_db
from .models import Lessons, LessonSchedule
from .schemas import LessonCreate, LessonResponse
from .security import get_current_user

router = APIRouter(prefix="/lessons", tags=["Lessons"])

UPLOAD_DIR = Path("static/lesson_previews")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=LessonResponse)
def create_lesson(
    lesson: LessonCreate,  # Параметр называется lesson_
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # ИСПОЛЬЗУЙ lesson_ (как в параметре), а не lesson_data!
    new_lesson = Lessons(
        title=lesson.title,  # type: ignore[assignment]
        description=lesson.description,  # type: ignore[assignment]
        content=lesson.content,  # type: ignore[assignment]
        video_url=lesson.video_url,  # type: ignore[assignment]
        cost=lesson.cost,  # type: ignore[assignment]
        reward=lesson.reward,  # type: ignore[assignment]
        is_premium=lesson.is_premium,  # type: ignore[assignment]
        is_published=True,
        user_id=current_user['id'],  # type: ignore[assignment]
        updated_at=datetime.now(),
        preview_image=None,
    )

    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)

    # Расписание
    if lesson.schedule:
        schedule_entry = LessonSchedule(
            lesson_id=new_lesson.id,
            start_time=lesson.schedule.start_time,  # type: ignore[assignment]
            duration_minutes=lesson.schedule.duration_minutes,  # type: ignore[assignment]
            days_of_week=",".join(lesson.schedule.days_of_week)  # type: ignore[assignment]
        )
        db.add(schedule_entry)
        db.commit()

    return LessonResponse.model_validate({
        "id": new_lesson.id,
        "title": new_lesson.title,
        "description": new_lesson.description,
        "preview_image": new_lesson.preview_image,
        "cost": new_lesson.cost,
        "reward": new_lesson.reward,
        "is_published": new_lesson.is_published,
        "is_premium": new_lesson.is_premium,
        "created_at": new_lesson.created_at
    })


@router.post("/{lesson_id}/upload-preview")
def upload_preview(
    lesson_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    lesson = db.query(Lessons).filter(Lessons.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    if lesson.user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Нет прав")
    
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    if not file.filename:
        raise HTTPException(status_code=400, detail="Имя файла отсутствует")
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")
    
    file_name = f"lesson_{lesson_id}{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    lesson.preview_image = f"/static/lesson_previews/{file_name}" # type: ignore[assignment]
    db.commit()
    
    return {"preview_image": lesson.preview_image}


@router.get("/", response_model=List[LessonResponse])
def get_my_lessons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    lessons = db.query(Lessons).filter(Lessons.user_id == current_user['id']).all()
    
    # Используем model_validate для каждого урока
    return [LessonResponse.model_validate({
        "id": l.id,
        "title": l.title,
        "description": l.description,
        "preview_image": l.preview_image,
        "cost": l.cost,
        "reward": l.reward,
        "is_published": l.is_published,
        "is_premium": l.is_premium,
        "created_at": l.created_at
    }) for l in lessons]


@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_data: LessonCreate,  # ИСПРАВЛЕНО: было lesson_ LessonCreate
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    lesson = db.query(Lessons).filter(Lessons.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    if lesson.user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Нет прав")
    
    # Обновляем поля
    lesson.title = lesson_data.title  # type: ignore[assignment]
    lesson.description = lesson_data.description  # type: ignore[assignment]
    lesson.content = lesson_data.content  # type: ignore[assignment]
    lesson.video_url = lesson_data.video_url  # type: ignore[assignment]
    lesson.cost = lesson_data.cost  # type: ignore[assignment]
    lesson.reward = lesson_data.reward  # type: ignore[assignment]
    lesson.is_premium = lesson_data.is_premium  # type: ignore[assignment]
    
    # Обновляем расписание
    if lesson_data.schedule:
        schedule = db.query(LessonSchedule).filter(
            LessonSchedule.lesson_id == lesson_id
        ).first()
        if schedule:
            schedule.start_time = lesson_data.schedule.start_time # type: ignore[assignment]
            schedule.duration_minutes = lesson_data.schedule.duration_minutes # type: ignore[assignment]
            schedule.days_of_week = ",".join(lesson_data.schedule.days_of_week) # type: ignore[assignment]
        else:
            schedule = LessonSchedule(
                lesson_id=lesson_id,
                start_time=lesson_data.schedule.start_time,
                duration_minutes=lesson_data.schedule.duration_minutes,
                days_of_week=",".join(lesson_data.schedule.days_of_week)
            )
            db.add(schedule)
    
    db.commit()
    db.refresh(lesson)
    
    # ИСПРАВЛЕНО: используем model_validate вместо прямого возврата
    return LessonResponse.model_validate({
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "preview_image": lesson.preview_image,
        "cost": lesson.cost,
        "reward": lesson.reward,
        "is_published": lesson.is_published,
        "is_premium": lesson.is_premium,
        "created_at": lesson.created_at
    })


@router.delete("/{lesson_id}")
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    lesson = db.query(Lessons).filter(Lessons.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    if lesson.user_id != current_user['id']:
        raise HTTPException(status_code=403, detail="Нет прав")
    
    db.delete(lesson)
    db.commit()
    return {"message": "Урок удален"}