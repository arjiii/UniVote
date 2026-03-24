import random
from typing import Optional, List, Dict, Any
from locust import HttpUser, task, between, events

class UniVoteUser(HttpUser):
    host = "http://127.0.0.1:8000"  # Default host for local testing
    wait_time = between(1, 4)
    student_id: str = ""
    token: Optional[str] = None
    election_id: Optional[str] = None
    student_record: Optional[Dict[str, Any]] = None

    def on_start(self):
        """Pre-test setup: Login/Validate a student to get a token."""
        try:
            # Mass Testing: Randomly pick from our 5000 test students (TEST-0001 to TEST-5000)
            self.student_id = f"TEST-{random.randint(1, 5000):04d}"
            
            # 1. Login/Authorize
            response = self.client.post("/api/student/validate", json={"student_id": self.student_id})
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.student_record = data.get("student")
                # Pick the first available election
                elections = data.get("active_elections", [])
                if elections:
                    self.election_id = elections[0]["id"]
                
                token_val = self.token or ""
                token_snip = token_val[:10]
                print(f"Validated student {self.student_id}. Token: {token_snip}...")
            else:
                print(f"Failed to validate student {self.student_id}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"CRITICAL ERROR in on_start for student: {e}")

    @task(3)
    def view_candidates(self):
        """Simulate a student viewing the ballot."""
        if not self.token or not self.election_id:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"/api/student/candidates?election_id={self.election_id}"
        self.client.get(url, headers=headers, name="/api/student/candidates")

    @task(1)
    def cast_vote(self):
        """Simulate a student casting their votes."""
        if not self.token or not self.election_id or not self.student_record:
            return

        # Fetch candidates first to know whom to vote for
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"/api/student/candidates?election_id={self.election_id}"
        resp = self.client.get(url, headers=headers, name="/api/student/candidates")
        
        if resp.status_code == 200:
            candidates = resp.json().get("data", [])
            if not candidates:
                return

            # Group candidates by position (rough simulation)
            positions = {}
            for c in candidates:
                pos = c.get("position", "Unknown")
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(c)

            # Select one candidate per position
            votes = []
            for pos, cand_list in positions.items():
                chosen = random.choice(cand_list)
                votes.append({
                    "candidate_id": chosen["id"],
                    "position": chosen.get("position")
                })

            payload = {
                "student_id": self.student_id,
                "election_id": self.election_id,
                "votes": votes
            }

            # Post the vote
            print(f"Student {self.student_id} is casting votes for {len(votes)} positions...")
            self.client.post("/api/student/vote", json=payload, headers=headers, name="/api/student/vote")
        else:
            print(f"Error fetching candidates for voting: {resp.status_code}")

    @task(2)
    def check_results(self):
        """Simulate checking live results."""
        if not self.election_id:
            return
            
        url = f"/api/student/results?election_id={self.election_id}"
        self.client.get(url, name="/api/student/results")

def on_test_start(environment, **kwargs):
    print("UniVote High-Concurrency Test Started")

def on_test_stop(environment, **kwargs):
    print("UniVote High-Concurrency Test Completed")

# Register listeners explicitly
events.test_start.add_listener(on_test_start)
events.test_stop.add_listener(on_test_stop)
