"""Print the filing passages a human needs to hand-check: headcount, median pay, the founder's shares.

Usage: python pipeline/explore.py KEY [jobs|median|own NAME]
"""
import re
import sys

from common import CACHE


def sentences(text):
    return re.split(r"(?<=[.;])\s+|\n", text)


def grep(text, pattern, need=None, limit=8, width=330):
    n = 0
    for s in sentences(text):
        if re.search(pattern, s, re.I) and (need is None or re.search(need, s, re.I)):
            print("  >", s.strip()[:width])
            n += 1
            if n >= limit:
                break


def own(text, name, limit=10):
    lines = text.split("\n")
    n = 0
    for i, l in enumerate(lines):
        if name.lower() in l.lower() and re.search(r"\d{1,3}(,\d{3}){2,}", l):
            print("  >", l.strip()[:400])
            n += 1
            if n >= limit:
                break


if __name__ == "__main__":
    key, what = sys.argv[1], sys.argv[2]
    form = {"jobs": "10-K", "median": "DEF14A", "own": "DEF14A"}[what]
    path = CACHE / "text" / f"{key}-{form}.txt"
    if not path.exists():
        path = CACHE / "text" / f"{key}-20-F.txt"
    text = path.read_text(encoding="utf-8")
    print(f"== {key} {what} ({path.name})")
    if what == "jobs":
        grep(text, r"\b(employ|headcount|team members|associates)", need=r"\d{1,3}(,\d{3})+|\d+(\.\d+)?\s*million", limit=6)
    elif what == "median":
        grep(text, r"median", need=r"\$\s?\d", limit=6)
    else:
        own(text, sys.argv[3])
