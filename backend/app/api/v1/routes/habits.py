from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import create_habit, delete_habit, list_habits, update_habit, get_user_pairs
from app.database import get_db
from app.deps import get_current_user
from app.models import User


router = APIRouter(prefix="/habits", tags=["habits"])


def _require_single_pair(db: Session, user_id: int) -> int:
    pairs = get_user_pairs(db, user_id)
    if not pairs:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please create or join a pair first")
    # Simplify to single pair for MVP
    return pairs[0].id


@router.get("/", response_model=list[schemas.HabitRead])
def list_habits_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair_id = _require_single_pair(db, current_user.id)
    return list_habits(db, pair_id)


@router.post("/", response_model=schemas.HabitRead)
def create_habit_endpoint(payload: schemas.HabitCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair_id = _require_single_pair(db, current_user.id)
    return create_habit(db, pair_id, payload.name, payload.type, payload.is_active, payload.order_index)


@router.patch("/{habit_id}", response_model=schemas.HabitRead)
def update_habit_endpoint(habit_id: int, payload: schemas.HabitUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    habit = update_habit(db, habit_id, **payload.dict(exclude_unset=True))
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit


@router.delete("/{habit_id}")
def delete_habit_endpoint(habit_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_habit(db, habit_id)
    return {"ok": True}
