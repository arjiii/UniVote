from fastapi import APIRouter, Depends
from models import PartylistCreate, CandidateCreate
from services import adviser_service, audit_service
from deps import require_adviser, AuthUser

router = APIRouter()


@router.get("/partylists")
async def get_partylists(
    election_id: str | None = None,
    user: AuthUser = Depends(require_adviser),
):
    return {"data": await adviser_service.get_partylists(election_id)}


@router.post("/partylists")
async def create_partylist(
    partylist: PartylistCreate,
    election_id: str,
    user: AuthUser = Depends(require_adviser),
):
    data = await adviser_service.create_partylist(election_id, partylist.name)
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="CREATE_PARTYLIST", target_type="partylist",
        target_id=data[0]["id"] if data else None,
        details={"name": partylist.name, "election_id": election_id},
    )
    return {"message": "Partylist created", "data": data}


@router.put("/partylists/{partylist_id}")
async def update_partylist(
    partylist_id: str,
    partylist: PartylistCreate,
    user: AuthUser = Depends(require_adviser),
):
    data = await adviser_service.update_partylist(partylist_id, partylist.name)
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="UPDATE_PARTYLIST", target_type="partylist",
        target_id=partylist_id,
        details={"name": partylist.name},
    )
    return {"message": "Partylist updated", "data": data}


@router.delete("/partylists/{partylist_id}")
async def delete_partylist(
    partylist_id: str,
    user: AuthUser = Depends(require_adviser),
):
    data = await adviser_service.delete_partylist(partylist_id)
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="DELETE_PARTYLIST", target_type="partylist",
        target_id=partylist_id,
        details={},
    )
    return {"message": "Partylist deleted"}


@router.get("/candidates")
async def get_candidates(
    election_id: str | None = None,
    user: AuthUser = Depends(require_adviser),
):
    return {"data": await adviser_service.get_candidates(election_id)}


@router.post("/candidates")
async def create_candidate(
    candidate: CandidateCreate,
    election_id: str,
    user: AuthUser = Depends(require_adviser),
):
    data = await adviser_service.create_candidate(
        student_id=candidate.student_id,
        position=candidate.position,
        election_id=election_id,
        partylist_id=candidate.partylist_id,
    )
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="ADD_CANDIDATE", target_type="candidate",
        target_id=data[0]["id"] if data else None,
        details={"student_id": candidate.student_id, "position": candidate.position},
    )
    return {"message": "Candidate added", "data": data}


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    user: AuthUser = Depends(require_adviser),
):
    data = await adviser_service.delete_candidate(candidate_id)
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="DELETE_CANDIDATE", target_type="candidate",
        target_id=candidate_id,
        details={},
    )
    return {"message": "Candidate deleted"}


@router.get("/live-results/{election_id}")
async def get_live_results(
    election_id: str,
    user: AuthUser = Depends(require_adviser),
):
    return {"data": await adviser_service.get_live_results(election_id)}


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    user: AuthUser = Depends(require_adviser),
):
    return {"data": await audit_service.get_audit_log(limit)}


@router.post("/elections/{election_id}/refresh-passcode")
async def refresh_passcode(
    election_id: str,
    user: AuthUser = Depends(require_adviser),
):
    new_passcode = await adviser_service.refresh_adviser_passcode(election_id)
    await audit_service.log_action(
        actor_id=user.id, actor_role=user.role,
        action="REFRESH_PASSCODE", target_type="election",
        target_id=election_id,
        details={"passcode": new_passcode},
    )
    return {"message": "Passcode refreshed", "adviser_passcode": new_passcode}
