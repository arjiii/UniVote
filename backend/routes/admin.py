from fastapi import APIRouter, UploadFile, File, Depends, Body
from models import ElectionCreate, ElectionStatusUpdate, StudentManualCreate
from services import election_service
from services import audit_service
from deps import require_admin, AuthUser
import csv
from io import StringIO

router = APIRouter()


from deps import require_admin, require_adviser, AuthUser

@router.get("/elections")
def get_elections(user: AuthUser = Depends(require_adviser)):
    return {"data": election_service.get_elections()}


@router.post("/elections")
def create_election(
    election: ElectionCreate,
    user: AuthUser = Depends(require_admin),
):
    data = election_service.create_election(
        name=election.name,
        start_date=election.start_date,
        end_date=election.end_date,
        description=election.description
    )
    election_id = data[0]["id"] if data else None
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="CREATE_ELECTION", target_type="election",
        target_id=election_id, details={"name": election.name},
    )
    return {"message": "Election created", "data": data}


@router.put("/elections/{election_id}/status")
def update_election_status(
    election_id: str,
    body: ElectionStatusUpdate,
    user: AuthUser = Depends(require_admin),
):
    data = election_service.update_election_status(election_id, body.status)
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="UPDATE_ELECTION_STATUS", target_type="election",
        target_id=election_id, details={"status": body.status},
    )
    return {"message": "Status updated", "data": data}


@router.delete("/elections/{election_id}")
def delete_election(
    election_id: str,
    user: AuthUser = Depends(require_admin),
):
    result = election_service.delete_election(election_id)
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="DELETE_ELECTION", target_type="election",
        target_id=election_id, details={"status": "deleted"},
    )
    return result


@router.get("/students")
def get_students(user: AuthUser = Depends(require_admin)):
    """Retrieve all students (voter list)."""
    # Simply using supabase directly for this list
    from database import supabase
    res = supabase.table("students").select("*").order("full_name").execute()
    return {"data": res.data}


@router.put("/students/{student_id}")
def update_student(
    student_id: str,
    payload: dict = Body(...),
    user: AuthUser = Depends(require_admin),
):
    data = election_service.update_student(student_id, payload)
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="UPDATE_STUDENT", target_type="student",
        target_id=student_id, details=payload,
    )
    return {"message": "Student updated", "data": data}


@router.delete("/students/{student_id}")
def delete_student(
    student_id: str,
    user: AuthUser = Depends(require_admin),
):
    result = election_service.delete_student(student_id)
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="DELETE_STUDENT", target_type="student",
        target_id=student_id,
    )
    return result


# Adviser Management
@router.get("/advisers")
def get_advisers(user: AuthUser = Depends(require_admin)):
    from database import supabase
    res = supabase.table("advisers").select("id, full_name, email, department, created_at").execute()
    return {"data": res.data}


@router.post("/advisers")
def create_adviser(
    payload: dict = Body(...),
    user: AuthUser = Depends(require_admin),
):
    from database import supabase
    from passlib.hash import argon2
    
    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")
    department = payload.get("department")
    
    if not email or not password or not full_name:
        raise HTTPException(status_code=400, detail="Email, password, and full name are required.")
    
    # Check if exists
    exists = supabase.table("advisers").select("id").eq("email", email).execute()
    if exists.data:
        raise HTTPException(status_code=400, detail="Adviser with this email already exists.")
    
    hashed = argon2.hash(password)
    res = supabase.table("advisers").insert({
        "email": email,
        "full_name": full_name,
        "password_hash": hashed,
        "department": department
    }).execute()
    
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="CREATE_ADVISER", target_type="adviser",
        details={"email": email},
    )
    return {"message": "Adviser created", "data": res.data}


@router.delete("/advisers/{adviser_id}")
def delete_adviser(
    adviser_id: str,
    user: AuthUser = Depends(require_admin),
):
    from database import supabase
    # Note: deleting an adviser won't delete their created partylists/candidates 
    # unless we want to cascade that too. For now just delete the user.
    res = supabase.table("advisers").delete().eq("id", adviser_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Adviser not found.")
        
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="DELETE_ADVISER", target_type="adviser",
        target_id=adviser_id,
    )
    return {"message": "Adviser account deleted."}


@router.post("/students/upload")
async def upload_students(
    file: UploadFile = File(...),
    user: AuthUser = Depends(require_admin),
):
    contents = await file.read()
    reader = csv.DictReader(StringIO(contents.decode("utf-8")))
    rows = list(reader)
    data = election_service.import_students_from_rows(rows)
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="IMPORT_STUDENTS", target_type="student",
        details={"count": len(data)},
    )
    return {"message": f"Successfully imported {len(data)} students.", "data": data}


@router.post("/students")
def add_student(
    student: StudentManualCreate,
    user: AuthUser = Depends(require_admin),
):
    data = election_service.import_students_from_rows([student.dict()])
    audit_service.log_action(
        actor_id=user.id, actor_role="admin",
        action="ADD_STUDENT_MANUAL", target_type="student",
        details={"student_id": student.student_id},
    )
    return {"message": "Student added successfully.", "data": data}


@router.get("/audit-log")
def get_audit_log(user: AuthUser = Depends(require_admin)):
    return {"data": audit_service.get_audit_log()}
