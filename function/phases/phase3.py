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
from function.utils.response import ResponseResult, make_response
from function.io.frame_logger import FrameLog, FrameRecorder
from function.utils.event_utils import check_escape
from function.utils.progress_bar import TimeProgressBar
from function.utils.draw_marker import draw_marker
from function.utils.sounds import preload_sound, schedule_sound


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
    char1, char2 = trial["char1"], trial["char2"]

    # Get meaning from phase2 response (use corrected key)
    if trial.get("phase2_response"):
        response_idx = int(trial["phase2_response"]) - 1
        meaning = trial["meaning_opts"][response_idx]
    else:
        meaning = trial.get("meaning", "?")

    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()

    # Load/decode once before the frame loop. ``preload_sound`` is cached, so
    # all later Phase 3 trials reuse the same in-memory Sound object.
    response_sound = preload_sound("sound_effect.wav")

    # ── Build stimuli ──────────────────────────────────────────────────────────
    question_stim = make_text(
        win,
        cfg.P3_QUESTION,
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
        color="black",
        font=cfg.P23_MEANING_FONT,
    )

    # Create 5 circles in cross pattern AND pre-load character stimuli
    circles = {}
    for pos_name, offset in cfg.P3_POSITIONS.items():
        circle_pos = (cfg.P3_CROSS_CENTER[0] + offset[0], cfg.P3_CROSS_CENTER[1] + offset[1])
        
        # [최적화] 각 위치별로 배치될 글자 스티뮬러스를 루프 밖에서 미리 모두 생성해 둡니다.
        char1_placed_stim = make_chinese_char(win, char1, pos=circle_pos, size=80)
        char2_placed_stim = make_chinese_char(win, char2, pos=circle_pos, size=80)
        char1_placed_stim.color = "white"
        char2_placed_stim.color = "white"
        
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
            # [최적화] 미리 생성한 스티뮬러스를 딕셔너리에 저장합니다.
            "char_stims": {
                "char1": char1_placed_stim,
                "char2": char2_placed_stim
            }
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
    result = make_response()
    prev_pressed = False

    progress_bar = TimeProgressBar(win=win)
    rec = FrameRecorder(frame_log, global_clock)

    # 완료 시간을 기록할 변수 초기화
    completion_time = None
    completion_delay = 0.5
    # 응답(배치 완료) 시점의 rec.idx를 기록 — 여기서부터 몇 프레임 동안 마커를 켤지 계산하는 기준점
    response_frame_start = None

    while result["response"] is None and not result["timed_out"]:
        # ── Update visual states ──────────────────────────────────────────────
        mouse_pos = mouse.getPos()
        
        # [최적화] 매 프레임 리스트 생성을 피하기 위해 한 번만 캐싱합니다.
        placed_chars = list(state["placements"].values())

        # Selected character follows the mouse cursor
        if state["selected_char"] == "char1":
            char1_stim.pos = mouse_pos # 선택한 mouse 위치가 char1의 위치가 됨. 
        elif state["selected_char"] == "char2":
            char2_stim.pos = mouse_pos
        else:
            char1_stim.pos = cfg.P3_CHAR1_POS
            char2_stim.pos = cfg.P3_CHAR2_POS

        # [최적화] 인자로 캐싱해둔 placed_chars를 넘깁니다.
        char1_color, char1_opacity = get_char_color(state, "char1", mouse_pos, cfg.P3_CHAR1_POS, placed_chars)
        char2_color, char2_opacity = get_char_color(state, "char2", mouse_pos, cfg.P3_CHAR2_POS, placed_chars)

        char1_stim.color = char1_color
        char1_stim.opacity = char1_opacity

        char2_stim.color = char2_color
        char2_stim.opacity = char2_opacity


        # Update circle colors and placed characters
        center_filled = state["placements"]["CENTER"] is not None # center circle에서 char이 채워짐.
        selected = state["selected_char"] is not None  # char가 선택됨

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
                        circle_color = "purple"
                    else:
                        circle_color = "white"
            else:
                # 처음부터 CENTER는 보라색으로 표시
                circle_color = "purple" if pos_name == "CENTER" else "white"

            circle_data["stim"].lineColor = circle_color

            # [최적화] 배치된 글자 처리는 그리기(draw) 단계에서 미리 생성된 객체를 사용하므로, 
            # 여기서는 원의 투명도만 조절합니다.
            if placed_char:
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

        # [최적화] 이미 배치된 글자 그리기 (미리 생성해둔 객체 사용)
        for pos_name, circle_data in circles.items():
            placed_char = state["placements"][pos_name]
            if placed_char:
                if selected and is_hovering(mouse_pos, circle_data["pos"], cfg.P3_CIRCLE_RADIUS):
                    continue
                # 미리 만들어둔 객체를 가져와 draw()만 호출 (연산 비용 대폭 감소)
                circle_data["char_stims"][placed_char].draw()

        progress_bar.draw(elapsed_time=phase_clock.getTime())

        # 응답(두 글자 배치 완료) 시점부터 MARKER_FRAMES_RESPONSE["phase3"] 프레임 동안 마커 표시.
        # rec.flip_and_log()가 그리는 onset 마커와는 별개로, 응답 시점 마커는 여기서 직접 그린다.
        if response_frame_start is not None:
            n_resp_frames = cfg.MARKER_FRAMES_RESPONSE.get("phase3", 0)
            if (rec.idx - response_frame_start) < n_resp_frames:
                draw_marker(win)

        rec.flip_and_log(
            win,
            marker="phase3_response_onset" if rec.idx == response_frame_start else None,
        )

        if rec.idx == 1:
            phase_clock.reset()

        # ── Handle mouse clicks ───────────────────────────────────────────────
        btn = bool(mouse.getPressed()[P3_MOUSE_BUTTON])

        #  실험이 완료되어 지연 중이 아닐 때만 처리
        if completion_time is None:
            if btn and not prev_pressed:
                rt = phase_clock.getTime()

                # Check if clicking on char1 (right side)
                if is_hovering(mouse_pos, cfg.P3_CHAR1_POS, 60) and "char1" not in placed_chars:
                    if state["selected_char"] == "char1":
                        state["selected_char"] = None
                    elif state["selected_char"] == None:
                        state["selected_char"] = "char1"

                # Check if clicking on char2 (right side)
                elif is_hovering(mouse_pos, cfg.P3_CHAR2_POS, 60) and "char2" not in placed_chars:
                    if state["selected_char"] == "char2":
                        # 이미 들고 있는 상태에서 원래 자리를 클릭하면 내려놓기(취소)
                        state["selected_char"] = None
                    elif state["selected_char"] is None:
                        # 빈 손일 때는 집어들기
                        state["selected_char"] = "char2"

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
                                # [최적화] 동적 객체 삭제가 더 이상 필요하지 않아 제거되었습니다.

                            break

        # 마우스에서 손을 떼었을 때 prev_pressed 상태가 False로 갱신
        prev_pressed = btn
        check_escape(win)

        # ── 논블로킹 타이머 로직 (자동 넘김 지연 처리) ────────────────────────────────
        if is_complete(state):
            if completion_time is None:
                # Reserve playback for the exact response-completion time.
                # Scheduling is non-blocking and performs no file I/O here.
                completion_time = phase_clock.getTime()
                response_frame_start = rec.idx
                schedule_sound(response_sound, delay=completion_delay)
                
            elif phase_clock.getTime() - completion_time >= completion_delay:
                # 완료 후 feedback delay가 경과 -> 루프 탈출
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

    frame_log = rec.log_final(win, result)
    return result, frame_log


# ─── Helper functions ────────────────────────────────────────────────────────

# [최적화] 매 프레임 dict.values() 호출을 방지하기 위해 placed_chars 매개변수를 추가했습니다.
def get_char_color(state: Dict[str, Any], char_name: str, mouse_pos: Tuple[float, float], char_pos: Tuple[float, float], placed_chars: list) -> str:
    """Determine display color for a character based on state."""

    # 이미 왼쪽 원에 배치된 경우
    if char_name in placed_chars:
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
