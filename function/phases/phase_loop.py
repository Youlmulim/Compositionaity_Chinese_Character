import gc
from pathlib import Path

from function.config import settings as cfg
from function.utils.inter_trial import run_hover_iti
from function.io.frame_logger import make_frame_log, get_rows
from function.io.frame_saver import save_frame_log
from function.io.metadata import (
    export_metadata,
    make_phase0_result,
    save_phase0,
    save_trial_metadata_json,
    update_trial,
)
from function.io.path_builder import ensure_trial_save_dir, get_subject_dir
from function.phases.phase0 import run_phase0
from function.stimuli.trial_loader import build_phase0_trials, preload_images
from function.utils.screen_utils import show_instructions


def run_phase0_loop(
        win, 
        char_list, 
        global_clock, 
        subject_id
        ):
    
    """Run Phase 0 over char_list and persist results."""
    image_dir   = Path(cfg.STIMULI_DIR)
    image_cache = preload_images(char_list, win, image_dir)
    trials      = build_phase0_trials(char_list, image_dir, image_cache=image_cache)
    results     = []

    for trial in trials:
        fl = make_frame_log(
            phase="phase_0",
            trial_id=trial["trial_id"],
            stim_pair_id=trial["stim_pair_id"],
        )
        result, fl = run_phase0(win, trial, global_clock, fl)

        results.append(make_phase0_result(trial, result))
        # Checkpoint immediately after each completed trial. The cumulative
        # summary is rewritten with all completed results, while this trial's
        # frame log is persisted in its own directory.
        save_phase0(results, [fl], get_subject_dir(subject_id), subject_id)
        run_hover_iti(win)


def run_phase_loop(
        win,
        trials,
        global_clock,
        subject_id,
        phase_fns
        ):

    for i in range(len(trials)):
        trial = trials[i]
        gc.disable()

        trial_frame_rows = []  # 각 trial마다 프레임 로그 누적할 리스트
        save_dir = ensure_trial_save_dir(
            subject_id,
            "trial_summary",
            trial["stim_pair_id"],
        )

        for phase_num in [1, 2, 3]:
            phase_key = f"phase{phase_num}"
            run_fn = phase_fns[phase_num]

            # 첫 번째 pair에서만 instruction 제시
            if i == 0:
                show_instructions(win, cfg.PHASE_CONFIG[phase_num - 1][1])

            # 1. frame logger
            fl = make_frame_log(
                phase=phase_key,
                trial_id=trial["trial_id"],
                stim_pair_id=trial["stim_pair_id"]
            )

            # 2. run phase
            result, fl = run_fn(
                win,
                trial,
                global_clock,
                fl
            )

            # 3. trial dictionary UPDATE
            trial = update_trial(trial, {
                f"{phase_key}_response": result["response"],
                f"{phase_key}_rt":       result["rt"],
            })

            trials[i] = trial  # 갱신된 trial을 리스트에 반영

            # list에 data 누적 추가
            trial_frame_rows.extend(get_rows(fl))

            # Checkpoint after every completed phase. If the experiment stops
            # during a later phase, all earlier phase rows remain on disk.
            save_trial_metadata_json(trial, save_dir)
            save_frame_log(trial_frame_rows, save_dir)

            # Phase 3 completes one full trial. Update the subject-level
            # cumulative CSV/JSON before entering the ITI, so an Escape during
            # or after the ITI cannot discard this completed trial.
            if phase_num == 3:
                export_metadata(
                    trials[:i + 1],
                    get_subject_dir(subject_id),
                    subject_id,
                    fmt="both",
                )

            # 4. inter-trial interval
            run_hover_iti(win)
