from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models import RefreshToken, User, Pair, PairMember, Habit, DailyCheckin
from app.security import hash_password
from app.utils import generate_pair_code


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_user(db: Session, email: str, password: str, display_name: Optional[str]) -> User:
    user = User(email=email, hashed_password=hash_password(password), display_name=display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
    rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_valid_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    return db.execute(
        select(RefreshToken).where(RefreshToken.token == token, RefreshToken.revoked == False)  # noqa: E712
    ).scalar_one_or_none()


def revoke_refresh_token(db: Session, token: RefreshToken) -> None:
    token.revoked = True
    db.add(token)
    db.commit()


# Pairing
def create_pair(db: Session, owner_user_id: int) -> Pair:
    pair = Pair(code=generate_pair_code())
    db.add(pair)
    db.flush()
    db.add(PairMember(pair_id=pair.id, user_id=owner_user_id))
    db.commit()
    db.refresh(pair)
    return pair


def get_pair_by_code(db: Session, code: str) -> Optional[Pair]:
    return db.execute(select(Pair).where(Pair.code == code)).scalar_one_or_none()


def join_pair(db: Session, pair: Pair, user_id: int) -> None:
    existing = db.execute(
        select(PairMember).where(PairMember.pair_id == pair.id, PairMember.user_id == user_id)
    ).scalar_one_or_none()
    if existing:
        return
    db.add(PairMember(pair_id=pair.id, user_id=user_id))
    db.commit()


def get_user_pairs(db: Session, user_id: int) -> List[Pair]:
    pairs = db.execute(
        select(Pair).join(PairMember, PairMember.pair_id == Pair.id).where(PairMember.user_id == user_id)
    ).scalars().all()
    return pairs


def get_pair_member_user_ids(db: Session, pair_id: int) -> List[int]:
    return db.execute(select(PairMember.user_id).where(PairMember.pair_id == pair_id)).scalars().all()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


# Habits
def list_habits(db: Session, pair_id: int) -> List[Habit]:
    return db.execute(select(Habit).where(Habit.pair_id == pair_id).order_by(Habit.order_index)).scalars().all()


def create_habit(db: Session, pair_id: int, name: str, type_: str, is_active: bool, order_index: int) -> Habit:
    habit = Habit(pair_id=pair_id, name=name, type=type_, is_active=is_active, order_index=order_index)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def update_habit(db: Session, habit_id: int, **fields) -> Optional[Habit]:
    habit = db.get(Habit, habit_id)
    if not habit:
        return None
    for k, v in fields.items():
        if v is not None:
            setattr(habit, k, v)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit_id: int) -> None:
    habit = db.get(Habit, habit_id)
    if habit:
        db.delete(habit)
        db.commit()


# Check-ins
def upsert_checkin(
    db: Session,
    pair_id: int,
    user_id: int,
    habit_id: int,
    date_value: date,
    values: dict,
) -> DailyCheckin:
    existing = db.execute(
        select(DailyCheckin).where(
            and_(
                DailyCheckin.pair_id == pair_id,
                DailyCheckin.user_id == user_id,
                DailyCheckin.habit_id == habit_id,
                DailyCheckin.date == date_value,
            )
        )
    ).scalar_one_or_none()

    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    checkin = DailyCheckin(
        pair_id=pair_id,
        user_id=user_id,
        habit_id=habit_id,
        date=date_value,
        **values,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def list_checkins_for_date(db: Session, pair_id: int, date_value: date) -> List[DailyCheckin]:
    return db.execute(
        select(DailyCheckin).where(DailyCheckin.pair_id == pair_id, DailyCheckin.date == date_value)
    ).scalars().all()


def get_checkin_for_user_habit_date(
    db: Session, pair_id: int, user_id: int, habit_id: int, date_value: date
) -> Optional[DailyCheckin]:
    return db.execute(
        select(DailyCheckin).where(
            and_(
                DailyCheckin.pair_id == pair_id,
                DailyCheckin.user_id == user_id,
                DailyCheckin.habit_id == habit_id,
                DailyCheckin.date == date_value,
            )
        )
    ).scalar_one_or_none()


def list_recent_checkins(db: Session, pair_id: int, start_date: date) -> List[DailyCheckin]:
    return db.execute(
        select(DailyCheckin)
        .where(and_(DailyCheckin.pair_id == pair_id, DailyCheckin.date >= start_date))
        .order_by(DailyCheckin.date.desc(), DailyCheckin.updated_at.desc())
    ).scalars().all()
