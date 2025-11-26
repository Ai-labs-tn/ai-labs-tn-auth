from fastapi import APIRouter
import app.services.supabase_service as supabase_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.get("/register", response_model=dict)
async def register(email: str | None, phone: str | None, password: str):
    token = supabase_service.register(email, phone, password)
    return token

@router.get("/login", response_model=dict)
async def login(email: str, password: str):
    access_token = supabase_service.login(email, password)
    return access_token

@router.get("/refresh", response_model=dict)
async def refresh(refresh_token: str):
    refresh_token = supabase_service.refresh(refresh_token)
    return refresh_token

