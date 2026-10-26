from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # ../
DATA_PATH = BASE_DIR / "data"
SETTINGS_FILE = DATA_PATH / "settings.json"
LOG_FILE = DATA_PATH / "pocket_games.log"
HIGHSCORE_FILE = DATA_PATH / "highscores.json"
TRANSLATIONS_FILE = DATA_PATH / "translations.json"
GAME_METADATA_FILE = DATA_PATH / "game_metadata.json"
TUNING_DIR = DATA_PATH / "tuning"
CYBER_FLIPPER_TUNING_FILE = TUNING_DIR / "cyber_flipper.json"


class Settings:
    """Application settings manager for user configuration persistence.

    Centralizes the storage and retrieval of user-configurable
    application settings, including audio controls, display
    preferences, and localization. Configuration values are
    persisted to a JSON file and restored during initialization,
    with default values applied when the file is absent or
    contains malformed data.

    :ivar sound_enabled: Indicates whether sound output is enabled.
    :ivar master_volume: Global volume level from 0.0 (muted) to
        1.0 (full).
    :ivar fullscreen: Indicates whether the application displays in
        fullscreen mode.
    :ivar language: Active language identifier for localization."""
    def __init__(self) -> None:
        self.sound_enabled: bool = True
        self.master_volume: float = 0.6
        self.fullscreen: bool = True
        self.language: str = "English"  # Default: English
        self.load()

    def load(self) -> None:
        """
        Load persisted application settings from the configuration file.

        Reads the JSON settings file and restores previously saved user
        preferences, including sound state, master volume level, display
        mode, and interface language. If the settings file does not exist,
        this method performs no action. On any parsing or I/O failure, the
        error is logged and the current in-memory values remain unchanged.

        :return:
        """
        if SETTINGS_FILE.exists():
            try:
                data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
                self.sound_enabled = data.get("sound_enabled", True)
                self.master_volume = data.get("master_volume", 0.8)
                self.fullscreen = data.get("fullscreen", True)
                self.language = data.get("language", "English")
            except Exception as e:  # noqa: BLE001
                from pocket_games.core.logger import logger
                logger.error(e)

    def save(self) -> None:
        """
        Save the current application settings to the settings file as a JSON document.

        The method serializes the active configuration values (sound enabled state,
        master volume, fullscreen flag, and language) into a JSON object and writes
        it to the settings file using UTF-8 encoding. If an error occurs during the
        write operation, the exception is caught and logged via the core logger
        rather than being propagated to the caller.

        :return: Nothing. This method has no meaningful return value.
        """
        data = {
            "sound_enabled": self.sound_enabled,
            "master_volume": self.master_volume,
            "fullscreen": self.fullscreen,
            "language": self.language
        }
        try:
            SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            from pocket_games.core.logger import logger
            logger.error(e)
