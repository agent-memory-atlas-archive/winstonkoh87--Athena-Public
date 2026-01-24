"""
athena.memory
=============

Memory subsystems: Vector DB, Context, Cache.
"""

import os
from dotenv import load_dotenv
from .local_store import LocalStore

load_dotenv()

def get_store():
    """Factory to get the appropriate vector store based on config."""
    mode = os.getenv("ATHENA_MODE", "cloud").lower()
    
    if mode == "local":
        return LocalStore()
    else:
        # Default fallback to Supabase (imported lazily to avoid confusing dependency errors in local mode)
        # Note: The original implementation in vectors.py exposes rpc calls directly. 
        # This factory is a high-level abstraction recommendation.
        # For now, we return LocalStore if requested, else None (caller should use vectors.py directly)
        return None

