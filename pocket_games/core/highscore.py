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
        self.scores: dict[str, dict | int] = {}
        self.load()

    def load(self) -> None:
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
            except Exception as e:
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
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Highscores: {e}", exc_info=True)

    def get_score(self, game_name: str) -> int:
        entry = self.scores.get(game_name, 0)
        if isinstance(entry, dict):
            return entry.get("all_time", 0)
        return int(entry)

    def get_best_run(self, game_name: str) -> dict:
        entry = self.scores.get(game_name, {})
        if isinstance(entry, dict):
            return entry.get("best_run", {"score": self.get_score(game_name), "level": 1, "time": 0.0})
        return {"score": int(entry), "level": 1, "time": 0.0}

    def get_runs(self, game_name: str) -> list[dict]:
        entry = self.scores.get(game_name, {})
        if isinstance(entry, dict):
            return entry.get("runs", [])
        return [{"score": int(entry), "level": 1, "time": 0.0}]

    def submit_score(self, game_name: str, score: int, level: int = 1, time_played: float = 0.0) -> bool:
        if game_name not in self.scores or not isinstance(self.scores[game_name], dict):
            self.scores[game_name] = {"all_time": score, "best_run": {"score": score, "level": level, "time": time_played}, "runs": []}

        entry = self.scores[game_name]
        current_best = entry.get("all_time", 0)

        runs = entry.get("runs", [])

        # Verhindere Duplikate: Aktualisiere bestehenden 0.0s-Eintrag mit demselben Score statt einen neuen hinzuzufügen
        if runs and runs[0]["score"] == score and runs[0]["time"] == 0.0 and time_played > 0.0:
            runs[0]["level"] = level
            runs[0]["time"] = round(time_played, 1)
        elif runs and runs[0]["score"] == score and runs[0]["level"] == level:
            if time_played > runs[0]["time"]:
                runs[0]["time"] = round(time_played, 1)
        else:
            new_run = {
                "score": score,
                "level": level,
                "time": round(time_played, 1)
            }
            runs.insert(0, new_run)
            entry["runs"] = runs[:3]  # Maximal die letzten 3 Durchläufe speichern

        updated = False
        if score >= current_best:
            entry["all_time"] = score
            entry["best_run"] = {"score": score, "level": level, "time": round(time_played, 1)}
            updated = True

        self.save()
        return updated
