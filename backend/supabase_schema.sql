-- Supabase Schema for UniVote

-- Users table (Admins, Advisers)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'adviser'))
);

-- Students (Voters) table
CREATE TABLE students (
  student_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  has_voted BOOLEAN DEFAULT FALSE
);

-- Elections table
CREATE TABLE elections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  is_active BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Partylists table
CREATE TABLE partylists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL
);

-- Candidates table
CREATE TABLE candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
  position TEXT NOT NULL,
  partylist_id UUID REFERENCES partylists(id) ON DELETE SET NULL
);

-- Votes table
CREATE TABLE votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id TEXT REFERENCES students(student_id) ON DELETE CASCADE,
  candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
  position TEXT NOT NULL, -- To easily count/prevent multiple votes for same position by one student
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(student_id, position) -- A student can only vote once per position
);

-- Default Admin User (Password: admin123 -> you should hash this in python or just do plain for demo if needed. For now, we will create an endpoint to init.)
