"""
phase1.py
---------
Phase 1 screen: shows  char1 + char2 = ?  with Yes / No buttons.

Returns (ResponseResult, FrameLog); the caller (main.py) stores the response.

Screen layout (matches PDF page 1)
-----------------------------------
  [top]  Q. Can the two characters below be combined to form a new character?

  [centre]         水   +   火   =  ?

  [bottom]    [ Yes ]               [ No ]
"""

from typing import Dict, Any, Tuple

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P1_YES_KEY, P1_NO_KEY, P1_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text, make_button, build_char_equation, draw_char_equation, is_clicked,
    update_button_states,
)
from function.utils.response import ResponseResult, make_response, confirm_click
from function.io.frame_logger import FrameLog, FrameRecorder
from function.utils.event_utils import check_escape
from function.utils.progress_bar import TimeProgressBar



def run_phase1(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
    frame_log: FrameLog,
) -> Tuple[ResponseResult, FrameLog]:
    """
    Display Phase 1 screen and collect Yes/No response.

    Parameters
    ----------
    win          : PsychoPy Window
    trial        : trial dict with "char1", "char2", "stim_pair_id"
    global_clock : experiment-wide clock (for global_time in frame log)
    frame_log    : pre-initialised FrameLog for this trial

    Returns
    -------
    (ResponseResult, FrameLog)  — response is "yes" or "no"
    """
    char1 = trial["char1"]
    char2 = trial["char2"]
    mouse = event.Mouse(visible=True, win=win)

    # ── Build stimuli ──────────────────────────────────────────────────────────
    question_stim = make_text(
        win,
        cfg.P1_QUESTION,
        pos=(0, 380),
        height=38,
    )

    yes_rect, yes_txt = make_button(win, cfg.P1_YES_LABEL, pos=cfg.P1_YES_BOX_POS)
    no_rect,  no_txt  = make_button(win, cfg.P1_NO_LABEL,  pos=cfg.P1_NO_BOX_POS)

    yes_button = {"rect": yes_rect, "label": "yes"}
    no_button  = {"rect": no_rect,  "label": "no"}
    buttons    = [yes_button, no_button]

    eq_stims = build_char_equation(
        win, char1, char2,
        char1_pos=cfg.STIM_CHAR1_POS,
        plus_pos=cfg.STIM_PLUS_POS,
        char2_pos=cfg.STIM_CHAR2_POS,
        eq_pos=cfg.STIM_EQ_POS,
        qmark_pos=cfg.STIM_QMARK_POS,
    )

    clickable = [
        (yes_rect, "yes"),
        (no_rect,  "no"),
    ]

    # ── Flip loop ─────────────────────────────────────────────────────────────
    phase_clock     = core.Clock()
    result          = make_response()
    prev_pressed    = False
    selected_button = None
    mouse.clickReset()

    progress_bar = TimeProgressBar(win=win)
    rec = FrameRecorder(frame_log, global_clock)

    def redraw():
        update_button_states(buttons, mouse, selected_button)
        question_stim.draw()
        draw_char_equation(eq_stims)
        yes_rect.draw(); yes_txt.draw()
        no_rect.draw();  no_txt.draw()

    while result["response"] is None and not result["timed_out"]:
        redraw()

        # Show running progress bar from trial start (like Phase 0).
        progress_bar.draw(elapsed_time=phase_clock.getTime())

        rec.flip_and_log(win)

        # ── Response check (mouse) ────────────────────────────────────────────
        btn = bool(mouse.getPressed()[P1_MOUSE_BUTTON])
        if btn and not prev_pressed:
            pos = mouse.getPos()
            for region, label in clickable:
                if region.contains(pos):
                    selected_button = label
                    rt = phase_clock.getTime()

                    confirm_click(win, mouse, button=P1_MOUSE_BUTTON, redraw_fn=redraw, hold=0.2)

                    result = make_response(response=label, rt=rt, raw_key="mouse")
                    break
        prev_pressed = btn

        check_escape(win)

    frame_log = rec.log_final(win, result)
    return result, frame_log
