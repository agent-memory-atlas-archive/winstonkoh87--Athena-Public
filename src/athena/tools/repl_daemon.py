"""
Persistent Python REPL Daemon module.
"""
import code
import collections
import contextlib
import csv
import datetime
import io
import json
import os
import pathlib
import sqlite3
import sys
import time
from dataclasses import dataclass
from typing import Any

SDK_PATH = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SDK_PATH))


@dataclass
class ReplResult:
    stdout: str
    stderr: str
    success: bool
    elapsed_seconds: float
    variables_created: list[str]

class ReplDaemon:
    def __init__(self):
        self._history: list[str] = []
        self._initial_keys = set()
        self.reset()

    def reset(self):
        self.namespace = {
            'os': os,
            'sys': sys,
            'Path': pathlib.Path,
            'json': json,
            'csv': csv,
            'sqlite3': sqlite3,
            'collections': collections,
            'datetime': datetime,
        }
        self.interpreter = code.InteractiveInterpreter(self.namespace)
        self._history = []
        self._initial_keys = set(self.namespace.keys())

    def execute(self, code_str: str) -> ReplResult:
        self._history.append(code_str)
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        start_time = time.time()
        before_keys = set(self.namespace.keys())

        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                # Try to compile as single statement for expression printing
                compile(code_str, "<input>", "single")
                symbol = "single"
            except SyntaxError:
                symbol = "exec"
            except Exception:
                symbol = "exec"

            is_incomplete = self.interpreter.runsource(code_str, symbol=symbol)
            if is_incomplete:
                print("Error: Incomplete input", file=sys.stderr)

        end_time = time.time()
        stdout_str = stdout_capture.getvalue()
        stderr_str = stderr_capture.getvalue()

        success = not bool(stderr_str)
        after_keys = set(self.namespace.keys())
        new_keys = list(after_keys - before_keys)
        if '__builtins__' in new_keys:
            new_keys.remove('__builtins__')

        return ReplResult(
            stdout=stdout_str,
            stderr=stderr_str,
            success=success,
            elapsed_seconds=end_time - start_time,
            variables_created=new_keys
        )

    def get_variable(self, name: str) -> Any:
        return self.namespace.get(name)

    def set_variable(self, name: str, value: Any):
        self.namespace[name] = value

    def list_variables(self) -> list[dict]:
        variables = []
        for name, val in self.namespace.items():
            if name in self._initial_keys:
                continue
            if name.startswith('__') and name.endswith('__'):
                continue
            if type(val).__name__ == 'module':
                continue

            val_repr = repr(val)
            if len(val_repr) > 100:
                val_repr = val_repr[:97] + '...'

            variables.append({
                'name': name,
                'type': type(val).__name__,
                'repr': val_repr
            })
        return variables

    def history(self) -> list[str]:
        return self._history.copy()
