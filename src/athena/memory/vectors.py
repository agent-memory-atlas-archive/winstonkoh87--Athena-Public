"""
athena.memory.vectors
=====================

Interface to Supabase pgvector and Gemini Embeddings.
"""

import os
import sys
import hashlib
import requests
from functools import lru_cache
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    # Gentle fallback if deps aren't installed yet
    Client = Any

# Load env early (or rely on usage)
load_dotenv()

EMBEDDING_CACHE_SIZE = 128
_supabase_client: Optional[Client] = None

def get_client() -> Client:
    """Singleton Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in environment.")
        _supabase_client = create_client(url, key)
    return _supabase_client

# --- Embedding Logic ---

def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

@lru_cache(maxsize=EMBEDDING_CACHE_SIZE)
def _get_embedding_cached(text_hash: str, text: str) -> tuple:
    """Internal cached embedding function."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {
            "parts": [{"text": text}]
        }
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return tuple(response.json()["embedding"]["values"])

def get_embedding(text: str) -> List[float]:
    """Generate embedding using Google Gemini (Cached)."""
    text_hash = _hash_text(text)
    result = _get_embedding_cached(text_hash, text)
    return list(result)

# --- Search RPC Wrappers ---

def search_rpc(rpc_name: str, query_embedding: List[float], limit: int = 5, threshold: float = 0.3) -> List[Dict]:
    """Generic RPC caller."""
    client = get_client()
    result = client.rpc(
        rpc_name,
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit
        }
    ).execute()
    return result.data 


# Specific Wrappers (Matching legacy signatures for easy porting)

def search_sessions(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_sessions", query_embedding, limit, threshold)

def search_case_studies(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_case_studies", query_embedding, limit, threshold)

def search_protocols(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_protocols", query_embedding, limit, threshold)

def search_capabilities(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_capabilities", query_embedding, limit, threshold)

def search_playbooks(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_playbooks", query_embedding, limit, threshold)

def search_references(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_references", query_embedding, limit, threshold)

def search_frameworks(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_frameworks", query_embedding, limit, threshold)

def search_workflows(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_workflows", query_embedding, limit, threshold)

def search_entities(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_entities", query_embedding, limit, threshold)

def search_user_profile(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_user_profile", query_embedding, limit, threshold)

def search_system_docs(client: Client, query_embedding: List[float], limit: int = 5, threshold: float = 0.3):
    return search_rpc("search_system_docs", query_embedding, limit, threshold)
