# core/highscore.py

## HighScoreManager

`class HighScoreManager`

Initializes the HighScoreManager instance with a file path configuration.

Creates the manager object, determines the highscore file location using default settings if not provided, sets up internal storage dictionaries for scores, and triggers an initial load from the persistent storage file to populate state upon construction.

:param filepath: The path to the highscore storage file, or None for default settings location.
:type filepath: str | Path | None

### __init__

`def __init__(self, filepath: str | Path | None=None) -> None`

### load

`def load(self) -> None`

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

### save

`def save(self) -> None`

Persists the current highscores data to the file path specified by self.filepath. This method ensures that the parent directory for the filepath exists, creating it if necessary before writing. It includes a check to prevent accidental overwriting of an existing non-empty file when the internal score set is empty, and handles all exceptions by logging errors without re-raising them. Serialization to JSON format and writing to disk occur within the try-except block using the logger module for status messages.

:param self: The instance object containing the filepath and scores attributes.
:returns: None after successfully saving the highscores or returning early if conditions prevent overwrite.

### get_score

`def get_score(self, game_name: str) -> int`

Returns the score for a specific game by resolving the value from the internal scores storage.

:param game_name: The identifier of the game used to look up the stored score.
:return: The integer score associated with the game, or zero if the game has no recorded score.

### get_best_run

`def get_best_run(self, game_name: str) -> dict`

Retrieves the best run data for a specific game from internal score records or calculates fallback values based on available information.

:param game_name: The unique identifier for the game to retrieve best run data for.
:return: A dictionary containing 'score', 'level', and 'time' keys representing the best run metrics or default calculations.

### get_runs

`def get_runs(self, game_name: str) -> list[dict]`

Retrieves the list of runs associated with the provided game identifier by querying the internal score storage dictionary. If the score for the game is stored as a dictionary containing a 'runs' key, the stored runs are returned. Otherwise, default run information structures are constructed using integer values present in the score entry and returned as a list.

:param game_name: The string name of the game to query.
:return: A list of dictionaries representing the run data for the specified game.

### submit_score

`def submit_score(self, game_name: str, score: int, level: int=1, time_played: float=0.0) -> bool`

Submits a game score and updates the player's record by tracking all-time highs and maintaining the top three run entries per game.

:param game_name: The name of the game to submit the score for.
:param score: The achieved score integer value for this run.
:param level: The current game level reached at the moment of scoring. Defaults to 1.
:param time_played: The time spent playing in minutes or seconds, rounded to one decimal place upon storage. Defaults to 0.0.
:return: True if the all-time best score was updated with this run; False otherwise.
