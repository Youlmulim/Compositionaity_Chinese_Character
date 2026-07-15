"""
practice_loop.py
----------------
Practice-mode loops.

Flow
----
1. run_practice_phase0_loop()
       Run Phase 0 familiarity ratings for every character without saving data.

2. run_practice_loop()
       Repeat Phases 1→2→3 until the main-experiment button is clicked.
       show_practice_screen() → SPACE → Phase 1 → Phase 2 → Phase 3 → Hover ITI → restart
"""

import itertools
import random
from pathlib import Path

from psychopy import visual, core

from function.practice.practice_phase0 import run_practice_phase0
from function.practice.practice_phase1 import run_practice_trial
from function.practice.practice_phase2 import run_practice_phase2
from function.practice.practice_phase3 import run_practice_phase3
from function.utils.screen_utils import show_practice_screen
from function.utils.inter_trial import run_hover_iti
from function.stimuli.trial_loader import build_phase0_trials, preload_images
from function.config import settings as cfg


def run_practice_phase0_loop(
        win: visual.Window,
        char_list: list,
        global_clock: core.Clock,
) -> None:
    """
    Run the practice Phase 0 familiarity screen for every character in order.
    Data is not saved in practice mode.

    Parameters
    ----------
    win          : PsychoPy Window
    char_list    : list of Chinese characters to rate
    global_clock : experiment-wide clock
    """
    image_dir   = Path(cfg.STIMULI_PRAC_DIR)
    image_cache = preload_images(char_list, win, image_dir)
    trials      = build_phase0_trials(char_list, image_dir, image_cache=image_cache)

    for trial in trials:
        run_practice_phase0(win, trial, global_clock)
        run_hover_iti(win)


def run_practice_loop(
    win: visual.Window,
    practice_trials: list,
    global_clock: core.Clock,
) -> None:
    """
    Cycle through practice trials in Phase 1→2→3 order until Exit is clicked.

    Parameters
    ----------
    win             : PsychoPy Window
    practice_trials : trials sampled from trial_table
    global_clock    : experiment-wide clock
    """
    shuffled = practice_trials.copy()
    random.shuffle(shuffled)
    trial_cycle = itertools.cycle(shuffled)

    while True:
        action = show_practice_screen(win, cfg.PRACTICE_INSTRUCTION)
        if action == "exit":
            break

        trial = next(trial_cycle)

        # ── Phase 1: Yes/No judgment ────────────────────────────────────────────
        run_hover_iti(win)
        run_practice_trial(win, trial, global_clock)

        # ── Phase 2: Meaning selection (final screen only) ──────────────────
        run_hover_iti(win)
        result2 = run_practice_phase2(win, trial, global_clock)

        # ── Phase 3: Position placement using the Phase 2 meaning ──────────
        run_hover_iti(win)
        trial_with_p2 = {**trial, "phase2_response": result2["response"]}
        run_practice_phase3(win, trial_with_p2, global_clock)

        run_hover_iti(win)
