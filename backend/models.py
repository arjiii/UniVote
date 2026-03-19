from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class UserLogin(BaseModel):
    username: str
    password: str

class StudentImport(BaseModel):
    student_id: str
    full_name: str

class StudentManualCreate(BaseModel):
    student_id: str
    full_name: str
    course: Optional[str] = None
    year_level: Optional[int] = None

class ElectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: str  # ISO format
    end_date: str    # ISO format

class ElectionStatusUpdate(BaseModel):
    status: str  # 'upcoming', 'active', or 'completed'

class PartylistCreate(BaseModel):
    name: str

class CandidateCreate(BaseModel):
    student_id: str
    position: str
    partylist_id: Optional[UUID] = None

class VoteItem(BaseModel):
    candidate_id: UUID
    position: str

class VoteSubmit(BaseModel):
    student_id: str
    election_id: UUID
    votes: List[VoteItem]

class StudentAuth(BaseModel):
    student_id: str
