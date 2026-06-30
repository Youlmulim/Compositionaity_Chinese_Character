"""
practice_phase2.py
------------------
Phase 2 연습용 — 최종 4선택지 화면만 표시합니다.
순차 제시(선택지 하나씩), Gaussian ITI, Hover ITI 없음.
타이머와 데이터 저장 없음.
"""

from typing import Dict, Any, List

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P2_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text, build_char_equation, draw_char_equation, update_button_states,
)
from function.utils.response import ResponseResult, make_response, confirm_click
from function.utils.event_utils import check_escape


def run_practice_phase2(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
) -> ResponseResult:
    """
    연습용 Phase 2 trial — 최종 선택 화면만 표시합니다.

    Returns
    -------
    ResponseResult — response는 "1"~"4" (의미 선택지 인덱스)
    """
    char1 = trial["char1"]
    char2 = trial["char2"]
    meaning_opts: List[str] = trial["meaning_opts"]

    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()

    # ── 수식 (화면 중앙 Y=0) ───────────────────────────────────────────────────
    eq_stims = build_char_equation(
        win, char1, char2,
        char1_pos=(cfg.P2_EQ_CHAR1_POS[0], 0),
        plus_pos=(cfg.P2_EQ_PLUS_POS[0], 0),
        char2_pos=(cfg.P2_EQ_CHAR2_POS[0], 0),
        eq_pos=(cfg.P2_EQ_EQ_POS[0], 0),
        qmark_pos=(cfg.P2_EQ_QMARK_POS[0], 0),
        stim_dir=cfg.STIMULI_PRAC_DIR,
    )

    question_stim = make_text(
        win,
        cfg.P2_QUESTION,
        pos=cfg.P2_QUESTION_POS,
        height=cfg.P2_QUESTION_HEIGHT,
        align_horiz="center",
    )

    # ── 선택지 패널 ────────────────────────────────────────────────────────────
    panel_width  = 250
    panel_height = 120
    row_y        = -250
    panel_gap    = 100

    n_opts = len(meaning_opts)
    step   = panel_width + panel_gap
    start_x = -(n_opts - 1) * step / 2

    choice_panels = []
    choice_texts  = []

    for i, opt_text in enumerate(meaning_opts):
        cx = start_x + i * step
        panel_pos = (cx, row_y)

        rect = visual.Rect(
            win, width=panel_width, height=panel_height,
            pos=panel_pos,
            lineColor="white", lineWidth=3,
            fillColor="white", opacity=1,
        )
        opt_txt = make_text(
            win, text=opt_text, pos=panel_pos,
            height=cfg.P2_CHOICE_HEIGHT,
            font=cfg.P23_MEANING_FONT,
        )
        opt_txt.color = "black"

        choice_panels.append(rect)
        choice_texts.append(opt_txt)

    resp_data = [{"rect": choice_panels[i], "label": str(i + 1)} for i in range(n_opts)]

    # ── 응답 루프 ──────────────────────────────────────────────────────────────
    phase_clock     = core.Clock()
    result          = make_response()
    prev_pressed    = False
    selected_rating = None

    def redraw():
        update_button_states(resp_data, mouse, selected_button=selected_rating)
        question_stim.draw()
        draw_char_equation(eq_stims)
        for panel, txt in zip(choice_panels, choice_texts):
            panel.draw()
            txt.draw()

    while result["response"] is None:
        redraw()
        win.flip()

        btn = bool(mouse.getPressed()[P2_MOUSE_BUTTON])
        if btn and not prev_pressed:
            pos = mouse.getPos()
            for data in resp_data:
                if data["rect"].contains(pos):
                    selected_rating = data["label"]
                    rt = float(phase_clock.getTime())
                    confirm_click(win, mouse, button=P2_MOUSE_BUTTON, redraw_fn=redraw, hold=0.5)
                    result = make_response(
                        response=selected_rating,
                        response_idx=int(selected_rating) - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break
        prev_pressed = btn

        check_escape(win)

    return result
