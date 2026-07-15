# function/utils/draw_marker.py
from psychopy import visual
from function.config.settings import WINDOW_SIZE

# ─── Grid position ────────────────────────────────────────────────────────
N_ROWS = 6
N_COLS = 8
MARKER_ROW = 1
MARKER_COL = N_COLS  # 오른쪽 위

# ─── Marker size ──────────────────────────────────────────────────────────
MARKER_SIZE_FRAC = 0.6  # 셀의 짧은 변에 대한 비율

# Cache the stimulus on the PsychoPy Window itself. The experiment normally
# owns one window, and keeping the cache there also prevents a marker created
# for one window from being drawn on another window.
_MARKER_CACHE_ATTR = "_photodiode_marker_stim"


def _cell_center(win_width, win_height, row, col):
    x_center = win_width * ((col - 0.5) / N_COLS - 0.5)
    y_center = win_height * (0.5 - (row - 0.5) / N_ROWS)
    return x_center, y_center


def draw_marker(win):
    marker = getattr(win, _MARKER_CACHE_ATTR, None)

    if marker is None:
        win_width, win_height = WINDOW_SIZE
        pos = _cell_center(win_width, win_height, MARKER_ROW, MARKER_COL)

        cell_width = win_width / N_COLS
        cell_height = win_height / N_ROWS
        side = min(cell_width, cell_height) * MARKER_SIZE_FRAC

        marker = visual.Rect(
            win=win,
            pos=pos,
            width=side,
            height=side,
            fillColor="white",
            lineColor="white",
            units="pix",
        )
        setattr(win, _MARKER_CACHE_ATTR, marker)

    marker.draw()
