"""Print a person's row from the beneficial-ownership table of a cached proxy statement.

Usage: python pipeline/ownrow.py KEY "Name fragment" [lines]
Rows are split across lines in the text dump, so the row plus the next few lines are joined.
"""
import re
import sys

from common import CACHE

key, name = sys.argv[1], sys.argv[2]
span = int(sys.argv[3]) if len(sys.argv) > 3 else 8
lines = (CACHE / "text" / f"{key}-DEF14A.txt").read_text(encoding="utf-8").split("\n")
heads = [i for i, l in enumerate(lines) if re.search(r"Name (and Address )?of Beneficial Owner|Amount and Nature of Beneficial", l, re.I)]
print(f"== {key}: ownership table headers at lines {heads[:4]}")
for h in heads[:2]:
    for i in range(h, min(h + 400, len(lines))):
        if name.lower() in lines[i].lower():
            row = " ".join(l.strip() for l in lines[i:i + span] if l.strip() not in ("", "|"))
            row = re.sub(r"(\| )+", "| ", row)
            print(f"  L{i}: {row[:360]}")
            break
