#!/usr/bin/env python3
"""
tests/test_codebase_ast.py
==========================

Automated test suite for the Athena AST Codebase Graph Engine.

Tests cover:
  1. Parsing accuracy — classes, functions, methods, imports, call sites
  2. Caller-callee resolution — bidirectional graph queries
  3. SQLite persistence — build → close → reopen → query
  4. Dead symbol detection
  5. Stats computation
  6. Edge cases — syntax errors, empty files, nested classes
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# SDK path is set by conftest.py
from athena.tools.ast_graph import (
    CodebaseIndex,
    parse_file,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def tmp_py_file(tmp_path: Path) -> Path:
    """Create a sample Python file for parsing tests."""
    code = textwrap.dedent("""\
        import os
        from pathlib import Path

        GLOBAL_VAR = 42


        class DatabaseEngine:
            \"\"\"Main database engine.\"\"\"

            def __init__(self, db_path: str) -> None:
                self.db_path = db_path
                self.conn = self._connect()

            def _connect(self):
                \"\"\"Open a database connection.\"\"\"
                return sqlite3.connect(self.db_path)

            def execute_query(self, sql: str):
                \"\"\"Run a SQL query.\"\"\"
                cursor = self.conn.cursor()
                result = cursor.execute(sql)
                return result.fetchall()


        class ChildEngine(DatabaseEngine):
            \"\"\"Inherits from DatabaseEngine.\"\"\"

            def specialised_query(self):
                return self.execute_query("SELECT 1")


        def standalone_function(x: int, y: int) -> int:
            \"\"\"A module-level function.\"\"\"
            result = os.path.join(str(x), str(y))
            return len(result)


        def caller_function():
            \"\"\"Calls other things.\"\"\"
            engine = DatabaseEngine("test.db")
            engine.execute_query("SELECT 1")
            standalone_function(1, 2)


        def _private_unused():
            \"\"\"Never called anywhere.\"\"\"
            pass
    """)
    p = tmp_path / "sample_module.py"
    p.write_text(code, encoding="utf-8")
    return p


@pytest.fixture
def tmp_index(tmp_path: Path, tmp_py_file: Path) -> CodebaseIndex:
    """Build an index over the sample file."""
    db_path = tmp_path / "test_ast.db"
    idx = CodebaseIndex(db_path=db_path)
    idx.build(scan_dirs=[tmp_path], relative_to=tmp_path)
    return idx


# ---------------------------------------------------------------------------
# 1. Parsing Accuracy
# ---------------------------------------------------------------------------
class TestParsing:
    """Verify that the AST extractor correctly identifies symbols."""

    def test_parse_extracts_classes(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        class_names = [s.name for s in symbols if s.symbol_type == "class"]
        assert "DatabaseEngine" in class_names
        assert "ChildEngine" in class_names

    def test_parse_extracts_methods(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        methods = [s for s in symbols if s.symbol_type == "method"]
        method_names = [m.name for m in methods]
        assert "__init__" in method_names
        assert "_connect" in method_names
        assert "execute_query" in method_names
        assert "specialised_query" in method_names

    def test_parse_extracts_functions(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        funcs = [s for s in symbols if s.symbol_type == "function"]
        func_names = [f.name for f in funcs]
        assert "standalone_function" in func_names
        assert "caller_function" in func_names
        assert "_private_unused" in func_names

    def test_parse_extracts_docstrings(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        engine = next(s for s in symbols if s.name == "DatabaseEngine")
        assert "Main database engine" in engine.docstring

    def test_parse_extracts_imports(self, tmp_py_file: Path, tmp_path: Path):
        _, imports, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        import_names = [i.name for i in imports]
        assert "os" in import_names
        assert "Path" in import_names

    def test_parse_extracts_call_sites(self, tmp_py_file: Path, tmp_path: Path):
        _, _, calls, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        callee_names = [c.callee_name for c in calls]
        assert "standalone_function" in callee_names
        assert "DatabaseEngine" in callee_names

    def test_parse_file_stats(self, tmp_py_file: Path, tmp_path: Path):
        _, _, _, stats = parse_file(tmp_py_file, relative_to=tmp_path)
        assert stats.line_count > 0
        assert stats.class_count == 2
        assert stats.function_count > 0

    def test_qualified_names_for_methods(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        init_sym = next(
            s for s in symbols if s.name == "__init__" and s.parent_class == "DatabaseEngine"
        )
        assert init_sym.qualified_name == "DatabaseEngine.__init__"

    def test_parent_class_set_for_methods(self, tmp_py_file: Path, tmp_path: Path):
        symbols, _, _, _ = parse_file(tmp_py_file, relative_to=tmp_path)
        methods = [s for s in symbols if s.symbol_type == "method"]
        for m in methods:
            assert m.parent_class != "", f"Method {m.name} should have a parent_class"


# ---------------------------------------------------------------------------
# 2. SQLite Persistence & Queries
# ---------------------------------------------------------------------------
class TestIndexQueries:
    """Verify index build, persistence, and query operations."""

    def test_build_returns_counts(self, tmp_index: CodebaseIndex):
        # The index was already built by the fixture; verify stats
        s = tmp_index.stats()
        assert s["files"] >= 1
        assert s["classes"] == 2
        assert s["functions"] > 0

    def test_find_symbol_exact(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_symbol("DatabaseEngine", exact=True)
        assert len(results) == 1
        assert results[0]["symbol_type"] == "class"

    def test_find_symbol_fuzzy(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_symbol("Engine")
        names = [r["name"] for r in results]
        assert "DatabaseEngine" in names
        assert "ChildEngine" in names

    def test_find_symbol_no_match(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_symbol("NonExistentXyz123", exact=True)
        assert len(results) == 0

    def test_find_callers(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_callers("standalone_function")
        assert len(results) >= 1
        callers = [r["caller_qualified"] for r in results]
        assert any("caller_function" in c for c in callers)

    def test_find_callers_method(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_callers("execute_query")
        assert len(results) >= 1

    def test_find_callees(self, tmp_index: CodebaseIndex):
        results = tmp_index.find_callees("caller_function")
        callee_names = [r["callee_name"] for r in results]
        assert "DatabaseEngine" in callee_names
        assert "standalone_function" in callee_names

    def test_persistence_survives_close_reopen(self, tmp_path: Path, tmp_py_file: Path):
        """Build, close, reopen a fresh connection, and verify data persists."""
        db_path = tmp_path / "persist_test.db"
        idx1 = CodebaseIndex(db_path=db_path)
        idx1.build(scan_dirs=[tmp_path], relative_to=tmp_path)
        idx1.close()

        # Reopen with a fresh instance
        idx2 = CodebaseIndex(db_path=db_path)
        results = idx2.find_symbol("DatabaseEngine", exact=True)
        assert len(results) == 1
        s = idx2.stats()
        assert s["files"] >= 1
        idx2.close()


# ---------------------------------------------------------------------------
# 3. Dead Symbol Detection
# ---------------------------------------------------------------------------
class TestDeadSymbols:
    """Verify dead symbol detection logic."""

    def test_private_unused_detected(self, tmp_index: CodebaseIndex):
        dead = tmp_index.find_dead_symbols()
        dead_names = [d["name"] for d in dead]
        # _private_unused is defined but never called
        assert "_private_unused" in dead_names

    def test_called_symbols_not_flagged(self, tmp_index: CodebaseIndex):
        dead = tmp_index.find_dead_symbols()
        dead_names = [d["name"] for d in dead]
        # standalone_function IS called by caller_function
        assert "standalone_function" not in dead_names


# ---------------------------------------------------------------------------
# 4. Edge Cases
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """Handle broken, empty, and unusual Python files gracefully."""

    def test_syntax_error_file(self, tmp_path: Path):
        """A file with a syntax error should not crash the parser."""
        bad_file = tmp_path / "broken.py"
        bad_file.write_text("def foo(\n    # missing closing paren", encoding="utf-8")

        symbols, imports, calls, stats = parse_file(bad_file, relative_to=tmp_path)
        assert len(symbols) == 0
        assert stats.line_count > 0  # still counts lines

    def test_empty_file(self, tmp_path: Path):
        """An empty .py file should parse cleanly with zero symbols."""
        empty = tmp_path / "empty.py"
        empty.write_text("", encoding="utf-8")

        symbols, imports, calls, stats = parse_file(empty, relative_to=tmp_path)
        assert len(symbols) == 0
        assert len(imports) == 0
        assert stats.line_count == 1  # one line (empty)

    def test_nested_class(self, tmp_path: Path):
        """Nested classes should get correct qualified names."""
        code = textwrap.dedent("""\
            class Outer:
                class Inner:
                    def inner_method(self):
                        pass
        """)
        f = tmp_path / "nested.py"
        f.write_text(code, encoding="utf-8")

        symbols, _, _, _ = parse_file(f, relative_to=tmp_path)
        inner = next((s for s in symbols if s.name == "Inner"), None)
        assert inner is not None
        assert inner.qualified_name == "Outer.Inner"

        method = next((s for s in symbols if s.name == "inner_method"), None)
        assert method is not None
        assert method.qualified_name == "Outer.Inner.inner_method"

    def test_async_function(self, tmp_path: Path):
        """Async functions should be parsed as regular functions."""
        code = textwrap.dedent("""\
            import asyncio

            async def fetch_data(url: str):
                \"\"\"Async data fetcher.\"\"\"
                pass
        """)
        f = tmp_path / "async_mod.py"
        f.write_text(code, encoding="utf-8")

        symbols, _, _, _ = parse_file(f, relative_to=tmp_path)
        func = next((s for s in symbols if s.name == "fetch_data"), None)
        assert func is not None
        assert func.symbol_type == "function"
        assert "Async data fetcher" in func.docstring


# ---------------------------------------------------------------------------
# 5. Summary Report
# ---------------------------------------------------------------------------
class TestSummaryReport:
    """Verify the human-readable summary output."""

    def test_summary_report_format(self, tmp_index: CodebaseIndex):
        report = tmp_index.summary_report()
        assert "Athena Codebase AST Index" in report
        assert "Files indexed:" in report
        assert "Classes:" in report
        assert "Functions/Methods:" in report

    def test_stats_returns_dict(self, tmp_index: CodebaseIndex):
        s = tmp_index.stats()
        assert isinstance(s, dict)
        assert "files" in s
        assert "lines" in s
        assert "classes" in s
        assert "call_sites" in s
