import requests
from app.core.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

def register(email: str | None, phone: str | None, password: str):
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "password": password,
        "email": email,
        "phone": phone,
        "email_confirm": bool(email),
        "phone_confirm": bool(phone),
    }
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def login(email: str, password: str):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
    }
    payload = {"email": email, "password": password}
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()

def refresh(refresh_token: str):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
    }
    payload = {"refresh_token": refresh_token}
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r.json()
