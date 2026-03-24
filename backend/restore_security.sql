-- RESTORE SECURITY: Drop temporary testing policies
-- Run this in your Supabase SQL Editor
DROP POLICY IF EXISTS "Allow public insert for testing" ON students;
DROP POLICY IF EXISTS "Allow public delete for testing" ON students;
DROP POLICY IF EXISTS "Allow public delete votes for testing" ON votes;
