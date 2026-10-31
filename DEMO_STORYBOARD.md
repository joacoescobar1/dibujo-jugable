# DEMO STORYBOARD — Dibujo Jugable (3:00)

Based on the pitch in SUBMISSION.md. North-star: % of drawings that are playable and winnable with no human edits.
Offline fallback: `game/demo.html` (fail→fix→WIN timeline) + `scripts/demo.sh`.

| t | Screen | Voice-over |
|---|---|---|
| 0:00–0:10 | A kid's hand drawing with colored pencils: river, dog, grandma's house. | "A kid drew this. In a minute it's a game." |
| 0:10–0:25 | Phone photo + voice: "the dog has to reach the house without touching the river". Live transcription. | "He tells the rules out loud." |
| 0:25–0:45 | SAM masks over each stroke with labels; clean sprites next to the original (same stroke). | "SAM understands even a pencil sketch." |
| 0:45–1:00 | Muse Spark writes the GameSpec (JSON), loads the game. **v1 broken**: the river cuts across the whole map. | "First try: unwinnable." |
| 1:00–1:20 | The agent tries the shortest route and **hits the bug on the board** (CAUGHT! 👾 / falls in the river / NO WAY OUT 🧱); pulsing red 🐞 mark + BugReport card. Offline: `demo.html?iter=0&tour=1`. | "No human fixes it. The agent plays before shipping." |
| 1:20–1:45 | On the board: ghost + 🔧 arrow "moved it" / bridge planks / door (spec diff k→k+1, `scripts/fix_marks.py`), sealed oracle ✔, Play→Bug→Fix timeline. | "Minimal fix that respects the drawing." |
| 1:45–2:05 | The kid plays and wins; confetti, YOU WIN! ribbon at the top with the route drawn and the sprites visible. | "Now it's winnable — and he wins." |
| 2:05–2:35 | Live: a new drawing from the audience → playable game. | "A drawing it has never seen." |
| 2:35–2:50 | Metrics slide: first-try 0.48 (11/23) → after-loop 0.96 (22/23) (`evidence/eval.json`, offline/mock), median iterations, $/game; Meta models + Muse Code. | "From 50% to 95% winnable drawings, no humans." |
| 2:50–3:00 | "Draw it. Play it. The agent tests it for you." URL + QR. | "Draw it. Play it." |

Notes: drawings only, no children's faces; adult voices or with consent.
