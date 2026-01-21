-- Migration: add cedula and full_name to users table
-- Generated: 2026-01-21

ALTER TABLE IF EXISTS public.users
  ADD COLUMN IF NOT EXISTS cedula text,
  ADD COLUMN IF NOT EXISTS full_name text;
