-- 1. Sync script to update vote_count based on existing rows in votes table
-- Run this if your Results page shows 0 votes but the Votes table has data.

UPDATE candidates c
SET vote_count = (
  SELECT count(*) 
  FROM votes v 
  WHERE v.candidate_id = c.id
);

-- 2. Also ensure that the backend can read the vote counts!
-- Verify that this policy exists (I included it in fix_rls_visibility.sql)
DROP POLICY IF EXISTS "Allow public read-only access to candidates" ON candidates;
CREATE POLICY "Allow public read-only access to candidates" ON candidates
  FOR SELECT USING (TRUE);

-- 3. Optional: To see individual votes in the dashboard (if you ever need to)
-- Usually better to keep restricted, but for testing:
DROP POLICY IF EXISTS "Allow public read-only access to votes" ON votes;
CREATE POLICY "Allow public read-only access to votes" ON votes
  FOR SELECT USING (TRUE);
