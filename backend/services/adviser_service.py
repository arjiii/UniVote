from fastapi import HTTPException
from database import get_async_supabase
from uuid import UUID
from typing import Optional
import secrets
import string


async def _ensure_election_modifiable(election_id: str):
    """Raise error if election is active or completed."""
    supabase = await get_async_supabase()
    res = await supabase.table("elections").select("status").eq("id", election_id).execute()
    if res.data:
        status = res.data[0]["status"]
        if status in ("active", "completed"):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot modify data because the election is already {status}."
            )


async def get_partylists(election_id: Optional[str] = None) -> list:
    supabase = await get_async_supabase()
    query = supabase.table("partylists").select("id, name, election_id, created_at")
    if election_id:
        query = query.eq("election_id", election_id)
    result = await query.execute()
    return result.data


async def create_partylist(election_id: str, name: str) -> dict:
    await _ensure_election_modifiable(election_id)
    supabase = await get_async_supabase()
    result = await supabase.table("partylists").insert({"election_id": election_id, "name": name}).execute()
    return result.data


async def update_partylist(partylist_id: str, name: str) -> dict:
    supabase = await get_async_supabase()
    result = await supabase.table("partylists").update({"name": name}).eq("id", partylist_id).execute()
    return result.data


async def delete_partylist(partylist_id: str) -> dict:
    # Get election_id first to check status
    supabase = await get_async_supabase()
    pl = await supabase.table("partylists").select("election_id").eq("id", partylist_id).execute()
    if pl.data:
        await _ensure_election_modifiable(pl.data[0]["election_id"])

    # Explicitly delete candidates associated with this partylist first (Cascading Delete)
    await supabase.table("candidates").delete().eq("partylist_id", partylist_id).execute()
    # Then delete the partylist
    result = await supabase.table("partylists").delete().eq("id", partylist_id).execute()
    return result.data


async def get_candidates(election_id: Optional[str] = None) -> list:
    # Fixed: use full_name (matches new schema), join partylists for name
    supabase = await get_async_supabase()
    query = supabase.table("candidates").select(
        "id, position, election_id, student_id, partylist_id, vote_count, students!inner(student_id, full_name), partylists(name)"
    )
    if election_id:
        query = query.eq("election_id", election_id)
    result = await query.execute()
    return result.data


async def create_candidate(student_id: str, position: str, election_id: str, partylist_id: Optional[UUID] = None) -> dict:
    await _ensure_election_modifiable(election_id)
    # Verify the student exists
    supabase = await get_async_supabase()
    student = await supabase.table("students").select("id").eq("student_id", student_id).execute()
    if not student.data:
        raise HTTPException(status_code=404, detail="Student not found. Cannot be made a candidate.")

    student_uuid = student.data[0]["id"]
    
    # Check for duplicate
    existing = await supabase.table("candidates")\
        .select("id")\
        .eq("election_id", election_id)\
        .eq("student_id", student_uuid)\
        .execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="This student is already a candidate in this election.")

    payload = {
        "election_id": election_id,
        "student_id": student_uuid,
        "position": position,
    }
    if partylist_id:
        payload["partylist_id"] = str(partylist_id)

    result = await supabase.table("candidates").insert(payload).execute()
    return result.data


async def delete_candidate(candidate_id: str) -> dict:
    # Get election_id to check status
    supabase = await get_async_supabase()
    cand = await supabase.table("candidates").select("election_id").eq("id", candidate_id).execute()
    if cand.data:
        await _ensure_election_modifiable(cand.data[0]["election_id"])
        
    result = await supabase.table("candidates").delete().eq("id", candidate_id).execute()
    return result.data


async def get_live_results(election_id: str) -> dict:
    """Retrieve tallies using the optimized vote_count column."""
    supabase = await get_async_supabase()
    elec_res = await supabase.table("elections").select("status").eq("id", election_id).execute()
    status = elec_res.data[0]["status"] if elec_res.data else "unknown"

    # Fetch candidates and their vote_counts directly (Optimized for High Concurrency)
    candidates_res = await (
        supabase.table("candidates")
        .select("id, position, vote_count")
        .eq("election_id", election_id)
        .execute()
    )

    tallies: dict = {}
    for cand in candidates_res.data:
        pos = cand["position"]
        cid = cand["id"]
        count = cand.get("vote_count", 0)
        tallies.setdefault(pos, {})
        tallies[pos][cid] = count

    return {
        "status": status,
        "tallies": tallies
    }


async def refresh_adviser_passcode(election_id: str) -> str:
    """Generate a new 16-digit alphanumeric passcode for an election."""
    # Format: XXXX-XXXX-XXXX-XXXX
    alphabet = string.ascii_uppercase + string.digits
    blocks = []
    for _ in range(4):
        blocks.append(''.join(secrets.choice(alphabet) for _ in range(4)))
    
    new_passcode = "-".join(blocks)
    
    supabase = await get_async_supabase()
    await supabase.table("elections").update({"adviser_passcode": new_passcode}).eq("id", election_id).execute()
    
    return new_passcode
