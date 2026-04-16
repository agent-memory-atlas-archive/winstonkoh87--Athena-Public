-- ============================================================
-- 015_rls_vector_tables.sql
-- Purpose: Enable Row Level Security on ALL vector/memory tables.
--
-- Threat Model:
--   If the anon key leaks (e.g., embedded in a client-side app or
--   exposed via a misconfigured MCP server), an attacker can currently
--   read/write the entire vector knowledge base. This migration locks
--   every table to service_role-only access.
--
-- Policy: service_role gets full CRUD. anon/authenticated get NOTHING.
-- This is correct for a single-user sovereign system where all reads
-- and writes go through the Python SDK (which uses service_role).
--
-- Date: 2026-04-17
-- Audit Ref: Tier 0 Security — RLS Hardening
-- ============================================================

DO $$
DECLARE
    tbl TEXT;
    tables TEXT[] := ARRAY[
        'sessions',
        'protocols',
        'case_studies',
        'capabilities',
        'playbooks',
        'references',
        'frameworks',
        'workflows',
        'user_profile',
        'system_docs',
        'entities',
        'insights'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables
    LOOP
        -- Only proceed if the table exists
        IF EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public' AND tablename = tbl
        ) THEN
            -- Enable RLS (idempotent — no error if already enabled)
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);

            -- Force RLS even for table owners (defense in depth)
            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);

            -- Drop any legacy permissive policies that might exist
            EXECUTE format(
                'DROP POLICY IF EXISTS "Allow all for anon" ON %I', tbl
            );
            EXECUTE format(
                'DROP POLICY IF EXISTS "Enable read access for all users" ON %I', tbl
            );

            -- Create service_role-only policy (full CRUD)
            EXECUTE format(
                'DROP POLICY IF EXISTS "service_role_full_access" ON %I', tbl
            );
            EXECUTE format(
                'CREATE POLICY "service_role_full_access" ON %I '
                'FOR ALL '
                'TO service_role '
                'USING (true) '
                'WITH CHECK (true)',
                tbl
            );

            RAISE NOTICE 'RLS enabled on: %', tbl;
        ELSE
            RAISE NOTICE 'Table % does not exist — skipping', tbl;
        END IF;
    END LOOP;
END $$;

-- ============================================================
-- Verify: telegram_messages (should already have RLS from 008)
-- ============================================================
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public' AND tablename = 'telegram_messages'
    ) THEN
        ALTER TABLE telegram_messages FORCE ROW LEVEL SECURITY;
        RAISE NOTICE 'telegram_messages: FORCE RLS confirmed';
    END IF;
END $$;

SELECT 'RLS hardening complete — all vector tables locked to service_role' AS status;
