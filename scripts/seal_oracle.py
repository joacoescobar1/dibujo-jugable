#!/usr/bin/env python3
"""Seal oracle files: write sha256 manifest to evidence/oracle.sha256 (sha256sum format). Run ONLY in a reviewed oracle-change task."""
import hashlib, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
SEALED = ["scripts/validate_spec.py", "scripts/solver_reachability.py", "scripts/check_win_artifact.py", "specs/game-spec.schema.json"]
if __name__ == "__main__":
    lines = [f"{hashlib.sha256((ROOT / f).read_bytes()).hexdigest()}  {f}" for f in SEALED]
    (ROOT / "evidence/oracle.sha256").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
