"""
athena.memory.local_store
=========================

Local vector store implementation using ChromaDB and SentenceTransformers.
This allows Athena to run entirely offline without external API keys.
"""

import os
import json
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except ImportError:
    chromadb = None
    SentenceTransformer = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalStore:
    """
    Local implementation of the Athena memory interface.
    Replaces Supabase (PGVector) with ChromaDB (Local SQLite/DuckDB).
    Replaces Google Gemini Embeddings with SentenceTransformers (Local CPU/GPU).
    """

    def __init__(self, persist_path: Optional[str] = None):
        if chromadb is None or SentenceTransformer is None:
            raise ImportError(
                "Local mode dependencies missing. "
                "Run: pip install -e '.[local]'"
            )
            
        # 1. Initialize Vector DB
        if not persist_path:
            persist_path = os.getenv("ATHENA_LOCAL_DB_PATH", os.path.expanduser("~/.athena/chroma_db"))
            
        logger.info(f"Initializing LocalStore at {persist_path}")
        os.makedirs(persist_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # 2. Initialize Embedding Model
        # using all-MiniLM-L6-v2 as it's fast and effective for local use
        model_name = os.getenv("ATHENA_LOCAL_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Loading local embedding model: {model_name}...")
        self.encoder = SentenceTransformer(model_name)
        logger.info("Local embedding model loaded.")

        # 3. Initialize Collections
        self.session_col = self.client.get_or_create_collection("sessions")
        # Reuse 'sessions' or create separate cols if schema diverges significantly
        # mimicking Supabase RPC search functions by simple filtering or separate collections
        self.collections = {
            "sessions": self.session_col,
            # Map other 'tables' to this or separate collections as needed
        }

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding locally."""
        return self.encoder.encode(text).tolist()

    def add_memory(self, text: str, metadata: Dict[str, Any], table: str = "sessions"):
        """Save a memory fragment."""
        vector = self.get_embedding(text)
        collection = self.client.get_or_create_collection(table)
        
        collection.add(
            documents=[text],
            embeddings=[vector],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )
        logger.info(f"Saved to local {table}: {text[:50]}...")

    def search(self, query: str, table: str = "sessions", limit: int = 5) -> List[Dict]:
        """Generic search."""
        vector = self.get_embedding(query)
        collection = self.client.get_or_create_collection(table)
        
        results = collection.query(
            query_embeddings=[vector],
            n_results=limit
        )
        
        # Format to match Supabase RPC output style
        formatted = []
        if results["ids"]:
            count = len(results["ids"][0])
            for i in range(count):
                formatted.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity": 1.0 - results["distances"][0][i] if "distances" in results else 0.0
                })
        return formatted

    # --- RPC Compat Layer ---
    # These match the Supabase RPC calls used in vectors.py
    # But here we do the embedding generation internally for simplicity in calling code
    
    def search_sessions(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        # Note: In local mode, we usually re-generate embedding from text, 
        # but if the caller passes embedding, we use it directly using query()
        return self._search_by_vector("sessions", query_embedding, limit)

    def search_case_studies(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("case_studies", query_embedding, limit)

    def search_protocols(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("protocols", query_embedding, limit)

    def search_capabilities(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("capabilities", query_embedding, limit)

    def search_playbooks(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("playbooks", query_embedding, limit)

    def search_references(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("references", query_embedding, limit)

    def search_frameworks(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("frameworks", query_embedding, limit)

    def search_workflows(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("workflows", query_embedding, limit)

    def search_entities(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("entities", query_embedding, limit)

    def search_user_profile(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("user_profile", query_embedding, limit)

    def search_system_docs(self, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
        return self._search_by_vector("system_docs", query_embedding, limit)


    def _search_by_vector(self, table: str, vector: List[float], limit: int) -> List[Dict]:
        collection = self.client.get_or_create_collection(table)
        results = collection.query(
            query_embeddings=[vector],
            n_results=limit
        )
        
        formatted = []
        if results["ids"]:
            count = len(results["ids"][0])
            for i in range(count):
                formatted.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    # Chroma returns distance, Supabase returns similarity. Sim = 1 - Dist (roughly for cosine)
                    "similarity": 1.0 - results["distances"][0][i] if results["distances"] else 0.0
                })
        return formatted
