"""Shared Meta Muse client. Reads ../../.env; key never logged/printed.
CLI: python -m agent.meta_client models | ping MODEL [--dry] | segment IMAGE --nouns a,b
     | image_edit IMAGE --prompt "..." [--live] | transcribe AUDIO [--live]   (dry by default; live refuses unless model listed)
Fails closed: errors return {"ok": false, ...}; nothing is fabricated."""
import os, sys, json, pathlib, urllib.request, urllib.error
ENV = pathlib.Path(__file__).resolve().parents[2] / ".env"
def _load():
    if ENV.exists():
        for l in ENV.read_text().splitlines():
            if "=" in l and not l.startswith("#"):
                k, v = l.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"'))
def provider(): _load(); return os.environ.get("PROVIDER", "meta").lower()
def _key():
    _load(); return os.environ.get("BASETEN_API_KEY" if provider() == "baseten" else "META_API_KEY", "")
def base():
    _load()
    if provider() == "baseten": return os.environ.get("BASETEN_BASE_URL", "https://inference.baseten.co/v1")
    return os.environ.get("META_BASE_URL") or "https://api.meta.ai/v1"
def has_key(): return bool(_key())
def model():
    _load()
    if provider() == "baseten": return os.environ.get("BASETEN_MODEL", "meta-models/muse-spark-open-1026")
    return os.environ.get("META_DEFAULT_MODEL") or "muse-spark"
def client():
    from openai import OpenAI
    _load(); return OpenAI(base_url=base(), api_key=_key())
def log_usage(m, usage, note=""):
    """Append usage to runs/usage.jsonl and SPEND.md via scripts/log_usage.py (no key involved)."""
    import subprocess, datetime
    root = pathlib.Path(__file__).resolve().parents[1]; (root / "runs").mkdir(exist_ok=True)
    with open(root / "runs/usage.jsonl", "a") as f: f.write(json.dumps({"ts": datetime.datetime.now().isoformat(timespec="seconds"), "model": m, "usage": usage, "note": note}) + "\n")
    subprocess.run([sys.executable, str(root / "scripts/log_usage.py"), "-", "--model", m, "--note", note], input=json.dumps({"usage": usage}), text=True, capture_output=True)
def chat_live(messages, m=None, note="", timeout=300, **kw):
    """LIVE POST /chat/completions; logs usage. Returns {ok, content, usage, model} or {ok: False, error}."""
    import time, random
    m = m or model()
    for k in range(6):  # Meta entitlement flaps (404 model_not_found / disconnects seen 2026-10-28) -> backoff + retry
        r = _req("/chat/completions", {"model": m, "messages": messages, **kw}, timeout=timeout)
        if r["ok"] or r["http_status"] not in (None, 404, 429, 500, 502, 503): break
        time.sleep(min(60, 3 * 2 ** k) + random.random() * 2)
    d = r.get("data") or {}
    if not r["ok"]: return {"ok": False, "model": m, "http_status": r["http_status"], "error": r["error"]}
    u = d.get("usage") or {}; log_usage(m, u, note)
    return {"ok": True, "model": d.get("model", m), "content": d["choices"][0]["message"].get("content"), "usage": u}
def image_part(path):
    import base64, mimetypes
    f = pathlib.Path(path); ct = mimetypes.guess_type(str(f))[0] or "image/png"
    return {"type": "image_url", "image_url": {"url": f"data:{ct};base64," + base64.b64encode(f.read_bytes()).decode()}}
def parse_json(text):
    t = (text or "").strip()
    if "```" in t: t = t.split("```")[1].removeprefix("json").strip()
    i, j = t.find("{"), t.rfind("}"); return json.loads(t[i:j+1])
def chat(messages, **kw):
    """Live chat used by patch_loop muse_fix; logs usage. Raises on API error (fail closed)."""
    r = chat_live(messages, note=kw.pop("note", "chat"), **kw)
    if not r["ok"]: raise RuntimeError(f"Meta chat failed: {r.get('http_status')} {r.get('error')}")
    return r["content"]
def _req(path, body=None, timeout=30):
    key = _key()
    req = urllib.request.Request(base() + path, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "dibujo-jugable/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return {"ok": True, "http_status": r.status, "data": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "http_status": e.code, "error": e.read().decode(errors="replace")[:600].replace(key or "\0", "[REDACTED]")}
    except Exception as e:
        return {"ok": False, "http_status": None, "error": repr(e)[:400].replace(key or "\0", "[REDACTED]")}
def list_models():
    """GET /models (free). Returns {ok, count, models[]} — empty list is a valid answer (locked team)."""
    if not has_key(): return {"ok": False, "error": ("BASETEN_API_KEY" if provider() == "baseten" else "META_API_KEY") + " missing", "provider": provider(), "count": 0, "models": []}
    r = _req("/models")
    ids = [m.get("id") for m in (r.get("data") or {}).get("data", [])] if r["ok"] else []
    return {"ok": r["ok"], "http_status": r["http_status"], "count": len(ids), "models": ids, **({"error": r["error"]} if not r["ok"] else {})}
def responses_ping(m, dry=True):
    """POST /responses with tiny input. dry=True (default) sends nothing. Refuses live if model not listed."""
    if dry: return {"ok": None, "dry": True, "model": m, "would_post": base() + "/responses"}
    lm = list_models()
    if m not in lm["models"]: return {"ok": False, "model": m, "skipped": "model not in /models (fail closed, no spend)"}
    r = _req("/responses", {"model": m, "input": "OK"}, timeout=60)
    d = r.get("data") or {}
    return {"ok": r["ok"], "model": m, "http_status": r["http_status"], "response_model": d.get("model"), "usage": d.get("usage"), **({"error": r["error"]} if not r["ok"] else {})}
import re as _re
_BOX = _re.compile(r"<\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+);w=(\d+);h=(\d+)\|>")
def segment(image, nouns, m="sam-3.1"):
    """LIVE SAM 3.1 via POST /responses (input_image data URL + input_text noun). Returns boxes in source-pixel coords per noun.
    SAM also returns an RLE-ish mask string (format undocumented) -> kept raw in masks_raw_len; alpha is cut locally inside the box."""
    from PIL import Image
    f = pathlib.Path(image); W, H = Image.open(f).size; url = image_part(f)["image_url"]["url"]; out = {}
    for n in nouns:
        r = _req("/responses", {"model": m, "input": [{"role": "user", "content": [{"type": "input_image", "image_url": url}, {"type": "input_text", "text": n}]}]}, timeout=120)
        if not r["ok"]: out[n] = {"ok": False, "http_status": r["http_status"], "error": r["error"]}; continue
        txt = "".join(c.get("text", "") for o in r["data"].get("output", []) for c in o.get("content", []))
        boxes = [[int(x1) * W // int(w), int(y1) * H // int(h), int(x2) * W // int(w), int(y2) * H // int(h)] for x1, y1, x2, y2, w, h in _BOX.findall(txt)]
        out[n] = {"ok": True, "boxes": boxes, "masks_raw_len": len(txt), "response_id": r["data"].get("id")}
    return {"ok": any(v.get("ok") for v in out.values()), "model": m, "image": str(f), "size": [W, H], "nouns": out, "images_billed": len(nouns)}
segment_stub = segment
def _multipart(path, fields, files, timeout=120):
    """multipart/form-data POST. files: {name: pathlib.Path}. Key redacted from any error."""
    import uuid, mimetypes
    key = _key(); b = uuid.uuid4().hex; body = b""
    for k, v in fields.items(): body += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    for k, f in files.items():
        ct = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
        body += f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{f.name}\"\r\nContent-Type: {ct}\r\n\r\n".encode() + f.read_bytes() + b"\r\n"
    body += f"--{b}--\r\n".encode()
    req = urllib.request.Request(base() + path, data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={b}", "User-Agent": "dibujo-jugable/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return {"ok": True, "http_status": r.status, "data": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        return {"ok": False, "http_status": e.code, "error": e.read().decode(errors="replace")[:600].replace(key or "\0", "[REDACTED]")}
    except Exception as e:
        return {"ok": False, "http_status": None, "error": repr(e)[:400].replace(key or "\0", "[REDACTED]")}
def _gate(m, dry, would, extra):
    if dry: return {"ok": None, "dry": True, "model": m, "would_post": base() + would, **extra}
    lm = list_models()
    if m not in lm["models"]: return {"ok": False, "model": m, "locked": True, "skipped": f"LOCKED: {m} not in /models (count={lm['count']}); no spend", **extra}
    return None
def image_edit(image, prompt, m="muse-image-1.0", dry=True):
    """POST /images/edits (multipart: model, image, prompt). $0.01/img. Returns b64/url as given by API; nothing fabricated."""
    f = pathlib.Path(image); ex = {"image": str(f), "prompt": prompt}
    if not f.exists(): return {"ok": False, "error": f"image not found: {f}", **ex}
    g = _gate(m, dry, "/images/edits", ex)
    if g: return g
    r = _multipart("/images/edits", {"model": m, "prompt": prompt}, {"image": f}); d = r.get("data") or {}
    return {"ok": r["ok"], "model": m, "http_status": r["http_status"], "data": d.get("data"), "usage": d.get("usage"), **({"error": r["error"]} if not r["ok"] else {})}
def transcribe(audio, m="muse-voice-transcribe-1.0", language="es", dry=True):
    """POST /asr/transcribe (multipart: model, file, language). $0.18/hr."""
    f = pathlib.Path(audio); ex = {"audio": str(f), "language": language}
    if not f.exists(): return {"ok": False, "error": f"audio not found: {f}", **ex}
    g = _gate(m, dry, "/asr/transcribe", ex)
    if g: return g
    import wave
    try: sr = wave.open(str(f)).getframerate()
    except Exception: sr = 16000
    req = {"model": m, "language": language, "audioEncoding": "WAV", "sampleRate": sr}  # verified live 2026-10-28: multipart parts 'request' (JSON) + 'audio'
    r = _multipart("/asr/transcribe", {"request": json.dumps(req)}, {"audio": f}); d = r.get("data") or {}
    return {"ok": r["ok"], "model": m, "http_status": r["http_status"], "text": d.get("transcript", d.get("text")), "audio_ms": d.get("audioDurationMs"), "turns": d.get("turns"), "usage": d.get("usage"), **({"error": r["error"]} if not r["ok"] else {})}
if __name__ == "__main__":
    a = sys.argv[1:]; cmd = a[0] if a else "models"
    if cmd == "models": out = list_models()
    elif cmd == "ping": out = responses_ping(a[1] if len(a) > 1 else model(), dry="--live" not in a)
    elif cmd in ("segment", "sam"): out = segment(a[1] if len(a) > 1 else None, (a[a.index("--nouns")+1].split(",") if "--nouns" in a else []))
    elif cmd in ("image_edit", "image-edit"): out = image_edit(a[1] if len(a) > 1 else "", a[a.index("--prompt")+1] if "--prompt" in a else "", dry="--live" not in a)
    elif cmd == "transcribe": out = transcribe(a[1] if len(a) > 1 else "", dry="--live" not in a)
    else: print(__doc__); sys.exit(2)
    print(json.dumps(out, indent=2, ensure_ascii=False)); sys.exit(0 if out.get("ok") is not False or cmd == "models" and has_key() else 1)
