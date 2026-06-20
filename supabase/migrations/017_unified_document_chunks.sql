-- Migration: Version-control the unified document chunks schema and search RPC
-- Created: 2026-06-19
-- Purpose: Shift vector storage to segment-level chunk embeddings for higher precision.

CREATE TABLE IF NOT EXISTS public.document_chunks (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    table_name TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    embedding vector(3072),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(file_path, chunk_index)
);

-- Note: 3072-dimensional vector index (ivfflat/hnsw) is omitted here because pgvector limits ivfflat to 2000 dimensions.
-- Exact sequential scan is used, which is sub-millisecond for our corpus scale.

-- Redefine search_all_vectors to search the unified chunk table directly
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
    SELECT 
        dc.table_name AS source_table,
        dc.id::text,
        dc.file_path,
        1 - (dc.embedding <=> query_embedding) AS similarity,
        dc.title,
        dc.content,
        dc.metadata || jsonb_build_object('chunk_index', dc.chunk_index) AS metadata
    FROM public.document_chunks dc
    WHERE dc.embedding IS NOT NULL AND 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
