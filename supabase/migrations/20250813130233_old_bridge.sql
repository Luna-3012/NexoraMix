<<<<<<< HEAD
/*
  # Create brand combos table and related functionality

  1. New Tables
    - `brand_combos`
      - `id` (uuid, primary key)
      - `name` (text, combo name)
      - `slogan` (text, marketing slogan)
      - `description` (text, detailed description)
      - `product1` (text, first brand)
      - `product2` (text, second brand)
      - `mode` (text, fusion mode)
      - `votes` (integer, vote count)
      - `host_reaction` (text, AI host reaction)
      - `image_url` (text, generated image URL)
      - `compatibility_score` (integer, AI compatibility score)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on `brand_combos` table
    - Add policies for public read access
    - Add policies for authenticated users to create combos

  3. Functions
    - `increment_votes` function to safely increment vote counts
*/

CREATE TABLE IF NOT EXISTS brand_combos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slogan text,
  description text,
  product1 text NOT NULL,
  product2 text NOT NULL,
  mode text DEFAULT 'competitive',
  votes integer DEFAULT 0,
  host_reaction text,
  image_url text,
  compatibility_score integer DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE brand_combos ENABLE ROW LEVEL SECURITY;

-- Allow public read access to combos
CREATE POLICY "Public read access for brand_combos"
  ON brand_combos
  FOR SELECT
  TO public
  USING (true);

-- Allow public insert access (for demo purposes)
CREATE POLICY "Public insert access for brand_combos"
  ON brand_combos
  FOR INSERT
  TO public
  WITH CHECK (true);

-- Allow public update for votes only
CREATE POLICY "Public update votes for brand_combos"
  ON brand_combos
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

-- Function to safely increment votes
CREATE OR REPLACE FUNCTION increment_votes(combo_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE brand_combos 
  SET votes = votes + 1, updated_at = now()
  WHERE id = combo_id;
END;
$$;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_brand_combos_votes ON brand_combos(votes DESC);
=======
/*
  # Create brand combos table and related functionality

  1. New Tables
    - `brand_combos`
      - `id` (uuid, primary key)
      - `name` (text, combo name)
      - `slogan` (text, marketing slogan)
      - `description` (text, detailed description)
      - `product1` (text, first brand)
      - `product2` (text, second brand)
      - `mode` (text, fusion mode)
      - `votes` (integer, vote count)
      - `host_reaction` (text, AI host reaction)
      - `image_url` (text, generated image URL)
      - `compatibility_score` (integer, AI compatibility score)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Security
    - Enable RLS on `brand_combos` table
    - Add policies for public read access
    - Add policies for authenticated users to create combos

  3. Functions
    - `increment_votes` function to safely increment vote counts
*/

CREATE TABLE IF NOT EXISTS brand_combos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  slogan text,
  description text,
  product1 text NOT NULL,
  product2 text NOT NULL,
  mode text DEFAULT 'competitive',
  votes integer DEFAULT 0,
  host_reaction text,
  image_url text,
  compatibility_score integer DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE brand_combos ENABLE ROW LEVEL SECURITY;

-- Allow public read access to combos
CREATE POLICY "Public read access for brand_combos"
  ON brand_combos
  FOR SELECT
  TO public
  USING (true);

-- Allow public insert access (for demo purposes)
CREATE POLICY "Public insert access for brand_combos"
  ON brand_combos
  FOR INSERT
  TO public
  WITH CHECK (true);

-- Allow public update for votes only
CREATE POLICY "Public update votes for brand_combos"
  ON brand_combos
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

-- Function to safely increment votes
CREATE OR REPLACE FUNCTION increment_votes(combo_id uuid)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  UPDATE brand_combos 
  SET votes = votes + 1, updated_at = now()
  WHERE id = combo_id;
END;
$$;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_brand_combos_votes ON brand_combos(votes DESC);
>>>>>>> 0c35e51d1f88f94a184b1dd117166884ad88c5af
CREATE INDEX IF NOT EXISTS idx_brand_combos_created_at ON brand_combos(created_at DESC);