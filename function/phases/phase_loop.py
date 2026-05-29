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

        trial_frame_rows = []  # 각 trial마다 프레임 로그 누적할 리스트

        for phase_num in [1, 2, 3]:
            phase_key = f"phase{phase_num}"
            run_fn = phase_fns[phase_num]

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

            #3. trial dictionary UPDATE
            trials[i] = update_trial(trial, {
                f"{phase_key}_response": result["response"],
                f"{phase_key}_rt":       result["rt"],
            })

            trials[i] = trial # 갱신된 trial을 리스트에 반영

            # list에 data 누적 추가
            trial_frame_rows.extend(get_rows(fl))

            # 4. inter-trial interval
            run_hover_iti(win)

        # 5. save DATA

        # 5-1. integrated folder path 생성
        save_dir = ensure_trial_save_dir(
            subject_id,
            "trial_summary", # phase_key로 frame logger 생성
            trial["stim_pair_id"]
        )

        # 5-2. JSON과 누적된 frame log 저장
        save_trial_metadata_json(trials[i], save_dir)
        save_frame_log(trial_frame_rows, save_dir)

        # Q: 통합데이터를 따로 빼는 것이 낫지 않을까?
        # 프레임 로그는 메모리에 모았다가 트라이얼 종료 시점에 일괄 저장하는 방식이 나을듯?


