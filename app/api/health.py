from fastapi import APIRouter
router = APIRouter(prefix="/api/health", tags=["API Health"])

@router.get("/")
async def health():
    return {"ok": True, "service": "ai-labs-tn-api"}