#!/usr/bin/env python3
"""
athena.tools.ast_graph
=======================

AST-based codebase graph engine for Project Athena.

Parses all Python source files using the standard-library ``ast`` module and
stores a relational symbol graph in a local SQLite database.  Provides fast
structural queries:

* **find-symbol**  — locate any class, function, or method by name
* **find-callers** — all call sites that invoke a given symbol
* **find-callees** — all symbols called by a given function/method
* **stats**        — codebase summary (files, classes, functions, LOC)

Zero external dependencies — uses only ``ast``, ``sqlite3``, and ``pathlib``.
"""

from __future__ import annotations

import ast
import logging
import sqlite3
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# SDK path bootstrap (consistent with other tools in this package)
# ---------------------------------------------------------------------------
SDK_PATH = Path(__file__).resolve().parent.parent.parent
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from athena.core.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_DB_PATH = PROJECT_ROOT / ".athena" / "codebase_ast.db"
DEFAULT_SCAN_DIRS = [
    PROJECT_ROOT / "src",
    PROJECT_ROOT / ".agent" / "scripts",
]

# Directories to always skip
_SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    "archive_skills",
    ".athena",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class SymbolRecord:
    """A single extracted symbol (class, function, or method)."""

    file_path: str
    symbol_type: str  # 'class' | 'function' | 'method'
    name: str
    qualified_name: str  # e.g. 'ClassName.method_name'
    line_start: int
    line_end: int
    docstring: str = ""
    parent_class: str = ""


@dataclass
class ImportRecord:
    """A single import statement."""

    file_path: str
    module: str  # 'from X' or 'import X'
    name: str  # the imported name
    alias: str = ""
    line: int = 0


@dataclass
class CallSiteRecord:
    """A detected function/method call."""

    file_path: str
    caller_qualified: str  # qualified name of the enclosing function
    callee_name: str  # the name being called
    line: int = 0


@dataclass
class FileStats:
    """Per-file statistics."""

    file_path: str
    line_count: int
    class_count: int = 0
    function_count: int = 0
    import_count: int = 0


# ---------------------------------------------------------------------------
# AST Visitor
# ---------------------------------------------------------------------------
class _SymbolExtractor(ast.NodeVisitor):
    """Walk an AST tree and collect symbols, imports, and call sites."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.symbols: list[SymbolRecord] = []
        self.imports: list[ImportRecord] = []
        self.call_sites: list[CallSiteRecord] = []
        self._scope_stack: list[str] = []  # tracks enclosing class/function

    @property
    def _current_scope(self) -> str:
        return ".".join(self._scope_stack) if self._scope_stack else "<module>"

    def _get_docstring(self, node: ast.AST) -> str:
        """Extract docstring from a class or function node."""
        try:
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef, ast.Module)):
                return ast.get_docstring(node) or ""
            return ""
        except Exception:
            return ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        rec = SymbolRecord(
            file_path=self.file_path,
            symbol_type="class",
            name=node.name,
            qualified_name=(
                f"{self._current_scope}.{node.name}"
                if self._scope_stack
                else node.name
            ),
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=self._get_docstring(node),
        )
        self.symbols.append(rec)
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def _visit_func(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # Determine if this is a method (inside a class) or a module-level function
        is_method = (
            len(self._scope_stack) > 0
            and any(
                s.symbol_type == "class" and s.name == self._scope_stack[-1]
                for s in self.symbols
            )
        )
        qname = (
            f"{self._current_scope}.{node.name}"
            if self._scope_stack
            else node.name
        )
        parent = self._scope_stack[-1] if is_method else ""

        rec = SymbolRecord(
            file_path=self.file_path,
            symbol_type="method" if is_method else "function",
            name=node.name,
            qualified_name=qname,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=self._get_docstring(node),
            parent_class=parent,
        )
        self.symbols.append(rec)

        # Walk the function body for call sites
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                ImportRecord(
                    file_path=self.file_path,
                    module=alias.name,
                    name=alias.name.rsplit(".", 1)[-1],
                    alias=alias.asname or "",
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            self.imports.append(
                ImportRecord(
                    file_path=self.file_path,
                    module=module,
                    name=alias.name,
                    alias=alias.asname or "",
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee = self._resolve_call_name(node.func)
        if callee:
            self.call_sites.append(
                CallSiteRecord(
                    file_path=self.file_path,
                    caller_qualified=self._current_scope,
                    callee_name=callee,
                    line=node.lineno,
                )
            )
        self.generic_visit(node)

    @staticmethod
    def _resolve_call_name(node: ast.expr) -> str:
        """Flatten an AST call target to a dotted string."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = _SymbolExtractor._resolve_call_name(node.value)
            if prefix:
                return f"{prefix}.{node.attr}"
            return node.attr
        # Subscripts, starred, etc. — skip
        return ""


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------
def discover_python_files(
    scan_dirs: list[Path] | None = None,
) -> Iterator[Path]:
    """Yield all .py files under the scan directories, skipping exclusions."""
    dirs = scan_dirs or DEFAULT_SCAN_DIRS
    for d in dirs:
        if not d.exists():
            continue
        for py_file in sorted(d.rglob("*.py")):
            # Skip excluded directories
            if any(part in _SKIP_DIRS for part in py_file.parts):
                continue
            yield py_file


# ---------------------------------------------------------------------------
# Parse a single file
# ---------------------------------------------------------------------------
def parse_file(
    py_file: Path,
    relative_to: Path | None = None,
) -> tuple[list[SymbolRecord], list[ImportRecord], list[CallSiteRecord], FileStats]:
    """Parse one Python file and return extracted records."""
    rel = relative_to or PROJECT_ROOT
    file_key = str(py_file.relative_to(rel))

    try:
        source = py_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.warning("Cannot read %s: %s", py_file, exc)
        return [], [], [], FileStats(file_path=file_key, line_count=0)

    line_count = source.count("\n") + 1

    try:
        tree = ast.parse(source, filename=str(py_file))
    except SyntaxError as exc:
        logger.warning("Syntax error in %s: %s", py_file, exc)
        return [], [], [], FileStats(file_path=file_key, line_count=line_count)

    extractor = _SymbolExtractor(file_key)
    extractor.visit(tree)

    stats = FileStats(
        file_path=file_key,
        line_count=line_count,
        class_count=sum(1 for s in extractor.symbols if s.symbol_type == "class"),
        function_count=sum(
            1 for s in extractor.symbols if s.symbol_type in ("function", "method")
        ),
        import_count=len(extractor.imports),
    )

    return extractor.symbols, extractor.imports, extractor.call_sites, stats


# ---------------------------------------------------------------------------
# SQLite Schema & Persistence
# ---------------------------------------------------------------------------
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS symbols (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    symbol_type TEXT NOT NULL CHECK (symbol_type IN ('class', 'function', 'method')),
    name TEXT NOT NULL,
    qualified_name TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    docstring TEXT DEFAULT '',
    parent_class TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    module TEXT NOT NULL,
    name TEXT NOT NULL,
    alias TEXT DEFAULT '',
    line INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS call_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    caller_qualified TEXT NOT NULL,
    callee_name TEXT NOT NULL,
    line INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS file_stats (
    file_path TEXT PRIMARY KEY,
    line_count INTEGER NOT NULL,
    class_count INTEGER DEFAULT 0,
    function_count INTEGER DEFAULT 0,
    import_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS index_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_qualified ON symbols(qualified_name);
CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_path);
CREATE INDEX IF NOT EXISTS idx_imports_name ON imports(name);
CREATE INDEX IF NOT EXISTS idx_imports_module ON imports(module);
CREATE INDEX IF NOT EXISTS idx_call_sites_callee ON call_sites(callee_name);
CREATE INDEX IF NOT EXISTS idx_call_sites_caller ON call_sites(caller_qualified);
"""


class CodebaseIndex:
    """
    Manages the SQLite-backed codebase AST index.

    Usage::

        idx = CodebaseIndex()
        idx.build()                         # full index from scan dirs
        idx.find_symbol("context_gate")     # locate definitions
        idx.find_callers("context_gate")    # who calls it?
        idx.find_callees("parse_file")      # what does it call?
        idx.stats()                         # summary dict
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    # -- Connection management -----------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    # -- Schema --------------------------------------------------------------
    def _ensure_schema(self) -> None:
        conn = self._connect()
        conn.executescript(_SCHEMA_SQL)
        conn.commit()

    def _clear_data(self) -> None:
        conn = self._connect()
        for table in ("symbols", "imports", "call_sites", "file_stats", "index_meta"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()

    # -- Build index ----------------------------------------------------------
    def build(
        self,
        scan_dirs: list[Path] | None = None,
        relative_to: Path | None = None,
    ) -> dict:
        """
        Full re-index: parse all Python files and persist to SQLite.

        Returns a summary dict with counts.
        """
        t0 = time.monotonic()
        self._ensure_schema()
        self._clear_data()

        conn = self._connect()
        rel = relative_to or PROJECT_ROOT

        file_count = 0
        total_symbols = 0
        total_imports = 0
        total_calls = 0
        total_lines = 0

        for py_file in discover_python_files(scan_dirs):
            symbols, imports, calls, fstats = parse_file(py_file, relative_to=rel)

            for s in symbols:
                conn.execute(
                    "INSERT INTO symbols "
                    "(file_path, symbol_type, name, qualified_name, "
                    "line_start, line_end, docstring, parent_class) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        s.file_path,
                        s.symbol_type,
                        s.name,
                        s.qualified_name,
                        s.line_start,
                        s.line_end,
                        s.docstring,
                        s.parent_class,
                    ),
                )

            for imp in imports:
                conn.execute(
                    "INSERT INTO imports (file_path, module, name, alias, line) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (imp.file_path, imp.module, imp.name, imp.alias, imp.line),
                )

            for call in calls:
                conn.execute(
                    "INSERT INTO call_sites "
                    "(file_path, caller_qualified, callee_name, line) "
                    "VALUES (?, ?, ?, ?)",
                    (call.file_path, call.caller_qualified, call.callee_name, call.line),
                )

            conn.execute(
                "INSERT OR REPLACE INTO file_stats "
                "(file_path, line_count, class_count, function_count, import_count) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    fstats.file_path,
                    fstats.line_count,
                    fstats.class_count,
                    fstats.function_count,
                    fstats.import_count,
                ),
            )

            file_count += 1
            total_symbols += len(symbols)
            total_imports += len(imports)
            total_calls += len(calls)
            total_lines += fstats.line_count

        elapsed = time.monotonic() - t0

        # Store metadata
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        meta = {
            "indexed_at": now,
            "elapsed_seconds": f"{elapsed:.2f}",
            "file_count": str(file_count),
            "symbol_count": str(total_symbols),
            "import_count": str(total_imports),
            "call_site_count": str(total_calls),
            "total_lines": str(total_lines),
        }
        for k, v in meta.items():
            conn.execute(
                "INSERT OR REPLACE INTO index_meta (key, value) VALUES (?, ?)",
                (k, v),
            )

        conn.commit()

        summary = {
            "files": file_count,
            "symbols": total_symbols,
            "imports": total_imports,
            "call_sites": total_calls,
            "lines": total_lines,
            "elapsed_seconds": round(elapsed, 2),
            "db_path": str(self.db_path),
        }
        logger.info("Index built: %s", summary)
        return summary

    # -- Query: find symbol ---------------------------------------------------
    def find_symbol(self, name: str, exact: bool = False) -> list[dict]:
        """
        Find symbol definitions matching *name*.

        With ``exact=True``, matches only ``symbols.name = name``.
        Otherwise uses a case-insensitive LIKE search.
        """
        conn = self._connect()
        if exact:
            rows = conn.execute(
                "SELECT * FROM symbols WHERE name = ? ORDER BY file_path, line_start",
                (name,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM symbols WHERE name LIKE ? "
                "ORDER BY file_path, line_start",
                (f"%{name}%",),
            ).fetchall()
        return [dict(r) for r in rows]

    # -- Query: find callers --------------------------------------------------
    def find_callers(self, callee_name: str) -> list[dict]:
        """
        Find all call sites that invoke *callee_name*.

        Matches the *tail* of the callee (e.g. ``context_gate`` matches
        ``self.context_gate``, ``athena.context_gate``, and bare ``context_gate``).
        """
        conn = self._connect()
        rows = conn.execute(
            "SELECT cs.file_path, cs.caller_qualified, cs.callee_name, cs.line, "
            "       s.symbol_type, s.qualified_name AS caller_symbol "
            "FROM call_sites cs "
            "LEFT JOIN symbols s "
            "  ON cs.file_path = s.file_path "
            "  AND cs.caller_qualified = s.qualified_name "
            "WHERE cs.callee_name = ? "
            "   OR cs.callee_name LIKE ? "
            "ORDER BY cs.file_path, cs.line",
            (callee_name, f"%.{callee_name}"),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Query: find callees --------------------------------------------------
    def find_callees(self, caller_name: str) -> list[dict]:
        """
        Find all symbols called *by* a given function/method.

        Matches the caller by qualified name (exact) or trailing name (fuzzy).
        """
        conn = self._connect()
        rows = conn.execute(
            "SELECT cs.file_path, cs.caller_qualified, cs.callee_name, cs.line "
            "FROM call_sites cs "
            "WHERE cs.caller_qualified = ? "
            "   OR cs.caller_qualified LIKE ? "
            "ORDER BY cs.line",
            (caller_name, f"%.{caller_name}"),
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Query: stats ---------------------------------------------------------
    def stats(self) -> dict:
        """Return aggregate codebase statistics from the index."""
        conn = self._connect()

        # File-level aggregates
        row = conn.execute(
            "SELECT COUNT(*) AS files, "
            "       COALESCE(SUM(line_count), 0) AS lines, "
            "       COALESCE(SUM(class_count), 0) AS classes, "
            "       COALESCE(SUM(function_count), 0) AS functions, "
            "       COALESCE(SUM(import_count), 0) AS imports "
            "FROM file_stats"
        ).fetchone()

        call_count = conn.execute(
            "SELECT COUNT(*) FROM call_sites"
        ).fetchone()[0]

        # Index metadata
        meta_rows = conn.execute("SELECT key, value FROM index_meta").fetchall()
        meta = {r["key"]: r["value"] for r in meta_rows}

        return {
            "files": row["files"],
            "lines": row["lines"],
            "classes": row["classes"],
            "functions": row["functions"],
            "imports": row["imports"],
            "call_sites": call_count,
            "indexed_at": meta.get("indexed_at", "unknown"),
            "elapsed_seconds": meta.get("elapsed_seconds", "unknown"),
        }

    # -- Query: dead symbols (defined but never called) -----------------------
    def find_dead_symbols(self) -> list[dict]:
        """
        Find functions and methods that are defined but never appear as
        a callee in any call site.  Excludes dunder methods, test functions,
        and ``if __name__`` blocks.
        """
        conn = self._connect()
        rows = conn.execute(
            "SELECT s.file_path, s.symbol_type, s.name, s.qualified_name, "
            "       s.line_start "
            "FROM symbols s "
            "WHERE s.symbol_type IN ('function', 'method') "
            "  AND s.name NOT LIKE '\\_\\_%' ESCAPE '\\' "
            "  AND s.name NOT LIKE 'test\\_%' ESCAPE '\\' "
            "  AND NOT EXISTS ( "
            "      SELECT 1 FROM call_sites cs "
            "      WHERE cs.callee_name = s.name "
            "         OR cs.callee_name LIKE '%.' || s.name "
            "  ) "
            "ORDER BY s.file_path, s.line_start"
        ).fetchall()
        return [dict(r) for r in rows]

    # -- Query: top-level summary for humans ----------------------------------
    def summary_report(self) -> str:
        """Return a human-readable codebase summary string."""
        s = self.stats()
        lines = [
            "Athena Codebase AST Index",
            "=" * 40,
            f"  Files indexed:     {s['files']}",
            f"  Total lines:       {s['lines']:,}",
            f"  Classes:           {s['classes']}",
            f"  Functions/Methods: {s['functions']}",
            f"  Import statements: {s['imports']}",
            f"  Call sites:        {s['call_sites']:,}",
            f"  Indexed at:        {s['indexed_at']}",
            f"  Index time:        {s['elapsed_seconds']}s",
        ]
        return "\n".join(lines)
