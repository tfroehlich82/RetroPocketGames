# core/settings.py

## Settings

`class Settings`

Application settings manager for user configuration persistence.

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
:ivar language: Active language identifier for localization.

### __init__

`def __init__(self) -> None`

### load

`def load(self) -> None`

Load persisted application settings from the configuration file.

Reads the JSON settings file and restores previously saved user
preferences, including sound state, master volume level, display
mode, and interface language. If the settings file does not exist,
this method performs no action. On any parsing or I/O failure, the
error is logged and the current in-memory values remain unchanged.

:return:

### save

`def save(self) -> None`

Save the current application settings to the settings file as a JSON document.

The method serializes the active configuration values (sound enabled state,
master volume, fullscreen flag, and language) into a JSON object and writes
it to the settings file using UTF-8 encoding. If an error occurs during the
write operation, the exception is caught and logged via the core logger
rather than being propagated to the caller.

:return: Nothing. This method has no meaningful return value.
