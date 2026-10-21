from __future__ import annotations

import json
from pathlib import Path

from pocket_games.core.logger import logger

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "data/settings.json"


class Settings:
    def __init__(self) -> None:
        self.sound_enabled: bool = True
        self.master_volume: float = 0.6
        self.fullscreen: bool = True
        self.language: str = "English"  # Default: English
        self.load()

    def load(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                self.sound_enabled = data.get("sound_enabled", True)
                self.master_volume = data.get("master_volume", 0.8)
                self.fullscreen = data.get("fullscreen", True)
                self.language = data.get("language", "English")
            except Exception as e:  # noqa: BLE001
                logger.error(e)

    def save(self) -> None:
        data = {
            "sound_enabled": self.sound_enabled,
            "master_volume": self.master_volume,
            "fullscreen": self.fullscreen,
            "language": self.language
        }
        try:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            logger.error(e)
