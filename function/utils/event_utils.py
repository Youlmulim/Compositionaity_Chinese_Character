from psychopy import event, visual, core

_escape_tick = 0


def check_escape(win: visual.Window) -> None:
    global _escape_tick
    _escape_tick += 1
    if _escape_tick % 6 != 0:
        return
    if event.getKeys(keyList=["escape"]):
        win.close()
        core.quit()
