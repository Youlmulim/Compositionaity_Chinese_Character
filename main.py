"""
main.py
-------
Top-level experiment controller.

Execution flow
--------------
1. initiate_experiment() — subject info, trials, window, EyeLink
2. Phase 0 — familiarity ratings for basic characters
3. Phases 1-3 — phase loops (Phase 1: first N trials, Phase 2-3: all trials)
4. Export full summary (CSV + JSON)
5. Close window
"""

import random

from psychopy import core

from function.phases.phase1 import run_phase1
from function.phases.phase2 import run_phase2
from function.phases.phase3 import run_phase3
from function.phases.phase_loop import run_phase0_loop, run_phase_loop
from function.practice.practice_loop import run_practice_loop
from function.io.metadata import export_metadata
from function.io.path_builder import get_subject_dir
from function.config import settings as cfg
from function.utils.screen_utils import show_instructions
from initiate import initiate_experiment


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ctx = initiate_experiment()

    # Phase 0 — familiarity ratings
    show_instructions(ctx.win, cfg.P0_INSTRUCTION)
    run_phase0_loop(
        ctx.win,
        ctx.char_list,
        ctx.global_clock,
        ctx.subject_id,
    )

    # Practice — unlimited trials, exit button leads to main experiment
    practice_trials = random.sample(ctx.trials, min(cfg.PRACTICE_N_TRIALS, len(ctx.trials)))
    run_practice_loop(ctx.win, practice_trials, ctx.global_clock)

    # Phases 1–3
    _phase_fns = {1: run_phase1, 2: run_phase2, 3: run_phase3}
    random.shuffle(ctx.trials)
    run_phase_loop(
        ctx.win,
        ctx.trials,
        ctx.global_clock,
        ctx.subject_id,
        _phase_fns,
    )

    # Export full summary
    paths = export_metadata(
        ctx.trials,
        get_subject_dir(ctx.subject_id),
        ctx.subject_id,
        fmt="both",
    )
    print(f"[main] Summary saved → {paths}")

    # Farewell & close
    show_instructions(ctx.win, "实验完成。\n\n谢谢！\n\n按空格键退出。")
    ctx.win.close()
    core.quit()


if __name__ == "__main__":
    main()