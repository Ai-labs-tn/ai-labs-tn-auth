from datetime import datetime
from typing import Optional
import asyncpg

from app.utils.otp_utils import generate_otp, compute_expiry


async def create_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
    purpose: str,
    ttl_minutes: int = 10,
) -> str:
    """
    Create a new OTP for an email+purpose and return the raw OTP.
    For now we store the OTP raw in otp_hash (later: change to hash).
    """
    otp = generate_otp(6)
    expires_at = compute_expiry(ttl_minutes)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # mark old OTPs as consumed
            await conn.execute(
                """
                update email_otp
                   set consumed_at = now()
                 where email = $1
                   and purpose = $2
                   and consumed_at is null;
                """,
                email,
                purpose,
            )

            await conn.execute(
                """
                insert into email_otp (email, otp_hash, purpose, expires_at)
                values ($1, $2, $3, $4);
                """,
                email,
                otp,
                purpose,
                expires_at,
            )

    return otp


async def verify_email_otp(
    pool: asyncpg.pool.Pool,
    email: str,
    otp: str,
    purpose: str,
) -> bool:
    """
    Verify the latest OTP for email+purpose.
    Returns True if valid and marks it as consumed, otherwise False.
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            select id, created_at, expires_at, consumed_at, otp_hash
              from email_otp
             where email = $1
               and purpose = $2
             order by created_at desc
             limit 1;
            """,
            email,
            purpose,
        )

        if not row:
            return False

        if row["consumed_at"] is not None:
            return False

        now = datetime.utcnow()
        if now > row["expires_at"]:
            return False

        if row["otp_hash"] != otp:
            return False

        # OTP valid -> mark as consumed
        await conn.execute(
            """
            update email_otp
               set consumed_at = now()
             where id = $1;
            """,
            row["id"],
        )

    return True
