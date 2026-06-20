-- Migration: Version-control the search_all_vectors RPC function
-- Created: 2026-06-03 (Opus GTO Audit)
-- Purpose: This function powers the ENTIRE Athena search pipeline.
--          It was previously only in Supabase directly (not version-controlled).
--          This migration captures the exact production definition.

CREATE OR REPLACE FUNCTION public.search_all_vectors(
    query_embedding vector,
    match_threshold double precision DEFAULT 0.3,
    match_count integer DEFAULT 5
)
RETURNS TABLE(
    source_table text,
    id text,
    file_path text,
    similarity double precision,
    title text,
    content text,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    -- sessions
    SELECT 'session'::text, s.id::text, s.file_path, 1 - (s.embedding <=> query_embedding) AS similarity, s.title, s.content,
           jsonb_build_object('date', s.date, 'summary', s.summary, 'session_number', s.session_number) || s.metadata
    FROM sessions s WHERE s.embedding IS NOT NULL AND 1 - (s.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- case_studies
    SELECT 'case_study'::text, cs.id::text, cs.file_path, 1 - (cs.embedding <=> query_embedding) AS similarity, cs.title, cs.content,
           jsonb_build_object('code', cs.code, 'tags', cs.tags) || cs.metadata
    FROM case_studies cs WHERE cs.embedding IS NOT NULL AND 1 - (cs.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- protocols
    SELECT 'protocol'::text, p.id::text, p.file_path, 1 - (p.embedding <=> query_embedding) AS similarity, p.title, p.content,
           jsonb_build_object('code', p.code, 'name', p.name, 'category', p.category) || p.metadata
    FROM protocols p WHERE p.embedding IS NOT NULL AND 1 - (p.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- capabilities
    SELECT 'capability'::text, c.id::text, c.file_path, 1 - (c.embedding <=> query_embedding) AS similarity, c.title, c.content,
           jsonb_build_object('name', c.name) || c.metadata
    FROM capabilities c WHERE c.embedding IS NOT NULL AND 1 - (c.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- playbooks
    SELECT 'playbook'::text, pl.id::text, pl.file_path, 1 - (pl.embedding <=> query_embedding) AS similarity, pl.title, pl.content,
           jsonb_build_object('name', pl.name) || pl.metadata
    FROM playbooks pl WHERE pl.embedding IS NOT NULL AND 1 - (pl.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- references
    SELECT 'reference'::text, r.id::text, r.file_path, 1 - (r.embedding <=> query_embedding) AS similarity, r.title, r.content,
           jsonb_build_object('name', r.name) || r.metadata
    FROM "references" r WHERE r.embedding IS NOT NULL AND 1 - (r.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- frameworks
    SELECT 'framework'::text, f.id::text, f.file_path, 1 - (f.embedding <=> query_embedding) AS similarity, f.title, f.content,
           jsonb_build_object('name', f.name) || f.metadata
    FROM frameworks f WHERE f.embedding IS NOT NULL AND 1 - (f.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- workflows
    SELECT 'workflow'::text, w.id::text, w.file_path, 1 - (w.embedding <=> query_embedding) AS similarity, w.name, w.content,
           jsonb_build_object('description', w.description) || w.metadata
    FROM workflows w WHERE w.embedding IS NOT NULL AND 1 - (w.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- system_docs
    SELECT 'system_doc'::text, sd.id::text, sd.file_path, 1 - (sd.embedding <=> query_embedding) AS similarity, sd.title, sd.content,
           jsonb_build_object('filename', sd.filename, 'doc_type', sd.doc_type) || sd.metadata
    FROM system_docs sd WHERE sd.embedding IS NOT NULL AND 1 - (sd.embedding <=> query_embedding) > match_threshold
    UNION ALL
    -- user_profile
    SELECT 'user_profile'::text, up.id::text, up.file_path, 1 - (up.embedding <=> query_embedding) AS similarity, up.title, up.content,
           jsonb_build_object('filename', up.filename, 'category', up.category) || up.metadata
    FROM user_profile up WHERE up.embedding IS NOT NULL AND 1 - (up.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
