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
    make_text, build_char_equation, draw_char_equation, update_button_states,
    warm_up_frame,
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

    SINGLE_OPT_DURATION = 1.5  # 노출 시간
    
    single_opt_stim = make_text(
        win,
        text="",
        pos=(0, -100),
        height=cfg.P2_CHOICE_HEIGHT,
        font=cfg.P23_MEANING_FONT,
    )

    # [수정] Clock 객체는 단 한 번만 생성하여 재사용 (메모리 파편화 및 드롭 방지)
    phase_clock = core.Clock()

    for seq_num, (orig_idx, opt_text) in enumerate(opts_with_idx, start=1):
        single_opt_stim.text = opt_text

        def draw_single_option():
            question_stim.draw()
            draw_char_equation(seq_eq_stims)
            single_opt_stim.draw()

        warm_up_frame(win, draw_single_option)

        rec.start_segment()
        onset_marker = f"single_opt_onset_seq{seq_num}_opt{orig_idx+1}_{opt_text}"
        
        # 각 시퀀스 시작 전 시계 초기화 (임시 구동용)
        phase_clock.reset()

        while phase_clock.getTime() < SINGLE_OPT_DURATION:
            draw_single_option()

            rec.flip_and_log(win, marker=onset_marker if rec.idx == 0 else None)
            
            # [수정] 첫 번째 자극 프레임이 화면에 완전히 출력(V-Sync 완료)된 직후 시계 리셋
            if rec.idx == 1:
                phase_clock.reset()
                
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
    final_eq_stims = build_char_equation(
        win, char1, char2,
        char1_pos=(cfg.P2_EQ_CHAR1_POS[0], 0),
        plus_pos=(cfg.P2_EQ_PLUS_POS[0], 0),
        char2_pos=(cfg.P2_EQ_CHAR2_POS[0], 0),
        eq_pos=(cfg.P2_EQ_EQ_POS[0], 0),
        qmark_pos=(cfg.P2_EQ_QMARK_POS[0], 0),
    )

    panel_width = 250
    panel_height = 120
    panel_positions = [(-200, -180), (200, -180)]

    choice_panels = []
    choice_texts = []

    for i, opt_text in enumerate(meaning_opts):
        panel_pos = panel_positions[i]
        rect = visual.Rect(
            win, width=panel_width, height=panel_height,
            pos=panel_pos, 
            lineColor="white", lineWidth=3,
            fillColor="white", opacity=1,
        )
        opt_txt = make_text(
            win,
            text=opt_text,
            pos=panel_pos,
            height=cfg.P2_CHOICE_HEIGHT,
            font=cfg.P23_MEANING_FONT,
        )
        opt_txt.color = "black"

        choice_panels.append(rect)
        choice_texts.append(opt_txt)

    resp_data = []
    for i in range(len(choice_panels)):
        resp_data.append({
            "rect": choice_panels[i],
            "label": str(i + 1)
        })

    mouse.clickReset()
    
    # 최종 응답용으로 클록 리셋
    phase_clock.reset()
    progress_bar = TimeProgressBar(win=win)
    rec.start_segment()
    result = make_response()
    prev_pressed = False
    selected_rating = None

    def redraw_final():
        update_button_states(resp_data, mouse, selected_button=selected_rating)
        question_stim.draw()
        draw_char_equation(final_eq_stims)

        for panel, txt in zip(choice_panels, choice_texts):
            panel.draw()
            txt.draw()

    # Prepare the neutral and every possible selected-feedback state before
    # the final-choice onset.
    warm_up_frame(win, redraw_final)
    for data in resp_data:
        selected_rating = data["label"]
        warm_up_frame(win, redraw_final)
    selected_rating = None

    while result["response"] is None and not result["timed_out"]:
        redraw_final()

        # [수정] 첫 번째 flip(idx==0)이 완전히 끝나 모니터에 자극이 켜지기 전까지는 
        # 진행바에 0초를 강제 주입하여 비정상적인 게이지 튐 및 연산 부하 방지
        current_time = phase_clock.getTime() if rec.idx > 0 else 0.0
        progress_bar.draw(elapsed_time=current_time)

        rec.flip_and_log(win, marker="final_choice_onset" if rec.idx == 0 else None)

        # [수정] 자극이 모니터에 처음 켜진 바로 그 순간 RT 시계를 0.000초로 고정
        if rec.idx == 1:
            phase_clock.reset()

        btn_pressed = bool(mouse.getPressed()[P2_MOUSE_BUTTON])
        if btn_pressed and not prev_pressed:
            pos = mouse.getPos()
            for data in resp_data:
                if data["rect"].contains(pos):
                    selected_rating = data["label"]
                    # 순수 자극 등장 기점(0ms)으로부터의 RT 정확히 측정
                    rt = float(phase_clock.getTime())

                    confirm_click(win, mouse, button=P2_MOUSE_BUTTON, redraw_fn=redraw_final, hold=0.5, phase="phase2", rec=rec)

                    result = make_response(
                        response=selected_rating,
                        response_idx=int(selected_rating) - 1,
                        rt=rt,
                        raw_key="mouse",
                    )
                    break
        prev_pressed = btn_pressed

        check_escape(win)

        # 타임아웃 계산도 정렬된 시계 기준으로 처리
        if cfg.MAX_RESPONSE_TIME and phase_clock.getTime() > cfg.MAX_RESPONSE_TIME:
            result = make_response(timed_out=True)

    frame_log = rec.log_final(win, result)
    return result, frame_log
