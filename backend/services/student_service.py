from fastapi import HTTPException
from database import supabase
from services import election_service
from deps import create_access_token
from datetime import timedelta
import hashlib
import time


def validate_student(student_id: str) -> dict:
    """Check that a student exists and return all active/completed elections with a secure access token."""
    available_elections = election_service.get_available_elections()
    if not available_elections:
        raise HTTPException(status_code=400, detail="No active or completed elections currently available.")

    # Role guard: check if this ID belongs to an adviser or admin to prevent unauthorized access
    adviser_check = supabase.table("advisers").select("id").eq("email", student_id).execute()
    admin_check = supabase.table("admins").select("id").eq("email", student_id).execute()
    if adviser_check.data or admin_check.data:
        raise HTTPException(
            status_code=403,
            detail="This ID belongs to a staff account. Only registered students can access the voting portal."
        )

    result = supabase.table("students").select("*").eq("student_id", student_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Student ID not found in the registered voters list.")

    student = result.data[0]

    # Generate a short-lived student token (30 minutes)
    access_token = create_access_token(
        data={"sub": student["id"], "student_id": student["student_id"], "role": "student"},
        expires_delta=timedelta(minutes=30)
    )

    # Check which elections the student has already voted in
    voted_result = (
        supabase.table("votes")
        .select("election_id")
        .eq("student_id", student["id"])
        .execute()
    )
    voted_election_ids = set(v["election_id"] for v in (voted_result.data or []))

    # Annotate each election with has_voted
    elections_with_status = []
    for election in available_elections:
        elections_with_status.append({
            **election,
            "has_voted": election["id"] in voted_election_ids
        })

    return {
        "access_token": access_token,
        "student": student,
        "active_elections": elections_with_status
    }


def _generate_receipt_id(student_uuid: str, election_id: str) -> str:
    """Generate a unique, deterministic receipt ID for vote verification."""
    raw = f"{student_uuid}:{election_id}:{int(time.time())}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def cast_votes(student_id: str, election_id: str, votes: list) -> dict:
    """Insert vote records and mark the student as voted. Returns receipt info."""
    student_result = supabase.table("students").select("id").eq("student_id", student_id).execute()

    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student ID not found.")

    student_uuid = student_result.data[0]["id"]

    # Check for existing vote in this specific election to prevent double voting
    already_voted = (
        supabase.table("votes")
        .select("id")
        .eq("student_id", student_uuid)
        .eq("election_id", election_id)
        .execute()
    )
    if already_voted.data:
        raise HTTPException(status_code=403, detail="You have already cast your ballot for this election.")

    receipt_id = _generate_receipt_id(student_uuid, election_id)

    votes_to_insert = [
        {
            "election_id": election_id,
            "student_id": student_uuid,
            "candidate_id": str(vote["candidate_id"]),
            "position": vote["position"],
        }
        for vote in votes
    ]

    try:
        supabase.table("votes").insert(votes_to_insert).execute()
        supabase.table("students").update({"has_voted": True}).eq("id", student_uuid).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"receipt_id": receipt_id, "vote_count": len(votes_to_insert)}


def get_vote_summary(student_id: str, election_id: str) -> dict:
    """Get the vote summary for a student in a specific election."""
    student_result = supabase.table("students").select("id, student_id, full_name").eq("student_id", student_id).execute()
    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student not found.")

    student_uuid = student_result.data[0]["id"]

    # Get votes with candidate and partylist info
    votes_result = (
        supabase.table("votes")
        .select("position, candidate_id, created_at, candidates!inner(id, students!inner(full_name), partylists(name))")
        .eq("student_id", student_uuid)
        .eq("election_id", election_id)
        .execute()
    )

    if not votes_result.data:
        return {"has_voted": False, "votes": [], "receipt_id": None}

    # Generate deterministic receipt from student+election
    receipt_id = hashlib.sha256(f"{student_uuid}:{election_id}".encode()).hexdigest()[:12].upper()

    return {
        "has_voted": True,
        "receipt_id": receipt_id,
        "voted_at": votes_result.data[0].get("created_at") if votes_result.data else None,
        "votes": votes_result.data
    }
