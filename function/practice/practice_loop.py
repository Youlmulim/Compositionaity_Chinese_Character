"""
practice_loop.py
----------------
연습 모드 루프.

Flow
----
1. run_practice_phase0_loop()
       데이터 저장 없이 char_list의 모든 글자에 대해 Phase 0 친숙도 평가 실행.

2. run_practice_loop()
       [본 실험 시작] 클릭 때까지 Phase 1→2→3 순서로 무한 반복.
       show_practice_screen() → SPACE → Phase 1 → Phase 2 → Phase 3 → Hover ITI → 처음으로
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
    연습용 Phase 0 루프 — 친숙도 평가 화면을 char_list 전체에 걸쳐 순서대로 실행합니다.
    데이터는 저장하지 않습니다 (연습 전용).

    Parameters
    ----------
    win          : PsychoPy Window
    char_list    : 평가할 한자 목록
    global_clock : 실험 전체 시계
    """
    image_dir   = Path(cfg.STIMULI_DIR)
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
    연습 trial을 Phase 1→2→3 순서로 순환하며,
    Exit 버튼이 눌릴 때까지 계속 실행합니다.

    Parameters
    ----------
    win             : PsychoPy Window
    practice_trials : trial_table에서 샘플링된 trial 목록
    global_clock    : 실험 전체 시계
    """
    shuffled = practice_trials.copy()
    random.shuffle(shuffled)
    trial_cycle = itertools.cycle(shuffled)

    while True:
        action = show_practice_screen(win, cfg.PRACTICE_INSTRUCTION)
        if action == "exit":
            break

        trial = next(trial_cycle)

        # ── Phase 1: 是/否 판단 ──────────────────────────────────────────────
        run_hover_iti(win)
        run_practice_trial(win, trial, global_clock)

        # ── Phase 2: 의미 선택 (최종 화면만) ────────────────────────────────
        run_hover_iti(win)
        result2 = run_practice_phase2(win, trial, global_clock)

        # ── Phase 3: 위치 배치 (Phase 2 선택 의미 전달) ──────────────────────
        run_hover_iti(win)
        trial_with_p2 = {**trial, "phase2_response": result2["response"]}
        run_practice_phase3(win, trial_with_p2, global_clock)

        run_hover_iti(win)
