-- Hardening the votes table to prevent double-voting during concurrent submissions
-- This ensures that a single student can only have ONE vote record per position in any given election.

ALTER TABLE votes 
ADD CONSTRAINT unique_vote_per_student_election_position 
UNIQUE (election_id, student_id, position);

-- Optional: Ensure index for performance on large datasets
CREATE INDEX IF NOT EXISTS idx_votes_student_election ON votes(student_id, election_id);
