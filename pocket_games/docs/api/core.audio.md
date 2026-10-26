# core/audio.py

## AudioManager

`class AudioManager`

AudioManager manages the audio output for game effects and sound generation.

This class initializes a mixer system capable of playing synthesized tones with various waveforms. It provides controls for enabling/disabling audio and adjusting volume levels. The manager caches generated sound objects to optimize playback performance, clearing the cache when volume changes. Audio errors during initialization or playback are logged internally without interrupting application flow.

:ivar enabled: Boolean flag indicating if the audio subsystem is active and sounds will play.
:type enabled: bool
:ivar volume: Float representing the current master volume level, clamped between 0.0 and 1.0.
:type volume: float

### __init__

`def __init__(self, enabled: bool=True, volume: float=0.6) -> None`

### set_volume

`def set_volume(self, volume: float) -> None`

Sets the volume level within the valid range between zero and one, ensuring the internal cache is cleared upon update.

Parameters
----------
volume : float
    The target volume value to be set.

Returns
-------
None

### play

`def play(self, sound_type: str) -> None`

Play an audio effect corresponding to the specified sound identifier. This method checks current enabled state and volume level before playing the appropriate stored tone. Any processing errors occurring during playback are logged internally without propagating exceptions to the caller.

:param sound_type: The string identifier representing the desired sound effect, such as select, confirm, jump, coin, crash, laser, or gameover.
:return: None
