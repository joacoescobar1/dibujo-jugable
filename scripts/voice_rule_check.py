"""Voice-rule QA: the transcript says the butterfly must carry ALL kids; a spec that wins on reach_goal while kids stay optional betrays the rule.
Returns a report the Muse fixer consumes (same shape as playtest bugs)."""
import json, re, sys
def check(spec):
    t = spec.get("source", {}).get("voice_transcript", "").lower()
    need = bool(re.search(r"\b(todos|tres|3)\b", t)) and ("nene" in t or "chic" in t)
    wc = spec["win_condition"]["type"]; kids = [g for g in spec.get("goals", []) if "nen" in (g.get("label", "") + g["id"]).lower()]
    bugs = [] if (not need or (wc == "collect_all" and len(kids) >= 3)) else [{"kind": "voice_rule_violated", "detail": f"La voz dice que la mariposa junta a los 3 nenes antes de volar, pero win_condition={wc} y solo {len(kids)} nenes son goals: la mariposa puede irse sola. Hacé que los 3 nenes sean goals (ids nene_*) con win_condition collect_all; el sol queda como decorado (characters role=friend no se usa para nenes)."}]
    return {"winnable": False if bugs else True, "bugs": bugs, "steps": 0}
if __name__ == "__main__": print(json.dumps(check(json.load(open(sys.argv[1]))), ensure_ascii=False, indent=1))
