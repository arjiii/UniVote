-- TEMPORARY: Allow anyone to insert students for load testing
-- Run this in your Supabase SQL Editor
CREATE POLICY "Allow public insert for testing" ON students FOR INSERT WITH CHECK (TRUE);

-- Also allow deletion for the cleanup script to work
CREATE POLICY "Allow public delete for testing" ON students FOR DELETE USING (TRUE);

-- If votes deletion is also needed for cleanup
CREATE POLICY "Allow public delete votes for testing" ON votes FOR DELETE USING (TRUE);
