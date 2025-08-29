from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Tuple


class SessionStore:
    def __init__(self, path: Path = Path(".detector.session")):
        self.path = path

    def load(self) -> Optional[Tuple[str, str]]:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get("detectorId"), data.get("sessionToken")
        except Exception:
            return None

    def save(self, detector_id: str, session_token: str) -> None:
        payload = {"detectorId": detector_id, "sessionToken": session_token}
        self.path.write_text(json.dumps(payload), encoding="utf-8")


