from __future__ import annotations

import math
import random
import struct

import pygame

from pocket_games.core.logger import logger


class AudioManager:
    """
    AudioManager manages the audio output for game effects and sound generation.

    This class initializes a mixer system capable of playing synthesized tones with various waveforms. It provides controls for enabling/disabling audio and adjusting volume levels. The manager caches generated sound objects to optimize playback performance, clearing the cache when volume changes. Audio errors during initialization or playback are logged internally without interrupting application flow.

    :ivar enabled: Boolean flag indicating if the audio subsystem is active and sounds will play.
    :type enabled: bool
    :ivar volume: Float representing the current master volume level, clamped between 0.0 and 1.0.
    :type volume: float

    """
    def __init__(self, enabled: bool = True, volume: float = 0.6) -> None:
        self.enabled = enabled
        self.volume = volume
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except Exception as e:  # noqa: BLE001
            self.enabled = False
            logger.error(e)
        self._cache: dict[str, pygame.mixer.Sound] = {}

    def set_volume(self, volume: float) -> None:
        """
        Sets the volume level within the valid range between zero and one, ensuring the internal cache is cleared upon update.

        Parameters
        ----------
        volume : float
            The target volume value to be set.

        Returns
        -------
        None
        """
        self.volume = max(0.0, min(1.0, volume))
        self._cache.clear()

    def _create_tone(self, freq: float, duration: float, wave_type: str = "square") -> pygame.mixer.Sound:
        """
        Generate and return a synthesized audio sound object with specific waveform characteristics.
        The generated tone includes a fade-out envelope applied over the specified duration to avoid clicking artifacts during playback.
        Supported waveforms include square, sine, and noise signals mixed with volume control managed via instance attributes.

        :param freq: The frequency of the sound wave in Hertz.
        :param duration: The length of the generated sound in seconds.
        :param wave_type: The type of waveform to generate (square, sine, or noise). Defaults to square.
        :return: A pygame mixer Sound object initialized with the generated audio buffer.

        """
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buffer = bytearray()

        for i in range(num_samples):
            t = i / sample_rate
            if wave_type == "square":
                val = 1 if (int(t * freq * 2) % 2) == 0 else -1
            elif wave_type == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == "noise":
                val = random.uniform(-1, 1)
            else:
                val = 0

            envelope = 1.0 - (i / num_samples) * 0.3
            sample = int(32767 * self.volume * val * envelope)
            buffer.extend(struct.pack('<h', max(-32768, min(32767, sample))))

        return pygame.mixer.Sound(buffer=bytes(buffer))

    def play(self, sound_type: str) -> None:
        """
        Play an audio effect corresponding to the specified sound identifier. This method checks current enabled state and volume level before playing the appropriate stored tone. Any processing errors occurring during playback are logged internally without propagating exceptions to the caller.

        :param sound_type: The string identifier representing the desired sound effect, such as select, confirm, jump, coin, crash, laser, or gameover.
        :return: None
        """
        if not self.enabled or self.volume <= 0.0:
            return

        if sound_type not in self._cache:
            match sound_type:
                case "select":
                    self._cache[sound_type] = self._create_tone(440, 0.08, "square")
                case "confirm":
                    self._cache[sound_type] = self._create_tone(880, 0.1, "square")
                case "jump" | "bounce":
                    self._cache[sound_type] = self._create_tone(587.33, 0.08, "square")
                case "coin" | "score":
                    self._cache[sound_type] = self._create_tone(1046.5, 0.12, "sine")
                case "crash" | "hit":
                    self._cache[sound_type] = self._create_tone(150, 0.25, "noise")
                case "laser":
                    self._cache[sound_type] = self._create_tone(750, 0.06, "sine")
                case "gameover":
                    self._cache[sound_type] = self._create_tone(220, 0.4, "square")
                case _:
                    self._cache[sound_type] = self._create_tone(440, 0.05, "square")

        try:
            self._cache[sound_type].play()
        except Exception as e:  # noqa: BLE001
            logger.error(e)
