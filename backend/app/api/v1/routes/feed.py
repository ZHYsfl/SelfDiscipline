from __future__ import annotations

from datetime import date as date_cls, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.crud import (
    get_pair_member_user_ids,
    get_user_pairs,
    list_checkins_for_date,
    list_habits,
    list_recent_checkins,
    get_checkin_for_user_habit_date,
)
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.utils import today_utc


router = APIRouter(prefix="/overview", tags=["overview"])


def _require_single_pair(db: Session, user_id: int) -> int:
    pairs = get_user_pairs(db, user_id)
    return pairs[0].id


@router.get("/today", response_model=schemas.TodayResponse)
def today_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair_id = _require_single_pair(db, current_user.id)
    today = today_utc()
    habits = list_habits(db, pair_id)
    member_ids = get_pair_member_user_ids(db, pair_id)
    partner_id = [uid for uid in member_ids if uid != current_user.id]
    partner_id = partner_id[0] if partner_id else None

    tasks: list[schemas.TodayTask] = []
    for habit in habits:
        me_ci = get_checkin_for_user_habit_date(db, pair_id, current_user.id, habit.id, today)
        partner_ci = get_checkin_for_user_habit_date(db, pair_id, partner_id, habit.id, today) if partner_id else None
        tasks.append(
            schemas.TodayTask(
                habit=habit,
                me=me_ci and schemas.CheckinRead.model_validate(me_ci),
                partner=partner_ci and schemas.CheckinRead.model_validate(partner_ci),
            )
        )

    return schemas.TodayResponse(date=today, tasks=tasks)


@router.get("/feed", response_model=schemas.FeedResponse)
def feed_overview(days: int = 7, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair_id = _require_single_pair(db, current_user.id)
    start_date = today_utc() - timedelta(days=days - 1)
    recent = list_recent_checkins(db, pair_id, start_date)
    # Build a simple feed grouped by date-habit-user
    items: list[schemas.FeedItem] = []
    habit_map = {h.id: h for h in list_habits(db, pair_id)}
    for ci in recent:
        items.append(
            schemas.FeedItem(
                date=ci.date,
                habit=habit_map.get(ci.habit_id),
                user_id=ci.user_id,
                checkin=schemas.CheckinRead.model_validate(ci),
            )
        )
    return schemas.FeedResponse(items=items)
