#!/usr/bin/env python3
"""
athena.core.retrieval.pipeline
===============================
Reciprocal Rank Fusion (RRF) retrieval pipeline.
Combines multiple retrieval sources with configurable weights.

Based on: "Reciprocal Rank Fusion outperforms Condorcet and individual
          Rank Learning Methods" (Cormack et al., 2009)
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

# Try to import config loader
try:
    from athena.boot.config_loader import ManifestLoader, RetrievalConfig
except ImportError:
    ManifestLoader = None
    RetrievalConfig = None


@dataclass
class RetrievalResult:
    """A single retrieval result with source attribution."""

    content: str
    source: str  # 'vector', 'canonical', 'tags', 'filenames', 'graph_rag'
    score: float
    metadata: Dict[str, Any]
    file_path: Optional[str] = None


class RRFPipeline:
    """
    Reciprocal Rank Fusion pipeline for hybrid retrieval.

    RRF Formula: score(d) = Σ (1 / (k + rank(d)))
    where k is a constant (default 60) and rank is position in each list.
    """

    def __init__(self, config: Optional["RetrievalConfig"] = None):
        """Initialize with optional config from manifest."""
        if config is None and ManifestLoader is not None:
            try:
                config = ManifestLoader.get_retrieval_config()
            except Exception:
                pass

        # Defaults if no config
        self.rrf_k = config.rrf_k if config else 60
        self.per_source_top_k = config.per_source_top_k if config else 40
        self.post_fusion_top_k = config.post_fusion_top_k if config else 60
        self.post_rerank_top_k = config.post_rerank_top_k if config else 10
        self.rerank_enabled = config.rerank_enabled if config else True

        # Source weights (higher = more trusted)
        self.weights = (
            config.weights
            if config
            else {
                "canonical_markdown": 1.8,
                "vector_memory": 2.0,
                "tags_index": 1.2,
                "filenames": 0.8,
                "graph_rag": 1.0,
            }
        )

        # Enabled sources
        self.enabled_sources = (
            config.sources
            if config
            else {
                "canonical_markdown": True,
                "vector_memory": True,
                "tags_index": True,
                "filenames": True,
                "graph_rag": False,
            }
        )

    def rrf_score(self, rank: int, weight: float = 1.0) -> float:
        """
        Calculate RRF score for a document at given rank.

        Args:
            rank: 1-indexed position in the ranked list
            weight: Source-specific weight multiplier

        Returns:
            RRF score contribution
        """
        return weight * (1.0 / (self.rrf_k + rank))

    def fuse(
        self, source_results: Dict[str, List[RetrievalResult]]
    ) -> List[RetrievalResult]:
        """
        Fuse results from multiple sources using RRF.

        Args:
            source_results: Dict mapping source name to ranked result list

        Returns:
            Fused and re-ranked results
        """
        # Document ID -> (total_score, best_result)
        doc_scores: Dict[str, Tuple[float, RetrievalResult]] = {}

        for source_name, results in source_results.items():
            if not self.enabled_sources.get(source_name, False):
                continue

            weight = self.weights.get(source_name, 1.0)

            for rank, result in enumerate(results[: self.per_source_top_k], start=1):
                # Create document ID from content hash or path
                doc_id = result.file_path or hash(result.content)

                rrf_contribution = self.rrf_score(rank, weight)

                if doc_id in doc_scores:
                    current_score, current_result = doc_scores[doc_id]
                    # Accumulate RRF score
                    doc_scores[doc_id] = (
                        current_score + rrf_contribution,
                        current_result,  # Keep first encountered result
                    )
                else:
                    doc_scores[doc_id] = (rrf_contribution, result)

        # Sort by accumulated RRF score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1][0], reverse=True)

        # Extract results up to post_fusion limit
        fused_results = []
        for doc_id, (score, result) in sorted_docs[: self.post_fusion_top_k]:
            # Update the score to be the fused RRF score
            result.score = score
            fused_results.append(result)

        return fused_results

    def rerank(
        self, query: str, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Rerank results using a cross-encoder (placeholder for integration).

        Args:
            query: Original search query
            results: Fused results to rerank

        Returns:
            Reranked results (top_k)
        """
        if not self.rerank_enabled:
            return results[: self.post_rerank_top_k]

        # TODO: Integrate sentence-transformers cross-encoder
        # For now, return as-is with score decay
        reranked = []
        for i, result in enumerate(results[: self.post_rerank_top_k]):
            # Simple decay for now
            result.score = result.score * (0.95**i)
            reranked.append(result)

        return reranked

    def retrieve(
        self, query: str, sources: Optional[Dict[str, List[RetrievalResult]]] = None
    ) -> List[RetrievalResult]:
        """
        Full retrieval pipeline: gather sources -> fuse -> rerank.

        Args:
            query: Search query
            sources: Pre-fetched source results (or None to fetch fresh)

        Returns:
            Final ranked results
        """
        if sources is None:
            # In production, this would call each retrieval source
            sources = self._gather_sources(query)

        fused = self.fuse(sources)
        final = self.rerank(query, fused)

        return final

    def _gather_sources(self, query: str) -> Dict[str, List[RetrievalResult]]:
        """
        Gather results from all enabled sources.
        Override this in subclasses to add real retrieval logic.
        """
        # Placeholder - in production, this would call:
        # - smart_search.py for vector_memory
        # - TAG_INDEX lookup for tags_index
        # - glob search for filenames
        # - KNOWLEDGE_GRAPH.md for graph_rag
        return {
            "canonical_markdown": [],
            "vector_memory": [],
            "tags_index": [],
            "filenames": [],
            "graph_rag": [],
        }


class AthenaRetriever(RRFPipeline):
    """
    Athena-specific retriever with hooks into existing search infrastructure.
    """

    def __init__(self):
        super().__init__()
        self.project_root = Path(__file__).resolve().parents[4]
        self.tag_index_path = self.project_root / ".context" / "TAG_INDEX.md"

    def _gather_sources(self, query: str) -> Dict[str, List[RetrievalResult]]:
        """Gather from Athena's actual sources."""
        results = {}

        # 1. Vector Memory (via existing search.py)
        results["vector_memory"] = self._search_vector(query)

        # 2. Tag Index
        results["tags_index"] = self._search_tags(query)

        # 3. Filenames
        results["filenames"] = self._search_filenames(query)

        # 4. Canonical Markdown (direct file matches)
        results["canonical_markdown"] = self._search_canonical(query)

        return results

    def _search_vector(self, query: str) -> List[RetrievalResult]:
        """Search vector store (Supabase pgvector)."""
        try:
            from athena.tools.search import search_memory

            raw_results = search_memory(query, limit=self.per_source_top_k)
            return [
                RetrievalResult(
                    content=r.get("content", ""),
                    source="vector_memory",
                    score=r.get("similarity", 0.0),
                    metadata=r.get("metadata", {}),
                    file_path=r.get("file_path"),
                )
                for r in raw_results
            ]
        except Exception:
            return []

    def _search_tags(self, query: str) -> List[RetrievalResult]:
        """Search TAG_INDEX.md for matching tags."""
        if not self.tag_index_path.exists():
            return []

        results = []
        query_lower = query.lower()

        try:
            content = self.tag_index_path.read_text()
            for line in content.split("\n"):
                if "::" in line:
                    tag, files = line.split("::", 1)
                    if query_lower in tag.lower():
                        results.append(
                            RetrievalResult(
                                content=line,
                                source="tags_index",
                                score=1.0 if query_lower == tag.lower() else 0.5,
                                metadata={"tag": tag},
                                file_path=None,
                            )
                        )
        except Exception:
            pass

        return results[: self.per_source_top_k]

    def _search_filenames(self, query: str) -> List[RetrievalResult]:
        """Search for files matching query in name."""
        results = []
        query_lower = query.lower().replace(" ", "_")

        search_dirs = [
            self.project_root / ".agent" / "protocols",
            self.project_root / ".context",
            self.project_root / ".framework",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for path in search_dir.rglob("*.md"):
                if query_lower in path.stem.lower():
                    results.append(
                        RetrievalResult(
                            content=f"File: {path.name}",
                            source="filenames",
                            score=1.0 if query_lower == path.stem.lower() else 0.3,
                            metadata={"path": str(path)},
                            file_path=str(path),
                        )
                    )

        return results[: self.per_source_top_k]

    def _search_canonical(self, query: str) -> List[RetrievalResult]:
        """Search canonical markdown files by content."""
        # This is expensive - in production, use pre-indexed content
        return []


# Convenience function
def retrieve(query: str, top_k: int = 10) -> List[RetrievalResult]:
    """Quick access to Athena retrieval."""
    retriever = AthenaRetriever()
    results = retriever.retrieve(query)
    return results[:top_k]


if __name__ == "__main__":
    # Test the pipeline
    print("Testing RRF Pipeline...")
    pipeline = RRFPipeline()

    # Create mock results
    mock_sources = {
        "vector_memory": [
            RetrievalResult("Doc A from vector", "vector_memory", 0.9, {}, "a.md"),
            RetrievalResult("Doc B from vector", "vector_memory", 0.8, {}, "b.md"),
        ],
        "canonical_markdown": [
            RetrievalResult(
                "Doc B from canonical", "canonical_markdown", 1.0, {}, "b.md"
            ),
            RetrievalResult(
                "Doc C from canonical", "canonical_markdown", 0.7, {}, "c.md"
            ),
        ],
    }

    fused = pipeline.fuse(mock_sources)
    print(f"Fused {len(fused)} results:")
    for r in fused:
        print(f"  - {r.file_path}: {r.score:.4f}")
