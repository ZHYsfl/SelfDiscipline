from __future__ import annotations

from datetime import date as date_cls

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app import schemas
from app.crud import get_user_pairs, list_checkins_for_date, upsert_checkin
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.utils import today_utc, save_upload


router = APIRouter(prefix="/checkins", tags=["checkins"])


def _require_single_pair(db: Session, user_id: int) -> int:
    pairs = get_user_pairs(db, user_id)
    return pairs[0].id


@router.get("/today", response_model=list[schemas.CheckinRead])
def today_checkins(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair_id = _require_single_pair(db, current_user.id)
    return list_checkins_for_date(db, pair_id, today_utc())


@router.post("/{habit_id}", response_model=schemas.CheckinRead)
async def submit_checkin(
    habit_id: int,
    value_bool: bool | None = Form(default=None),
    value_number: int | None = Form(default=None),
    value_text: str | None = Form(default=None),
    value_time: str | None = Form(default=None),
    note: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    date: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pair_id = _require_single_pair(db, current_user.id)
    image_url = None
    if image is not None:
        image_url = await save_upload(image, subdir="checkins")

    date_value = today_utc() if not date else date_cls.fromisoformat(date)
    values = {
        "value_bool": value_bool,
        "value_number": value_number,
        "value_text": value_text,
        "value_time": value_time,
        "note": note,
        "image_path": image_url,
    }
    checkin = upsert_checkin(
        db,
        pair_id=pair_id,
        user_id=current_user.id,
        habit_id=habit_id,
        date_value=date_value,
        values=values,
    )

    # Map image_path -> image_url in schema
    return schemas.CheckinRead(
        id=checkin.id,
        habit_id=checkin.habit_id,
        user_id=checkin.user_id,
        date=checkin.date,
        value_bool=checkin.value_bool,
        value_number=checkin.value_number,
        value_text=checkin.value_text,
        value_time=checkin.value_time,
        note=checkin.note,
        image_url=checkin.image_path,
    )
