"""
practice_phase3.py
------------------
Phase 3 연습용 — click-and-paste 배치 과제.
타이머(TimeProgressBar)와 데이터 저장(FrameLog) 없음.
로직은 phase3.py와 동일합니다.
"""

from typing import Dict, Any, Tuple

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P3_MOUSE_BUTTON
from function.utils.draw_utils import make_text, make_chinese_char, is_hovering
from function.utils.response import ResponseResult, make_response, wait_for_mouse_release
from function.utils.event_utils import check_escape


def run_practice_phase3(
    win: visual.Window,
    trial: Dict[str, Any],
    global_clock: core.Clock,
) -> ResponseResult:
    """
    연습용 Phase 3 trial — click-and-paste 배치.

    Parameters
    ----------
    trial : "char1", "char2", "meaning_opts", "phase2_response" 키 필요
            phase2_response가 없으면 meaning = "?" 로 폴백.

    Returns
    -------
    ResponseResult — response는 "{char1_pos}_{char2_pos}"
    """
    char1, char2 = trial["char1"], trial["char2"]

    if trial.get("phase2_response"):
        response_idx = int(trial["phase2_response"]) - 1
        meaning = trial["meaning_opts"][response_idx]
    else:
        meaning = trial.get("meaning", "?")

    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()

    # ── 자극 생성 ──────────────────────────────────────────────────────────────
    question_stim = make_text(
        win, cfg.P3_QUESTION, pos=(0, 390), height=28, align_horiz="center",
    )

    meaning_bg = visual.Rect(
        win, width=260, height=65,
        pos=cfg.P3_MEANING_BOX_POS,
        fillColor="white", lineColor="white",
    )
    meaning_txt = make_text(
        win, meaning, pos=cfg.P3_MEANING_BOX_POS,
        height=34, color="black", font=cfg.P23_MEANING_FONT,
    )

    circles = {}
    for pos_name, offset in cfg.P3_POSITIONS.items():
        circle_pos = (cfg.P3_CROSS_CENTER[0] + offset[0], cfg.P3_CROSS_CENTER[1] + offset[1])
        circles[pos_name] = {
            "stim": visual.Circle(
                win, radius=cfg.P3_CIRCLE_RADIUS, pos=circle_pos,
                fillColor=None, lineColor="white", lineWidth=3,
            ),
            "pos": circle_pos,
            "char_stim": None,
        }

    char1_stim = make_chinese_char(win, char1, pos=cfg.P3_CHAR1_POS, size=100, stim_dir=cfg.STIMULI_PRAC_DIR)
    char2_stim = make_chinese_char(win, char2, pos=cfg.P3_CHAR2_POS, size=100, stim_dir=cfg.STIMULI_PRAC_DIR)

    state = {
        "selected_char": None,
        "placements": {pos: None for pos in circles.keys()},
    }

    # ── 응답 루프 ──────────────────────────────────────────────────────────────
    phase_clock     = core.Clock()
    result          = make_response()
    prev_pressed    = False
    completion_time = None

    while result["response"] is None:
        mouse_pos = mouse.getPos()

        if state["selected_char"] == "char1":
            char1_stim.pos = mouse_pos
        elif state["selected_char"] == "char2":
            char2_stim.pos = mouse_pos
        else:
            char1_stim.pos = cfg.P3_CHAR1_POS
            char2_stim.pos = cfg.P3_CHAR2_POS

        char1_color, char1_opacity = _get_char_color(state, "char1", mouse_pos, cfg.P3_CHAR1_POS)
        char2_color, char2_opacity = _get_char_color(state, "char2", mouse_pos, cfg.P3_CHAR2_POS)
        char1_stim.color   = char1_color
        char1_stim.opacity = char1_opacity
        char2_stim.color   = char2_color
        char2_stim.opacity = char2_opacity

        center_filled = state["placements"]["CENTER"] is not None
        selected      = state["selected_char"] is not None

        for pos_name, circle_data in circles.items():
            placed_char = state["placements"][pos_name]

            if placed_char:
                if pos_name == "CENTER" and selected and center_filled:
                    circle_color = "white"
                else:
                    circle_color = "purple"
            elif selected:
                if not center_filled:
                    circle_color = "purple" if pos_name == "CENTER" else "white"
                else:
                    circle_color = "purple" if is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS) else "white"
            else:
                circle_color = "purple" if pos_name == "CENTER" else "white"

            circle_data["stim"].lineColor = circle_color

            if placed_char:
                displayed_char = char1 if placed_char == "char1" else char2
                if circle_data["char_stim"] is None:
                    circle_data["char_stim"] = make_chinese_char(
                        win, displayed_char, pos=circle_data["pos"], size=80,
                        stim_dir=cfg.STIMULI_PRAC_DIR,
                    )
                circle_data["char_stim"].color = "white"
                circle_data["stim"].opacity = 0
            else:
                circle_data["stim"].opacity = 1

        # ── 그리기 ─────────────────────────────────────────────────────────────
        question_stim.draw()
        meaning_bg.draw()
        meaning_txt.draw()

        for circle_data in circles.values():
            circle_data["stim"].draw()

        char1_stim.draw()
        char2_stim.draw()

        for pos_name, circle_data in circles.items():
            if circle_data["char_stim"] and state["placements"][pos_name]:
                if selected and is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS):
                    continue
                circle_data["char_stim"].draw()

        win.flip()

        # ── 클릭 처리 ──────────────────────────────────────────────────────────
        btn = bool(mouse.getPressed()[P3_MOUSE_BUTTON])

        if completion_time is None:
            if btn and not prev_pressed:
                if is_hovering(mouse_pos, cfg.P3_CHAR1_POS, 60) and "char1" not in state["placements"].values():
                    if state["selected_char"] == "char1":
                        state["selected_char"] = None
                    elif state["selected_char"] is None:
                        state["selected_char"] = "char1"
                    wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)

                elif is_hovering(mouse_pos, cfg.P3_CHAR2_POS, 60) and "char2" not in state["placements"].values():
                    if state["selected_char"] == "char2":
                        state["selected_char"] = None
                    elif state["selected_char"] is None:
                        state["selected_char"] = "char2"
                    wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)

                else:
                    _center_filled = state["placements"]["CENTER"] is not None
                    for pos_name, circle_data in circles.items():
                        if is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS):
                            if state["selected_char"] and not _center_filled and pos_name != "CENTER":
                                break
                            placed_char = state["placements"][pos_name]
                            if state["selected_char"]:
                                state["placements"][pos_name] = state["selected_char"]
                                state["selected_char"] = None
                            elif placed_char:
                                state["selected_char"] = placed_char
                                state["placements"][pos_name] = None
                                circle_data["char_stim"] = None
                            wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)
                            break

        prev_pressed = btn
        check_escape(win)

        # ── 완료 감지 (0.5초 지연 후 루프 종료) ───────────────────────────────
        if _is_complete(state):
            if completion_time is None:
                completion_time = phase_clock.getTime()
            elif phase_clock.getTime() - completion_time >= 0.5:
                char1_pos = [k for k, v in state["placements"].items() if v == "char1"][0]
                char2_pos = [k for k, v in state["placements"].items() if v == "char2"][0]
                result = make_response(
                    response=f"{char1_pos}_{char2_pos}",
                    response_idx=0,
                    rt=completion_time,
                    raw_key="mouse",
                )

    return result


# ─── 헬퍼 ────────────────────────────────────────────────────────────────────

def _get_char_color(
    state: Dict[str, Any],
    char_name: str,
    mouse_pos: Tuple,
    char_pos: Tuple,
) -> Tuple[str, float]:
    if char_name in state["placements"].values():
        return "white", 0.0
    if state["selected_char"] == char_name:
        return "purple", 1.0
    if is_hovering(mouse_pos, char_pos, 60):
        return "purple", 1.0
    return "white", 1.0


def _is_complete(state: Dict[str, Any]) -> bool:
    placed = list(state["placements"].values())
    return "char1" in placed and "char2" in placed
