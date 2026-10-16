from __future__ import annotations
import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")

class Settings:
    def __init__(self) -> None:
        self.sound_enabled: bool = True
        self.master_volume: float = 0.8
        self.fullscreen: bool = True
        self.load()

    def load(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text())
                self.sound_enabled = data.get("sound_enabled", True)
                self.master_volume = data.get("master_volume", 0.8)
                self.fullscreen = data.get("fullscreen", True)
            except Exception:
                pass

    def save(self) -> None:
        data = {
            "sound_enabled": self.sound_enabled,
            "master_volume": self.master_volume,
            "fullscreen": self.fullscreen
        }
        try:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
