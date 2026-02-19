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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
from athena.core.config import get_project_root

PROJECT_ROOT = get_project_root()  # Uses .athena_root marker detection (cross-platform)
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
        self.rag_instance = None

        # Add scripts to path to import wrapper
        scripts_path = str(PROJECT_ROOT / ".agent" / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)

    def run(self):
        logger.info("🧠 BackgroundIndexer: Online (Waiting for tasks...)")

        while True:
            try:
                from lightrag_wrapper import setup_rag

                self.rag_instance = setup_rag()
                if self.rag_instance:
                    logger.info("✅ Persistent LightRAG Instance Initialized.")
                else:
                    logger.warning("⚠️ LightRAG init returned None. Retrying in 15s...")
                    time.sleep(15)
                    continue
            except Exception as e:
                logger.error(f"Failed to initialize LightRAG: {e}. Retrying in 15s...")
                time.sleep(15)
                continue

            try:
                while True:
                    filepath = self.task_queue.get()
                    if filepath is None:
                        # Poison pill
                        return

                    self.index_file_in_graph(filepath)
                    self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Indexer Worker Crash: {e}. Restarting loop...")
                time.sleep(5)
                continue

    def index_file_in_graph(self, filepath):
        """Indexes file using the persistent LightRAG instance."""
        if not self.rag_instance:
            logger.error("LightRAG instance not available.")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) < 50:  # Skip empty/stub files
                    return

            logger.info(f"🕸️  Graph Vectorizing: {Path(filepath).name}")

            # Persistent insert
            self.rag_instance.insert(f"File: {filepath}\nContent:\n{content}")
            logger.info(f"✅ Graph Updated: {Path(filepath).name}")

        except Exception as e:
            logger.error(f"Graph Indexing Error: {e}")


# --- FILE WATCHER SERVICE ---
class AthenaEventHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def _process_event(self, event):
        if event.is_directory:
            return
        filepath = event.dest_path if hasattr(event, "dest_path") else event.src_path
        if not filepath.endswith(".md"):
            return
        if any(p in filepath for p in EXCLUDED_PATTERNS):
            return

        self.watcher.queue_check(filepath)

    def on_created(self, event):
        self._process_event(event)

    def on_modified(self, event):
        self._process_event(event)


class FileWatcher:
    def __init__(self, indexer_queue):
        self.indexer_queue = indexer_queue
        self.running = False
        self.observer = None
        self.pending_checks = set()
        self.check_lock = threading.Lock()

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable WAL (Write-Ahead Logging) for concurrent reads/writes without locking
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
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

    def queue_check(self, filepath):
        with self.check_lock:
            self.pending_checks.add(filepath)

    def process_pending_checks(self):
        with self.check_lock:
            if not self.pending_checks:
                return
            filepaths = list(self.pending_checks)
            self.pending_checks.clear()

        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            file_data = []
            for filepath in filepaths:
                checksum = calculate_checksum(filepath)
                if checksum:
                    file_data.append((filepath, checksum))

            if not file_data:
                return

            paths_to_check = [fd[0] for fd in file_data]
            existing_checksums = {}
            chunk_size = 500
            for i in range(0, len(paths_to_check), chunk_size):
                chunk = paths_to_check[i : i + chunk_size]
                placeholders = ",".join(["?"] * len(chunk))
                cursor.execute(
                    f"SELECT path, checksum FROM files WHERE path IN ({placeholders})",
                    chunk,
                )
                for row in cursor.fetchall():
                    existing_checksums[row["path"]] = row["checksum"]

            changes = 0
            for filepath, checksum in file_data:
                if existing_checksums.get(filepath) != checksum:
                    cursor.execute(
                        "INSERT OR REPLACE INTO files (path, last_modified, checksum, type) VALUES (?, ?, ?, ?)",
                        (filepath, time.time(), checksum, "text/markdown"),
                    )

                    tags = extract_tags(filepath)
                    cursor.execute(
                        "DELETE FROM file_tags WHERE file_path = ?", (filepath,)
                    )
                    for tag in tags:
                        cursor.execute(
                            "INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,)
                        )
                        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                        tag_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT OR IGNORE INTO file_tags (file_path, tag_id) VALUES (?, ?)",
                            (filepath, tag_id),
                        )
                    changes += 1
                    self.indexer_queue.put(filepath)

            if changes > 0:
                conn.commit()
                logger.info(f"Processed {changes} file updates via Watchdog.")
        except Exception as e:
            logger.error(f"Watcher DB Error: {e}")
        finally:
            conn.close()

    def _initial_scan(self):
        """Runs the initial fallback scan to queue existing files (Non-blocking)."""
        logger.info("🔍 Background workspace crawler started...")
        try:
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
                        self.queue_check(filepath)
            logger.info(
                f"✅ Background workspace crawler finished. {len(self.pending_checks)} items queued."
            )
        except Exception as e:
            logger.error(f"Initial Scan Error: {e}")

    async def watch_loop(self):
        self.running = True
        self.init_db()
        logger.info(f"👀 Watcher Event-Driven Started: {[str(d) for d in WATCH_DIRS]}")

        # Deduplicate paths: Do not watch a directory if its parent is already being watched
        deduped_dirs = []
        # Sort by length of path string to process shortest (parents) first
        sorted_dirs = sorted(
            [d.resolve() for d in WATCH_DIRS], key=lambda x: len(str(x))
        )
        for watch_dir in sorted_dirs:
            if not watch_dir.exists():
                continue
            is_child = False
            for d in deduped_dirs:
                if str(watch_dir).startswith(str(d)):
                    is_child = True
                    break
            if not is_child:
                deduped_dirs.append(watch_dir)

        self.observer = Observer()
        handler = AthenaEventHandler(self)
        for watch_dir in deduped_dirs:
            self.observer.schedule(handler, str(watch_dir), recursive=True)
            logger.info(f"📁 Watching Hook: {watch_dir.name}")
        self.observer.start()

        # Fire initial fallback scan into a background thread so it doesn't block the API lifespan
        asyncio.create_task(asyncio.to_thread(self._initial_scan))

        while self.running:
            self.process_pending_checks()
            await asyncio.sleep(POLL_INTERVAL)

    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()


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
