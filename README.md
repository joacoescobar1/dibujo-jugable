# Dibujo Jugable 🎨🕹️
*"Playable Drawing"* — a photo of a kid's drawing + 20–30 s of spoken rules → a playable HTML5 game. An agent **builds → plays → fixes** the level on its own until it is winnable, and the QA loop is visible live (our differentiator vs. Meta's "Kitchen Game").

## ▶ Play now (no install, no API key)
- **Online:** https://joacoescobar1.github.io/dibujo-jugable/game/gallery.html — pick a world and press **Play**.
- **Offline:** clone the repo and open `game/gallery.html` (works over `file://`).
- UI is in **English by default**; add `?lang=es` for Spanish.
- Fail → fix → win loop demo: `game/demo.html` (press **▶ Judge mode**).

## Pipeline
1. `samples/` photo + audio → **Voice Transcribe** (rules) + **SAM** (cut out characters/objects) + **Muse Image** (background / sprite cleanup).
2. Meta's reasoning model (Muse Spark series) builds `spec.json` (validated against `specs/game-spec.schema.json`) and generates the level on top of `game/`.
3. `agent/playtest.py` plays through the state API (`window.__GAME__`), not pixels; it reports win/bug.
4. `agent/patch_loop.py` sends the report to the Meta model, applies the patch, and replays (up to N iterations). Logs go to `runs/`.

## Run
```bash
# from the repo root
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m playwright install chromium   # once
. .venv/bin/activate
./scripts/demo_offline.sh               # offline, no key
python -m http.server -d game 8000       # play the stub: arrow keys, reach the house, avoid the water
python agent/patch_loop.py --spec specs/example.spec.json
```
Credentials live only in `../.env` (never in code/git). See `.env.example`.

## Meta models
Muse Spark (spec + code + fixes), SAM 3.1, Muse Image, Voice Transcribe.

## Offline demo (no API)
`./scripts/demo_offline.sh` — broken level → headless player loses → **local mock patcher** fixes it → wins. Production uses the **Meta Model API** patcher. Evidence in `runs/<ts>-mock/`.

## Judge demo (offline, 0 API) — one command
```
scripts/serve_demo.sh 8000 --rebuild     # build (mock patcher, 0 Meta) + serve → http://localhost:8000/demo.html?iter=0&tour=1
```
(or `xdg-open game/demo.html`: `file://` works, everything is embedded). The **▶ Judge mode** button runs a hands-free tour:
1. **Attempt #1, broken**: the agent tries the shortest route (`agent/browser_playtest.optimistic`, the same plan Chromium played) and **hits the bug** on the board: the monster catches it / it falls into the river / it is stuck against the fence. A pulsing red 🐞 marks the problem.
2. **Fix**: the attempt #2 board shows what the fixer changed (ghost + 🔧 arrow "moved it", bridge, door). The marks come from a data diff of spec k → k+1 (`scripts/fix_marks.py`), not from text.
3. **WIN**: the agent plays the solver's path; the route stays drawn and the win banner is a ribbon at the top, so the kid's drawing stays visible.

Checks: `tests/demo/test_demo_legibility.py` + `tests/demo/test_demo_labels.py` (Chromium; 5 broken drawings 02/04/08/11/12 — default is `synthetic_12`, a kid-style drawing; non-overlapping labels, no ghost creature on the goal sprite; on-screen failure, marks, % of board visible). Screenshots: `evidence/judge_demo_fail.png`, `evidence/judge_demo.png` (`scripts/shoot_judge_demo.py`). Another drawing: `.venv/bin/python scripts/build_judge_demo.py --sample samples/synthetic_08` (fence).
