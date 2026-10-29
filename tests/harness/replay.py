#!/usr/bin/env python3
"""T11: replay generate -> validate -> play(STUCK) -> patch (via muse_fix w/ injected chat) -> play(WIN) against recorded-shape
Responses API fixtures. Offline, $0, no network. Exit 0 = pass."""
import json, sys, pathlib, subprocess, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path[:0] = [str(ROOT / "agent"), str(ROOT)]
from patch_loop import muse_fix, fix_prompt
from playtest import playtest
from outcomes import from_solver, RunOutcome
from game_guide import write_guide
FX = ROOT / "tests/harness/fixtures"
def text(fx): return next(c["text"] for o in fx["output"] if o["type"] == "message" for c in o["content"] if c["type"] == "output_text")
def fake_chat(name):
    seen = []
    def chat(messages, **kw): seen.append(messages); return text(json.loads((FX / name).read_text()))
    chat.seen = seen; return chat
fails = []
def check(c, m): print(("PASS " if c else "FAIL ") + m); c or fails.append(m)
gen = json.loads(text(json.loads((FX / "generate.responses.json").read_text())))
with tempfile.TemporaryDirectory() as d:
    sp = pathlib.Path(d) / "spec.json"; sp.write_text(json.dumps(gen)); g = write_guide(gen, sp)
    v = subprocess.run([sys.executable, str(ROOT / "scripts/validate_spec.py"), str(sp)], capture_output=True, text=True)
    check(v.returncode == 0, f"generate fixture validates ({v.stdout.strip()[-80:]})")
    check("Agua" in g.read_text(), "GAME_GUIDE.md lists hazard")
r = playtest(gen); check(from_solver(r) is RunOutcome.STUCK, "generated spec is STUCK (river blocks column)")
ep = [{"iter": 0, "patch_summary": "moved goal", "outcome": "STUCK", "bugs": r["bugs"]}]
chat = fake_chat("patch.responses.json"); fixed = muse_fix(gen, r, ep, chat=chat)
check("moved goal" in chat.seen[0][0]["content"], "fixer prompt includes episode memory")
check(from_solver(playtest(fixed)) is RunOutcome.WIN, "patched spec is WIN")
print("replay:", "OK" if not fails else f"{len(fails)} FAIL"); sys.exit(1 if fails else 0)
