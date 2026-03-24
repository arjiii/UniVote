import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client, create_async_client, AsyncClient
from supabase.client import ClientOptions

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY is missing. Please set them in .env")

# Force HTTP/1.1 to avoid "RemoteProtocolError: Server disconnected" errors with HTTP/2
# Also increase timeouts for complex queries
options = ClientOptions(
    postgrest_client_timeout=30,
    storage_client_timeout=30,
)

supabase: Client = create_client(
    SUPABASE_URL or "", 
    SUPABASE_KEY or "",
    options=options
)

_async_supabase: Optional[AsyncClient] = None

async def get_async_supabase() -> AsyncClient:
    global _async_supabase
    if _async_supabase is None:
        _async_supabase = await create_async_client(
            SUPABASE_URL or "",
            SUPABASE_KEY or "",
            options=options
        )
    return _async_supabase
