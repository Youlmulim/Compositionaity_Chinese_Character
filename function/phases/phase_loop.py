from pathlib import Path

from function.config import settings as cfg
from function.utils.inter_trial import run_hover_iti
from function.io.frame_logger import make_frame_log, get_rows
from function.io.frame_saver import save_frame_log
from function.io.metadata import make_phase0_result, update_trial, save_trial_metadata_json, save_phase0
from function.io.path_builder import ensure_trial_save_dir, get_subject_dir
from function.phases.phase0 import run_phase0
from function.stimuli.trial_loader import build_phase0_trials, preload_images


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
    frame_logs  = []

    for trial in trials:
        fl = make_frame_log(
            phase="phase_0",
            trial_id=trial["trial_id"],
            stim_pair_id=trial["stim_pair_id"],
        )
        result, fl = run_phase0(win, trial, global_clock, fl)

        results.append(make_phase0_result(trial, result))
        frame_logs.append(fl)
        run_hover_iti(win)

    save_phase0(results, frame_logs, get_subject_dir(subject_id), subject_id)


def run_phase_loop(
        win,
        trials,
        global_clock,
        subject_id,
        phase_fns
        ):
    for i in range(len(trials)):
        trial = trials[i]

        for phase_num in [1, 2, 3]:
            phase_key = f"phase{phase_num}"
            run_fn = phase_fns[phase_num]

            fl = make_frame_log(
                phase=phase_key,
                trial_id=trial["trial_id"],
                stim_pair_id=trial["stim_pair_id"]
            )

            result, fl = run_fn(
                win,
                trial,
                global_clock,
                fl
            )

            trials[i] = update_trial(trial, {
                f"{phase_key}_response": result["response"],
                f"{phase_key}_rt":       result["rt"],
            })

            save_dir = ensure_trial_save_dir(
                subject_id,
                phase_key,
                trial["stim_pair_id"]
            )

            save_frame_log(get_rows(fl), save_dir)
            save_trial_metadata_json(trials[i], save_dir)
            run_hover_iti(win)
