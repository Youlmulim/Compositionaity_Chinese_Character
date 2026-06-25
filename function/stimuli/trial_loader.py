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

from function.config.settings import TRIAL_TABLE_CSV, ROOT_DIR
from function.io.path_builder import get_subject_dir
from config import TEST_MODE


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
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            trial: Dict[str, Any] = {
                "trial_id":        idx,
                "stim_pair_id":    row["stim_pair_id"].strip(),
                "char1":           row["char1"].strip(),
                "char2":           row["char2"].strip(),
                "canonical_pair":  row["canonical_pair"].strip(),
                "char_order":      row.get("char_order", "AB").strip(),  # Default to "AB" if not present
                "meaning":         row["meaning"].strip(),
                "meaning_opts": [
                    opt for opt in [
                        row["meaning_opt1"].strip(),
                        row["meaning_opt2"].strip(),
                    ] if opt
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

def get_or_create_subject_trials(subject_id: str) -> List[Dict[str, Any]]:
    """
    피험자 고유의 trial_table을 불러오거나, 없다면 새로 생성하여 저장합니다.
    """
    # 피험자 데이터 폴더 경로 확보 (예: data/sub-001/)
    subject_dir = get_subject_dir(subject_id)
    subject_dir.mkdir(parents=True, exist_ok=True)
    
    # 피험자 고유의 CSV 파일 경로 지정
    subject_csv_path = subject_dir / f"sub-{subject_id}_trial_table.csv"
    
    # 1. 이미 피험자의 trial table이 존재한다면 (예: 실험 재시작) 그것을 불러옴
    # TEST_MODE일 때는 피험자 캐시를 무시하고 test CSV를 사용
    if not TEST_MODE and subject_csv_path.exists():
        print(f"Loading existing trial table for subject {subject_id}")
        return load_trial_table(subject_csv_path)
    
    # 2. 존재하지 않는다면 원본 파일에서 불러와서 랜덤화 진행 후 저장
    print(f"Creating new randomized trial table for subject {subject_id}")
    base_trials = load_trial_table(TRIAL_TABLE_CSV)
    
    # Randomize character order and meaning options for each trial
    for trial in base_trials:
        if random.choice([True, False]):
            trial["char1"], trial["char2"] = trial["char2"], trial["char1"]
            trial["char_order"] = "BA"
        else:
            trial["char_order"] = "AB"
        
        # Shuffle meaning options
        shuffled_opts = trial["meaning_opts"].copy()
        random.shuffle(shuffled_opts)
        trial["meaning_opts"] = shuffled_opts
    
    save_rows = []
    for trial in base_trials:
        save_rows.append({
            "trial_id": trial["trial_id"],
            "stim_pair_id": trial["stim_pair_id"],
            "char1": trial["char1"],
            "char2": trial["char2"],
            "canonical_pair": trial["canonical_pair"],
            "char_order": trial["char_order"],
            "meaning": trial["meaning"],
            "meaning_opt1": trial["meaning_opts"][0] if len(trial["meaning_opts"]) > 0 else "",
            "meaning_opt2": trial["meaning_opts"][1] if len(trial["meaning_opts"]) > 1 else "",
        })

    fieldnames = list(save_rows[0].keys())

    with open(subject_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(save_rows)
            
    return base_trials


def load_char_list(csv_path: Path = None) -> List[str]:
    """Load the basic character list from basic_characters.csv."""
    if csv_path is None:
        csv_path = ROOT_DIR / "stimuli" / "basic_characters.csv"
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