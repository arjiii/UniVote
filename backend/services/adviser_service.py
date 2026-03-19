from fastapi import HTTPException
from database import supabase
from uuid import UUID
from typing import Optional


def _ensure_election_modifiable(election_id: str):
    """Raise error if election is active or completed."""
    res = supabase.table("elections").select("status").eq("id", election_id).execute()
    if res.data:
        status = res.data[0]["status"]
        if status in ("active", "completed"):
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot modify data because the election is already {status}."
            )


def get_partylists(election_id: Optional[str] = None) -> list:
    query = supabase.table("partylists").select("*")
    if election_id:
        query = query.eq("election_id", election_id)
    return query.execute().data


def create_partylist(election_id: str, name: str) -> dict:
    _ensure_election_modifiable(election_id)
    result = supabase.table("partylists").insert({"election_id": election_id, "name": name}).execute()
    return result.data


def update_partylist(partylist_id: str, name: str) -> dict:
    result = supabase.table("partylists").update({"name": name}).eq("id", partylist_id).execute()
    return result.data


def delete_partylist(partylist_id: str) -> dict:
    # Get election_id first to check status
    pl = supabase.table("partylists").select("election_id").eq("id", partylist_id).execute()
    if pl.data:
        _ensure_election_modifiable(pl.data[0]["election_id"])

    # Explicitly delete candidates associated with this partylist first (Cascading Delete)
    supabase.table("candidates").delete().eq("partylist_id", partylist_id).execute()
    # Then delete the partylist
    result = supabase.table("partylists").delete().eq("id", partylist_id).execute()
    return result.data


def get_candidates(election_id: Optional[str] = None) -> list:
    # Fixed: use full_name (matches new schema), join partylists for name
    query = supabase.table("candidates").select(
        "*, students!inner(student_id, full_name), partylists(name)"
    )
    if election_id:
        query = query.eq("election_id", election_id)
    return query.execute().data


def create_candidate(student_id: str, position: str, election_id: str, partylist_id: Optional[UUID] = None) -> dict:
    _ensure_election_modifiable(election_id)
    # Verify the student exists
    student = supabase.table("students").select("id").eq("student_id", student_id).execute()
    if not student.data:
        raise HTTPException(status_code=404, detail="Student not found. Cannot be made a candidate.")

    student_uuid = student.data[0]["id"]
    
    # Check for duplicate
    existing = supabase.table("candidates")\
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

    result = supabase.table("candidates").insert(payload).execute()
    return result.data


def delete_candidate(candidate_id: str) -> dict:
    # Get election_id to check status
    cand = supabase.table("candidates").select("election_id").eq("id", candidate_id).execute()
    if cand.data:
        _ensure_election_modifiable(cand.data[0]["election_id"])
        
    result = supabase.table("candidates").delete().eq("id", candidate_id).execute()
    return result.data


def get_live_results(election_id: str) -> dict:
    elec_res = supabase.table("elections").select("status").eq("id", election_id).execute()
    status = elec_res.data[0]["status"] if elec_res.data else "unknown"

    votes_result = (
        supabase.table("votes")
        .select("position, candidate_id")
        .eq("election_id", election_id)
        .execute()
    )

    tallies: dict = {}
    for vote in votes_result.data:
        pos = vote["position"]
        cid = vote["candidate_id"]
        tallies.setdefault(pos, {})
        tallies[pos][cid] = tallies.get(pos, {}).get(cid, 0) + 1

    return {
        "status": status,
        "tallies": tallies
    }
