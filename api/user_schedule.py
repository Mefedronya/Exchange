from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .database import get_db
from .models import UserLessonSchedule, Lessons, UserLessonStatus
from .schemas import UserLessonScheduleCreate, UserLessonScheduleResponse
from .security import get_current_user

router = APIRouter(prefix="/my-schedule", tags=["User Schedule"])


@router.post("/", response_model=UserLessonScheduleResponse)
def add_lesson_to_schedule(
    schedule_data: UserLessonScheduleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Добавить урок в личное расписание"""

    lesson = db.query(Lessons).filter(Lessons.id == schedule_data.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")

    existing = db.query(UserLessonSchedule).filter(
        UserLessonSchedule.user_id == current_user['id'],
        UserLessonSchedule.lesson_id == schedule_data.lesson_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Этот урок уже есть в вашем расписании"
        )

    new_schedule = UserLessonSchedule(
        user_id=current_user['id'],
        lesson_id=schedule_data.lesson_id,
        status=schedule_data.status,
        IsCompleted=False,
        ScheduleDate=datetime.utcnow(),   
        CreatedAt=datetime.utcnow()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return UserLessonScheduleResponse(
        id=new_schedule.id,# type: ignore[assignment]
        lesson_id=new_schedule.lesson_id, # type: ignore[assignment]
        lesson_title=lesson.title, # type: ignore[assignment]
        status=new_schedule.status, # type: ignore[assignment]
        CreatedAt=new_schedule.CreatedAt # type: ignore[assignment]
    )


@router.get("/", response_model=List[UserLessonScheduleResponse])
def get_my_schedule(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status_filter: Optional[str] = None
):
    """Получить мое расписание"""

    query = db.query(UserLessonSchedule).filter(
        UserLessonSchedule.user_id == current_user['id']
    )

    if status_filter:
        query = query.filter(UserLessonSchedule.status == status_filter)

    schedules = query.all()

    result = []
    for schedule in schedules:
        lesson = db.query(Lessons).filter(Lessons.id == schedule.lesson_id).first()

        result.append(UserLessonScheduleResponse(
            id=schedule.id,# type: ignore[assignment]
            lesson_id=schedule.lesson_id, # type: ignore[assignment]
            lesson_title=lesson.title if lesson else "Урок удален", # type: ignore[assignment]
            status=schedule.status, # type: ignore[assignment]
            ScheduleDate=schedule.ScheduleDate,   # type: ignore[assignment]    
            IsCompleted=schedule.IsCompleted,    # type: ignore[assignment]     
            CreatedAt=schedule.CreatedAt # type: ignore[assignment]
        ))

    return result


@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить статус урока"""

    schedule = db.query(UserLessonSchedule).filter(
        UserLessonSchedule.id == schedule_id,
        UserLessonSchedule.user_id == current_user['id']
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if status is not None:
        schedule.status = status # type: ignore[assignment]
        schedule.IsCompleted = True # type: ignore[assignment]

    db.commit()
    db.refresh(schedule)

    return {"message": "Обновлено", "schedule_id": schedule.id}


@router.delete("/{schedule_id}")
def remove_from_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить урок из расписания"""

    schedule = db.query(UserLessonSchedule).filter(
        UserLessonSchedule.id == schedule_id,
        UserLessonSchedule.user_id == current_user['id']
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    db.delete(schedule)
    db.commit()

    return {"message": "Удалено"}


@router.post("/{schedule_id}/complete")
def complete_lesson(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отметить урок как пройденный"""

    schedule = db.query(UserLessonSchedule).filter(
        UserLessonSchedule.id == schedule_id,
        UserLessonSchedule.user_id == current_user['id']
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    schedule.status = UserLessonStatus.COMPLETED.value # type: ignore[assignment]

    db.commit()

    return {"message": "Урок завершен"}