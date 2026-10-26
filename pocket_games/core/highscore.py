from __future__ import annotations

import json
from pathlib import Path

from pocket_games.core.logger import logger


class HighScoreManager:
    """
    Initializes the HighScoreManager instance with a file path configuration.

    Creates the manager object, determines the highscore file location using default settings if not provided, sets up internal storage dictionaries for scores, and triggers an initial load from the persistent storage file to populate state upon construction.

    :param filepath: The path to the highscore storage file, or None for default settings location.
    :type filepath: str | Path | None
    """
    def __init__(self, filepath: str | Path | None = None) -> None:
        if filepath is None:
            from pocket_games.core.settings import HIGHSCORE_FILE
            filepath = HIGHSCORE_FILE
        self.filepath = Path(filepath)
        self.scores: dict[str, dict | int] = {}
        self.load()

    def load(self) -> None:
        """
        Load and parse highscore data from the JSON storage file,
        normalizing each entry into a consistent structure containing
        all-time score, best run details, and a list of runs.

        If the loaded data is a valid dictionary, each key-value pair is
        processed: integer values are converted into a full score entry,
        dictionary values are validated to ensure a best_run key exists
        and populated from runs or all_time if missing, and any other
        values are replaced with a default empty score entry. If no valid
        data is found, the current in-memory scores are serialized and
        written back to the file to initialize it.

        :return: None
        """
        loaded_data = self._read_json_file(self.filepath)

        if loaded_data and isinstance(loaded_data, dict):
            for k, v in loaded_data.items():
                if isinstance(v, int):
                    self.scores[k] = {
                        "all_time": v,
                        "best_run": {"score": v, "level": 1, "time": 0.0},
                        "runs": []
                    }
                elif isinstance(v, dict):
                    if "best_run" not in v:
                        runs = v.get("runs", [])
                        v["best_run"] = max(runs, key=lambda r: r.get("score", 0)) if runs else {"score": v.get("all_time", 0), "level": 1, "time": 0.0}
                    self.scores[k] = v
                else:
                    self.scores[k] = {"all_time": 0, "best_run": {"score": 0, "level": 1, "time": 0.0}, "runs": []}
            logger.info(
                f"Highscores erfolgreich geladen ({len(self.scores)} Einträge)."
            )
        else:
            self.filepath.write_text(json.dumps(self.scores), encoding="utf-8")

    def _read_json_file(self, path: Path) -> dict:
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
        """
        Persists the current highscores data to the file path specified by self.filepath. This method ensures that the parent directory for the filepath exists, creating it if necessary before writing. It includes a check to prevent accidental overwriting of an existing non-empty file when the internal score set is empty, and handles all exceptions by logging errors without re-raising them. Serialization to JSON format and writing to disk occur within the try-except block using the logger module for status messages.

        :param self: The instance object containing the filepath and scores attributes.
        :returns: None after successfully saving the highscores or returning early if conditions prevent overwrite.
        """
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
        """
        Returns the score for a specific game by resolving the value from the internal scores storage.

        :param game_name: The identifier of the game used to look up the stored score.
        :return: The integer score associated with the game, or zero if the game has no recorded score.
        """
        entry = self.scores.get(game_name, 0)
        if isinstance(entry, dict):
            return entry.get("all_time", 0)
        return int(entry)

    def get_best_run(self, game_name: str) -> dict:
        """
        Retrieves the best run data for a specific game from internal score records or calculates fallback values based on available information.

        :param game_name: The unique identifier for the game to retrieve best run data for.
        :return: A dictionary containing 'score', 'level', and 'time' keys representing the best run metrics or default calculations.

        """
        entry = self.scores.get(game_name, {})
        if isinstance(entry, dict):
            return entry.get("best_run", {"score": self.get_score(game_name), "level": 1, "time": 0.0})
        return {"score": int(entry), "level": 1, "time": 0.0}

    def get_runs(self, game_name: str) -> list[dict]:
        """
        Retrieves the list of runs associated with the provided game identifier by querying the internal score storage dictionary. If the score for the game is stored as a dictionary containing a 'runs' key, the stored runs are returned. Otherwise, default run information structures are constructed using integer values present in the score entry and returned as a list.

        :param game_name: The string name of the game to query.
        :return: A list of dictionaries representing the run data for the specified game.
        """
        entry = self.scores.get(game_name, {})
        if isinstance(entry, dict):
            return entry.get("runs", [])
        return [{"score": int(entry), "level": 1, "time": 0.0}]

    def submit_score(self, game_name: str, score: int, level: int = 1, time_played: float = 0.0) -> bool:
        """
        Submits a game score and updates the player's record by tracking all-time highs and maintaining the top three run entries per game.

        :param game_name: The name of the game to submit the score for.
        :param score: The achieved score integer value for this run.
        :param level: The current game level reached at the moment of scoring. Defaults to 1.
        :param time_played: The time spent playing in minutes or seconds, rounded to one decimal place upon storage. Defaults to 0.0.
        :return: True if the all-time best score was updated with this run; False otherwise.

        """
        if game_name not in self.scores or not isinstance(self.scores[game_name], dict):
            self.scores[game_name] = {"all_time": score, "best_run": {"score": score, "level": level, "time": time_played}, "runs": []}

        entry = self.scores[game_name]
        current_best = entry.get("all_time", 0)

        runs = entry.get("runs", [])
        new_run = {
            "score": score,
            "level": level,
            "time": round(time_played, 1)
        }
        runs.append(new_run)
        runs = sorted(runs, key=lambda r: (r.get("score", 0), -r.get("time", 0.0)), reverse=True)
        entry["runs"] = runs[:3]

        updated = False
        if score >= current_best:
            entry["all_time"] = score
            entry["best_run"] = {"score": score, "level": level, "time": round(time_played, 1)}
            updated = True

        self.save()
        return updated
