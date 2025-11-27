import os
from dotenv import load_dotenv
load_dotenv()
CORS_ORIGIN = os.getenv("ROOTS_VISION_AI_CORS_ORIGIN", "http://localhost:4200")
SUPABASE_URL = os.getenv("ROOTS_VISION_AI_SB_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("ROOTS_VISION_AI_SB_SR_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("ROOTS_VISION_AI_SB_JWT_SECRET", "")
AUTH_DB_URL = os.getenv("ROOTS_VISION_AI_AUTH_DB_URL", "")