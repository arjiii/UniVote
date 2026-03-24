from fastapi import APIRouter, HTTPException, Depends, Request
from models import StudentAuth, VoteSubmit, PasscodeVerify
from services import student_service, adviser_service
from deps import CurrentStudent, StudentUser
from limiter import limiter

router = APIRouter()


@router.post("/validate")
@limiter.limit("5/minute")
async def validate_student(request: Request, auth: StudentAuth):
    result = await student_service.validate_student(auth.student_id)
    return {
        "message": "Access granted",
        "student": result["student"],
        "access_token": result["access_token"],
        "active_elections": result["active_elections"]
    }


@router.post("/vote")
@limiter.limit("2/minute")
async def cast_vote(
    request: Request,
    vote_submit: VoteSubmit,
    student: StudentUser = CurrentStudent,
):
    # Security check: ensure student_id in payload matches token
    if vote_submit.student_id != student.student_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Student ID mismatch.")

    votes_payload = [
        {"candidate_id": str(v.candidate_id), "position": v.position}
        for v in vote_submit.votes
    ]
    result = await student_service.cast_votes(
        student_id=vote_submit.student_id,
        election_id=str(vote_submit.election_id),
        votes=votes_payload,
        voting_pin=vote_submit.voting_pin,
    )
    return {
        "message": "Vote submitted successfully",
        "receipt_id": result["receipt_id"],
        "vote_count": result["vote_count"]
    }


@router.get("/candidates")
async def get_candidates(election_id: str, student: StudentUser = CurrentStudent):
    return {"data": await adviser_service.get_candidates(election_id)}


@router.get("/vote-summary")
async def get_vote_summary(student_id: str, election_id: str, student: StudentUser = CurrentStudent):
    # Security check
    if student_id != student.student_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot view other students' summary.")
    return await student_service.get_vote_summary(student_id, election_id)


@router.get("/results")
async def get_results(election_id: str):
    # Results are usually public for students once the election is active/completed
    return {"data": await adviser_service.get_live_results(election_id)}


@router.post("/verify-passcode")
async def verify_passcode(payload: PasscodeVerify, student: StudentUser = CurrentStudent):
    supabase = await student_service.get_async_supabase()
    res = await supabase.table("elections").select("adviser_passcode").eq("id", str(payload.election_id)).execute()
    
    if not res.data or res.data[0].get("adviser_passcode") != payload.passcode:
        raise HTTPException(status_code=403, detail="Invalid Adviser Passcode.")
    
    return {"message": "Passcode verified"}


@router.get("/voting-pin")
async def get_voting_pin(student_id: str, student: StudentUser = CurrentStudent):
    if student_id != student.student_id:
         raise HTTPException(status_code=403, detail="Unauthorized")
    
    # We need the UUID for the service call
    supabase = await student_service.get_async_supabase()
    st_res = await supabase.table("students").select("id").eq("student_id", student_id).execute()
    if not st_res.data:
        raise HTTPException(status_code=404, detail="Student not found")
        
    pin = await student_service.get_or_create_voting_pin(st_res.data[0]["id"])
    return {"voting_pin": pin}
