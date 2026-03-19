-- Supabase PostgreSQL Schema for UniVote
-- Run this in the Supabase SQL Editor

-- 1. Admins Table
CREATE TABLE public.admins (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Advisers Table
CREATE TABLE public.advisers (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  department TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Students (Voters) Table
CREATE TABLE public.students (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  student_id TEXT UNIQUE NOT NULL, -- University ID number
  full_name TEXT NOT NULL,
  course TEXT,
  year_level INTEGER,
  has_voted BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Elections Table
CREATE TABLE public.elections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  start_date TIMESTAMPTZ NOT NULL,
  end_date TIMESTAMPTZ NOT NULL,
  status TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'completed')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Partylists Table
CREATE TABLE public.partylists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Candidates Table
CREATE TABLE public.candidates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  partylist_id UUID REFERENCES public.partylists(id) ON DELETE SET NULL,
  position TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(election_id, student_id) -- A student can only run once per election
);

-- 7. Votes Table
CREATE TABLE public.votes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
  student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
  candidate_id UUID REFERENCES public.candidates(id) ON DELETE CASCADE,
  position TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(election_id, student_id, position) -- A student can only vote once per position
);

-- Note: Row Level Security (RLS) is not yet enabled. 
-- For production, you should enable RLS and write policies to secure these tables.

-- 8. Audit Log Table
-- Records every key action performed by admins and advisers for accountability.
CREATE TABLE public.audit_log (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id    UUID        REFERENCES auth.users(id) ON DELETE SET NULL,
  actor_role  TEXT        NOT NULL CHECK (actor_role IN ('admin', 'adviser')),
  action      TEXT        NOT NULL,  -- e.g. 'CREATE_ELECTION', 'TOGGLE_ELECTION', 'IMPORT_STUDENTS', 'ADD_CANDIDATE', 'CREATE_PARTYLIST'
  target_type TEXT,                  -- e.g. 'election', 'student', 'candidate', 'partylist'
  target_id   TEXT,                  -- UUID or identifier of the affected row
  details     JSONB,                 -- Optional extra context (name, count, etc.)
  created_at  TIMESTAMPTZ DEFAULT now()
);
