"""
Seed script: inject dummy partylists, students, and candidates into the database.
Run from backend dir: python seed_data.py
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY missing in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── 1. Get the first active or upcoming election ──
elections = supabase.table("elections").select("*").execute().data
if not elections:
    print("No elections found. Creating a test election...")
    result = supabase.table("elections").insert({
        "name": "SY 2025-2026 Student Council Election",
        "description": "Annual student council election",
        "start_date": "2026-03-01T00:00:00",
        "end_date": "2026-04-01T00:00:00",
        "status": "active"
    }).execute()
    election = result.data[0]
    print(f"  Created election: {election['name']} (ID: {election['id']})")
else:
    election = elections[0]
    print(f"  Using election: {election['name']} (ID: {election['id']})")

election_id = election["id"]

# ── 2. Create partylists ──
partylist_names = ["Progressive Alliance", "Student First Coalition", "Independent Movement"]
partylist_map = {}

for name in partylist_names:
    # Check if already exists
    existing = supabase.table("partylists").select("*").eq("election_id", election_id).eq("name", name).execute().data
    if existing:
        partylist_map[name] = existing[0]["id"]
        print(f"  Partylist '{name}' already exists (ID: {existing[0]['id']})")
    else:
        result = supabase.table("partylists").insert({"election_id": election_id, "name": name}).execute()
        partylist_map[name] = result.data[0]["id"]
        print(f"  Created partylist '{name}' (ID: {result.data[0]['id']})")

# ── 3. Create students (voters + candidates) ──
students_data = [
    # Candidates
    {"student_id": "2021-00001", "full_name": "Alex Rivera"},
    {"student_id": "2021-00002", "full_name": "Maria Santos"},
    {"student_id": "2021-00003", "full_name": "James Lee"},
    {"student_id": "2021-00004", "full_name": "Sarah Chen"},
    {"student_id": "2021-00005", "full_name": "David Park"},
    {"student_id": "2021-00006", "full_name": "Lena Torres"},
    {"student_id": "2021-00007", "full_name": "Noah Kim"},
    {"student_id": "2021-00008", "full_name": "Emma Garcia"},
    {"student_id": "2021-00009", "full_name": "Carlos Reyes"},
    # Regular voters
    {"student_id": "2022-00100", "full_name": "Jane Smith"},
    {"student_id": "2022-00101", "full_name": "John Doe"},
    {"student_id": "2022-00102", "full_name": "Anna Cruz"},
]

result = supabase.table("students").upsert(students_data).execute()
print(f"  Upserted {len(result.data)} students")

# Build student_id → UUID map
student_uuid_map = {}
for s in result.data:
    student_uuid_map[s["student_id"]] = s["id"]

# ── 4. Create candidates ──
candidates_data = [
    # President (3 candidates)
    {"student_id": "2021-00001", "position": "President",       "party": "Progressive Alliance"},
    {"student_id": "2021-00002", "position": "President",       "party": "Student First Coalition"},
    {"student_id": "2021-00003", "position": "President",       "party": "Independent Movement"},
    # Vice President (2 candidates)
    {"student_id": "2021-00004", "position": "Vice President",  "party": "Progressive Alliance"},
    {"student_id": "2021-00005", "position": "Vice President",  "party": "Student First Coalition"},
    # Secretary General (2 candidates)
    {"student_id": "2021-00006", "position": "Secretary",       "party": "Independent Movement"},
    {"student_id": "2021-00007", "position": "Secretary",       "party": "Student First Coalition"},
    # Treasurer (2 candidates) 
    {"student_id": "2021-00008", "position": "Treasurer",       "party": "Progressive Alliance"},
    {"student_id": "2021-00009", "position": "Treasurer",       "party": "Independent Movement"},
]

created = 0
skipped = 0
for c in candidates_data:
    student_uuid = student_uuid_map.get(c["student_id"])
    if not student_uuid:
        print(f"  WARNING: Student {c['student_id']} not found, skipping")
        continue

    # Check if already a candidate
    existing = supabase.table("candidates") \
        .select("id") \
        .eq("election_id", election_id) \
        .eq("student_id", student_uuid) \
        .execute().data
    
    if existing:
        skipped += 1
        continue

    payload = {
        "election_id": election_id,
        "student_id": student_uuid,
        "position": c["position"],
        "partylist_id": partylist_map.get(c["party"]),
    }
    supabase.table("candidates").insert(payload).execute()
    created += 1

print(f"  Created {created} candidates, skipped {skipped} (already exist)")

print("\n✅ Seed complete!")
print(f"   Election: {election['name']}")
print(f"   Partylists: {', '.join(partylist_names)}")
print(f"   Positions: President, Vice President, Secretary, Treasurer")
print(f"   Test voter IDs: 2022-00100, 2022-00101, 2022-00102")
