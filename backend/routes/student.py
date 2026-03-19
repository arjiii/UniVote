from fastapi import APIRouter, HTTPException, Depends
from models import StudentAuth, VoteSubmit
from services import student_service, adviser_service
from deps import CurrentStudent, StudentUser

router = APIRouter()


@router.post("/validate")
def validate_student(auth: StudentAuth):
    result = student_service.validate_student(auth.student_id)
    return {
        "message": "Access granted",
        "student": result["student"],
        "access_token": result["access_token"],
        "active_elections": result["active_elections"]
    }


@router.post("/vote")
def cast_vote(
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
    result = student_service.cast_votes(
        student_id=vote_submit.student_id,
        election_id=str(vote_submit.election_id),
        votes=votes_payload,
    )
    return {
        "message": "Vote submitted successfully",
        "receipt_id": result["receipt_id"],
        "vote_count": result["vote_count"]
    }


@router.get("/candidates")
def get_candidates(election_id: str, student: StudentUser = CurrentStudent):
    from services import adviser_service
    return {"data": adviser_service.get_candidates(election_id)}


@router.get("/vote-summary")
def get_vote_summary(student_id: str, election_id: str, student: StudentUser = CurrentStudent):
    # Security check
    if student_id != student.student_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot view other students' summary.")
    return student_service.get_vote_summary(student_id, election_id)


@router.get("/results")
def get_results(election_id: str):
    # Results are usually public for students once the election is active/completed
    return {"data": adviser_service.get_live_results(election_id)}
