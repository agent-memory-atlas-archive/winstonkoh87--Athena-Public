"""
Tests for the Persistent Python REPL Daemon.
"""
import pathlib
import sys

SDK_PATH = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SDK_PATH))

from src.athena.tools.repl_daemon import ReplDaemon


def test_basic_expression():
    daemon = ReplDaemon()
    res = daemon.execute("2 + 2")
    assert res.success is True
    assert res.stdout.strip() == "4"

def test_variable_persistence():
    daemon = ReplDaemon()
    res = daemon.execute("x = 10")
    assert res.success is True
    assert "x" in res.variables_created

    res2 = daemon.execute("x * 2")
    assert res2.success is True
    assert res2.stdout.strip() == "20"

def test_import_persistence():
    daemon = ReplDaemon()
    daemon.execute("import math")
    res = daemon.execute("math.sqrt(16)")
    assert res.success is True
    assert res.stdout.strip() == "4.0"

def test_function_persistence():
    daemon = ReplDaemon()
    code = "def my_func(a):\n    return a + 5\n"
    res = daemon.execute(code)
    assert res.success is True

    res2 = daemon.execute("my_func(10)")
    assert res2.stdout.strip() == "15"

def test_class_persistence():
    daemon = ReplDaemon()
    code = "class MyClass:\n    def __init__(self):\n        self.val = 42\n"
    daemon.execute(code)

    daemon.execute("obj = MyClass()")
    res = daemon.execute("obj.val")
    assert res.stdout.strip() == "42"

def test_syntax_error():
    daemon = ReplDaemon()
    res = daemon.execute("2 + * 3")
    assert res.success is False
    assert "SyntaxError" in res.stderr

def test_name_error():
    daemon = ReplDaemon()
    res = daemon.execute("undefined_var")
    assert res.success is False
    assert "NameError" in res.stderr

def test_get_set_variable():
    daemon = ReplDaemon()
    daemon.set_variable("test_var", "hello")
    assert daemon.get_variable("test_var") == "hello"

    res = daemon.execute("test_var + ' world'")
    assert res.stdout.strip() == "'hello world'"

def test_list_variables_user_only():
    daemon = ReplDaemon()
    daemon.execute("a = 1")
    daemon.execute("b = 'test'")
    vars_list = daemon.list_variables()

    var_names = [v['name'] for v in vars_list]
    assert "a" in var_names
    assert "b" in var_names
    assert "os" not in var_names
    assert "sys" not in var_names

def test_reset_clears_variables():
    daemon = ReplDaemon()
    daemon.execute("x = 100")
    assert daemon.get_variable("x") == 100

    daemon.reset()
    assert daemon.get_variable("x") is None

    vars_list = daemon.list_variables()
    assert len(vars_list) == 0

def test_history_tracks_executed_code():
    daemon = ReplDaemon()
    daemon.execute("a = 1")
    daemon.execute("b = 2")

    hist = daemon.history()
    assert len(hist) == 2
    assert hist[0] == "a = 1"
    assert hist[1] == "b = 2"

def test_variables_created_tracking():
    daemon = ReplDaemon()
    res = daemon.execute("y = 5\nz = 10")
    assert set(res.variables_created) == {"y", "z"}

def test_stdout_capture():
    daemon = ReplDaemon()
    res = daemon.execute("print('hello out')")
    assert res.stdout.strip() == "hello out"

def test_elapsed_time_non_negative():
    daemon = ReplDaemon()
    res = daemon.execute("1 + 1")
    assert res.elapsed_seconds >= 0

def test_multi_line_code_execution():
    daemon = ReplDaemon()
    code = "for i in range(3):\n    print(i)\n"
    res = daemon.execute(code)
    assert res.success is True
    assert res.stdout.strip() == "0\n1\n2"
