-- ==========================================
-- UniVote Consolidated Supabase Schema
-- ==========================================
-- This script sets up all tables and relationships for the UniVote application.
-- It includes custom authentication structures for Admins and Advisers.

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Clean Up (Optional: Uncomment if you want to wipe existing tables)
-- DROP TABLE IF EXISTS public.audit_log CASCADE;
-- DROP TABLE IF EXISTS public.votes CASCADE;
-- DROP TABLE IF EXISTS public.candidates CASCADE;
-- DROP TABLE IF EXISTS public.partylists CASCADE;
-- DROP TABLE IF EXISTS public.elections CASCADE;
-- DROP TABLE IF EXISTS public.students CASCADE;
-- DROP TABLE IF EXISTS public.advisers CASCADE;
-- DROP TABLE IF EXISTS public.admins CASCADE;

-- 3. Admins Table
CREATE TABLE public.admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Advisers Table
CREATE TABLE public.advisers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    department TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Students (Voters) Table
CREATE TABLE public.students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id TEXT UNIQUE NOT NULL, -- University ID number
    full_name TEXT NOT NULL,
    course TEXT,
    year_level INTEGER,
    has_voted BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Elections Table
CREATE TABLE public.elections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    status TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'active', 'completed')),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Partylists Table
CREATE TABLE public.partylists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 8. Candidates Table
CREATE TABLE public.candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
    student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
    partylist_id UUID REFERENCES public.partylists(id) ON DELETE SET NULL,
    position TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(election_id, student_id) -- A student can only run once per election
);

-- 9. Votes Table
CREATE TABLE public.votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    election_id UUID REFERENCES public.elections(id) ON DELETE CASCADE,
    student_id UUID REFERENCES public.students(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES public.candidates(id) ON DELETE CASCADE,
    position TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(election_id, student_id, position) -- A student can only vote once per position
);

-- 10. Audit Log Table
CREATE TABLE public.audit_log (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id    UUID,                   -- Handled by application logic
    actor_role  TEXT        NOT NULL CHECK (actor_role IN ('admin', 'adviser')),
    action      TEXT        NOT NULL,  -- e.g. 'CREATE_ELECTION', 'TOGGLE_ELECTION', 'IMPORT_STUDENTS'
    target_type TEXT,                  -- e.g. 'election', 'student', 'candidate'
    target_id   TEXT,                  -- UUID or identifier of affected row
    details     JSONB,                 -- Extra context
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 11. Permissions and Security
-- Disable Row Level Security (RLS) for the simplified version
ALTER TABLE public.admins DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.advisers DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.students DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.elections DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.partylists DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidates DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.votes DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_log DISABLE ROW LEVEL SECURITY;

-- Grant access to standard Supabase roles
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;

-- ==========================================
-- END OF SCRIPT
-- ==========================================
