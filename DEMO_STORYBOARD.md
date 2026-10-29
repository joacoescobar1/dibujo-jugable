# DEMO STORYBOARD — Dibujo Jugable (3:00)

Basado en CONTEXT_FOR_MUSE.md §7 y el pitch de SUBMISSION.md. North-star: % de dibujos jugables y ganables sin edición humana.
Fallback offline: `game/demo.html` (timeline fail→fix→WIN) + `scripts/demo.sh`.

| t | Pantalla | VO (es) | EN cue |
|---|---|---|---|
| 0:00–0:10 | Mano de un nene dibujando con lápices: río, perro, casa de la abuela. | "Un nene dibujó esto. En un minuto va a ser un juego." | "A kid drew this. In a minute it's a game." |
| 0:10–0:25 | Foto con el celu + voz: "el perro tiene que llegar a la casa sin tocar el río". Transcripción en vivo. | "Le cuenta las reglas con la voz." | "He tells the rules out loud." |
| 0:25–0:45 | Máscaras SAM sobre cada trazo con labels; sprites limpios al lado del original (mismo trazo). | "SAM entiende hasta un dibujo a lápiz." | "SAM understands even a pencil sketch." |
| 0:45–1:00 | Muse escribe el GameSpec (JSON), carga el juego. **v1 rota**: el río corta todo el mapa. | "Primer intento: no se puede ganar." | "First try: unwinnable." |
| 1:00–1:20 | El agente prueba la ruta más corta y **choca en el tablero justo con el bug** (¡TE ATRAPÓ! 👾 / se cae al río / SIN SALIDA 🧱); marca roja 🐞 pulsante + tarjeta BugReport. Offline: `demo.html?iter=0&tour=1`. | "Nadie lo arregla a mano. El agente juega antes de entregarlo." | "No human fixes it. The agent plays before shipping." |
| 1:20–1:45 | En el tablero: fantasma + flecha 🔧 "lo corrí" / tablones de puente / puerta (diff spec k→k+1, `scripts/fix_marks.py`), oracle sellado ✔, timeline Play→Bug→Fix. | "Arreglo mínimo, respetando el dibujo." | "Minimal fix that respects the drawing." |
| 1:45–2:05 | El nene juega y gana; confetti, cinta ¡GANASTE! arriba con el recorrido dibujado y sus sprites a la vista. | "Y ahora sí: ganó." | "Now it's winnable — and he wins." |
| 2:05–2:35 | En vivo: dibujo nuevo del público → juego jugable. | "Un dibujo que nunca vio." | "A drawing it has never seen." |
| 2:35–2:50 | Slide métricas: first-try 0.48 (11/23) → after-loop 0.96 (22/23) (`evidence/eval.json` 2026-10-28 12:17 ART, offline/mock; reemplazar con números reales Meta), iters medianas, $/juego; modelos Meta + Muse Code. | "Del 50% al 95% de dibujos ganables, sin humanos." | "From 50% to 95% winnable drawings, no humans." |
| 2:50–3:00 | "Dibujá. Jugá. El agente lo prueba por vos." URL + QR. | "Dibujá. Jugá." | "Draw it. Play it. The agent tests it for you." |

Notas: solo dibujos, sin caras de chicos; voces de adultos o con consentimiento. Números de la slide son offline hasta que Meta desbloquee modelos.
