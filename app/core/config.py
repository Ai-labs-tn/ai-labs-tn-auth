import os
from dotenv import load_dotenv
load_dotenv()
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:4200")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")