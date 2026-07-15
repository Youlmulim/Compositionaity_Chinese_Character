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
    warm_up_frame,
)
from function.utils.response import ResponseResult, make_response, confirm_click
from function.config import settings as cfg
from function.io.frame_logger import FrameLog, FrameRecorder
from function.utils.event_utils import check_escape
from function.utils.progress_bar import TimeProgressBar


def draw_phase0_screen(
    question_text,
    target_img,
    rating_buttons,
):
    """
    Draw all visual stimuli for one Phase 0 trial.
    ``win.flip()`` is called outside this function.
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

    result         = make_response()
    selected_rating = None

    progress_bar = TimeProgressBar(win=win)
    rec = FrameRecorder(frame_log, global_clock)

    def redraw():
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

    # Warm both the neutral screen and every possible selected-feedback state.
    warm_up_frame(win, redraw)
    for warmup_rating in range(1, 7):
        selected_rating = warmup_rating
        warm_up_frame(win, redraw)
    selected_rating = None

    while result["response"] is None and not result["timed_out"]:
        check_escape(win)

        redraw()
        progress_bar.draw(elapsed_time=phase_clock.getTime())
        rec.flip_and_log(win)

        if cfg.MAX_RESPONSE_TIME and phase_clock.getTime() > cfg.MAX_RESPONSE_TIME:
            result = make_response(timed_out=True)
            continue

        if mouse.getPressed()[0]:
            for button in rating_buttons:
                if button["circle"].contains(mouse):
                    selected_rating = int(button["rating"])
                    rt = float(phase_clock.getTime())

                    confirm_click(win, mouse, button=0, redraw_fn=redraw, hold=0.2, phase="phase_0", rec=rec)

                    result = make_response(
                        response=str(selected_rating),
                        response_idx=selected_rating - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break

    frame_log = rec.log_final(win, result)
    return result, frame_log
