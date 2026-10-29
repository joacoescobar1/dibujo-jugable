# critic — is this level demo-worthy?
Input: original drawing + transcript, final spec, winning run summary + screenshot.
Score 1–5 each: fidelity (looks like the drawing), rules (kid's rules respected), fun (non-trivial path, >10 steps), clarity (a judge understands in 5 s).
Output JSON: {"scores":{...},"ship":true|false,"top_issue":"...","next_action":"..."}. ship=false if any score < 3. Be harsh; this is for a hackathon jury.
