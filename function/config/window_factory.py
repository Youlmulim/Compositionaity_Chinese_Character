"""
window_factory.py
-----------------
Creates and returns a configured PsychoPy Window.
Keeping window creation isolated makes it easy to swap
monitor profiles or resolution without touching phase logic.
"""

from psychopy import visual, monitors
from function.config.settings import (
    WINDOW_SIZE, WINDOW_UNITS, WINDOW_FULLSCR,
    BACKGROUND_COLOR, MONITOR_NAME, SCREEN_NUMBER,
)


def create_window() -> visual.Window:
    """
    Build and return the experiment Window.

    Returns
    -------
    visual.Window
        A fully initialised PsychoPy window ready for drawing.
    """
    mon = monitors.Monitor(MONITOR_NAME)
    # TODO: set mon.setSizePix(), mon.setWidth(), mon.setDistance()
    #       to match your physical setup for correct visual-angle scaling.

    win = visual.Window(
        size=WINDOW_SIZE,
        fullscr=WINDOW_FULLSCR,
        units=WINDOW_UNITS,
        monitor=mon,
        color=BACKGROUND_COLOR,
        colorSpace="hex",
        allowGUI=True,
        winType="pyglet",
        screen=SCREEN_NUMBER,
    )
    return win
