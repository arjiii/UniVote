-- Add verification columns for Two-Step Verification
ALTER TABLE public.students ADD COLUMN IF NOT EXISTS voting_pin TEXT;
ALTER TABLE public.elections ADD COLUMN IF NOT EXISTS adviser_passcode TEXT;

-- Index for performance (optional but good practice)
CREATE INDEX IF NOT EXISTS idx_students_voting_pin ON public.students(voting_pin);
CREATE INDEX IF NOT EXISTS idx_elections_adviser_passcode ON public.elections(adviser_passcode);
