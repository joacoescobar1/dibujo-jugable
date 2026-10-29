# Dibujo Jugable 🎨🕹️
Foto de un dibujo de un nene + 20–30 s de reglas por voz → juego HTML5 jugable. Un agente **construye → juega → arregla** solo hasta que el nivel sea ganable, y el loop de QA se ve en vivo (diferencial vs. "Kitchen Game" de Meta).

## Pipeline
1. `samples/` foto + audio → **Voice Transcribe** (reglas) + **SAM** (recorte de personajes/objetos) + **Muse Image** (fondo/limpieza de sprites).
2. el modelo Meta de razonamiento (Muse Spark series) arma `spec.json` (valida contra `specs/game-spec.schema.json`) y genera el nivel sobre `game/`.
3. `agent/playtest.py` juega vía state API (`window.__GAME__`), no píxeles; reporta si ganó/bug.
4. `agent/patch_loop.py` le pasa el reporte al modelo Meta, aplica patch, re-juega (máx N iteraciones). Log en `runs/`.

## Correr
```bash
cd /workspace/hackathon-meta/dibujo-jugable
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m playwright install chromium   # una vez
. .venv/bin/activate
./scripts/demo_offline.sh               # offline, sin key
python -m http.server -d game 8000       # jugar stub: flechas, llegar a la casa, evitar el agua
python agent/patch_loop.py --spec specs/example.spec.json
```
Credenciales sólo en `../.env` (nunca en código/git).

## Modelos Meta
Muse Spark (spec + código + fixes), SAM 3.1, Muse Image, Voice Transcribe.

## Demo offline (sin API)
`./scripts/demo_offline.sh` — nivel roto → jugador headless pierde → **mock patcher local** arregla → gana. Producción usa el patcher de **Meta Model API**. Evidencia en `runs/<ts>-mock/`.

## Judge demo (offline, 0 API) — un comando
```
scripts/serve_demo.sh 8000 --rebuild     # build (mock patcher, 0 Meta) + serve → http://localhost:8000/demo.html?iter=0&tour=1
```
(o `xdg-open game/demo.html`: file:// anda, todo embebido). Botón **▶ Modo juez** = recorrido solo, sin clicks:
1. **Intento #1 roto**: el agente prueba la ruta más corta (`agent/browser_playtest.optimistic`, el mismo plan que jugó Chromium) y **choca justo con el bug** en el tablero: el monstruo lo atrapa / se cae al río / queda sin salida contra el cerco. Marca roja pulsante 🐞 donde está el problema.
2. **Arreglo**: el tablero del intento #2 muestra qué cambió el fixer (fantasma + flecha 🔧 "lo corrí", puente, puerta). Las marcas salen de un diff de datos spec k → k+1 (`scripts/fix_marks.py`), no de texto.
3. **WIN**: el agente lo juega con el camino del solver; queda dibujado el recorrido y el cartel ¡GANASTE! es una cinta arriba → se sigue viendo el dibujo del nene vivo.

Chequeo: `tests/demo/test_demo_legibility.py` + `tests/demo/test_demo_labels.py` (Chromium; 5 dibujos rotos 02/04/08/11/12 — el default es `synthetic_12`, dibujo con trazo de nene; etiquetas sin pisarse, sin bicho fantasma en el sprite de la meta; falla en pantalla, marcas, % de tablero visible). Screenshots: `evidence/judge_demo_fail.png`, `evidence/judge_demo.png` (`scripts/shoot_judge_demo.py`). Otro dibujo: `.venv/bin/python scripts/build_judge_demo.py --sample samples/synthetic_08` (cerco).
