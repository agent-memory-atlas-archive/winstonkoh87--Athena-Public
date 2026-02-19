"""
Athena Daemon (athenad)
=======================
Role: The Headless Kernel (Active OS).
Responsibilities:
  1.  API Server (FastAPI) -> External Interface
  2.  File System Watcher (Background Task) -> Updates SQLite Metadata
  3.  Background Worker (Threading) -> Vectors Content into GraphRAG
  4.  Health Monitor -> Self-healing

Architecture:
  [API Client] <--(HTTP)--> [FastAPI Server] --(Queue)--> [Indexer Worker]
                                    |
                               (Background Task)
                                    |
                                    v
                               [File Watcher]
"""

import os
import time
import sqlite3
import hashlib
import re
import sys
import threading
import queue
import logging
import subprocess
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from rich.logging import RichHandler

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/athena/core -> ROOT
DB_PATH = PROJECT_ROOT / ".agent" / "inputs" / "athena.db"
SCHEMA_PATH = PROJECT_ROOT / ".agent" / "inputs" / "schema.sql"
ACTIVE_CONTEXT_PATH = PROJECT_ROOT / ".context" / "memory_bank" / "activeContext.md"

# Watch Configuration
WATCH_DIRS = [
    PROJECT_ROOT / ".context",
    PROJECT_ROOT / ".agent" / "skills",
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "Athena-Public",
]

EXCLUDED_PATTERNS = [
    "/Winston/",
    "/archive/",
    "/history/",
    "/.venv/",
    "/__pycache__/",
    "/.git/",
    "/lightrag_store/",
    "athenad.log",
    ".semantic_audit_log.json",
    "/knowledge/",
    "/cache/",
    "/data_lake/",
    "/ventures/",
    "/dumps/",
    "/raw_data/",
    "/brand_references/",
    "/.tmp/",
    "/node_modules/",
    "/.pytest_cache/",
]

POLL_INTERVAL = 5
LOG_LEVEL = logging.INFO


# --- LOGGING SETUP ---
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("athenad")


# --- UTILITIES ---
def calculate_checksum(filepath):
    """Fast checksum of file stats to detect changes."""
    try:
        stats = os.stat(filepath)
        return f"{stats.st_size}-{stats.st_mtime}"
    except FileNotFoundError:
        return None


def extract_tags(filepath):
    """Extract tags from Markdown."""
    tags = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tags = re.findall(r"#([\w-]+)", content)
    except Exception as e:
        logger.warning(f"Failed to read tags from {filepath}: {e}")
    return list(set(tags))


# --- WORKER: BACKGROUND INDEXER ---
class BackgroundIndexer(threading.Thread):
    def __init__(self, task_queue):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.wrapper_path = PROJECT_ROOT / ".agent" / "scripts" / "lightrag_wrapper.py"

    def run(self):
        logger.info("🧠 BackgroundIndexer: Online (Waiting for tasks...)")
        while True:
            try:
                filepath = self.task_queue.get()
                if filepath is None:
                    break

                self.index_file_in_graph(filepath)
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Indexer Worker Crash: {e}")

    def index_file_in_graph(self, filepath):
        """Calls lightrag_wrapper.py to index the file."""
        if not self.wrapper_path.exists():
            logger.error(f"Missing LightRAG wrapper: {self.wrapper_path}")
            return

        try:
            # Read content to verify it's valid
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) < 50:  # Skip empty/stub files
                    return

            logger.info(f"🕸️  Graph Vectorizing: {Path(filepath).name}")

            cmd = [
                sys.executable,
                str(self.wrapper_path),
                "--insert",
                f"File: {filepath}\nContent:\n{content}",
            ]

            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True,
                timeout=120,
            )
            logger.info(f"✅ Graph Updated: {Path(filepath).name}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Graph Indexing Failed: {e.stderr.decode()}")
        except Exception as e:
            logger.error(f"Graph Indexing Error: {e}")


# --- FILE WATCHER SERVICE ---
class FileWatcher:
    def __init__(self, indexer_queue):
        self.indexer_queue = indexer_queue
        self.running = False

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        if not DB_PATH.parent.exists():
            DB_PATH.parent.mkdir(parents=True)

        if not DB_PATH.exists() and SCHEMA_PATH.exists():
            conn = self.get_db_connection()
            with open(SCHEMA_PATH, "r") as f:
                conn.executescript(f.read())
            conn.commit()
            conn.close()
            logger.info("Initialized Metadata DB.")

    def check_and_update(self, conn, filepath):
        """Returns True if file updated."""
        checksum = calculate_checksum(filepath)
        if not checksum:
            return False

        cursor = conn.cursor()
        cursor.execute("SELECT checksum FROM files WHERE path = ?", (filepath,))
        row = cursor.fetchone()

        if not row or row["checksum"] != checksum:
            # Index Metadata
            cursor.execute(
                "INSERT OR REPLACE INTO files (path, last_modified, checksum, type) VALUES (?, ?, ?, ?)",
                (filepath, time.time(), checksum, "text/markdown"),
            )

            # Index Tags
            tags = extract_tags(filepath)
            cursor.execute("DELETE FROM file_tags WHERE file_path = ?", (filepath,))
            for tag in tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                tag_id = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT OR IGNORE INTO file_tags (file_path, tag_id) VALUES (?, ?)",
                    (filepath, tag_id),
                )
            return True
        return False

    async def watch_loop(self):
        self.running = True
        self.init_db()
        logger.info(f"👀 Watcher Started: {[str(d) for d in WATCH_DIRS]}")

        while self.running:
            try:
                conn = self.get_db_connection()
                changes = 0
                for watch_dir in WATCH_DIRS:
                    if not watch_dir.exists():
                        continue

                    for root, _, files in os.walk(watch_dir):
                        if any(p in root for p in EXCLUDED_PATTERNS):
                            continue

                        for file in files:
                            if not file.endswith(".md"):
                                continue

                            filepath = os.path.join(root, file)
                            if any(p in filepath for p in EXCLUDED_PATTERNS):
                                continue

                            if self.check_and_update(conn, filepath):
                                changes += 1
                                self.indexer_queue.put(filepath)

                if changes > 0:
                    conn.commit()
                    logger.info(f"Processed {changes} file updates.")

                conn.close()
            except Exception as e:
                logger.error(f"Watcher Error: {e}")

            await asyncio.sleep(POLL_INTERVAL)

    def stop(self):
        self.running = False


# --- FASTAPI APP ---
indexer_queue = queue.Queue()
indexer_thread = BackgroundIndexer(indexer_queue)
file_watcher = FileWatcher(indexer_queue)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🛡️  Athena Headless Kernel Starting...")
    indexer_thread.start()
    asyncio.create_task(file_watcher.watch_loop())
    yield
    # Shutdown
    logger.info("🛑 Shutting down...")
    file_watcher.stop()
    # indexer_thread is daemon, will die with process


app = FastAPI(title="Athena Kernel", version="9.2.0", lifespan=lifespan)


class ThinkRequest(BaseModel):
    prompt: str


@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": "athena-kernel",
        "version": "9.2.0",
        "components": {
            "indexer": indexer_thread.is_alive(),
            "watcher": file_watcher.running,
        },
    }


@app.get("/context/active")
async def get_active_context():
    if not ACTIVE_CONTEXT_PATH.exists():
        raise HTTPException(status_code=404, detail="Active context not found")

    with open(ACTIVE_CONTEXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}


@app.post("/agent/think")
async def agent_think(request: ThinkRequest):
    # Stub for now
    return {"thought": f"I am thinking about: {request.prompt}", "complexity": "Λ+10"}


if __name__ == "__main__":
    uvicorn.run("athenad:app", host="0.0.0.0", port=8000, reload=False)
