from __future__ import annotations
import math
import random
import struct
import pygame

class AudioManager:
    def __init__(self, enabled: bool = True, volume: float = 0.8) -> None:
        self.enabled = enabled
        self.volume = volume
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        except Exception:
            self.enabled = False
        self._cache: dict[str, pygame.mixer.Sound] = {}

    def _create_tone(self, freq: float, duration: float, wave_type: str = "square") -> pygame.mixer.Sound:
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

            # Apply slight volume decay envelope
            envelope = 1.0 - (i / num_samples) * 0.3
            sample = int(32767 * self.volume * val * envelope)
            buffer.extend(struct.pack('<h', max(-32768, min(32767, sample))))

        return pygame.mixer.Sound(buffer=bytes(buffer))

    def play(self, sound_type: str) -> None:
        if not self.enabled:
            return

        if sound_type not in self._cache:
            match sound_type:
                case "select":
                    self._cache[sound_type] = self._create_tone(440, 0.05, "square")
                case "confirm":
                    self._cache[sound_type] = self._create_tone(880, 0.1, "square")
                case "jump":
                    self._cache[sound_type] = self._create_tone(587.33, 0.08, "square")
                case "coin":
                    self._cache[sound_type] = self._create_tone(1046.5, 0.12, "sine")
                case "crash":
                    self._cache[sound_type] = self._create_tone(150, 0.25, "noise")
                case "laser":
                    self._cache[sound_type] = self._create_tone(750, 0.06, "sine")
                case "score":
                    self._cache[sound_type] = self._create_tone(659.25, 0.1, "sine")
                case _:
                    self._cache[sound_type] = self._create_tone(440, 0.05, "square")

        try:
            self._cache[sound_type].play()
        except Exception:
            pass
