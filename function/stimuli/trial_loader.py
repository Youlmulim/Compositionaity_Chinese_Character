"""
trial_loader.py
---------------
Loads the trial table (CSV) and returns a list of trial dicts.

Expected CSV columns
--------------------
stim_pair_id    : str   e.g. "pair_001"
char1           : str   e.g. "日"
char2           : str   e.g. "月"
canonical_pair  : str   always list-order first, e.g. "日月"
char_order      : str   "AB" (canonical) or "BA" (reversed)
set             : str   "A" or "B" — counterbalance group
meaning         : str   meaning label shown in Phase 2 YES screen
meaning_opt1    : str   4-choice meaning for Phase 2 NO screen
meaning_opt2    : str
meaning_opt3    : str
meaning_opt4    : str
# correct_pos     : int   1–4, correct spatial position (Phase 2 YES)
# correct_meaning : int   1–4, index of correct meaning choice (Phase 2 NO)
"""

import csv
import math
import random
from pathlib import Path
from typing import List, Dict, Any

from function.config.settings import TRIAL_TABLE_CSV


def load_trial_table(
    csv_path: Path = TRIAL_TABLE_CSV,
) -> List[Dict[str, Any]]:
    """
    Read the trial table CSV and return all trials.

    Parameters
    ----------
    csv_path  : Path to the CSV file.

    Returns
    -------
    List[Dict[str, Any]]
        One dict per stimulus pair.
    """
    trials: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            trial: Dict[str, Any] = {
                "trial_id":        idx,
                "stim_pair_id":    row["stim_pair_id"].strip(),
                "char1":           row["char1"].strip(),
                "char2":           row["char2"].strip(),
                "canonical_pair":  row["canonical_pair"].strip(),
                "meaning":         row["meaning"].strip(),
                "meaning_opts": [
                    row["meaning_opt1"].strip(),
                    row["meaning_opt2"].strip(),
                    row["meaning_opt3"].strip(),
                    row["meaning_opt4"].strip(),
                ],
                # Phase results – filled in later
                "phase1_response": None,
                "phase1_rt":       None,
                "phase2_response": None,
                "phase2_rt":       None,
                "phase3_response": None,
                "phase3_rt":       None,
            }
            trials.append(trial)
    return trials


def load_char_list(csv_path: Path = None) -> List[str]:
    """Load the basic character list from basic_characters.csv."""
    if csv_path is None:
        csv_path = TRIAL_TABLE_CSV.parent / "basic_characters.csv"
    with open(csv_path, encoding="utf-8") as f:
        return [row["character"] for row in csv.DictReader(f)]


def build_phase0_trials(
    char_list: List[str],
    image_dir,
    image_cache: Dict[str, Any] = None,
    n: int = None,
) -> List[Dict[str, Any]]:
    """Build per-trial dicts for Phase 0 from a character list.

    Parameters
    ----------
    image_cache : optional dict {char: ImageStim} from preload_images().
                  When provided, each trial carries a pre-loaded ImageStim
                  so run_phase0() skips redundant texture uploads.
    """
    image_dir = Path(image_dir)
    selected  = char_list[:n] if n is not None else char_list
    return [
        {
            "trial_id":        i + 1,
            "character":       char,
            "stim_pair_id":    char,
            "image_path":      image_dir / f"{char}.png",
            "image_stim":      image_cache[char] if image_cache else None,
            "rotation_offset": random.uniform(0, 2 * math.pi),
        }
        for i, char in enumerate(selected)
    ]


def preload_images(
    char_list: List[str],
    win,
    image_dir: Path,
) -> Dict[str, Any]:
    """Load each character image once into a PsychoPy ImageStim.

    Returns a dict {char: ImageStim} to be passed into build_phase0_trials()
    and reused across all trials, avoiding repeated GPU texture uploads.
    """
    from psychopy.visual import ImageStim
    image_dir = Path(image_dir)
    cache: Dict[str, Any] = {}
    for char in char_list:
        path = image_dir / f"{char}.png"
        if not path.exists():
            raise FileNotFoundError(f"Character image not found: {path}")
        cache[char] = ImageStim(win, image=str(path), pos=(0, 0), size=(100, 100))
    return cache
