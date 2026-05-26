"""
phase0.py
---------
Phase 0: Prior knowledge assessment — single trial.

Participant rates their familiarity with one character using six circular buttons.

Returns (ResponseResult, FrameLog); result["response"] is "1"–"6" or None on timeout.

Screen layout
-------------
  [top]  Q. How familiar are you with the meaning of this character?

  [centre]  <character image>

  [around]  six numbered rating circles (randomly rotated each trial)
"""

from pathlib import Path
from typing import Any, Dict, Tuple

from psychopy import visual, event, core

from function.utils.draw_utils import (
    make_text,
    build_rating_buttons,
    update_rating_button_states,
)
from function.utils.response import ResponseResult, make_response
from function.config import settings as cfg
from function.io.frame_logger import FrameLog, set_onset, log_frame
from function.utils.event_utils import check_escape
from function.utils.progress_bar import TimeProgressBar


def draw_phase0_screen(
    question_text,
    target_img,
    rating_buttons,
):
    """
    Phase 0 한 trial의 모든 시각 자극을 draw합니다.
    win.flip()은 이 함수 밖에서 호출합니다.
    """

    question_text.draw()
    target_img.draw()

    for button in rating_buttons:
        button["circle"].draw()
        button["label"].draw()


# ─────────────────────────────────────────────────────────────────────────────
# Main Phase 0 — single trial
# ─────────────────────────────────────────────────────────────────────────────

def run_phase0(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
    frame_log: FrameLog,
) -> Tuple[ResponseResult, FrameLog]:
    """
    Phase 0: single-trial familiarity rating.

    Parameters
    ----------
    win          : PsychoPy Window
    trial        : trial dict; must contain "character" (str), "image_path" (Path/str),
                   "rotation_offset" (float, radians)
    global_clock : experiment-wide clock (for global_time in frame log)
    frame_log    : pre-initialised FrameLog for this trial

    Returns
    -------
    (ResponseResult, FrameLog)  — response is "1"–"6" or None on timeout
    """
    character       = trial["character"]
    rotation_offset = trial["rotation_offset"]

    if trial.get("image_stim") is not None:
        target_img = trial["image_stim"]
    else:
        image_path = Path(trial["image_path"])
        if not image_path.exists():
            raise FileNotFoundError(
                f"Phase 0 image not found for character '{character}': {image_path}"
            )
        target_img = visual.ImageStim(
            win=win,
            image=str(image_path),
            pos=(0, 0),
            size=(100, 100),
        )

    question_text = make_text(
        win=win,
        text=cfg.P0_QUESTION,
        pos=(0, 380),
        height=38,
        color=cfg.WHITE_COLOR,
    )

    rating_buttons = build_rating_buttons(
        win=win,
        radius=200,
        rotation_offset=rotation_offset,
    )

    mouse = event.Mouse(visible=True, win=win)
    phase_clock = core.Clock()
    mouse.clickReset()

    frame_idx      = 0
    result         = make_response()
    selected_rating = None

    progress_bar = TimeProgressBar(win=win)

    while result["response"] is None and not result["timed_out"]:
        check_escape(win)

        update_rating_button_states(
            rating_buttons=rating_buttons,
            mouse=mouse,
            selected_rating=selected_rating,
        )

        draw_phase0_screen(
            question_text=question_text,
            target_img=target_img,
            rating_buttons=rating_buttons,
        )

        progress_bar.draw(elapsed_time=phase_clock.getTime())

        flip_time = win.flip()

        if frame_idx == 0:
            frame_log = set_onset(frame_log, flip_time)
            marker = "stimulus_onset"
        else:
            marker = ""

        frame_log = log_frame(
            frame_log,
            frame_idx=frame_idx,
            flip_time=flip_time,
            global_time=global_clock.getTime(),
            event_marker=marker,
        )
        frame_idx += 1

        if cfg.MAX_RESPONSE_TIME and phase_clock.getTime() > cfg.MAX_RESPONSE_TIME:
            result = make_response(timed_out=True)
            continue

        if mouse.getPressed()[0]:
            for button in rating_buttons:
                if button["circle"].contains(mouse):
                    selected_rating = int(button["rating"])
                    rt = float(phase_clock.getTime())

                    update_rating_button_states(
                        rating_buttons=rating_buttons,
                        mouse=mouse,
                        selected_rating=selected_rating,
                    )
                    draw_phase0_screen(
                        question_text=question_text,
                        target_img=target_img,
                        rating_buttons=rating_buttons,
                    )
                    
                    win.flip()
                    core.wait(0.2)

                    while mouse.getPressed()[0]:
                        core.wait(0.01)

                    result = make_response(
                        response=str(selected_rating),
                        response_idx=selected_rating - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break

    frame_log = log_frame(
        frame_log,
        frame_idx=frame_idx,
        flip_time=win.lastFrameT,
        global_time=global_clock.getTime(),
        event_marker="response" if result["response"] else "timeout",
    )

    return result, frame_log
