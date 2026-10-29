#!/usr/bin/env python3
"""Eval harness. Items = sample dirs (with spec.json) or *.spec.json files.
Offline: validate_spec + BFS solver (first-try), then mock patch loop result (after-loop) if available.
--mode muse: smoke /models first; if locked -> offline fallback (logged). Muse generation is a TODO post-unlock.
Writes runs/eval-<ts>/summary.json (+ evidence/eval.json copy)."""
import argparse, json, sys, pathlib, datetime, subprocess
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from solver_reachability import reachability
ap = argparse.ArgumentParser(); ap.add_argument("--samples", default="samples"); ap.add_argument("--max", type=int, default=20)
ap.add_argument("--mode", choices=["offline", "muse"], default="offline"); ap.add_argument("--include-specs", action=argparse.BooleanOptionalAction, default=True, help="also score specs/*.spec.json incl. broken example"); ap.add_argument("--no-generate", action="store_true", help="skip drawing->spec for samples without spec.json"); a = ap.parse_args()
mode, note = a.mode, None
if mode == "muse":
    from agent import meta_client as mc
    lm = mc.list_models()
    if not lm["count"]: mode, note = "offline", f"muse smoke failed (models={lm['count']}, http={lm.get('http_status')}) -> offline fallback"
    else: mode, note = "offline", "models listed but Muse generation not wired in eval yet -> offline"
sd = (ROOT / a.samples) if not pathlib.Path(a.samples).is_absolute() else pathlib.Path(a.samples)
items = sorted(p / "spec.json" for p in sd.glob("*/") if (p / "spec.json").exists()) + sorted(sd.glob("*.spec.json"))
pending = sorted(p for p in sd.glob("*/") if not (p / "spec.json").exists() and any(p.glob("drawing.*")))
if not items and not pending: items = sorted((ROOT / "specs").glob("*.spec.json")); note = (note or "") + f" | no specs in {sd}, using specs/"
if a.include_specs and sd.resolve() != (ROOT / "specs").resolve(): items += [f for f in sorted((ROOT / "specs").glob("*.spec.json")) if f not in items]
items = items[:a.max]; py = str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else sys.executable
ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]; out = ROOT / "runs" / f"eval-{ts}"; out.mkdir(parents=True)
rows = []
if pending and not a.no_generate:  # T3: drawing->spec via generate_from_drawing (offline placeholder, or muse w/ LOCKED fallback)
    for p in pending:
        img = next(p.glob("drawing.*")); o = out / "gen" / p.name / "spec.json"
        g = subprocess.run([py, str(ROOT / "scripts/generate_from_drawing.py"), "--image", str(img), "--mode", a.mode, "--out", str(o)], capture_output=True, text=True)
        if g.returncode == 0: items.append(o)
        else: rows.append({"item": str(p.relative_to(ROOT)), "status": "generation_failed", "detail": (g.stdout + g.stderr).strip()[-400:]})
    gen_note = f"generated {len(pending)} spec(s) from drawings via generate_from_drawing --mode {a.mode} (offline crude colour-vision, no model)"
    note = (note + " | " if note else "") + gen_note; pending = []
for f in items:
    v = subprocess.run([py, str(ROOT / "scripts/validate_spec.py"), str(f)], capture_output=True, text=True)
    row = {"item": str(f.relative_to(ROOT) if f.is_relative_to(ROOT) else f), "valid": v.returncode == 0}
    if not row["valid"]: row.update(status="invalid_spec", detail=v.stdout.strip()[-400:]); rows.append(row); continue
    spec = json.loads(f.read_text()); r1 = reachability(spec); row["first_try"] = r1
    if r1["win"] is False:
        try:
            from agent.mock_patcher import mock_fix as patch  # optional
            r2 = reachability(patch(spec, {"bugs": ["no path"]})); row["after_loop"] = {**r2, "patcher": "mock"}
        except Exception as e: row["after_loop"] = {"win": None, "placeholder": True, "note": f"loop not run here ({type(e).__name__}); use demo.sh"}
    else: row["after_loop"] = {"win": r1["win"], "note": "no loop needed"}
    row["status"] = "win_first_try" if r1["win"] else ("win_after_loop" if row["after_loop"].get("win") else "lose")
    rows.append(row)
for p in pending: rows.append({"item": str(p.relative_to(ROOT)), "status": "pending_generation", "detail": "drawing without spec; needs Muse (locked)"})
n = len([r for r in rows if "first_try" in r]) or 1
S = {"timestamp": datetime.datetime.now().astimezone().isoformat(), "mode_requested": a.mode, "mode_used": mode, "note": note, "items": len(rows),
     "first_try_win_rate": sum(bool(r.get("first_try", {}).get("win")) for r in rows) / n,
     "after_loop_win_rate": sum(bool(r.get("after_loop", {}).get("win")) for r in rows) / n, "live_meta_calls": 0, "per_item": rows}
(out / "summary.json").write_text(json.dumps(S, indent=2, ensure_ascii=False)); (ROOT / "evidence/eval.json").write_text(json.dumps(S, indent=2, ensure_ascii=False))
print(json.dumps({k: S[k] for k in ("mode_used", "note", "items", "first_try_win_rate", "after_loop_win_rate")}), "->", out.relative_to(ROOT))
