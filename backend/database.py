import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY is missing. Please set them in .env")

# Using the service role key is recommended for backend to bypass RLS
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_KEY or "")
