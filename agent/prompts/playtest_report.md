# playtest_report — turn a headless run into a bug report
Input: spec.json, player trace (status, steps, events, last position), screenshot.
Output JSON: {"verdict":"WIN|FAIL","failure":"<one sentence, concrete: what blocked the player and where (x,y)>","cause":"layout|rule|engine|spec","evidence":["event ids / coords"],"suggested_fix":"<smallest change that keeps the kid's intent>"}
Be concrete; never say "the level is hard". One root cause, the worst one.
