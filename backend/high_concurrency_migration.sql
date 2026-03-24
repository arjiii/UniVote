-- 1. Add vote_count column to candidates for fast results retrieval
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS vote_count INT DEFAULT 0;

-- 2. Professional Atomic Voting RPC
-- This function handles the entire voting process in a single database transaction.
-- It prevents race conditions and ensures data integrity.
CREATE OR REPLACE FUNCTION cast_ballot_v2(
  election_id_param UUID,
  student_uuid_param UUID,
  votes_json JSONB -- Array of {candidate_id: "uuid", position: "string"}
)
RETURNS JSONB AS $$
DECLARE
  vote_item JSONB;
  receipt_id TEXT;
BEGIN
  -- A. Check if user already voted in this specific election (Security)
  IF EXISTS (SELECT 1 FROM votes WHERE student_id = student_uuid_param AND election_id = election_id_param) THEN
    RAISE EXCEPTION 'ALREADY_VOTED';
  END IF;

  -- B. Generate a deterministic receipt ID (Optional but consistent with our logic)
  receipt_id := UPPER(SUBSTRING(encode(digest(student_uuid_param::text || ':' || election_id_param::text, 'sha256'), 'hex') FROM 1 FOR 12));

  -- C. Atomic Loop: Insert votes and increment counts
  FOR vote_item IN SELECT * FROM jsonb_array_elements(votes_json) LOOP
    -- Insert into votes table
    INSERT INTO votes (election_id, student_id, candidate_id, position)
    VALUES (
      election_id_param, 
      student_uuid_param, 
      (vote_item->>'candidate_id')::UUID, 
      vote_item->>'position'
    );
    
    -- Increment the candidate's vote count atomically
    UPDATE candidates 
    SET vote_count = vote_count + 1 
    WHERE id = (vote_item->>'candidate_id')::UUID;
  END LOOP;

  -- D. Mark student as having voted
  UPDATE students SET has_voted = TRUE WHERE id = student_uuid_param;

  -- E. Return success info
  RETURN jsonb_build_object(
    'status', 'success',
    'receipt_id', receipt_id
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Enable Row Level Security (RLS)
-- Prevent direct updates to candidates and votes tables from the client side.
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE votes ENABLE ROW LEVEL SECURITY;

-- Note: You should configure specific policies in Supabase UI or via SQL 
-- to allow 'read' for authenticated users and 'insert' only via this RPC.

-- 4. Unique Constraint to physically block double-voting per position
-- This ensures that even if the RPC check is bypassed, the database 
-- will reject a second vote for the same student-election-position triad.
ALTER TABLE votes ADD CONSTRAINT unique_student_election_position_vote 
UNIQUE (student_id, election_id, position);

-- 5. Explicit RLS Policies (Example)
-- Allow students to read only their own votes
CREATE POLICY "Students can view their own votes" ON votes
  FOR SELECT USING (auth.uid() = student_id);

-- Allow the RPC (SECURITY DEFINER) to insert votes
-- In Supabase, the RPC runs as the owner by default if configured with SECURITY DEFINER.
-- We must ensure the public cannot insert directly.
CREATE POLICY "Public cannot insert votes directly" ON votes
  FOR INSERT WITH CHECK (FALSE);
