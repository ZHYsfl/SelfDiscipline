from __future__ import annotations

import secrets
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from app.config import settings


def generate_pair_code() -> str:
    # 12 char base32-ish, exclude ambiguous chars
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(8))


def today_utc() -> date:
    return date.today()


async def save_upload(file: UploadFile, subdir: str) -> str:
    ext = Path(file.filename or "").suffix
    filename = f"{secrets.token_hex(8)}{ext}"
    dest_dir = settings.static_dir / "uploads" / subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    content = await file.read()
    dest_path.write_bytes(content)
    # return web path
    rel_path = dest_path.relative_to(settings.static_dir)
    return f"/static/{rel_path.as_posix()}"
