from __future__ import annotations

import json
from pathlib import Path

from pocket_games.core.logger import logger


class HighScoreManager:
    def __init__(self, filepath: str | Path | None = None) -> None:
        if filepath is None:
            from pocket_games.core.settings import HIGHSCORE_FILE
            filepath = HIGHSCORE_FILE
        self.filepath = Path(filepath)
        self.scores: dict[str, int] = {}
        self.load()

    def load(self) -> None:
        loaded_data = self._read_json_file(self.filepath)

        if loaded_data and isinstance(loaded_data, dict):
            self.scores.update(loaded_data)
            logger.info(
                f"Highscores erfolgreich geladen ({len(self.scores)} Einträge)."
            )
        else:
            self.filepath.write_text(json.dumps(self.scores), encoding="utf-8")

    def _read_json_file(self, path: Path) -> dict[str, int]:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    data = json.loads(content)
                    if isinstance(data, dict):
                        return data
            except Exception as e:  # noqa: BLE001
                logger.error(f"Fehler beim Lesen von {path}: {e}")
        return {}

    def save(self) -> None:
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            if not self.scores and self.filepath.exists():
                existing = self._read_json_file(self.filepath)
                if existing:
                    logger.warning(
                        "WARNUNG: Leeres Highscore-Set im RAM erkannt, überschreibe bestehende Datei nicht!"
                    )
                    return

            json_data = json.dumps(self.scores, indent=4)
            self.filepath.write_text(json_data, encoding="utf-8")
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
