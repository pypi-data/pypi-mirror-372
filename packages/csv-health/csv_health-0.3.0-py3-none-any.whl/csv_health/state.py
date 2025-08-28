from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
import json
import os
import hashlib
import shutil
import sys


def default_home() -> Path:
    # Хранилище внутри активного интерпретатора/venv
    return Path(sys.prefix) / "var" / "csv_health"


def resolve_home() -> Path:
    custom = os.environ.get("CSV_HEALTH_HOME")
    return Path(custom).expanduser() if custom else default_home()


@dataclass
class State:
    original_path: str
    copy_path: str
    sha256: str
    last_audit_json: str | None = None
    last_audit_text: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StateManager:
    def __init__(self, home: Path | None = None) -> None:
        self.home = Path(home) if home else resolve_home()
        self.state_path = self.home / "state.json"
        self.copy_path = self.home / "last_input.csv"
        self.logs_dir = self.home / "logs"
        self.processed_dir = self.home / "processed"
        self.home.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _sha256_of_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def _write_state(self, state: State) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def write_copy_and_state(self, original: Path) -> State:
        shutil.copyfile(original, self.copy_path)
        sha = self._sha256_of_file(self.copy_path)
        state = State(str(original), str(self.copy_path), sha)
        self._write_state(state)
        return state

    def enhance_with_audit_paths(self, state: State, json_path: Path | None, text_path: Path | None) -> State:
        if json_path:
            state.last_audit_json = str(json_path)
        if text_path:
            state.last_audit_text = str(text_path)
        self._write_state(state)
        return state

    def read(self) -> Optional[State]:
        if not self.state_path.exists():
            return None
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return State(**data)
        except Exception:
            return None

    def clear(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()
        if self.copy_path.exists():
            self.copy_path.unlink()
