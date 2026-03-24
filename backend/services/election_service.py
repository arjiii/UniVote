from fastapi import HTTPException
from database import get_async_supabase
from datetime import datetime, timezone
from typing import Optional


async def get_elections() -> list:
    supabase = await get_async_supabase()
    result = await (
        supabase.table("elections")
        .select("id, name, start_date, end_date, description, status, created_at, adviser_passcode")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


async def create_election(name: str, start_date: str, end_date: str, description: Optional[str] = None) -> list:
    try:
        # Handle ISO strings from frontend (e.g. 2024-03-19T10:00:00.000Z)
        s_date = start_date.replace('Z', '+00:00')
        e_date = end_date.replace('Z', '+00:00')
        start = datetime.fromisoformat(s_date)
        end = datetime.fromisoformat(e_date)
        if end <= start:
            raise HTTPException(status_code=400, detail="End date must be after start date.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format provided.")

    payload = {
        "name": name,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
        "status": "upcoming"
    }
    supabase = await get_async_supabase()
    result = await supabase.table("elections").insert(payload).execute()
    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to store election. This may be due to database permissions (RLS). Please ensure you are using a service_role key."
        )
    return result.data


async def update_election_status(election_id: str, status: str) -> list:
    payload = {"status": status}
    if status == "completed":
        payload["ended_at"] = datetime.now(timezone.utc).isoformat()
        
    supabase = await get_async_supabase()
    result = (
        await supabase.table("elections")
        .update(payload)
        .eq("id", election_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Election not found.")
    return result.data


async def get_active_election() -> dict | None:
    """Retrieve the currently active election, if any."""
    supabase = await get_async_supabase()
    result = await supabase.table("elections").select("*").eq("status", "active").execute()
    return result.data[0] if result.data else None


async def get_active_elections() -> list:
    """Retrieve all currently active elections."""
    supabase = await get_async_supabase()
    result = await supabase.table("elections").select("id, name, start_date, end_date, description, status").eq("status", "active").execute()
    return result.data or []


async def get_available_elections() -> list:
    """Retrieve all active and completed elections for student access."""
    supabase = await get_async_supabase()
    result = await supabase.table("elections").select("id, name, start_date, end_date, description, status").in_("status", ["active", "completed"]).execute()
    return result.data or []


async def import_students_from_rows(rows: list[dict]) -> list:
    """
    Expects rows to be dicts with at least 'student_id' and 'name' keys.
    Returns the inserted data.
    """
    to_insert = []
    for row in rows:
        # Flexible support for 'name' or 'full_name'
        sid = row.get("student_id")
        fname = row.get("full_name") or row.get("name")
        
        if sid and fname:
            student_data = {
                "student_id": sid,
                "full_name": fname
            }
            if "program" in row:
                student_data["program"] = row["program"]
            if "year_level" in row:
                try:
                    student_data["year_level"] = int(row["year_level"])
                except (ValueError, TypeError):
                    pass
            to_insert.append(student_data)

    if not to_insert:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV format. Need student_id and name columns.",
        )

    supabase = await get_async_supabase()
    result = await supabase.table("students").upsert(to_insert).execute()
    if not result.data:
        raise HTTPException(
            status_code=500,
            detail="Failed to store students. This may be due to database permissions (RLS)."
        )
    return result.data


async def delete_election(election_id: str) -> dict:
    # 1. Delete all votes related to this election
    # We need to get all candidates first or just delete by election_id if votes table has it
    # Looking at the architecture, votes usually link to candidates.
    # If the database has FK with ON DELETE CASCADE, this is easier.
    # But we'll do it manually to be safe.
    
    # Actually, let's check if 'votes' has 'election_id'
    # For now, we'll try to delete from votes where candidate_id is in this election's candidates
    supabase = await get_async_supabase()
    candidates_res = await supabase.table("candidates").select("id").eq("election_id", election_id).execute()
    candidate_ids = [c["id"] for c in candidates_res.data]
    
    if candidate_ids:
        await supabase.table("votes").delete().in_("candidate_id", candidate_ids).execute()
        await supabase.table("candidates").delete().in_("id", candidate_ids).execute()
    
    # 2. Delete partylists
    await supabase.table("partylists").delete().eq("election_id", election_id).execute()
    
    # 3. Finally delete the election
    result = await supabase.table("elections").delete().eq("id", election_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Election not found.")
    
    return {"message": "Election and all related data deleted successfully."}


async def update_student(student_id: str, payload: dict) -> list:
    """Update student information with mass assignment protection."""
    # Whitelist allowed fields
    allowed_fields = {"full_name", "program", "year_level"}
    update_data = {k: v for k, v in payload.items() if k in allowed_fields}
    
    if "year_level" in update_data:
        try:
            update_data["year_level"] = int(update_data["year_level"])
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="year_level must be an integer.")

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid update fields provided.")

    supabase = await get_async_supabase()
    result = await supabase.table("students").update(update_data).eq("student_id", student_id).execute()
    return result.data


async def delete_student(student_id: str) -> dict:
    """Delete a student and their votes."""
    # First get the internal UUID
    supabase = await get_async_supabase()
    student_res = await supabase.table("students").select("id").eq("student_id", student_id).execute()
    if not student_res.data:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    student_uuid = student_res.data[0]["id"]
    
    # 1. Delete votes
    await supabase.table("votes").delete().eq("student_id", student_uuid).execute()
    
    # 2. Delete student
    await supabase.table("students").delete().eq("id", student_uuid).execute()
    
    return {"message": "Student and their votes deleted successfully."}
