from __future__ import annotations

import json
from pathlib import Path

from pocket_games.core.logger import logger

BASE_DIR = Path(__file__).resolve().parent.parent
HIGHSCORE_FILE = BASE_DIR / "data/highscores.json"


class HighScoreManager:
    def __init__(self, filepath: str | Path = HIGHSCORE_FILE) -> None:
        self.filepath = Path(filepath)
        self.scores: dict[str, int] = {}
        self.load()

    def load(self) -> None:
        if self.filepath.exists():
            try:
                content = self.filepath.read_text(encoding="utf-8").strip()
                if content:
                    loaded_data = json.loads(content)
                    if isinstance(loaded_data, dict):
                        self.scores.update(loaded_data)
                        logger.info(f"Highscores erfolgreich geladen aus {self.filepath}")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Fehler beim Laden der Highscores: {e}", exc_info=True)

    def save(self) -> None:
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            if not self.scores and self.filepath.exists():
                existing_content = self.filepath.read_text(encoding="utf-8").strip()
                if existing_content and existing_content != "{}":
                    logger.warning("Warnung: Leeres Highscore-Dictionary im Speicher erkannt, überschreibe Datei nicht!")
                    return
            self.filepath.write_text(json.dumps(self.scores, indent=4), encoding="utf-8")
            logger.info("Highscores erfolgreich gespeichert.")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Fehler beim Speichern der Highscores: {e}", exc_info=True)

    def get_score(self, game_name: str) -> int:
        return self.scores.get(game_name, 0)

    def submit_score(self, game_name: str, score: int) -> bool:
        current_best = self.scores.get(game_name, 0)
        if score > current_best:
            self.scores[game_name] = score
            self.save()
            return True
        return False
