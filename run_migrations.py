import os
from yoyo import get_backend, read_migrations

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("ROOTS_VISION_AI_AUTH_DB_URL")
if not DB_URL:
    raise RuntimeError("ROOTS_VISION_AI_AUTH_DB_URL is not set")

backend = get_backend(DB_URL)
migrations = read_migrations("./migrations")

with backend.lock():
    backend.apply_migrations(backend.to_apply(migrations))
