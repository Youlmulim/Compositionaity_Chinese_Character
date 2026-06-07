"""
metadata.py
-----------
Trial-level summary metadata management.

Design contract
---------------
- save_metadata()   : merges a result dict INTO the trial dict (in-memory only).
- export_metadata() : writes the accumulated summary CSV / JSON at the end.

This means no file I/O happens mid-experiment; all disk writes happen in bulk
at the end (or on demand when export_metadata is called).
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from function.io.frame_logger import FrameLog, get_rows
from function.io.frame_saver import save_frame_log
from function.io.path_builder import ensure_trial_save_dir
from function.utils.response import ResponseResult


# ─── Phase 0 result builder ───────────────────────────────────────────────────

def make_phase0_result(trial: Dict[str, Any], result: ResponseResult) -> Dict[str, Any]:
    """
    Merge static trial fields with dynamic response fields for Phase 0.

    Keeps stimulus definition (trial) and response (result) separate at
    collection time; this function combines them only at the point of saving.
    """
    return {
        "phase":           "phase_0",
        "trial_id":        f"phase0_{trial['trial_id']:02d}",
        "character":       trial["character"],
        "image_file":      f"{trial['character']}.png",
        "rating":          int(result["response"]) if result["response"] else None,
        "rt":              result["rt"],
        "timed_out":       result["timed_out"],
        "rotation_offset": trial["rotation_offset"],
    }


# ─── Phase 0 saver ───────────────────────────────────────────────────────────

def save_phase0(
    results: List[Dict[str, Any]],
    frame_logs: List[FrameLog],
    subject_dir: Path,
    subject_id: str,
) -> None:
    """Persist Phase 0 summary CSV and per-trial frame logs."""
    subject_dir.mkdir(parents=True, exist_ok=True)

    if results:
        path = subject_dir / f"{subject_id}_phase0_summary.csv"
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"[metadata] Phase 0 summary saved → {path}")

    for fl in frame_logs:
        save_dir = ensure_trial_save_dir(subject_id, "phase_0", fl["stim_pair_id"])
        save_frame_log(get_rows(fl), save_dir)


# ─── Pure trial updater ───────────────────────────────────────────────────────

def update_trial(trial: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a new trial dict with *updates* merged in (no mutation, no file I/O).

    Use once per phase to add phase results to the running trial record.

    Parameters
    ----------
    trial   : the trial dict from the trial table
    updates : keys/values to add or overwrite, e.g.
              {"phase1_response": "yes", "phase1_rt": 1.23}
    """
    return {**trial, **updates}


# ─── Per-trial metadata JSON saver ────────────────────────────────────────────

def save_trial_metadata_json(trial: Dict[str, Any], save_dir: Path) -> Path:
    """
    Write a single trial's accumulated metadata to save_dir / metadata.json.

    Called ONCE after all phases (1, 2, 3) for that trial have completed.
    This prevents unnecessary file I/O between phases and keeps data centralized.
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / "metadata.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(trial, f, ensure_ascii=False, indent=2)
    return out_path


# ─── Full experiment summary export ───────────────────────────────────────────

_SUMMARY_CSV_COLUMNS = [
    "trial_id",
    "stim_pair_id",
    "canonical_pair",
    "char_order",
    "set",
    "char1",
    "char2",
    "meaning",
    "phase0_response",
    "phase0_rt",
    "phase1_response",
    "phase1_rt",
    "phase2_response",
    "phase2_rt",
    "phase3_response",
    "phase3_rt",
    # "correct_pos",
    # "correct_meaning",
]


def export_metadata(
    trials: List[Dict[str, Any]],
    out_dir: Path,
    subject_id: str,
    fmt: str = "both",
) -> Dict[str, Path]:
    """
    Write the full summary of all trials to disk.

    Parameters
    ----------
    trials     : list of fully-populated trial dicts
    out_dir    : subject root directory (e.g. data/sub-001)
    subject_id : string written into filenames
    fmt        : "csv", "json", or "both"

    Returns
    -------
    dict with keys "csv" and/or "json" mapping to written file paths
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: Dict[str, Path] = {}

    if fmt in ("csv", "both"):
        csv_path = out_dir / f"{subject_id}_summary.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=_SUMMARY_CSV_COLUMNS,
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(trials)
        written["csv"] = csv_path

    if fmt in ("json", "both"):
        json_path = out_dir / f"{subject_id}_summary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(trials, f, ensure_ascii=False, indent=2)
        written["json"] = json_path

    return written
