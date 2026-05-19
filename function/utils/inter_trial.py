from psychopy import visual, core, event

from function.utils.event_utils import check_escape
from function.config.settings import (
    HOVER_ITI_MIN_DISPLAY,
    HOVER_ITI_DWELL_TIME,
    HOVER_BUTTON_RADIUS,
    HOVER_BUTTON_LABEL,
    HOVER_PROMPT_TEXT,
    WHITE_COLOR,   
    GREEN_COLOR,
)


def run_hover_iti(win) -> None:
    """Show a center button; proceed when the mouse dwells over it."""
    mouse = event.Mouse(win=win)
    clock = core.Clock()
    stims = _build_stims(win)
    hover_start = None

    while True:
        check_escape(win)
        t = clock.getTime()
        hovered = t >= HOVER_ITI_MIN_DISPLAY and stims["button"].contains(mouse)

        if hovered:
            if hover_start is None:
                hover_start = t
            if t - hover_start >= HOVER_ITI_DWELL_TIME:
                # stims["button"].fillColor = GREEN_COLOR
                _draw(stims)
                win.flip()
                break
            stims["button"].lineColor = GREEN_COLOR
            stims["label"].color = GREEN_COLOR
        else:
            hover_start = None
            stims["button"].lineColor = WHITE_COLOR
            stims["label"].color = WHITE_COLOR

        _draw(stims)
        win.flip()


# ─── helpers ─────────────────────────────────────────────────────────────────

def _build_stims(win) -> dict:
    button = visual.Circle(
        win,
        radius=HOVER_BUTTON_RADIUS,
        pos=(0, 0),
        lineColor=WHITE_COLOR,
        fillColor=None,
        lineWidth=2,
    )
    label = visual.TextStim(
        win,
        text=HOVER_BUTTON_LABEL,
        pos=(0, 0),
        color=WHITE_COLOR,
        height=28,
    )
    prompt = visual.TextStim(
        win,
        text=HOVER_PROMPT_TEXT,
        pos=(0, HOVER_BUTTON_RADIUS + 60),
        color=WHITE_COLOR,
        height=22,
    )
    return {"button": button, "label": label, "prompt": prompt}


def _draw(stims) -> None:
    stims["button"].draw()
    stims["label"].draw()
    stims["prompt"].draw()
