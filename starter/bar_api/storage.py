"""JSON-file persistence for one teaching server process; no database required."""
import json
from pathlib import Path
from threading import RLock

SEED = Path(__file__).resolve().parents[1] / "seed.json"

class JsonStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(json.loads(SEED.read_text(encoding="utf-8")))

    def load(self) -> dict:
        # A damaged file is a setup error: never silently replace existing work.
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict) -> None:
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
