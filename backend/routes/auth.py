from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import supabase
from passlib.hash import argon2
import jwt
from datetime import datetime, timedelta

router = APIRouter()

from deps import create_access_token

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # 'admin' or 'adviser'
    department: str | None = None  # for adviser only

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

@router.post("/login")
def login(body: LoginRequest):
    """Sign in via the custom admins/advisers tables using Argon2 and return PyJWT."""
    # Check admins first
    admin_check = supabase.table("admins").select("id, full_name, password_hash").eq("email", body.email).execute()
    user = None
    role = None
    
    if admin_check.data:
        user = admin_check.data[0]
        role = "admin"
    else:
        # Check advisers next
        adviser_check = supabase.table("advisers").select("id, full_name, password_hash").eq("email", body.email).execute()
        if adviser_check.data:
            user = adviser_check.data[0]
            role = "adviser"

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    # Verify password with Argon2
    if not argon2.verify(body.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "role": role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role,
        "full_name": user["full_name"],
        "user_id": user["id"],
    }

@router.post("/register")
def register(body: RegisterRequest):
    """Create a raw database account using Argon2 hashing."""
    if body.role not in ("admin", "adviser"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'adviser'.")

    # Hash password
    hashed_password = argon2.hash(body.password)

    # Check if email exists in either table to prevent duplicates
    try:
        admin_exists = supabase.table("admins").select("id").eq("email", body.email).execute()
        adviser_exists = supabase.table("advisers").select("id").eq("email", body.email).execute()
        
        if admin_exists.data or adviser_exists.data:
            raise HTTPException(status_code=400, detail="Email already registered.")

        if body.role == "admin":
            payload = {"email": body.email, "full_name": body.full_name, "password_hash": hashed_password}
            res = supabase.table("admins").insert(payload).execute()
        else:
            payload = {"email": body.email, "full_name": body.full_name, "password_hash": hashed_password}
            if body.department:
                payload["department"] = body.department
            res = supabase.table("advisers").insert(payload).execute()
            
        if not res.data:
            raise Exception("Failed to insert user into database.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error during registration: {str(e)}")

    return {"message": f"{body.role.capitalize()} registered successfully. Please log in."}

from deps import get_current_user, AuthUser, Depends, create_access_token

@router.get("/me")
def get_me(user: AuthUser = Depends(get_current_user)):
    """Retrieve user details for frontend validation using JWT."""
    admin = supabase.table("admins").select("id, full_name, email").eq("id", user.id).execute()
    if admin.data:
        return {"role": "admin", "full_name": admin.data[0]["full_name"], "email": admin.data[0]["email"]}
        
    adviser = supabase.table("advisers").select("id, full_name, email, department").eq("id", user.id).execute()
    if adviser.data:
        return {"role": "adviser", **adviser.data[0]}
        
    raise HTTPException(status_code=404, detail="User profile not found.")
