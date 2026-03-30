from fastapi import HTTPException
from database import get_async_supabase
from services import election_service
from deps import create_access_token
from datetime import timedelta
import hashlib
import secrets
import string


async def validate_student(student_id: str) -> dict:
    """Check that a student exists and return all active/completed elections with a secure access token."""
    available_elections = await election_service.get_available_elections()
    if not available_elections:
        raise HTTPException(
            status_code=400,
            detail="No active or completed elections currently available.",
        )

    # Role guard: check if this ID belongs to an adviser or admin to prevent unauthorized access
    supabase = await get_async_supabase()
    adviser_check = (
        await supabase.table("advisers")
        .select("id")
        .eq("id_number", student_id)
        .execute()
    )
    admin_check = (
        await supabase.table("admins")
        .select("id")
        .eq("id_number", student_id)
        .execute()
    )
    if adviser_check.data or admin_check.data:
        raise HTTPException(
            status_code=403,
            detail="Only registered students can access the voting portal.",
        )

    result = (
        await supabase.table("students")
        .select("id, student_id, full_name, program, year_level")
        .eq("student_id", student_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Student ID not found in the registered voters list.",
        )

    student = result.data[0]

    # Generate a short-lived student token (30 minutes)
    access_token = create_access_token(
        data={
            "sub": student["id"],
            "student_id": student["student_id"],
            "role": "student",
        },
        expires_delta=timedelta(minutes=30),
    )

    # Check which elections the student has already voted in
    voted_result = await (
        supabase.table("votes")
        .select("election_id")
        .eq("student_id", student["id"])
        .execute()
    )
    voted_election_ids = set(v["election_id"] for v in (voted_result.data or []))

    # Annotate each election with has_voted
    elections_with_status = []
    for election in available_elections:
        elections_with_status.append(
            {**election, "has_voted": election["id"] in voted_election_ids}
        )

    return {
        "access_token": access_token,
        "student": student,
        "active_elections": elections_with_status,
    }


async def get_or_create_voting_pin(student_uuid: str) -> str:
    """Generate a 6-character alphanumeric PIN if missing, excluding ambiguous chars."""
    supabase = await get_async_supabase()
    res = (
        await supabase.table("students")
        .select("voting_pin")
        .eq("id", student_uuid)
        .execute()
    )

    # If PIN already exists, return it (one PIN per voting session/life until used)
    if res.data and res.data[0].get("voting_pin"):
        return res.data[0]["voting_pin"]

    # Generate a fresh 6-character Alphanumeric PIN (excluding O, 0, I, 1)
    chars = string.ascii_uppercase + string.digits
    excluded = {"O", "0", "I", "1"}
    alphabet = "".join(c for c in chars if c not in excluded)
    new_pin = "".join(secrets.choice(alphabet) for _ in range(6))

    await (
        supabase.table("students")
        .update({"voting_pin": new_pin})
        .eq("id", student_uuid)
        .execute()
    )
    return new_pin


def _generate_receipt_id(student_uuid: str, election_id: str) -> str:
    """Generate a unique, deterministic receipt ID for vote verification."""
    raw = f"{student_uuid}:{election_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


async def cast_votes(
    student_id: str, election_id: str, votes: list, voting_pin: str
) -> dict:
    """Insert vote records via RPC and mark the student as voted. Returns receipt info."""
    supabase = await get_async_supabase()
    student_result = (
        await supabase.table("students")
        .select("id, voting_pin")
        .eq("student_id", student_id)
        .execute()
    )

    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student ID not found.")

    student_uuid = student_result.data[0]["id"]
    stored_pin = student_result.data[0].get("voting_pin")

    # Verify PIN
    if not stored_pin or voting_pin != stored_pin:
        raise HTTPException(
            status_code=403,
            detail="Invalid Voting PIN. Please enter the correct PIN to cast your vote.",
        )

    # Use the High-Concurrency RPC for atomic updates
    try:
        rpc_result = await supabase.rpc(
            "cast_ballot_v2",
            {
                "election_id_param": str(election_id),
                "student_uuid_param": str(student_uuid),
                "votes_json": votes,
            },
        ).execute()

        data = rpc_result.data
        result_dict = {}
        if isinstance(data, list) and len(data) > 0:
            result_dict = data[0]
        elif isinstance(data, dict):
            result_dict = data

        # Ensure we always have a receipt_id and vote_count for the frontend
        if not result_dict.get("receipt_id"):
            result_dict["receipt_id"] = _generate_receipt_id(str(student_uuid), str(election_id))
        if "vote_count" not in result_dict:
            result_dict["vote_count"] = len(votes)

        # IMPORTANT: Invalidate the PIN immediately after a successful vote
        await (
            supabase.table("students")
            .update({"voting_pin": None})
            .eq("id", student_uuid)
            .execute()
        )
        return result_dict
    except Exception as e:
        error_msg = str(e)
        if "already_voted" in error_msg.lower() or "duplicate key" in error_msg.lower():
            raise HTTPException(
                status_code=403,
                detail="You have already cast your ballot for this election.",
            )
        raise HTTPException(
            status_code=400, detail=f"Database error during voting: {error_msg}"
        )


async def get_vote_summary(student_id: str, election_id: str) -> dict:
    """Get the vote summary for a student in a specific election."""
    supabase = await get_async_supabase()
    student_result = (
        await supabase.table("students")
        .select("id, student_id, full_name")
        .eq("student_id", student_id)
        .execute()
    )
    if not student_result.data:
        raise HTTPException(status_code=404, detail="Student not found.")

    student_uuid = student_result.data[0]["id"]

    # Get votes with candidate and partylist info
    votes_result = await (
        supabase.table("votes")
        .select(
            "position, candidate_id, created_at, candidates!inner(id, students!inner(full_name), partylists(name))"
        )
        .eq("student_id", student_uuid)
        .eq("election_id", election_id)
        .execute()
    )

    if not votes_result.data:
        return {"has_voted": False, "votes": [], "receipt_id": None}

    # Generate deterministic receipt from student+election
    receipt_id = (
        hashlib.sha256(f"{student_uuid}:{election_id}".encode())
        .hexdigest()[:12]
        .upper()
    )

    return {
        "has_voted": True,
        "receipt_id": receipt_id,
        "voted_at": votes_result.data[0].get("created_at")
        if votes_result.data
        else None,
        "votes": votes_result.data,
    }
