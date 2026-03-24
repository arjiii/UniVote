import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")

# CORS origins separated by comma
ALLOWED_ORIGINS: list[str] = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,https://univote-celtech-v2.vercel.app,https://univote-celtech-v3.vercel.app"
).split(",")

if not SUPABASE_URL or not SUPABASE_KEY:

    print("Warning: SUPABASE_URL or SUPABASE_KEY is missing. Please set them in .env")
