from __future__ import annotations
import json
from pathlib import Path

HIGHSCORE_FILE = Path("highscores.json")

class HighScoreManager:
    def __init__(self) -> None:
        self.scores: dict[str, int] = {}
        self.load()

    def load(self) -> None:
        if HIGHSCORE_FILE.exists():
            try:
                self.scores = json.loads(HIGHSCORE_FILE.read_text())
            except Exception:
                self.scores = {}

    def save(self) -> None:
        try:
            HIGHSCORE_FILE.write_text(json.dumps(self.scores, indent=2))
        except Exception:
            pass

    def get_score(self, game_name: str) -> int:
        return self.scores.get(game_name, 0)

    def submit_score(self, game_name: str, score: int) -> bool:
        current = self.get_score(game_name)
        if score > current:
            self.scores[game_name] = score
            self.save()
            return True
        return False
