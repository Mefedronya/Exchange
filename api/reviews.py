from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from .database import get_db, engine
from .schemas import ReviewCreate, ReviewResponse, ReviewStatsResponse
from .models import Review, Account
from .security import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # Нельзя оценить самого себя
    if review_data.reviewed_user_id == current_user['id']:
        raise HTTPException(
            status_code=400, 
            detail="Нельзя оставить отзыв самому себе"
        )
    
    # Проверка: существует ли оцениваемый пользователь
    reviewed_user = db.query(Account).filter(
        Account.id == review_data.reviewed_user_id
    ).first()
    if not reviewed_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка: не оставлял ли пользователь уже отзыв этому человеку
    existing_review = db.query(Review).filter(
        Review.reviewer_id == current_user['id'],
        Review.reviewed_user_id == review_data.reviewed_user_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400, 
            detail="Вы уже оставляли отзыв этому пользователю"
        )

    new_review = Review(
        reviewer_id=current_user['id'],
        reviewed_user_id=review_data.reviewed_user_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # Формируем ответ с именами
    reviewer = db.query(Account).filter(Account.id == current_user['id']).first()
    reviewed = db.query(Account).filter(Account.id == review_data.reviewed_user_id).first()

    return ReviewResponse.model_validate({
    "id": new_review.id,
    "reviewer_id": new_review.reviewer_id,
    "reviewer_username": reviewer.username if reviewer else "Unknown",
    "reviewed_user_id": new_review.reviewed_user_id,
    "reviewed_username": reviewed.username if reviewed else "Unknown",
    "rating": new_review.rating,
    "comment": new_review.comment,
    "created_at": new_review.created_at
})


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_reviews_for_user(
    user_id: int, 
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Получить все отзывы, оставленные конкретному пользователю"""
    reviews = (db.query(Review)
               .filter(Review.reviewed_user_id == user_id)
               .order_by(Review.created_at.desc())
               .offset(offset)
               .limit(limit)
               .all())
    
    result = []
    for rev in reviews:
        reviewer = db.query(Account).filter(Account.id == rev.reviewer_id).first()
        reviewed = db.query(Account).filter(Account.id == rev.reviewed_user_id).first()
        result.append(ReviewResponse.model_validate({
            "id": rev.id,
            "reviewer_id": rev.reviewer_id,
            "reviewer_username": reviewer.username if reviewer else "Unknown",
            "reviewed_user_id": rev.reviewed_user_id,
            "reviewed_username": reviewed.username if reviewed else "Unknown",
            "rating": rev.rating,
            "comment": rev.comment,
            "created_at": rev.created_at
    }))
    return result


@router.get("/user/{user_id}/stats", response_model=ReviewStatsResponse)
def get_user_review_stats(user_id: int, db: Session = Depends(get_db)):
    """Получить статистику отзывов пользователя: средний рейтинг и количество"""
    stats = db.query(
        Review.reviewed_user_id,
        func.avg(Review.rating).label("average_rating"),
        func.count(Review.id).label("total_reviews")
    ).filter(
        Review.reviewed_user_id == user_id
    ).group_by(Review.reviewed_user_id).first()
    
    if not stats:
        return ReviewStatsResponse(
            user_id=user_id,
            average_rating=0.0,
            total_reviews=0
        )
    
    return ReviewStatsResponse(
        user_id=stats.reviewed_user_id,
        average_rating=round(float(stats.average_rating), 2),
        total_reviews=stats.total_reviews
    )


@router.get("/my-reviews", response_model=List[ReviewResponse])
def get_my_reviews(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """Получить отзывы, которые текущий пользователь оставил другим"""
    reviews = (db.query(Review)
               .filter(Review.reviewer_id == current_user['id'])
               .order_by(Review.created_at.desc())
               .all())
    
    result = []
    for rev in reviews:
        reviewer = db.query(Account).filter(Account.id == rev.reviewer_id).first()
        reviewed = db.query(Account).filter(Account.id == rev.reviewed_user_id).first()
        result.append(ReviewResponse.model_validate({
            "id": rev.id,
            "reviewer_id": rev.reviewer_id,
            "reviewer_username": reviewer.username if reviewer else "Unknown",
            "reviewed_user_id": rev.reviewed_user_id,
            "reviewed_username": reviewed.username if reviewed else "Unknown",
            "rating": rev.rating,
            "comment": rev.comment,
            "created_at": rev.created_at
    }))
    return result


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить свой отзыв (только оценку и комментарий)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    # Проверка прав: редактировать можно только свой отзыв
    if review.reviewer_id != current_user['id']:
        raise HTTPException(
            status_code=403, 
            detail="Нет прав на редактирование этого отзыва"
        )
    
    # Нельзя изменить пользователя, которому оставлен отзыв
    review.rating = review_data.rating # type: ignore[assignment]
    review.comment = review_data.comment # type: ignore[assignment]
    
    db.commit()
    db.refresh(review)
    
    reviewer = db.query(Account).filter(Account.id == review.reviewer_id).first()
    reviewed = db.query(Account).filter(Account.id == review.reviewed_user_id).first()
    
    return ReviewResponse.model_validate({
    "id": review.id,
    "reviewer_id": review.reviewer_id,
    "reviewer_username": reviewer.username if reviewer else "Unknown",
    "reviewed_user_id": review.reviewed_user_id,
    "reviewed_username": reviewed.username if reviewed else "Unknown",
    "rating": review.rating,
    "comment": review.comment,
    "created_at": review.created_at
})


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """Удалить отзыв (только автор может удалить)"""
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    
    if review.reviewer_id != current_user['id']:
        raise HTTPException(
            status_code=403, 
            detail="Нет прав на удаление этого отзыва"
        )

    db.delete(review)
    db.commit()
    return None
