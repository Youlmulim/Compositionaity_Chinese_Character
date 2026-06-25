from psychopy import core, event, visual, gui
from function.config import settings as cfg
from function.utils.draw_utils import make_button, update_button_states


# ─────────────────────────────────────────────────────────────────────────────
# 0. Subject info dialog
# ─────────────────────────────────────────────────────────────────────────────

def get_subject_info():
    dlg = gui.Dlg(title="Chinese Character Experiment")
    dlg.addField("Subject ID:", "001")
    dlg.addField("Session:",    "1")
    data = dlg.show()
    if not dlg.OK:
        core.quit()
    return {
        "subject_id": data[0].strip(),
        "session":    data[1].strip(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Instructions screen helper
# ─────────────────────────────────────────────────────────────────────────────

def show_instructions(win, text: str):
    msg = visual.TextStim(
        win,
        text=text,
        font=cfg.FONT,
        pos=(0, 0),
        height=38,
        color="white",
        wrapWidth=1400,
    )
    msg.draw()
    win.flip()
    event.waitKeys(keyList=["space"])   # press space to continue


def show_practice_screen(win, text: str) -> str:
    """
    연습 안내 화면을 표시합니다. Exit 버튼이 함께 표시됩니다.

    Returns
    -------
    "continue"  : 스페이스바 → 다음 연습 trial 시작
    "exit"      : Exit 버튼 클릭 → 본 실험으로 이동
    """
    msg = visual.TextStim(
        win,
        text=text,
        font=cfg.FONT,
        pos=(0, 100),
        height=38,
        color="white",
        wrapWidth=1400,
    )

    exit_rect, exit_txt = make_button(
        win,
        label=cfg.PRACTICE_EXIT_LABEL,
        pos=cfg.PRACTICE_EXIT_BTN_POS,
    )

    exit_button = {"rect": exit_rect, "label": "exit"}
    mouse = event.Mouse(visible=True, win=win)
    mouse.clickReset()
    prev_pressed = False

    while True:
        # 버튼 hover 상태 업데이트 후 draw
        update_button_states([exit_button], mouse, selected_button=None)
        msg.draw()
        exit_rect.draw()
        exit_txt.draw()
        win.flip()

        # Exit 버튼 클릭 감지
        btn = bool(mouse.getPressed()[0])
        if btn and not prev_pressed:
            if exit_rect.contains(mouse.getPos()):
                return "exit"
        prev_pressed = btn

        # 스페이스바 → 연습 계속
        keys = event.getKeys(keyList=["space", "escape"])
        if "escape" in keys:
            core.quit()
        if "space" in keys:
            return "continue"



