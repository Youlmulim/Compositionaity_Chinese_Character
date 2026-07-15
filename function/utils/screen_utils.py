from psychopy import core, event, visual, gui
from function.config import settings as cfg
from function.utils.draw_utils import make_button, update_button_states
from function.utils.sounds import preload_sound, schedule_sound


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
    Display the practice instruction screen with an Exit button.

    Returns
    -------
    "continue"  : press Space to start the next practice trial
    "exit"      : click Exit to proceed to the main experiment
    """
    # Decode before the screen's frame loop. Later calls reuse the cached Sound.
    quit_sound = preload_sound("sound_effect_quit.wav")

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
        # Update the button hover state before drawing.
        update_button_states([exit_button], mouse, selected_button=None)
        msg.draw()
        exit_rect.draw()
        exit_txt.draw()
        win.flip()

        # Detect an Exit-button click.
        btn = bool(mouse.getPressed()[0])
        if btn and not prev_pressed:
            if exit_rect.contains(mouse.getPos()):
                schedule_sound(quit_sound)
                return "exit"
        prev_pressed = btn

        # Press Space to continue practice.
        keys = event.getKeys(keyList=["space", "escape"])
        if "escape" in keys:
            core.quit()
        if "space" in keys:
            return "continue"

