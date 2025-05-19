/*
  # Initial Schema Setup for Escape Room Application

  1. New Tables
    - `teams`: Stores team information and progress
      - `id` (uuid, primary key)
      - `teamname` (text)
      - `username` (text, unique)
      - `password` (text)
      - `current_round` (integer)
      - Round completion timestamps
      - `created_at` (timestamptz)
    
    - `clues`: Stores clues and answers for each team
      - `id` (uuid, primary key)
      - `team_id` (uuid, foreign key)
      - Clues and answers for each round
  
  2. Security
    - Enable RLS on both tables
    - Policies for team access
    - Policies for admin access
*/

-- Create teams table
CREATE TABLE IF NOT EXISTS public.teams (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  teamname text NOT NULL,
  username text UNIQUE NOT NULL,
  password text NOT NULL,
  current_round integer DEFAULT 1,
  round1_completed timestamptz,
  round2_completed timestamptz,
  round3_completed timestamptz,
  created_at timestamptz DEFAULT now()
);

-- Create clues table
CREATE TABLE IF NOT EXISTS public.clues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id uuid REFERENCES public.teams(id),
  clue1 text,
  round1_answer text,
  clue2 text,
  round2_answer text,
  clue3 text,
  round3_answer text
);

-- Enable RLS
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clues ENABLE ROW LEVEL SECURITY;

-- Create policies for teams
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'teams' AND policyname = 'Teams can read own data'
  ) THEN
    CREATE POLICY "Teams can read own data"
      ON public.teams
      FOR SELECT
      TO authenticated
      USING (auth.uid() = id);
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'teams' AND policyname = 'Admin can read all teams'
  ) THEN
    CREATE POLICY "Admin can read all teams"
      ON public.teams
      FOR SELECT
      TO authenticated
      USING (auth.uid() IN (SELECT id FROM public.teams WHERE username = 'admin'));
  END IF;
END $$;

-- Create policies for clues
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'clues' AND policyname = 'Teams can read own clues'
  ) THEN
    CREATE POLICY "Teams can read own clues"
      ON public.clues
      FOR SELECT
      TO authenticated
      USING (team_id = auth.uid());
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_policies WHERE tablename = 'clues' AND policyname = 'Admin can read all clues'
  ) THEN
    CREATE POLICY "Admin can read all clues"
      ON public.clues
      FOR SELECT
      TO authenticated
      USING (auth.uid() IN (SELECT id FROM public.teams WHERE username = 'admin'));
  END IF;
END $$;