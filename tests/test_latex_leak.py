import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(".agent/scripts"))

from check_latex_leak import is_latex_leak  # noqa: E402  (path set up above)

FLAG_CASES = [
    "$O(N)$",
    "$O(N^2)$",
    "$N = 310$",
    "$R^2$",
    "$\\alpha$",
    "$\\rightarrow$",
    "$\\frac{a}{b}$",
    "$$E = mc^2$$",
    "\\(x+y\\)",
    "\\[ \\int_0^1 x \\]",
    "\\text{EV}",
]

IGNORE_CASES = [
    "Campaign EV = +10.45% (95% CI [+4.00%, +16.98%])",
    "S$1.3k injection",
    "$500 stop-out",
    "US$10K notional",
    "$100 budget ($50 each)",
    "price $50 and $60",
    "$0.07/0.01 lot",
    "set $HOME in your profile",
    "O(N^2)",
    "10.45%",
]

@pytest.mark.parametrize("text", FLAG_CASES)
def test_flag_cases(text):
    assert is_latex_leak(text), f"Expected FLAG for: {text}"

@pytest.mark.parametrize("text", IGNORE_CASES)
def test_ignore_cases(text):
    assert not is_latex_leak(text), f"Expected IGNORE for: {text}"
