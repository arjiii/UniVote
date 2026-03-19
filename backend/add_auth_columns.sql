-- Migration to fix the 500 registration error
-- This script removes the foreign key dependency on auth.users(id) 
-- and adds the password_hash column if it doesn't already exist.

-- 1. Fix Admins Table
DO $$ 
BEGIN
    -- Drop the FK if it exists (Supabase might have it if created from the first schema)
    ALTER TABLE public.admins DROP CONSTRAINT IF EXISTS admins_id_fkey;
    
    -- Ensure ID has a default UUID generation
    ALTER TABLE public.admins ALTER COLUMN id SET DEFAULT gen_random_uuid();
    
    -- Add password_hash if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='admins' AND column_name='password_hash') THEN
        ALTER TABLE public.admins ADD COLUMN password_hash TEXT NOT NULL;
    END IF;

    -- Add email if missing (from the first schema it might be missing or different)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='admins' AND column_name='email') THEN
        ALTER TABLE public.admins ADD COLUMN email TEXT UNIQUE NOT NULL;
    END IF;
END $$;

-- 2. Fix Advisers Table
DO $$ 
BEGIN
    ALTER TABLE public.advisers DROP CONSTRAINT IF EXISTS advisers_id_fkey;
    
    ALTER TABLE public.advisers ALTER COLUMN id SET DEFAULT gen_random_uuid();
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='advisers' AND column_name='password_hash') THEN
        ALTER TABLE public.advisers ADD COLUMN password_hash TEXT NOT NULL;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='advisers' AND column_name='email') THEN
        ALTER TABLE public.advisers ADD COLUMN email TEXT UNIQUE NOT NULL;
    END IF;
END $$;

-- 3. Fix Audit Log if it exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='audit_log') THEN
        ALTER TABLE public.audit_log DROP CONSTRAINT IF EXISTS audit_log_actor_id_fkey;
    END IF;
END $$;

-- 4. Disable RLS and Grant Permissions
-- This ensures the backend (running as a specific role or anonymous) can access the tables.
ALTER TABLE public.admins DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.advisers DISABLE ROW LEVEL SECURITY;

GRANT ALL ON public.admins TO anon, authenticated, service_role;
GRANT ALL ON public.advisers TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
