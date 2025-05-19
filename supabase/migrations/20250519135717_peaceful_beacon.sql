/*
  # Initial Schema Setup for Escape Room Application

  1. New Tables
    - `teams`
      - `id` (uuid, primary key)
      - `teamname` (text)
      - `username` (text, unique)
      - `password` (text)
      - `current_round` (integer)
      - `round1_completed` (timestamp)
      - `round2_completed` (timestamp)
      - `round3_completed` (timestamp)
      - `created_at` (timestamp)
    
    - `clues`
      - `id` (uuid, primary key)
      - `team_id` (uuid, foreign key)
      - `clue1` (text)
      - `round1_answer` (text)
      - `clue2` (text)
      - `round2_answer` (text)
      - `clue3` (text)
      - `round3_answer` (text)

  2. Security
    - Enable RLS on both tables
    - Add policies for authenticated users
*/

-- Create teams table
CREATE TABLE teams (
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
CREATE TABLE clues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id uuid REFERENCES teams(id),
  clue1 text,
  round1_answer text,
  clue2 text,
  round2_answer text,
  clue3 text,
  round3_answer text
);

-- Enable RLS
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE clues ENABLE ROW LEVEL SECURITY;

-- Create policies for teams
CREATE POLICY "Teams can read own data"
  ON teams
  FOR SELECT
  TO authenticated
  USING (auth.uid() = id);

CREATE POLICY "Admin can read all teams"
  ON teams
  FOR SELECT
  TO authenticated
  USING (auth.uid() IN (SELECT id FROM teams WHERE username = 'admin'));

-- Create policies for clues
CREATE POLICY "Teams can read own clues"
  ON clues
  FOR SELECT
  TO authenticated
  USING (team_id = auth.uid());

CREATE POLICY "Admin can read all clues"
  ON clues
  FOR SELECT
  TO authenticated
  USING (auth.uid() IN (SELECT id FROM teams WHERE username = 'admin'));