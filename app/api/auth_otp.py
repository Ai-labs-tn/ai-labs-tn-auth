from fastapi import APIRouter, Depends, HTTPException
import asyncpg

from app.db import get_db_pool
from app.services.email_otp_service import (
    start_register_with_email_otp,
    complete_register_with_email_otp,
    start_login_with_email_otp,
    complete_login_with_email_otp,
)

router = APIRouter(prefix="/api/auth/otp", tags=["Auth OTP"])


@router.post("/register/start")
async def start_register(
    email: str,
    password: str,
    pool: asyncpg.pool.Pool = Depends(get_db_pool),
):
    return await start_register_with_email_otp(pool=pool, email=email, password=password)


@router.post("/register/complete")
async def finish_register(
    email: str,
    password: str,
    otp: str,
    pool: asyncpg.pool.Pool = Depends(get_db_pool),
):
    try:
        user = await complete_register_with_email_otp(
            pool=pool,
            email=email,
            password=password,
            otp=otp,
            phone=None,     # or add as parameter
        )
        return {"success": True, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login/start")
async def start_login(
    email: str,
    pool: asyncpg.pool.Pool = Depends(get_db_pool),
):
    return await start_login_with_email_otp(pool=pool, email=email)


@router.post("/login/complete")
async def finish_login(
    email: str,
    otp: str,
    new_password: str | None = None,
    pool: asyncpg.pool.Pool = Depends(get_db_pool),
):
    try:
        result = await complete_login_with_email_otp(
            pool=pool,
            email=email,
            otp=otp,
            new_password=new_password,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
