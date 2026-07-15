"""Preloaded, non-blocking sound effects for PsychoPy tasks.

Sound files live beside this module. ``preload_sound`` performs file access and
decoding once, before a frame loop starts; subsequent calls return the cached
PsychoPy Sound object. PsychoPy's ``Sound.play`` starts playback asynchronously.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from psychopy import prefs

# Use the same low-latency backend on every machine. This must be set before
# importing ``psychopy.sound``.
prefs.hardware["audioLib"] = ["PTB"]

from psychopy import sound  # noqa: E402  (backend preference must be set first)
from psychtoolbox import GetSecs


SOUNDS_DIR = Path(__file__).resolve().parent
DEFAULT_SOUND_FILE = "sound_effect.wav"


@lru_cache(maxsize=None)
def preload_sound(filename: str = DEFAULT_SOUND_FILE) -> Any:
    """Load and cache a WAV sound located in this package directory."""
    sound_path = SOUNDS_DIR / filename
    if not sound_path.is_file():
        raise FileNotFoundError(f"Sound effect not found: {sound_path}")

    return sound.Sound(str(sound_path))


def play_sound(sound_effect: Any) -> None:
    """Start an already-preloaded sound without waiting for it to finish."""
    sound_effect.play()


def schedule_sound(sound_effect: Any, delay: float = 0.0) -> None:
    """Ask PTB to play a preloaded sound after ``delay`` seconds.

    PTB prepares playback on its audio thread, so the visual flip loop does not
    wait for file access, decoding, or the requested playback time.
    """
    if delay < 0:
        raise ValueError("delay must be greater than or equal to zero")
    sound_effect.play(when=GetSecs() + delay)
