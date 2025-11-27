import asyncio
import asyncpg

from app.services.email_otp_repo import create_email_otp, verify_email_otp
from app.services.email_service import send_otp_email
from app.services import supabase_service


# REGISTER: STEP 1 - send OTP
async def start_register_with_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
    password: str,
):
    """
    1) create OTP in DB (purpose='register')
    2) send OTP via email
    NOTE: do NOT create Supabase user yet.
    """
    otp = await create_email_otp(pool, email=email, purpose="register", ttl_minutes=10)

    # send_otp_email is sync -> run in thread to not block event loop
    await asyncio.to_thread(send_otp_email, email, otp)

    # For security, do NOT return OTP
    # You’ll store password client-side or ask again on finish step.
    return {"success": True, "message": "OTP sent to email"}


# REGISTER: STEP 2 - verify OTP and create Supabase user
async def complete_register_with_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
    password: str,
    otp: str,
    phone: str | None = None,
):
    ok = await verify_email_otp(pool, email=email, otp=otp, purpose="register")
    if not ok:
        raise ValueError("Invalid or expired OTP")

    # OTP is valid -> create Supabase user (sync call)
    user = await asyncio.to_thread(
        supabase_service.register,
        email,
        phone,
        password,
    )
    return user


# LOGIN VIA EMAIL OTP (forgot password / passwordless)
async def start_login_with_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
):
    """
    If user forgets password, they can login via OTP.
    """
    otp = await create_email_otp(pool, email=email, purpose="login", ttl_minutes=10)
    await asyncio.to_thread(send_otp_email, email, otp)
    return {"success": True, "message": "OTP sent to email"}


async def complete_login_with_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
    otp: str,
    new_password: str | None = None,
):
    """
    After OTP verification, either:
      - let user set new_password (then login with email+password)
      - or simply treat OTP as login and issue your own session (custom JWT).
    Here we'll assume you want to reset password and then login via Supabase.
    """
    ok = await verify_email_otp(pool, email=email, otp=otp, purpose="login")
    if not ok:
        raise ValueError("Invalid or expired OTP")

    # For simplicity here, just require new_password and call Supabase login directly
    if new_password is None:
        # You can instead return a flag telling UI to prompt for new password
        return {"success": True, "message": "OTP verified; please set new password"}

    # In a more complete implementation:
    #   1) Use Supabase admin API to update the user's password
    #   2) Then call supabase_service.login(email, new_password)
    # Here we'll simply call login (assuming password already matches stored):
    tokens = await asyncio.to_thread(
        supabase_service.login,
        email,
        new_password,
    )
    return tokens
