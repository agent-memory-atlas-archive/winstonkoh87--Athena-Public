#!/usr/bin/env python3
"""
contrast_check.py — Deterministic WCAG 2.x Contrast Ratio Checker

Mathematical relative luminance and contrast calculation per W3C WCAG 2.1 specifications.
Zero external dependencies. Exit code 0 on PASS, 1 on FAIL.

Usage:
    python3 scripts/contrast_check.py "#FFFFFF" "#2563EB"
    python3 scripts/contrast_check.py FFFFFF 2563EB
    python3 scripts/contrast_check.py "#0F172A" "#FFFFFF" --large-only
    python3 scripts/contrast_check.py --selftest
"""

import re
import sys

NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}

BENCHMARK_PAIRS = [
    ("#000000", "#FFFFFF", 21.00, True, True),
    ("#FFFFFF", "#000000", 21.00, True, True),
    ("#FFFFFF", "#333333", 12.63, True, True),
    ("#FFFFFF", "#666666", 5.74, True, True),
    ("#777777", "#FFFFFF", 4.48, False, True),
    ("#FFFFFF", "#888888", 3.54, False, True),
    ("#FFFFFF", "#999999", 2.85, False, False),
    ("#555555", "#000000", 2.82, False, False),
]


def parse_hex(value: str) -> tuple[int, int, int]:
    val = value.strip().lstrip("#")
    if val.lower() in NAMED_COLORS:
        return NAMED_COLORS[val.lower()]
    if len(val) == 3:
        val = "".join(ch * 2 for ch in val)
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", val):
        raise ValueError(
            f"Expected 3-digit or 6-digit hex color (e.g. #FFFFFF), got: {value!r}"
        )
    return (int(val[0:2], 16), int(val[2:4], 16), int(val[4:6], 16))


def linearize(channel: int) -> float:
    c = channel / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (linearize(ch) for ch in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(
    color_a: tuple[int, int, int], color_b: tuple[int, int, int]
) -> float:
    lum_a, lum_b = luminance(color_a), luminance(color_b)
    lighter, darker = sorted((lum_a, lum_b), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def selftest() -> int:
    failures = 0
    for fg, bg, expected_ratio, exp_normal, exp_large in BENCHMARK_PAIRS:
        computed = round(contrast_ratio(parse_hex(fg), parse_hex(bg)), 2)
        norm_pass = computed >= 4.5
        large_pass = computed >= 3.0
        if abs(computed - expected_ratio) > 0.05:
            print(
                f"FAIL: {fg} on {bg} expected ratio ~{expected_ratio}, got {computed}"
            )
            failures += 1
        if norm_pass != exp_normal:
            print(
                f"FAIL: {fg} on {bg} normal pass expected {exp_normal}, got {norm_pass}"
            )
            failures += 1
        if large_pass != exp_large:
            print(
                f"FAIL: {fg} on {bg} large pass expected {exp_large}, got {large_pass}"
            )
            failures += 1
    if failures == 0:
        print(f"✅ Self-test passed: {len(BENCHMARK_PAIRS)} reference pairs OK.")
        return 0
    return 1


def main(argv: list[str]) -> int:
    if len(argv) == 1 and argv[0] == "--selftest":
        return selftest()

    if len(argv) < 2:
        print(
            "Usage: python3 contrast_check.py <fg_hex> <bg_hex> [--large-only | --normal-only]"
        )
        print("       python3 contrast_check.py --selftest")
        return 2

    large_only = "--large-only" in argv
    normal_only = "--normal-only" in argv
    colors = [arg for arg in argv if not arg.startswith("--")]

    if len(colors) != 2:
        print("Error: Exactly two color hex codes required.")
        return 2

    try:
        c1 = parse_hex(colors[0])
        c2 = parse_hex(colors[1])
        ratio = contrast_ratio(c1, c2)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    pass_normal = ratio >= 4.5
    pass_large = ratio >= 3.0

    print(f"Contrast Ratio: {ratio:.2f}:1")
    print(f"  Normal Text (>= 4.5:1): {'PASS ✅' if pass_normal else 'FAIL ❌'}")
    print(f"  Large Text  (>= 3.0:1): {'PASS ✅' if pass_large else 'FAIL ❌'}")
    print(f"  UI Borders  (>= 3.0:1): {'PASS ✅' if pass_large else 'FAIL ❌'}")

    if large_only:
        return 0 if pass_large else 1
    if normal_only:
        return 0 if pass_normal else 1
    return 0 if pass_normal else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
