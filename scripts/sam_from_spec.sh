#!/usr/bin/env bash
# For each Muse-generated spec: Spark 1.3 turns entity labels into English SAM nouns -> sam_cutouts (+3 Muse Image cleanups).
cd "$(dirname "$0")/.."
for s in runs/muse_gen/synthetic_*.spec.json; do n=$(basename $s .spec.json)
  nouns=$(.venv/bin/python - "$s" <<'PY'
import sys,json; sys.path.insert(0,'agent'); import meta_client as mc
s=json.load(open(sys.argv[1])); labs=[e.get('label',e['id']) for e in [s['player']]+s.get('goals',[])+s.get('characters',[])+s.get('hazards',[])]+(['rock'] if s.get('walls') else [])
r=mc.chat_live([{"role":"user","content":"Translate each to ONE short English noun for an image segmenter, comma-separated, nothing else: "+", ".join(labs)}],m="muse-spark-1.3",note="sam nouns "+sys.argv[1].split('/')[-1],max_tokens=2000)
print(",".join(dict.fromkeys(w.strip().lower() for w in (r.get('content') or 'thing').split(',') if w.strip())))
PY
)
  echo "$n nouns=$nouns"; .venv/bin/python scripts/sam_cutouts.py samples/$n/drawing.png --nouns "$nouns" --out runs/sam_$n --clean 3 2>&1 | head -c 400; echo
done
