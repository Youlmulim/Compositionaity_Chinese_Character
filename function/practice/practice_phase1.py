"""
practice_trial.py
-----------------
Phase 1

Screen layout
-------------
  [top]    Q. 두 한자가 합쳐져 새로운 한자가 될 수 있습니까?

  [centre]        水   +   火   =   ?

  [bottom]   [ 是 ]                 [ 否 ]
"""

from typing import Dict, Any

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P1_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text,
    make_button,
    build_char_equation,
    draw_char_equation,
    update_button_states,
)
from function.utils.response import ResponseResult, make_response, confirm_click
from function.utils.event_utils import check_escape


def run_practice_trial(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
) -> ResponseResult:
    
    char1 = trial["char1"]
    char2 = trial["char2"]
    mouse = event.Mouse(visible=True, win=win)

    # ── 자극 생성 ──────────────────────────────────────────────────────────────
    question_stim = make_text(win, cfg.P1_QUESTION, pos=(0, 380), height=38)

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

    clickable       = [(yes_rect, "yes"), (no_rect, "no")]
    phase_clock     = core.Clock()
    result          = make_response()
    prev_pressed    = False
    selected_button = None
    mouse.clickReset()

    def redraw():
        update_button_states(buttons, mouse, selected_button)
        question_stim.draw()
        draw_char_equation(eq_stims)
        yes_rect.draw(); yes_txt.draw()
        no_rect.draw();  no_txt.draw()

    # ── 응답 대기 루프 (시간 제한 없음) ───────────────────────────────────────
    while result["response"] is None:
        redraw()
        win.flip()

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

    return result
