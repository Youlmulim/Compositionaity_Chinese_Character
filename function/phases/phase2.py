"""
phase2
----------------------------
  [top text]
      Q. If these two characters were combined to form a new character,
         what would its meaning be?

  [Sequential presentation]
      centre-top: 水 + 火 = ?
      below: (one of meaning options, 2s each, separated by Gaussian ITI)

  [Hover ITI]
      (Original hover button screen)

  [Final 4-choice rectangular grid]
      centre: 水 + 火 = ? (Moved to Y=0)
      diagonal: 4 rectangular choices at equal distance (Text inside rectangle, no numbers)
"""

import random
import math
from typing import Dict, Any, List, Tuple

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P2_MOUSE_BUTTON
from function.utils.draw_utils import (
    make_text, build_char_equation, draw_char_equation, update_button_states
)
from function.utils.progress_bar import TimeProgressBar
from function.utils.response import ResponseResult, make_response, confirm_click
from function.io.frame_logger import FrameLog, FrameRecorder
from function.utils.event_utils import check_escape
from function.utils.inter_trial import run_hover_iti, run_gaussian_iti


def run_phase2(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
    frame_log: FrameLog,
) -> Tuple[ResponseResult, FrameLog]:
    
    char1 = trial["char1"]
    char2 = trial["char2"]
    meaning_opts: List[str] = trial["meaning_opts"]

    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()

    rec = FrameRecorder(frame_log, global_clock)

    # ── 1. 순차적 제시용 자극 (수식 및 질문) 생성 ──────────────────────────────
    seq_eq_stims = build_char_equation(
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

    # ────────────────────────────────────────────────────────────────────────
    # 단계 1: 단일 선택지 순차적 제시
    # ────────────────────────────────────────────────────────────────────────
    opts_with_idx = list(enumerate(meaning_opts))
    random.shuffle(opts_with_idx)

    SINGLE_OPT_DURATION = 1.5  # 노출 시간 (2초)
    
    single_opt_stim = make_text(
        win,
        text="",
        pos=(0, -100),
        height=cfg.P2_CHOICE_HEIGHT,
        font=cfg.P23_MEANING_FONT,
    )

    for seq_num, (orig_idx, opt_text) in enumerate(opts_with_idx, start=1):
        single_opt_stim.text = opt_text

        phase_clock = core.Clock()
        rec.start_segment()
        onset_marker = f"single_opt_onset_seq{seq_num}_opt{orig_idx+1}_{opt_text}"

        while phase_clock.getTime() < SINGLE_OPT_DURATION:
            question_stim.draw()
            draw_char_equation(seq_eq_stims)
            single_opt_stim.draw()

            rec.flip_and_log(win, marker=onset_marker if rec.idx == 0 else None)
            check_escape(win)

        # 개별 보기 제시 후 Gaussian ITI 실행
        rec.frame_log = run_gaussian_iti(
            win=win,
            global_clock=global_clock,
            frame_log=rec.frame_log,
            min_t=0.6, max_t=1.8, mean_t=1.2, sd_t=0.3
        )

    # ────────────────────────────────────────────────────────────────────────
    # 단계 2: Hover ITI
    # ────────────────────────────────────────────────────────────────────────
    run_hover_iti(win)

    # ────────────────────────────────────────────────────────────────────────
    # 단계 3: 최종 응답 화면 (사각형 패널 내부에 텍스트만 배치)
    # ────────────────────────────────────────────────────────────────────────
    
    # 화면 '정중앙(Y=0)' 수식 빌드
    final_eq_stims = build_char_equation(
        win, char1, char2,
        char1_pos=(cfg.P2_EQ_CHAR1_POS[0], 0),
        plus_pos=(cfg.P2_EQ_PLUS_POS[0], 0),
        char2_pos=(cfg.P2_EQ_CHAR2_POS[0], 0),
        eq_pos=(cfg.P2_EQ_EQ_POS[0], 0),
        qmark_pos=(cfg.P2_EQ_QMARK_POS[0], 0),
    )

    # UI 디자인 변수 설정
    panel_width = 250
    panel_height = 120
    
    row_y = - 250
    panel_gap = 50

    
    n_opts = len(meaning_opts)
    step = panel_width + panel_gap
    # 전체 줄을 화면 중앙(x=0) 기준으로 정렬하기 위한 시작 x 좌표
    start_x = -(n_opts - 1) * step / 2


    choice_panels = []
    choice_texts = []

    for i, opt_text in enumerate(meaning_opts):
        cx = start_x + i * step
        cy = row_y
        panel_pos = (cx, cy)
        panel_pos = (cx, cy)
        
        # 1. 사각형 패널: 배경색(fillColor)을 흰색으로 통째로 채웁니다.
        rect = visual.Rect(
            win, width=panel_width, height=panel_height,
            pos=panel_pos, 
            lineColor="white", lineWidth=3,
            fillColor="white", opacity=1,  # 투명(None)에서 흰색으로 변경
        )

        # 2. 의미 텍스트: 흰 배경 위에 보이도록 글자 색상을 검은색으로 고정합니다.
        opt_txt = make_text(
            win,
            text=opt_text,
            pos=panel_pos,
            height=cfg.P2_CHOICE_HEIGHT,
            font=cfg.P23_MEANING_FONT,
        )
        opt_txt.color = "black"  # 색상 변경 필요 없으므로 검은색 고정

        choice_panels.append(rect)
        choice_texts.append(opt_txt)

    # update_button_states 규칙({"rect": ..., "label": ...})에 맞게 데이터 구성
    resp_data = []
    for i in range(len(choice_panels)):
        resp_data.append({
            "rect": choice_panels[i],
            "label": str(i + 1)
        })

    mouse.clickReset()
    phase_clock = core.Clock()
    # Time progress bar for response timeout visualization
    progress_bar = TimeProgressBar(win=win)
    rec.start_segment()
    result = make_response()
    prev_pressed = False
    selected_rating = None  # 선택된 라벨을 저장할 변수

    def redraw_final():
        # draw_utils.py의 함수를 그대로 호출하여 호버/선택 상태 업데이트
        update_button_states(resp_data, mouse, selected_button=selected_rating)
        question_stim.draw()
        draw_char_equation(final_eq_stims)

        for panel, txt in zip(choice_panels, choice_texts):
            panel.draw()
            txt.draw()

    while result["response"] is None and not result["timed_out"]:
        redraw_final()

        # Time progress bar 그리기
        progress_bar.draw(phase_clock.getTime())

        rec.flip_and_log(win, marker="final_choice_onset" if rec.idx == 0 else None)

        # 2. 마우스 클릭 체크 및 0.5초 대기 로직
        btn_pressed = bool(mouse.getPressed()[P2_MOUSE_BUTTON])
        if btn_pressed and not prev_pressed:
            pos = mouse.getPos()
            for data in resp_data:
                if data["rect"].contains(pos):
                    selected_rating = data["label"]  # 클릭한 선택지의 라벨("1"~"4") 저장
                    rt = float(phase_clock.getTime())

                    # 선택색을 0.5초 보여주고 마우스를 뗄 때까지 대기 (Phase 0, 1과 동일)
                    confirm_click(win, mouse, button=P2_MOUSE_BUTTON, redraw_fn=redraw_final, hold=0.5)

                    result = make_response(
                        response=selected_rating,
                        response_idx=int(selected_rating) - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break
        prev_pressed = btn_pressed

        check_escape(win)

        if cfg.MAX_RESPONSE_TIME and phase_clock.getTime() > cfg.MAX_RESPONSE_TIME:
            result = make_response(timed_out=True)

    frame_log = rec.log_final(win, result)
    return result, frame_log
