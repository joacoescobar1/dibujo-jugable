#!/usr/bin/env python3
"""Exit 0 if every file in evidence/oracle.sha256 matches; 2 on drift/missing (oracle tampering guard)."""
import hashlib, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; M = ROOT / "evidence/oracle.sha256"
if not M.exists(): print("BLOCK: evidence/oracle.sha256 missing — run scripts/seal_oracle.py in a reviewed task"); sys.exit(2)
bad = 0
for ln in M.read_text().splitlines():
    h, f = ln.split("  ", 1); p = ROOT / f
    cur = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
    if cur != h: print(f"DRIFT {f}: sealed {h[:12]} now {cur[:12]}"); bad += 1
print("OK: oracle seal intact" if not bad else f"BLOCK: {bad} sealed file(s) changed"); sys.exit(2 if bad else 0)
