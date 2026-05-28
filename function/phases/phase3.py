"""
phase3: Click-and-paste character arrangement task
---------------------------------------------------
Participants place two characters (char1, char2) into positions in a cross pattern.
Interaction: Click a character on the right → select it (purple).
            Click a circle position on the left → place it (green for target).
            Click a placed character → pick it back up (undo).
"""

from typing import Dict, Any, Tuple, Optional

from psychopy import visual, core, event

from function.config import settings as cfg
from function.config.key_mapping import P3_MOUSE_BUTTON
from function.utils.draw_utils import make_text, make_chinese_char, is_hovering
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
    Display Phase 3: Click-and-paste character arrangement.
    Participant places char1 and char2 into correct positions.

    Parameters
    ----------
    win          : PsychoPy Window
    trial        : trial dict; must contain "char1", "char2", "meaning_opts", "phase2_response"
    global_clock : experiment-wide clock
    frame_log    : pre-initialised FrameLog

    Returns
    -------
    (ResponseResult, FrameLog)  — response is "{char1_pos}_{char2_pos}"
    """
    char1 = trial["char1"]
    char2 = trial["char2"]

    # Get meaning from phase2 response (use corrected key)
    if trial.get("phase2_response"):
        response_idx = int(trial["phase2_response"]) - 1
        meaning = trial["meaning_opts"][response_idx]
    else:
        meaning = trial.get("meaning", "?")

    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()

    # ── Build stimuli ──────────────────────────────────────────────────────────
    question_stim = make_text(
        win,
        "Q. These two characters combine to convey the meaning below.\n"
        "Click a character on the right, then click a position to place it.",
        pos=(0, 390),
        height=28,
        align_horiz="center",
    )

    meaning_bg = visual.Rect(
        win,
        width=260, height=65,
        pos=cfg.P3_MEANING_BOX_POS,
        fillColor="white",
        lineColor="white",
    )
    meaning_txt = make_text(
        win,
        meaning,
        pos=cfg.P3_MEANING_BOX_POS,
        height=34,
        color="black"
    )

    # Create 5 circles in cross pattern
    circles = {}
    for pos_name, offset in cfg.P3_POSITIONS.items():
        circle_pos = (cfg.P3_CROSS_CENTER[0] + offset[0], cfg.P3_CROSS_CENTER[1] + offset[1])
        circles[pos_name] = {
            "stim": visual.Circle(
                win,
                radius=cfg.P3_CIRCLE_RADIUS,
                pos=circle_pos,
                fillColor=None,
                lineColor="white",
                lineWidth=3,
            ),
            "pos": circle_pos,
            "char_stim": None,
        }

    # Create character stimuli on the right (clickable)
    char1_stim = make_chinese_char(win, char1, pos=cfg.P3_CHAR1_POS, size=100)
    char2_stim = make_chinese_char(win, char2, pos=cfg.P3_CHAR2_POS, size=100)

    # State: tracking selection and placements
    state = {
        "selected_char": None,
        "placements": {pos: None for pos in circles.keys()},
    }

    # ── Main flip loop ───────────────────────────────────────────────────────────
    phase_clock = core.Clock()
    frame_idx = 0
    result = make_response()
    prev_pressed = False

    progress_bar = TimeProgressBar(win=win)

    # 완료 시간을 기록할 변수 초기화
    completion_time = None

    while result["response"] is None and not result["timed_out"]:
        # ── Update visual states ──────────────────────────────────────────────
        mouse_pos = mouse.getPos()

        # Selected character follows the mouse cursor
        if state["selected_char"] == "char1":
            char1_stim.pos = mouse_pos
        elif state["selected_char"] == "char2":
            char2_stim.pos = mouse_pos
        else:
            char1_stim.pos = cfg.P3_CHAR1_POS
            char2_stim.pos = cfg.P3_CHAR2_POS

        char1_color, char1_opacity = get_char_color(state, "char1", mouse_pos, cfg.P3_CHAR1_POS)
        char2_color, char2_opacity = get_char_color(state, "char2", mouse_pos, cfg.P3_CHAR2_POS)

        char1_stim.color = char1_color
        char1_stim.opacity = char1_opacity

        char2_stim.color = char2_color
        char2_stim.opacity = char2_opacity


        # Update circle colors and placed characters
        center_filled = state["placements"]["CENTER"] is not None
        selected = state["selected_char"] is not None

        for pos_name, circle_data in circles.items():
            placed_char = state["placements"][pos_name]

            if placed_char:
                # CENTER turns white when second char is selected; others stay purple
                if pos_name == "CENTER" and selected and center_filled:
                    circle_color = "white"
                else:
                    circle_color = "purple"

            elif selected:
                if not center_filled:
                    # First selection: only CENTER is highlighted (purple); others disabled
                    circle_color = "purple" if pos_name == "CENTER" else "white"
                else:
                    # Second selection: normal hover behavior for all positions
                    if is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS):
                        circle_color = "green"
                    else:
                        circle_color = "white"
            else:
                # 처음부터 CENTER는 보라색으로 표시
                circle_color = "purple" if pos_name == "CENTER" else "white"

            circle_data["stim"].lineColor = circle_color

            # 배치된 글자
            if placed_char:
                displayed_char = char1 if placed_char == "char1" else char2
                if circle_data["char_stim"] is None:
                    circle_data["char_stim"] = make_chinese_char(
                        win, displayed_char, pos=circle_data["pos"], size=80
                    )
                
                # 배치된 글자의 색상과 원의 테두리 투명도
                circle_data["char_stim"].color = "white"
                circle_data["stim"].opacity = 0
            else:
                circle_data["stim"].opacity = 1

        # ── Draw everything ─────────────────────────────────────────────────
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
            
        # ── Handle mouse clicks ───────────────────────────────────────────────
        btn = bool(mouse.getPressed()[P3_MOUSE_BUTTON])

        #  실험이 완료되어 지연 중이 아닐 때만 처리
        if completion_time is None:
            if btn and not prev_pressed:
                rt = phase_clock.getTime()

                # Check if clicking on char1 (right side)
                if is_hovering(mouse_pos, cfg.P3_CHAR1_POS, 60) and "char1" not in state["placements"].values():
                    state["selected_char"] = "char1"
                    wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)

                # Check if clicking on char2 (right side)
                elif is_hovering(mouse_pos, cfg.P3_CHAR2_POS, 60) and "char2" not in state["placements"].values():
                    state["selected_char"] = "char2"
                    wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)

                # Check if clicking on a circle position
                else:
                    _center_filled = state["placements"]["CENTER"] is not None
                    for pos_name, circle_data in circles.items():
                        if is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS):
                            # First placement must go to CENTER
                            if state["selected_char"] and not _center_filled and pos_name != "CENTER":
                                break

                            placed_char = state["placements"][pos_name]

                            if state["selected_char"]:
                                state["placements"][pos_name] = state["selected_char"]
                                state["selected_char"] = None

                            elif placed_char:
                                state["selected_char"] = placed_char
                                state["placements"][pos_name] = None
                                circle_data["char_stim"] = None  # clear stim to remove residue

                            wait_for_mouse_release(mouse, P3_MOUSE_BUTTON)
                            break

        # 마우스에서 손을 떼었을 때 prev_pressed 상태가 False로 갱신
        prev_pressed = btn
        check_escape(win)

        # ── 논블로킹 타이머 로직 (자동 넘김 지연 처리) ────────────────────────────────
        if is_complete(state):
            if completion_time is None:
                # 0.5 counting start
                completion_time = phase_clock.getTime()
                
            elif phase_clock.getTime() - completion_time >= 0.5:
                # 완료 후 0.5초가 경과 -> 루프 탈출
                char1_pos = [k for k, v in state["placements"].items() if v == "char1"][0]
                char2_pos = [k for k, v in state["placements"].items() if v == "char2"][0]
                response_str = f"{char1_pos}_{char2_pos}"

                result = make_response(
                    response=response_str,
                    response_idx=0,
                    rt=completion_time, # '완료된 순간' 기록
                    raw_key="mouse",
                )

        # Check for timeout
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


# ─── Helper functions ────────────────────────────────────────────────────────

def get_char_color(state: Dict[str, Any], char_name: str, mouse_pos: Tuple[float, float], char_pos: Tuple[float, float]) -> str:
    """Determine display color for a character based on state."""

    # 이미 왼쪽 원에 배치된 경우
    if char_name in state["placements"].values():
        return "white", 0.0

    # 마우스 선택해서 들고 이동중
    if state["selected_char"] == char_name:
        return "purple", 1.0

    # 마우스 글자 위에 올라간 경우
    if is_hovering(mouse_pos, char_pos, 60):
        return "purple", 1.0

    # 아무 상호작용이 없는 기본 대기 상태
    return "white", 1.0


def is_complete(state: Dict[str, Any]) -> bool:
    """Check if both characters are placed."""
    placed = list(state["placements"].values())
    return "char1" in placed and "char2" in placed