-- Migration: Add HNSW index on halfvec(3072) and optimize search_all_vectors RPC
-- Created: 2026-09-30
-- Solves: L0-4 statement timeout (code 57014) on 11,000+ vector sequential scan.

-- 1. Create HNSW index on halfvec(3072)
CREATE INDEX IF NOT EXISTS document_chunks_embedding_halfvec_idx 
ON public.document_chunks 
USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);

-- 2. Update search_all_vectors to use the halfvec HNSW index
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
DECLARE
    q_half halfvec(3072);
BEGIN
    q_half := query_embedding::halfvec(3072);
    RETURN QUERY
    SELECT 
        dc.table_name AS source_table,
        dc.id::text,
        dc.file_path,
        (1 - ((dc.embedding::halfvec(3072)) <=> q_half))::double precision AS similarity,
        dc.title,
        dc.content,
        dc.metadata || jsonb_build_object('chunk_index', dc.chunk_index) AS metadata
    FROM public.document_chunks dc
    WHERE (dc.embedding::halfvec(3072)) IS NOT NULL 
      AND (1 - ((dc.embedding::halfvec(3072)) <=> q_half)) > match_threshold
    ORDER BY (dc.embedding::halfvec(3072)) <=> q_half
    LIMIT match_count;
END;
$$;
