"""
image_paths.py
--------------
Centralises ALL image-path construction logic.
When the stimulus naming convention changes, only this file needs updating.

Convention:
    {STIMULI_DIR}/{char}.png
    e.g.  stimuli/images/水.png

One file per unique character — the same character image is reused across all pairs.
"""

from pathlib import Path
from function.config.settings import STIMULI_DIR


def get_char_image_path(char: str) -> Path:
    """Return path to the image for a single Chinese character."""
    return STIMULI_DIR / f"{char}.png"


def get_pair_image_paths(char1: str, char2: str) -> dict:
    """
    Return both character image paths for a pair.

    Returns
    -------
    dict with keys "char1_path" and "char2_path"
    """
    return {
        "char1_path": get_char_image_path(char1),
        "char2_path": get_char_image_path(char2),
    }
