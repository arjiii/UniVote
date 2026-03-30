from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from models import (
    ElectionCreate,
    ElectionUpdate,
    ElectionStatusUpdate,
    StudentManualCreate,
    StudentUpdate,
    AdviserCreate,
)
from services import election_service, audit_service
from deps import require_admin, require_adviser, AuthUser
from database import get_async_supabase, paginate
from passlib.hash import argon2
import csv
from io import StringIO
from typing import Optional

router = APIRouter()


@router.get("/elections")
async def get_elections(user: AuthUser = Depends(require_adviser)):
    return {"data": await election_service.get_elections()}


@router.post("/elections")
async def create_election(
    election: ElectionCreate,
    user: AuthUser = Depends(require_admin),
):
    data = await election_service.create_election(
        name=election.name,
        start_date=election.start_date,
        end_date=election.end_date,
        description=election.description,
    )
    election_id = data[0]["id"] if data else None
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="CREATE_ELECTION",
        target_type="election",
        target_id=election_id,
        details={"name": election.name},
    )
    return {"message": "Election created", "data": data}


@router.put("/elections/{election_id}/status")
async def update_election_status(
    election_id: str,
    body: ElectionStatusUpdate,
    user: AuthUser = Depends(require_admin),
):
    data = await election_service.update_election_status(election_id, body.status)
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="UPDATE_ELECTION_STATUS",
        target_type="election",
        target_id=election_id,
        details={"status": body.status},
    )
    return {"message": "Status updated", "data": data}


@router.put("/elections/{election_id}")
async def update_election(
    election_id: str,
    payload: ElectionUpdate,
    user: AuthUser = Depends(require_admin),
):
    data = await election_service.update_election(
        election_id, payload.dict(exclude_unset=True)
    )
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="UPDATE_ELECTION",
        target_type="election",
        target_id=election_id,
        details=payload.dict(exclude_unset=True),
    )
    return {"message": "Election updated", "data": data}


@router.delete("/elections/{election_id}")
async def delete_election(
    election_id: str,
    user: AuthUser = Depends(require_admin),
):
    result = await election_service.delete_election(election_id)
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="DELETE_ELECTION",
        target_type="election",
        target_id=election_id,
        details={"status": "deleted"},
    )
    return result


@router.get("/students")
async def get_students(
    user: AuthUser = Depends(require_admin),
    page_size: int = Query(50, ge=1, le=200),
    page_token: Optional[str] = Query(None),
):
    """Retrieve voters using AIP-158 cursor-based pagination."""
    result = await paginate(
        table="students",
        select="id, student_id, full_name, program, year_level, has_voted",
        order_column="id",
        page_size=page_size,
        page_token=page_token,
    )
    return result


@router.put("/students/{student_id}")
async def update_student(
    student_id: str,
    payload: StudentUpdate,
    user: AuthUser = Depends(require_admin),
):
    # Only allow specific fields via StudentUpdate model
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update fields provided.")

    data = await election_service.update_student(student_id, update_data)
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="UPDATE_STUDENT",
        target_type="student",
        target_id=student_id,
        details=payload,
    )
    return {"message": "Student updated", "data": data}


@router.delete("/students/{student_id}")
async def delete_student(
    student_id: str,
    user: AuthUser = Depends(require_admin),
):
    result = await election_service.delete_student(student_id)
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="DELETE_STUDENT",
        target_type="student",
        target_id=student_id,
    )
    return result


# Adviser Management
@router.get("/advisers")
async def get_advisers(
    user: AuthUser = Depends(require_admin),
    page_size: int = Query(50, ge=1, le=200),
    page_token: Optional[str] = Query(None),
):
    result = await paginate(
        table="advisers",
        select="id, full_name, email, department, created_at",
        order_column="id",
        page_size=page_size,
        page_token=page_token,
    )
    return result


@router.post("/advisers")
async def create_adviser(
    adviser: AdviserCreate,
    user: AuthUser = Depends(require_admin),
):
    # Check if exists
    supabase = await get_async_supabase()
    exists = (
        await supabase.table("advisers")
        .select("id")
        .eq("email", adviser.email)
        .execute()
    )
    if exists.data:
        raise HTTPException(
            status_code=400, detail="Adviser with this email already exists."
        )

    hashed = argon2.hash(adviser.password)
    res = (
        await supabase.table("advisers")
        .insert(
            {
                "email": adviser.email,
                "full_name": adviser.full_name,
                "password_hash": hashed,
                "department": adviser.department,
            }
        )
        .execute()
    )

    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="CREATE_ADVISER",
        target_type="adviser",
        details={"email": adviser.email},
    )
    return {"message": "Adviser created", "data": res.data}


@router.delete("/advisers/{adviser_id}")
async def delete_adviser(
    adviser_id: str,
    user: AuthUser = Depends(require_admin),
):
    # Note: deleting an adviser won't delete their created partylists/candidates
    # unless we want to cascade that too. For now just delete the user.
    supabase = await get_async_supabase()
    res = await supabase.table("advisers").delete().eq("id", adviser_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Adviser not found.")

    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="DELETE_ADVISER",
        target_type="adviser",
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
    data = await election_service.import_students_from_rows(rows)
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="IMPORT_STUDENTS",
        target_type="student",
        details={"count": len(data)},
    )
    return {"message": f"Successfully imported {len(data)} students.", "data": data}


@router.post("/students")
async def add_student(
    student: StudentManualCreate,
    user: AuthUser = Depends(require_admin),
):
    data = await election_service.import_students_from_rows([student.dict()])
    await audit_service.log_action(
        actor_id=user.id,
        actor_role="admin",
        action="ADD_STUDENT_MANUAL",
        target_type="student",
        details={"student_id": student.student_id},
    )
    return {"message": "Student added successfully.", "data": data}


@router.get("/audit-log")
async def get_audit_log(
    user: AuthUser = Depends(require_admin),
    page_size: int = Query(15, ge=1, le=500),
    page_token: Optional[str] = Query(None),
):
    result = await paginate(
        table="audit_log",
        select="*",
        order_column="id",
        page_size=page_size,
        page_token=page_token,
    )
    return result
