"""
practice_loop.py
----------------
연습 모드 루프. Exit 버튼을 누를 때까지 Phase 1→2→3 순서로 무한 반복합니다.

Flow per iteration
------------------
  show_practice_screen()
      ├── [본 실험 시작] 클릭 → 루프 종료 → 본 실험으로 이동
      └── SPACE 키 → Phase 1 → Phase 2 → Phase 3 → Hover ITI → 처음으로
"""

import itertools
import random

from psychopy import visual, core

from function.practice.practice_phase1 import run_practice_trial
from function.practice.practice_phase2 import run_practice_phase2
from function.practice.practice_phase3 import run_practice_phase3
from function.utils.screen_utils import show_practice_screen
from function.utils.inter_trial import run_hover_iti
from function.config import settings as cfg


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
