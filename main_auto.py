"""
main_auto.py
------------
Automated experiment runner for code / pipeline testing.

Skips practice phases entirely. Each phase generates a random but valid
response after drawing one frame, so the full data-saving pipeline runs
without any human interaction.

Usage
-----
    python main_auto.py --subject 999

The subject ID is passed on the command line instead of a GUI dialog.
Data is saved to data/sub-{subject_id}/ exactly as in the real experiment.
"""

import argparse
import random
from pathlib import Path

from psychopy import core

from function.config import settings as cfg
from function.config.window_factory import create_window
from function.io.frame_logger import make_frame_log, get_rows, FrameRecorder
from function.io.frame_saver import save_frame_log
from function.io.metadata import (
    export_metadata,
    make_phase0_result,
    save_phase0,
    save_trial_metadata_json,
    update_trial,
)
from function.io.path_builder import ensure_trial_save_dir, get_subject_dir
from function.stimuli.trial_loader import (
    build_phase0_trials,
    get_or_create_subject_trials,
    load_char_list,
    preload_images,
)
from function.utils.response import make_response


# ─── Auto phase stubs ────────────────────────────────────────────────────────
# Each stub draws exactly one frame so the window stays alive, then returns
# a randomly generated but structurally valid ResponseResult.

def _auto_phase0(win, trial, global_clock, frame_log):
    """Familiarity rating: random 1–6."""
    rec = FrameRecorder(frame_log, global_clock)
    rec.flip_and_log(win)
    rating = random.randint(1, 6)
    result = make_response(
        response=str(rating),
        response_idx=rating - 1,
        rt=0.01,
        raw_key="auto",
    )
    return result, rec.log_final(win, result)


def _auto_phase1(win, trial, global_clock, frame_log):
    """Yes / No: random choice."""
    rec = FrameRecorder(frame_log, global_clock)
    rec.flip_and_log(win)
    response = random.choice(["yes", "no"])
    result = make_response(response=response, rt=0.01, raw_key="auto")
    return result, rec.log_final(win, result)


def _auto_phase2(win, trial, global_clock, frame_log):
    """Meaning selection: random among available options."""
    rec = FrameRecorder(frame_log, global_clock)
    rec.flip_and_log(win)
    n_opts = len(trial.get("meaning_opts", ["a", "b"]))
    idx = random.randint(0, n_opts - 1)
    result = make_response(
        response=str(idx + 1),
        response_idx=idx,
        rt=0.01,
        raw_key="auto",
    )
    return result, rec.log_final(win, result)


def _auto_phase3(win, trial, global_clock, frame_log):
    """Character arrangement: char1 → CENTER, char2 → random other position."""
    rec = FrameRecorder(frame_log, global_clock)
    rec.flip_and_log(win)
    char2_pos = random.choice(["TOP", "LEFT", "RIGHT", "BOTTOM"])
    result = make_response(
        response=f"CENTER_{char2_pos}",
        response_idx=0,
        rt=0.01,
        raw_key="auto",
    )
    return result, rec.log_final(win, result)


# ─── Auto loop functions ──────────────────────────────────────────────────────

def _run_auto_phase0_loop(win, char_list, global_clock, subject_id):
    image_dir   = Path(cfg.STIMULI_DIR)
    image_cache = preload_images(char_list, win, image_dir)
    trials      = build_phase0_trials(char_list, image_dir, image_cache=image_cache)
    results     = []
    frame_logs  = []

    for trial in trials:
        fl = make_frame_log(
            phase="phase_0",
            trial_id=trial["trial_id"],
            stim_pair_id=trial["stim_pair_id"],
        )
        result, fl = _auto_phase0(win, trial, global_clock, fl)
        results.append(make_phase0_result(trial, result))
        frame_logs.append(fl)
        win.flip()  # replaces hover ITI

    save_phase0(results, frame_logs, get_subject_dir(subject_id), subject_id)
    print(f"[auto] Phase 0 complete ({len(trials)} trials)")


def _run_auto_phase_loop(win, trials, global_clock, subject_id):
    auto_fns = {
        1: _auto_phase1,
        2: _auto_phase2,
        3: _auto_phase3,
    }

    for i, trial in enumerate(trials):
        trial_frame_rows = []

        for phase_num in [1, 2, 3]:
            phase_key = f"phase{phase_num}"

            fl = make_frame_log(
                phase=phase_key,
                trial_id=trial["trial_id"],
                stim_pair_id=trial["stim_pair_id"],
            )
            result, fl = auto_fns[phase_num](win, trial, global_clock, fl)

            trial = update_trial(trial, {
                f"{phase_key}_response": result["response"],
                f"{phase_key}_rt":       result["rt"],
            })
            trials[i] = trial
            trial_frame_rows.extend(get_rows(fl))
            win.flip()  # replaces hover ITI

        save_dir = ensure_trial_save_dir(
            subject_id,
            "trial_summary",
            trial["stim_pair_id"],
        )
        save_trial_metadata_json(trial, save_dir)
        save_frame_log(trial_frame_rows, save_dir)

        if (i + 1) % 10 == 0 or i == 0:
            print(f"[auto] Trial {i + 1}/{len(trials)} done")

    print(f"[auto] Phases 1-3 complete ({len(trials)} trials)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Auto-run main experiment without practice or human input."
    )
    parser.add_argument(
        "--subject", required=True,
        help="Subject ID (e.g. 999). Data saved to data/sub-{subject_id}/",
    )
    args = parser.parse_args()
    subject_id = args.subject.strip()

    print(f"[auto] Starting automated run - subject: {subject_id}")

    trials    = get_or_create_subject_trials(subject_id)
    char_list = load_char_list()
    print(f"[auto] {len(trials)} trials | {len(char_list)} characters")

    win          = create_window()
    global_clock = core.Clock()

    # Phase 0 — familiarity ratings (auto)
    _run_auto_phase0_loop(win, char_list, global_clock, subject_id)

    # Phases 1–3 (auto, shuffled trial order)
    random.shuffle(trials)
    _run_auto_phase_loop(win, trials, global_clock, subject_id)

    # Export full summary
    paths = export_metadata(
        trials,
        get_subject_dir(subject_id),
        subject_id,
        fmt="both",
    )
    print(f"[auto] Summary saved → {paths}")

    win.close()
    core.quit()


if __name__ == "__main__":
    main()
