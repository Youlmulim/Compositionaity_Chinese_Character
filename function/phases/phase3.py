"""
phase3
-------------
  [top text]
      Q. These two characters combine to convey the meaning below.
      Where should the second character be placed relative to the first one
      to produce that meaning?

  [centre-left area]
      ①            [ Boiling ]   (meaning label box, centre-right)
    ② 水 ③ ◄ · · · · · · · · 火
      ④

  [bottom row]   ①    ②    ③    ④   (clickable choice circles)

Response: participant clicks one of the four numbered circles at the bottom.
"""

from typing import Dict, Any, Tuple

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P3_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text, make_chinese_char, make_phase_badge, draw_phase_badge,
    update_rating_button_states,
)
from function.utils.response import ResponseResult, make_response, wait_for_mouse_release
from function.io.frame_logger import FrameLog, set_onset, log_frame
from function.utils.event_utils import check_escape
from function.utils.progress_bar import TimeProgressBar


def run_phase3(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
    frame_log: FrameLog,
) -> Tuple[ResponseResult, FrameLog]:
    """
    Display Phase 3 screen and collect a 1–4 position response.

    Parameters
    ----------
    win          : PsychoPy Window
    trial        : trial dict; must contain "char1", "char2", "meaning"
    global_clock : experiment-wide clock
    frame_log    : pre-initialised FrameLog

    Returns
    -------
    (ResponseResult, FrameLog)  — response is "1"–"4", response_idx is 0–3
    """
    char1   = trial["char1"]
    char2   = trial["char2"]
    # Use Phase2 response to determine meaning; fallback to default if not answered
    if trial["phase2_response"]:
        response_idx = int(trial["phase2_response"]) - 1  # "1" -> 0, "2" -> 1, etc.
        meaning = trial["meaning_opts"][response_idx]
    else:
        meaning = trial["meaning"]
    mouse   = event.Mouse(visible=True, win=win)

    # ── Build stimuli ──────────────────────────────────────────────────────────
    question_stim = make_text(
        win,
        cfg.P3_QUESTION_TMPL,
        pos=(0, 390),
        height=34,
        align_horiz="center",
    )

    char1_stim = make_chinese_char(win, char1, pos=cfg._CHAR1_CENTRE)
    char2_stim = make_chinese_char(win, char2, pos=cfg._CHAR2_POS)

    arrow_stim = make_text(win, cfg._DASHED_ARROW_LABEL, pos=cfg._ARROW_POS, height=30)

    meaning_bg = visual.Rect(
        win,
        width=260, height=65,
        pos=cfg._MEANING_BOX_POS,
        fillColor="white",
        lineColor="white",
    )
    meaning_txt = make_text(
        win, 
        meaning, 
        pos=cfg._MEANING_BOX_POS, 
        height=34, 
        color="black")

    pos_label_stims = {
        i: make_text(
            win, 
            label,
            pos=(cfg._CHAR1_CENTRE[0] + ox, cfg._CHAR1_CENTRE[1] + oy),
            height=44,
        )
        for i, (label, (ox, oy)) in enumerate(
            zip(cfg.CIRCLE_NUMS, cfg._POS_LABEL_OFFSETS.values())
        )
    }

    choice_buttons = []
    for i, label in enumerate(cfg.CIRCLE_NUMS):
        pos = (cfg._CHOICE_XS[i], cfg._CHOICE_Y)
        circ = visual.Circle(
            win, radius=55, pos=pos,
            fillColor=None, lineColor="white", lineWidth=3,
        )
        lbl = make_text(win, label, pos=pos, height=54, bold=True)
        choice_buttons.append({"rating": i + 1, "circle": circ, "label": lbl})
    # badge = make_phase_badge(win, "phase3")

    # ── Flip loop ─────────────────────────────────────────────────────────────
    phase_clock  = core.Clock()
    frame_idx    = 0
    result       = make_response()
    prev_pressed = False

    progress_bar = TimeProgressBar(win=win)

    mouse.clickReset()

    while result["response"] is None and not result["timed_out"]:
        #draw_phase_badge(badge)
        question_stim.draw()
        char1_stim.draw()
        char2_stim.draw()
        arrow_stim.draw()
        meaning_bg.draw()
        meaning_txt.draw()

        for stim in pos_label_stims.values():
            stim.draw()

        update_rating_button_states(choice_buttons, mouse, selected_rating=None)
        for btn_stim in choice_buttons:
            btn_stim["circle"].draw()
            btn_stim["label"].draw()

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

        btn = bool(mouse.getPressed()[P3_MOUSE_BUTTON])
        if btn and not prev_pressed:
            pos = mouse.getPos()
            for btn_stim in choice_buttons:
                resp_val = str(btn_stim["rating"])
                if btn_stim["circle"].contains(pos):
                    rt = phase_clock.getTime()
                    wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)
                    result = make_response(
                        response=resp_val,
                        response_idx=int(resp_val) - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break
        prev_pressed = btn

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
