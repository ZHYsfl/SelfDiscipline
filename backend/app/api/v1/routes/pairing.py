from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import create_pair, get_pair_by_code, get_user_pairs, join_pair
from app.database import get_db
from app.deps import get_current_user
from app.models import User


router = APIRouter(prefix="/pair", tags=["pair"])


@router.post("/create", response_model=schemas.PairCreateResponse)
def create_pair_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pairs = get_user_pairs(db, current_user.id)
    if pairs:
        # allow only one pair for simplicity
        return schemas.PairCreateResponse(code=pairs[0].code)
    pair = create_pair(db, current_user.id)
    return schemas.PairCreateResponse(code=pair.code)


@router.post("/join")
def join_pair_endpoint(payload: schemas.PairJoinRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pair = get_pair_by_code(db, payload.code)
    if not pair:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pair not found")
    join_pair(db, pair, current_user.id)
    return {"ok": True}


@router.get("/me", response_model=list[schemas.PairInfo])
def my_pairs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_pairs(db, current_user.id)
