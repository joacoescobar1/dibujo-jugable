# Dibujo Jugable — Submission

**Deadline:** 2026-11-04 21:00 ET = **23:00 ART**. Track 1 (indie). Requisitos: repo GitHub público, video ≤3 min, teammates aceptados en Devpost.

**Tagline:** A kid's paper drawing becomes a level that is *proven* winnable — Meta models build it, an agent plays it, fixes it, replays.

## Cómo juegan los jueces (offline, sin API key)
- `git clone` → abrir `game/gallery.html` (file:// funciona) → 21 mundos jugables, cada uno con 3 escenas → ending.
- Demo del loop fail→fix→win: `game/demo.html` (botón **Modo juez**).
- Repo público: https://github.com/joacoescobar1/dibujo-jugable
- Online: GitHub Pages https://joacoescobar1.github.io/dibujo-jugable/game/gallery.html (activado 2026-10-29, deploy desde `main` `/`)
- Local (sin internet): `scripts/serve_demo.sh 8000` y abrir `http://localhost:8000/gallery.html` o `/demo.html`; también `python3 -m http.server 8000 -d game`. Abrir `game/gallery.html` directo con file:// también funciona.

## Evidencia
`evidence/eval.json` (win rates), `evidence/judge_demo.png`, `evidence/oracle.sha256` (checker sellado), `runs/` (trazas), `SPEND.md`.

**EN (short):** A kid draws on paper; Meta models turn the drawing into a playable level, then an agent *plays* it, sees it fail, patches it, and replays until it's winnable. Unlike Kitchen Game (prompt → game, no proof it's beatable), every level we ship comes with a verified win trace.

## Pitch (rioplatense)
Un nene dibuja un mapa con lápices: el río, el perro, la casa de la abuela. Le saca una foto y en segundos lo está jugando. La diferencia con Kitchen Game: ellos generan un juego desde un prompt y confían en que funcione; nosotros **jugamos el nivel antes de entregarlo**. Si el dibujo tiene un río que corta todo el mapa o un cerco alrededor de la meta, el agente lo detecta jugando, propone un arreglo mínimo (un puente, abrir una pared) respetando el dibujo, y vuelve a jugar. Se ve en pantalla: intento roto → arreglo → WIN.



## North-star metric
**% de dibujos que terminan jugables y ganables sin edición humana** (after-loop win rate), junto con first-try win rate.
Hoy (offline, mock, sin Meta; `evidence/eval.json` 2026-10-28 12:17 ART): first-try 0.48 (11/23) → after-loop 0.96 (22/23); el ítem nuevo synthetic_12 entra roto y sale ganable (único lose: `survive-trap`, imposible por diseño).

## Cómo correr el demo
- `xdg-open game/demo.html` (file:// anda, screenshots embebidos), o
- `scripts/serve_demo.sh 8000 [--rebuild]` → http://127.0.0.1:8000/demo.html (`?iter=0` = intento roto, `?iter=0&tour=1` o botón **Modo juez** = recorrido automático fail→fix→win)
  - En el tablero: el agente choca con el bug (🐞), se ve qué cambió el arreglo (🔧 flecha/puente/puerta) y el WIN deja el dibujo visible (cinta, no cortina). Guardia: `tests/demo/test_demo_legibility.py`.
- Reconstruir: `.venv/bin/python scripts/build_judge_demo.py` (default `samples/synthetic_12`: dibujo sintético con trazo de nene — cohete, piedras, monstruo violeta sobre la estrella — generado por `scripts/make_kid_sample.py`; `--sample samples/synthetic_11` = misma historia en formas geométricas; `--sample samples/synthetic_08` = cerco) + `scripts/shoot_judge_demo.py` → evidence/judge_demo.png
- Pipeline offline completo: `scripts/demo.sh`; estado rápido: `scripts/morning_status.sh`

## Modelos Meta (API unlocked 2026-10-28 vía egress Rosario)
- **Muse Spark (Meta Model API, Responses)**: visión del dibujo → GameSpec JSON + patches del loop.
- **SAM**: segmentar trazos (río, paredes, personajes).
- **Voice/transcribe**: el nene narra las reglas ("si te toca el perro perdés").
- **Image edit**: sprites a partir del trazo original.
- **Muse Code**: desarrollo del harness.

## Spend policy
$0 hasta unlock. Después: smoke primero, loops con tope por corrida, todo logueado en `SPEND.md` vía `scripts/log_usage.py`. Oracle de verificación sellado (`evidence/oracle.sha256`) para que el modelo no pueda "ganar" editando el checker.

## Links
[CONTEXT_FOR_MUSE.md](CONTEXT_FOR_MUSE.md) · [PROGRESS.md](PROGRESS.md) · [SPEND.md](SPEND.md) · [scripts/parity_check.md](scripts/parity_check.md)
