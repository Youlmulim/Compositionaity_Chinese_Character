"""
phase2
----------------------------
  [top text]
      Q. If these two characters were combined to form a new character,
         what would its meaning be?

  [centre]   水 + 火 = ?

  [4-choice grid]
      ① boiling          ② ice
      ③ extinguished fire   ④ nature

Response: participant clicks one of the four meaning choices.
"""

from typing import Dict, Any, List, Tuple

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P2_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text, build_char_equation, draw_char_equation,
    make_phase_badge, draw_phase_badge,
    update_rating_button_states,
)
from function.utils.response import ResponseResult, make_response, wait_for_mouse_release
from function.io.frame_logger import FrameLog, set_onset, log_frame
from function.utils.event_utils import check_escape


def run_phase2(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
    frame_log: FrameLog,
) -> Tuple[ResponseResult, FrameLog]:
    """
    Display Phase 2 screen and collect a 1-4 meaning choice response.

    Parameters
    ----------
    win          : PsychoPy Window
    trial        : trial dict; must contain "char1", "char2", "meaning_opts" (list of 4)
    global_clock : experiment-wide clock
    frame_log    : pre-initialised FrameLog

    Returns
    -------
    (ResponseResult, FrameLog)  — response is "1"-"4", response_idx is 0-3
    """
    char1        = trial["char1"]
    char2        = trial["char2"]
    meaning_opts: List[str] = trial["meaning_opts"]

    mouse = event.Mouse(win=win)
    mouse.clickReset()

    # ── Build stimuli ──────────────────────────────────────────────────────────
    eq_stims = build_char_equation(
        win, char1, char2,
        char1_pos=cfg.P2_EQ_CHAR1_POS,
        plus_pos=cfg.P2_EQ_PLUS_POS,
        char2_pos=cfg.P2_EQ_CHAR2_POS,
        eq_pos=cfg.P2_EQ_EQ_POS,
        qmark_pos=cfg.P2_EQ_QMARK_POS,
    )

    question_stim = make_text(
        win,
        cfg.P2_QUESTION,
        pos=cfg.P2_QUESTION_POS,
        height=cfg.P2_QUESTION_HEIGHT,
        align_horiz="center",
    )

    choice_buttons    = []
    choice_text_stims = []

    for i, (opt, num) in enumerate(zip(meaning_opts, cfg.CIRCLE_NUMS)):
        circ_pos = cfg.P2_CHOICE_CIRCLE_POS[i]
        text_pos = cfg.P2_CHOICE_TEXT_POS[i]

        circ = visual.Circle(
            win, radius=cfg.P2_CHOICE_CIRCLE_RADIUS, pos=circ_pos,
            fillColor=None, lineColor="white", lineWidth=3,
        )
        lbl = make_text(win, num, pos=circ_pos, height=54, bold=True)
        choice_buttons.append({"rating": i + 1, "circle": circ, "label": lbl})

        choice_text_stims.append(
            make_text(win, opt, pos=text_pos, height=cfg.P2_CHOICE_HEIGHT)
        )

    # badge = make_phase_badge(win, "phase2")

    # ── Flip loop ─────────────────────────────────────────────────────────────
    phase_clock  = core.Clock()
    frame_idx    = 0
    result       = make_response()
    prev_pressed = False

    while result["response"] is None and not result["timed_out"]:
        # draw_phase_badge(badge)
        question_stim.draw()
        draw_char_equation(eq_stims)

        update_rating_button_states(choice_buttons, mouse, selected_rating=None)
        for btn in choice_buttons:
            btn["circle"].draw()
            btn["label"].draw()
        for stim in choice_text_stims:
            stim.draw()

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

        btn_pressed = bool(mouse.getPressed()[P2_MOUSE_BUTTON])
        if btn_pressed and not prev_pressed:
            pos = mouse.getPos()
            for btn in choice_buttons:
                resp_val = str(btn["rating"])
                if btn["circle"].contains(pos):
                    rt = phase_clock.getTime()
                    wait_for_mouse_release(mouse, P2_MOUSE_BUTTON)
                    result = make_response(
                        response=resp_val,
                        response_idx=int(resp_val) - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break
        prev_pressed = btn_pressed

        check_escape(win)

        if cfg.MAX_RESPONSE_TIME and phase_clock.getTime() > cfg.MAX_RESPONSE_TIME:
            result = make_response(timed_out=True)

    frame_log = log_frame(
        frame_log,
        frame_idx=frame_idx,
        flip_time=win.lastFrameT,
        global_time=global_clock.getTime(),
        event_marker="response" if result["response"] else "timeout",
    )

    return result, frame_log
