from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str = "RetroPocketGames", log_filename: str | None = None ) -> logging.Logger:
    """
    Returns a configured logging.Logger instance associated with the provided name and handles configuration of file and stream output paths. If a logger exists with the given name and already possesses handlers, the existing instance is returned immediately. Otherwise, a new logger is initialized at DEBUG level for files and INFO level for streams. The default log file location is resolved from global application settings when the filename argument is omitted.

    :param name: Unique identifier string for the logger instance, typically following Python module naming conventions to prevent conflicts within logging systems.
    :param log_filename: Optional path string for the log file output location. Defaults to a value resolved from application core settings if this parameter is not specified.
    :return: A configured `logging.Logger` object instance with attached DEBUG level file handler and INFO level stream handler.
    :raises OSError: If the operating system fails to create the log directory or open the file due to permission issues or disk space constraints."""
    if log_filename is None:
        from pocket_games.core.settings import LOG_FILE
        log_filename = str(LOG_FILE.resolve())
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_path = Path(log_filename)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logger = get_logger()
