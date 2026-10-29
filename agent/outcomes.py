"""RunOutcome enum (T9). Every player report / summary uses exactly these values."""
from enum import Enum
class RunOutcome(str, Enum):
    WIN = "WIN"; LOSE = "LOSE"; STUCK = "STUCK"; CRASH = "CRASH"; TIMEOUT = "TIMEOUT"; INVALID = "INVALID"
def from_solver(r): return RunOutcome.WIN if r.get("winnable") else RunOutcome.STUCK
def from_browser(b):
    s = str(b.get("status", "")).lower()
    if b.get("won"): return RunOutcome.WIN
    if "lose" in s or "lost" in s or "hazard" in s: return RunOutcome.LOSE
    if "timeout" in s: return RunOutcome.TIMEOUT
    if "error" in s or "crash" in s: return RunOutcome.CRASH
    return RunOutcome.STUCK
