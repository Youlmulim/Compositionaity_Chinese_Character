"""
frame_logger.py
---------------
Immutable frame-level log accumulator using TypedDict.

Usage
-----
    log = make_frame_log(phase="phase_1", trial_id=0, stim_pair_id="pair_001")
    # inside the flip loop:
    log = set_onset(log, flip_time)
    log = log_frame(log, frame_idx, flip_time, global_clock.getTime(), "stimulus_onset")
    # after loop:
    rows = get_rows(log)
"""

from typing import Any, Dict, List, Optional, TypedDict


class FrameLog(TypedDict):
    """Accumulator for per-frame log entries of one trial/phase."""
    phase:        str
    trial_id:     int
    stim_pair_id: str
    onset_time:   Optional[float]
    rows:         List[Dict[str, Any]]


def make_frame_log(phase: str, trial_id: int, stim_pair_id: str) -> FrameLog:
    return {
        "phase":        phase,
        "trial_id":     trial_id,
        "stim_pair_id": stim_pair_id,
        "onset_time":   None,
        "rows":         [],
    }


def set_onset(log: FrameLog, t: float) -> FrameLog:
    """Return a new FrameLog with onset_time set to *t*."""
    return {**log, "onset_time": t}


def log_frame(
    log: FrameLog,
    frame_idx: int,
    flip_time: float,
    global_time: float,
    event_marker: str = "",
) -> FrameLog:
    """Return a new FrameLog with one frame entry appended."""
    elapsed = (flip_time - log["onset_time"]) if log["onset_time"] is not None else 0.0
    row: Dict[str, Any] = {
        "frame_idx":    frame_idx,
        "phase":        log["phase"],
        "trial_id":     log["trial_id"],
        "stim_pair_id": log["stim_pair_id"],
        "elapsed_time": round(elapsed, 6),
        "global_time":  round(global_time, 6),
        "flip_time":    round(flip_time, 6),
        "event_marker": event_marker,
    }
    return {**log, "rows": log["rows"] + [row]}


def get_rows(log: FrameLog) -> List[Dict[str, Any]]:
    """Return accumulated rows as a plain list."""
    return list(log["rows"])
