"""Drawing+voice -> spec.json (Muse) -> game/spec.json. TODO D2: SAM sprites, Muse Image background, Voice Transcribe."""
import argparse, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
GAME = pathlib.Path(__file__).resolve().parents[1] / "game"
SCHEMA = pathlib.Path(__file__).resolve().parents[1] / "specs/game-spec.schema.json"
def spec_from_inputs(transcript, drawing_desc=""):
    from meta_client import chat
    p = f"Devolvé SOLO JSON válido contra este schema:\n{SCHEMA.read_text()}\nReglas por voz: {transcript}\nDibujo: {drawing_desc}\nAsegurá que el nivel sea ganable."
    return json.loads(chat([{"role": "user", "content": p}], response_format={"type": "json_object"}))
if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--spec"); a.add_argument("--transcript"); a.add_argument("--drawing", default="")
    o = a.parse_args()
    spec = json.loads(pathlib.Path(o.spec).read_text()) if o.spec else spec_from_inputs(o.transcript, o.drawing)
    (GAME / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False)); print("wrote", GAME / "spec.json")
