"""
athena.tools.search
===================

Hybrid RAG Orchestrator (RRF + Rerank).
Integrates Canonical, Tags, Vectors, and Filesystem.
"""

import sys
import json
import subprocess
import argparse
from typing import List, Dict, Optional
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from athena.core.config import PROJECT_ROOT, TAG_INDEX_PATH, CANONICAL_PATH
from athena.core.models import SearchResult
from athena.core.cache import get_search_cache
from athena.memory.vectors import (
    get_embedding,
    get_client,
    search_sessions,
    search_case_studies,
    search_protocols,
    search_capabilities,
    search_playbooks,
    search_references,
    search_frameworks,
    search_workflows,
    search_entities,
    search_user_profile,
    search_system_docs,
)
from athena.tools.reranker import rerank_results

# Config
# Config
WEIGHTS = {
    "canonical": 3.0,  # The Constitution (highest priority)
    "graphrag": 2.0,  # The Context (rebalanced from 3.5)
    "tags": 1.5,  # The Index
    "vector": 2.0,  # The Content (boosted from 1.3)
    "filename": 1.0,  # The Map
}
RRF_K = 60
CONFIDENCE_HIGH = 0.03
CONFIDENCE_MED = 0.02
CONFIDENCE_LOW = 0.01

# GraphRAG paths
GRAPHRAG_DIR = PROJECT_ROOT / ".agent" / "graphrag"
COMMUNITIES_FILE = GRAPHRAG_DIR / "communities.json"
GRAPH_FILE = GRAPHRAG_DIR / "knowledge_graph.gpickle"
CHROMA_DIR = PROJECT_ROOT / ".agent" / "chroma_db"

# --- Collection Functions ---


def collect_canonical(query: str) -> List[SearchResult]:
    """Collect matches from CANONICAL.md"""
    results = []
    if not CANONICAL_PATH.exists():
        return []

    keywords = [
        w for w in query.split() if len(w) >= 2 and w.lower() not in ["the", "and", "for", "is"]
    ]
    if not keywords:
        return []

    try:
        text = CANONICAL_PATH.read_text(encoding="utf-8")
        for line_num, line in enumerate(text.splitlines(), 1):
            if any(k.lower() in line.lower() for k in keywords):
                if "|" in line and "http" not in line:
                    results.append(
                        SearchResult(
                            id=f"Canonical:L{line_num}",
                            content=line.strip(),
                            source="canonical",
                            score=1.0,
                        )
                    )
                elif "##" in line:
                    results.append(
                        SearchResult(
                            id=f"Canonical:Header:L{line_num}",
                            content=line.strip(),
                            source="canonical",
                            score=0.9,
                        )
                    )
    except Exception:
        pass
    return results[:5]


def collect_tags(query: str) -> List[SearchResult]:
    """Collect exact tag matches"""
    results = []
    if not TAG_INDEX_PATH.exists():
        return []

    try:
        # Use grep for speed
        cmd = f"grep -i '{query}' '{TAG_INDEX_PATH}' | head -n 10"
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if process.stdout:
            lines = process.stdout.strip().split("\n")
            for i, line in enumerate(lines):
                results.append(
                    SearchResult(
                        id=f"Tag:{line.split('|')[0].strip() if '|' in line else query}",
                        content=line.strip(),
                        source="tags",
                        score=1.0 - (i * 0.05),
                    )
                )
    except Exception:
        pass
    return results


def collect_vectors(query: str, limit: int = 20) -> List[SearchResult]:
    """Collect semantic matches via Supabase"""
    results = []
    try:
        client = get_client()  # Singleton initialization
        query_embedding = get_embedding(query)

        # Parallel search using ThreadPoolExecutor
        search_tasks = [
            ("protocol", search_protocols, 10, 0.3),
            ("case_study", search_case_studies, 10, 0.3),
            ("session", search_sessions, 5, 0.35),
            ("capability", search_capabilities, 5, 0.3),
            ("playbook", search_playbooks, 5, 0.3),
            ("workflow", search_workflows, 5, 0.3),
            ("entity", search_entities, 5, 0.3),
            ("reference", search_references, 5, 0.3),
            ("framework", search_frameworks, 5, 0.3),
            ("user_profile", search_user_profile, 5, 0.3),
            ("system_doc", search_system_docs, 5, 0.3),
        ]

        def run_task(task):
            type_label, func, limit, threshold = task
            try:
                return type_label, func(client, query_embedding, limit=limit, threshold=threshold)
            except Exception as e:
                print(f"   ⚠️ Search failed for {type_label}: {e}", file=sys.stderr)
                return type_label, []

        with ThreadPoolExecutor(max_workers=len(search_tasks)) as executor:
            task_results = list(executor.map(run_task, search_tasks))

        for type_label, raw_results in task_results:
            for item in raw_results or []:
                path = item.get("file_path", "")
                if "?" in path:
                    path = path.split("?")[0]

                # Dynamic Title/ID construction
                item_id = (
                    item.get("title")
                    or item.get("name")
                    or item.get("code")
                    or item.get("entity_name")
                    or item.get("filename")
                    or f"{type_label}"
                )
                if type_label == "protocol":
                    item_id = f"Protocol {item.get('code')}: {item.get('name')}"
                elif type_label == "session":
                    item_id = f"Session {item.get('date')}: {item.get('title')}"
                elif type_label == "case_study":
                    item_id = f"Case Study: {item.get('title')}"

                results.append(
                    SearchResult(
                        id=item_id,
                        content=item.get("content", "")[:200],
                        source="vector",
                        score=item.get("similarity", 0),
                        metadata={"type": type_label, "path": path},
                    )
                )

    except Exception as e:
        print(f"Vector search warning: {e}", file=sys.stderr)

    return results


def collect_graphrag(query: str, limit: int = 5) -> List[SearchResult]:
    """Collect entity and community matches from local GraphRAG."""
    results = []

    # Check if GraphRAG data exists
    if not COMMUNITIES_FILE.exists():
        return []

    try:
        import json as json_lib

        # 1. Community search (global context)
        with open(COMMUNITIES_FILE, "r") as f:
            data = json_lib.load(f)

        # Handle both dict and list formats
        communities = data.get("communities", []) if isinstance(data, dict) else data

        # Tokenize query into keywords (min 3 chars, strip common words)
        stopwords = {"the", "and", "for", "is", "in", "to", "of", "a", "an", "with"}
        query_tokens = [
            w.lower().strip("#")
            for w in query.split()
            if len(w) >= 3 and w.lower() not in stopwords
        ]

        if not query_tokens:
            return []

        matched_communities = []

        for comm in communities:
            if isinstance(comm, dict):
                comm_id = comm.get("community_id", "unknown")
                size = comm.get("size", 0)
                members = comm.get("members", [])
                summary = comm.get("summary", "")
            else:
                continue

            # Normalize members: strip hashtags and lowercase
            normalized_members = [str(m).lower().strip("#").replace("-", " ") for m in members]
            all_member_text = " ".join(normalized_members)
            summary_lower = summary.lower()

            # Count how many query tokens match (partial match allowed)
            match_count = 0
            matched_tokens = []
            for token in query_tokens:
                if token in all_member_text or token in summary_lower:
                    match_count += 1
                    matched_tokens.append(token)

            if match_count > 0:
                matched_communities.append(
                    {
                        "id": comm_id,
                        "size": size or len(members),
                        "summary": summary,
                        "members": members[:5],
                        "match_count": match_count,
                        "matched_tokens": matched_tokens,
                    }
                )

        # Sort by match_count first, then by size (more matches = more relevant)
        matched_communities.sort(key=lambda x: (x["match_count"], x["size"]), reverse=True)

        for i, comm in enumerate(matched_communities[:3]):
            results.append(
                SearchResult(
                    id=f"Community {comm['id']} ({comm['size']} members, {comm['match_count']} hits)",
                    content=f"Matched: {', '.join(comm['matched_tokens'])} | Cluster: {', '.join(str(m) for m in comm['members'][:5])}...",
                    source="graphrag",
                    score=1.0 - (i * 0.1),
                    metadata={
                        "type": "community",
                        "size": comm["size"],
                        "matches": comm["match_count"],
                    },
                )
            )

        # 2. ChromaDB entity search (if available)
        if CHROMA_DIR.exists():
            try:
                import chromadb
                from chromadb.utils import embedding_functions

                chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
                # Check if collection exists
                try:
                    collection = chroma_client.get_collection("athena_codex")

                    # Query for similar content
                    query_results = collection.query(query_texts=[query], n_results=limit)

                    if query_results and query_results.get("documents"):
                        for i, (doc, meta) in enumerate(
                            zip(
                                query_results["documents"][0],
                                query_results["metadatas"][0]
                                if query_results.get("metadatas")
                                else [{}] * len(query_results["documents"][0]),
                            )
                        ):
                            source_file = meta.get("source", "unknown")
                            results.append(
                                SearchResult(
                                    id=f"GraphEntity: {source_file.split('/')[-1] if '/' in source_file else source_file}",
                                    content=doc[:150] + "..." if len(doc) > 150 else doc,
                                    source="graphrag",
                                    score=0.8 - (i * 0.05),
                                    metadata={"type": "entity", "path": source_file},
                                )
                            )
                except Exception:
                    pass  # Collection doesn't exist yet
            except ImportError:
                pass  # ChromaDB not available in this interpreter

    except Exception as e:
        print(f"GraphRAG search warning: {e}", file=sys.stderr)

    return results[:limit]


def collect_filenames(query: str) -> List[SearchResult]:
    """Collect filename matches in Project Root"""
    results = []
    try:
        # Use relative search from PROJECT_ROOT
        cmd = f"find . -type f -name '*{query}*' -not -path '*/.*' | head -n 5"
        process = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
        if process.stdout:
            lines = process.stdout.strip().split("\n")
            for line in lines:
                if line.strip():
                    # line is relative to PROJECT_ROOT
                    full_path = PROJECT_ROOT / line
                    results.append(
                        SearchResult(
                            id=f"File: {full_path.name}",
                            content=f"Path: {line}",
                            source="filename",
                            score=1.0,
                            metadata={"path": str(full_path)},
                        )
                    )
    except Exception:
        pass
    return results


# --- Fusion Logic ---


def weighted_rrf(ranked_lists: Dict[str, List[SearchResult]], k: int = 60) -> List[SearchResult]:
    fused_scores = defaultdict(float)
    doc_map = {}
    doc_signals = defaultdict(dict)

    for source, docs in ranked_lists.items():
        weight = WEIGHTS.get(source, 1.0)
        for rank, doc in enumerate(docs, start=1):
            score_mod = 0.5 + doc.score  # Dynamic: range 0.5 to 1.5
            contrib = weight * score_mod * (1.0 / (k + rank))
            fused_scores[doc.id] += contrib

            if doc.id not in doc_map:
                doc_map[doc.id] = doc

            doc_signals[doc.id][source] = {"rank": rank, "contrib": round(contrib, 5)}

    final_list = []
    for doc_id, score in fused_scores.items():
        doc = doc_map[doc_id]
        doc.rrf_score = score
        doc.signals = doc_signals[doc_id]
        final_list.append(doc)

    return sorted(final_list, key=lambda x: x.rrf_score, reverse=True)


# --- Main Entry Point ---


def run_search(
    query: str,
    limit: int = 10,
    strict: bool = False,
    rerank: bool = False,
    debug: bool = False,
    json_output: bool = False,
):
    # 0. Check cache first
    cache = get_search_cache()
    cache_key = f"{query}|{limit}|{strict}|{rerank}"
    cached_results = cache.get(cache_key)

    if cached_results is not None:
        if not json_output:
            print(f'\n⚡ CACHE HIT: "{query}"')
            print("=" * 60)
        fused_results = cached_results
    else:
        if not json_output:
            print(
                f'\n🔍 SMART SEARCH (Parallel Hybrid RRF{" + Rerank" if rerank else ""}): "{query}"'
            )
            print("=" * 60)

        # 1. Collect (Parallel execution)
        collection_tasks = {
            "canonical": lambda: collect_canonical(query),
            "tags": lambda: collect_tags(query),
            "graphrag": lambda: collect_graphrag(query),
            "vector": lambda: collect_vectors(query),
            "filename": lambda: collect_filenames(query),
        }

        lists = {}
        with ThreadPoolExecutor(
            max_workers=len(collection_tasks)
        ) as executor:  # Changed max_workers
            future_to_source = {
                executor.submit(func): source for source, func in collection_tasks.items()
            }
            for future in future_to_source:
                source = future_to_source[future]
                try:
                    lists[source] = future.result()
                except Exception as e:
                    if not json_output:
                        print(f"   ⚠️ {source} failed: {e}", file=sys.stderr)
                    lists[source] = []

        # 2. Fuse
        fused_results = weighted_rrf(lists)

        # 3. Rerank
        if rerank and fused_results:
            candidates = fused_results[:25]
            if not json_output:
                print(f"   ⚡ Reranking top {len(candidates)} candidates...")
            fused_results = rerank_results(query, candidates, top_k=limit)

        # Store in cache for next time
        cache.set(cache_key, fused_results)

    # 4. Filter
    if strict:
        high_conf = [r for r in fused_results if r.rrf_score >= CONFIDENCE_MED]
        low_conf = [r for r in fused_results if r.rrf_score < CONFIDENCE_MED]
        suppressed_count = len(low_conf)
        fused_results = high_conf
        if not json_output and suppressed_count > 0:
            print(f"\n   🛡️ STRICT MODE: {suppressed_count} low-confidence result(s) suppressed")
    else:
        suppressed_count = 0

    # 5. Present
    if not fused_results:
        if json_output:
            print(
                json.dumps(
                    {
                        "results": [],
                        "suppressed": suppressed_count,
                        "message": "No high-confidence results",
                    }
                )
            )
        else:
            print("  (No high-confidence results found)" if strict else "  (No results found)")
        return

    if not json_output:
        print(f"\n🏆 TOP {limit} RESULTS:")
        for i, doc in enumerate(fused_results[:limit], 1):
            if doc.rrf_score >= CONFIDENCE_HIGH:
                conf_badge = "[HIGH]"
            elif doc.rrf_score >= CONFIDENCE_MED:
                conf_badge = "[MED]"
            else:
                conf_badge = "[LOW]"

            score_display = (
                f"Rerank:{doc.signals.get('reranker', {}).get('score', 0):.2f}"
                if rerank
                else f"RRF:{doc.rrf_score:.4f}"
            )
            print(f"\n  {i}. {conf_badge} [{score_display}] {doc.id}")

            if debug:
                print(f"     Signals: {json.dumps(doc.signals)}")

            if doc.metadata.get("path"):
                print(f"     📁 {doc.metadata['path']}")
            else:
                print(f"     📄 {doc.content[:100]}...")

        print("\n" + "=" * 60)

        # Log (Optional compliance hook)
        try:
            # Assuming logging logic will be migrated later or importable
            pass
        except Exception:
            pass
    else:
        # JSON output logic
        output = [doc.to_dict() for doc in fused_results[:limit]]
        print(json.dumps({"results": output, "suppressed": suppressed_count}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    run_search(args.query, args.limit, args.strict, args.rerank, args.debug, args.json)
