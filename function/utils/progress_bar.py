# function/utils/progress_bar.py

from psychopy import visual
from function.config import settings as cfg


class TimeProgressBar:
    """
    Progress bar showing the remaining response time at the bottom of the screen.

    Default position, size, and colors are managed in this file.
    Phase code only needs to instantiate ``TimeProgressBar(win)``.
    """

    DEFAULT_WIDTH = 600
    DEFAULT_HEIGHT = 16
    DEFAULT_POS = (0, -430)

    DEFAULT_FRAME_COLOR = "white"
    DEFAULT_FILL_COLOR = "white"
    DEFAULT_BG_COLOR = "gray"

    def __init__(
        self,
        win,
        total_width=None,
        height=None,
        pos=None,
        frame_color=None,
        fill_color=None,
        bg_color=None,
    ):
        self.win = win
        self.total_width = total_width if total_width is not None else self.DEFAULT_WIDTH
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.pos = pos if pos is not None else self.DEFAULT_POS

        frame_color = frame_color if frame_color is not None else self.DEFAULT_FRAME_COLOR
        fill_color = fill_color if fill_color is not None else self.DEFAULT_FILL_COLOR
        bg_color = bg_color if bg_color is not None else self.DEFAULT_BG_COLOR

        self.left_x = self.pos[0] - self.total_width / 2

        self.background = visual.Rect(
            win=self.win,
            width=self.total_width,
            height=self.height,
            pos=self.pos,
            lineColor=None,
            fillColor=bg_color,
        )

        self.fill = visual.Rect(
            win=self.win,
            width=self.total_width,
            height=self.height,
            pos=self.pos,
            lineColor=None,
            fillColor=fill_color,
        )

        self.frame = visual.Rect(
            win=self.win,
            width=self.total_width,
            height=self.height,
            pos=self.pos,
            lineColor=frame_color,
            fillColor=None,
            lineWidth=2,
        )

    def draw(self, elapsed_time, max_time=None):
        """
        elapsed_time:
            Value returned by ``phase_clock.getTime()``.

        max_time:
            Defaults to ``cfg.MAX_RESPONSE_TIME`` from settings.py.
            Phase code does not need to pass it explicitly.
        """

        if max_time is None:
            max_time = cfg.MAX_RESPONSE_TIME

        if not max_time or max_time <= 0:
            return

        remaining_ratio = 1.0 - (elapsed_time / max_time)
        remaining_ratio = max(0.0, min(1.0, remaining_ratio))

        current_width = self.total_width * remaining_ratio

        self.background.draw()

        if current_width > 0:
            self.fill.width = current_width

            # Keep the left edge fixed while shrinking from the right.
            self.fill.pos = (
                self.left_x + current_width / 2,
                self.pos[1],
            )

            self.fill.draw()

        self.frame.draw()
