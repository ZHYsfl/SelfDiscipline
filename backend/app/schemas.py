from __future__ import annotations

from datetime import datetime
from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str] = None

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Pairing
class PairCreateResponse(BaseModel):
    code: str


class PairJoinRequest(BaseModel):
    code: str


class PairInfo(BaseModel):
    id: int
    code: str

    class Config:
        from_attributes = True


# Habits
HabitType = Literal["boolean", "number", "text", "time"]


class HabitBase(BaseModel):
    name: str
    type: HabitType
    is_active: bool = True
    order_index: int = 0


class HabitCreate(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[HabitType] = None
    is_active: Optional[bool] = None
    order_index: Optional[int] = None


class HabitRead(HabitBase):
    id: int

    class Config:
        from_attributes = True


# Check-ins
class CheckinBase(BaseModel):
    date: Optional[date] = None
    value_bool: Optional[bool] = None
    value_number: Optional[int] = None
    value_text: Optional[str] = None
    value_time: Optional[str] = None
    note: Optional[str] = None
    image_url: Optional[str] = None


class CheckinCreate(CheckinBase):
    pass


class CheckinRead(CheckinBase):
    id: int
    habit_id: int
    user_id: int

    class Config:
        from_attributes = True


class TodayTask(BaseModel):
    habit: HabitRead
    me: Optional[CheckinRead] = None
    partner: Optional[CheckinRead] = None


class TodayResponse(BaseModel):
    date: date
    tasks: list[TodayTask]


class FeedItem(BaseModel):
    date: date
    habit: HabitRead
    user_id: int
    checkin: CheckinRead


class FeedResponse(BaseModel):
    items: list[FeedItem]
