from database import supabase
from passlib.hash import argon2

try:
    print("Hashing password...")
    pwd = argon2.hash("test1234")
    print("Testing admins table email check...")
    res = supabase.table("admins").select("id").eq("email", "test@test.com").execute()
    print("Admins email check passed:", res.data)
    
    print("Testing advisers table email check...")
    res2 = supabase.table("advisers").select("id").eq("email", "test@test.com").execute()
    print("Advisers email check passed:", res2.data)
except Exception as e:
    import traceback
    traceback.print_exc()
