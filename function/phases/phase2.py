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
    make_text, build_char_equation, draw_char_equation,
)
from function.utils.response import ResponseResult, make_response, wait_for_mouse_release
from function.io.frame_logger import FrameLog, set_onset, log_frame
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

    mouse = event.Mouse(win=win)
    mouse.clickReset()

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
        win, text="", pos=(0, -100), height=cfg.P2_CHOICE_HEIGHT
    )

    for seq_num, (orig_idx, opt_text) in enumerate(opts_with_idx, start=1):
        single_opt_stim.text = opt_text
        
        phase_clock = core.Clock()
        frame_idx = 0
        
        while phase_clock.getTime() < SINGLE_OPT_DURATION:
            question_stim.draw()
            draw_char_equation(seq_eq_stims) 
            single_opt_stim.draw()
            
            flip_time = win.flip()
            
            if frame_idx == 0:
                frame_log = set_onset(frame_log, flip_time)
                marker = f"single_opt_onset_seq{seq_num}_opt{orig_idx+1}_{opt_text}"
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
            check_escape(win)
            
        # 개별 보기 제시 후 Gaussian ITI 실행
        frame_log = run_gaussian_iti(
            win=win, 
            global_clock=global_clock, 
            frame_log=frame_log, 
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
    
    # 기존 diag_radius를 x와 y로 분리
    x_radius = 350  # 가로 반경: 이 값을 키울수록 양옆으로 벌어집니다. (예: 350~400)
    y_radius = 200  # 세로 반경: 이 값을 줄일수록 위아래로 가깝게 붙습니다. (예: 150~180)
    
    angles = [135, 45, 225, 315]

    DEFAULT_LINE_COLOR = "white"
    HOVER_COLOR = "cyan" 
    TEXT_COLOR = "white"

    choice_panels = []
    choice_texts = []

    for i, opt_text in enumerate(meaning_opts):
        rad = math.radians(angles[i])
        cx = x_radius * math.cos(rad)
        cy = y_radius * math.sin(rad)
        panel_pos = (cx, cy)
        
        # 사각형 패널 
        rect = visual.Rect(
            win, width=panel_width, height=panel_height,
            pos=panel_pos, 
            lineColor=DEFAULT_LINE_COLOR, lineWidth=3,
            fillColor=None, opacity=1,
        )

        # 의미 텍스트 (사각형 정중앙 배치)
        opt_txt = make_text(win, text=opt_text, pos=panel_pos, height=cfg.P2_CHOICE_HEIGHT)
        opt_txt.color = TEXT_COLOR

        choice_panels.append(rect)
        choice_texts.append(opt_txt)

    # 내부 기록용으로는 여전히 1~4 값을 사용 (분석 파일이 꼬이지 않도록)
    resp_data = []
    for i in range(len(choice_panels)):
        resp_data.append({"rating": i + 1, "rect": choice_panels[i]})

    mouse.clickReset()
    phase_clock = core.Clock()
    frame_idx = 0
    result = make_response()
    prev_pressed = False

    while result["response"] is None and not result["timed_out"]:
        question_stim.draw()
        draw_char_equation(final_eq_stims)

        mouse_pos = mouse.getPos()
        
        # Hover 마우스 상호작용 (패널 선과 텍스트 색상 변경)
        for i in range(len(choice_panels)):
            panel = choice_panels[i]
            text = choice_texts[i]
            
            if panel.contains(mouse_pos):
                panel.lineColor = HOVER_COLOR
                text.color = HOVER_COLOR
            else:
                panel.lineColor = DEFAULT_LINE_COLOR
                text.color = TEXT_COLOR
            
            panel.draw()
            text.draw()

        flip_time = win.flip()

        if frame_idx == 0:
            frame_log = set_onset(frame_log, flip_time)
            marker = "final_choice_onset"
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
            for data in resp_data:
                resp_val = str(data["rating"])
                if data["rect"].contains(pos):
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