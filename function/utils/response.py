"""
response.py
-----------
Collects keyboard or mouse responses during a phase.
Returns a ResponseResult TypedDict so callers never inspect raw dicts.
"""

from typing import TypedDict, Optional, List, Tuple

from psychopy import visual, event, core

from function.config.settings import MARKER_FRAMES_RESPONSE
from function.utils.draw_marker import draw_marker


class ResponseResult(TypedDict):
    """Outcome of a single response collection window."""
    response:     Optional[str]    # "yes"/"no"/position label/"1"–"4"
    response_idx: Optional[int]    # 0-based index for multi-choice
    rt:           Optional[float]  # seconds from onset
    timed_out:    bool
    raw_key:      Optional[str]    # the raw key name (for debugging)


def make_response(
    response:     Optional[str]   = None,
    response_idx: Optional[int]   = None,
    rt:           Optional[float] = None,
    timed_out:    bool            = False,
    raw_key:      Optional[str]   = None,
) -> ResponseResult:
    return {
        "response":     response,
        "response_idx": response_idx,
        "rt":           rt,
        "timed_out":    timed_out,
        "raw_key":      raw_key,
    }


def wait_for_key_response(
    valid_keys: List[str],
    quit_key: str = "escape",
    max_wait: Optional[float] = None,
    clock: Optional[core.Clock] = None,
) -> ResponseResult:
    """
    Block until one of *valid_keys* is pressed (or timeout / quit).

    Parameters
    ----------
    valid_keys  : keys that count as a valid response (lowercase)
    quit_key    : key that ends the experiment immediately
    max_wait    : seconds before timeout; None = wait forever
    clock       : a running core.Clock for RT measurement

    Returns
    -------
    ResponseResult
    """
    if clock is None:
        clock = core.Clock()

    event.clearEvents()
    deadline = (clock.getTime() + max_wait) if max_wait else None

    while True:
        keys = event.getKeys(timeStamped=clock)
        for key, t in keys:
            if key == quit_key:
                core.quit()
            if key in valid_keys:
                return make_response(response=key, rt=t, raw_key=key)
        if deadline and clock.getTime() >= deadline:
            return make_response(timed_out=True)
        core.wait(0.001, hogCPUperiod=0.001)


def wait_for_mouse_click(
    clickable_regions: List[Tuple[visual.BaseVisualStim, str]],
    mouse: event.Mouse,
    mouse_button: int = 0,
    quit_key: str = "escape",
    max_wait: Optional[float] = None,
    clock: Optional[core.Clock] = None,
) -> ResponseResult:
    """
    Block until the mouse clicks inside one of *clickable_regions*.

    Parameters
    ----------
    clickable_regions : list of (stim, label) where label is the response string
    mouse             : PsychoPy Mouse object
    mouse_button      : which button to watch (0 = left)
    quit_key          : keyboard key to abort experiment
    max_wait          : seconds before timeout
    clock             : running Clock for RT

    Returns
    -------
    ResponseResult
    """
    if clock is None:
        clock = core.Clock()

    mouse.clickReset()
    deadline = (clock.getTime() + max_wait) if max_wait else None

    while True:
        keys = event.getKeys()
        if quit_key in keys:
            core.quit()

        if mouse.getPressed()[mouse_button]:
            for idx, (region, label) in enumerate(clickable_regions):
                if mouse.isPressedIn(region, buttons=[mouse_button]):
                    rt = clock.getTime()
                    while mouse.getPressed()[mouse_button]:
                        core.wait(0.001)
                    return make_response(response=label, response_idx=idx, rt=rt)

        if deadline and clock.getTime() >= deadline:
            return make_response(timed_out=True)

        core.wait(0.001, hogCPUperiod=0.001)


def wait_for_mouse_release(mouse: event.Mouse, button: int = 0) -> None:
    """Block until the given mouse button is released (debounce helper)."""
    while mouse.getPressed()[button]:
        core.wait(0.001)


def confirm_click(
    win: visual.Window,
    mouse: event.Mouse,
    button: int = 0,
    redraw_fn=None,
    hold: float = 0.2,
    phase: Optional[str] = None,
    rec=None,
    response_marker: str = "response_onset",
) -> None:
    """
    phase : "phase1" 등 — MARKER_FRAMES_RESPONSE에서 프레임 수를 찾을 키
    rec   : 호출한 phase의 FrameRecorder. 반드시 넘겨야 마커 프레임들이
            CSV에 개별 row로 남는다 (안 넘기면 화면엔 보이지만 로그엔 안 남음).
    response_marker : 첫 마커 프레임에 붙는 event_marker 태그 문자열
    """
    n_marker_frames = MARKER_FRAMES_RESPONSE.get(phase, 0) if phase else 0

    if redraw_fn is None:
        # A frame cannot be redrawn safely without the caller's draw callback.
        core.wait(hold)
        wait_for_mouse_release(mouse, button)
        return

    hold_clock = core.Clock()

    # Keep flipping throughout the marker interval. Exactly the configured
    # number of rendered frames contain the photodiode square.
    for i in range(n_marker_frames):
        redraw_fn()
        draw_marker(win)
        if rec is not None:
            rec.flip_and_log(
                win,
                marker=response_marker if i == 0 else "",
            )
        else:
            win.flip()

    # The first marker-free flip is mandatory: otherwise the final marker
    # frame remains physically visible until some later screen performs a flip.
    # Continue marker-free flips for the remainder of the selection hold and
    # while the mouse button is still down, so response handling never freezes
    # the display.
    first_marker_free_frame = True
    while (
        first_marker_free_frame
        or hold_clock.getTime() < hold
        or mouse.getPressed()[button]
    ):
        redraw_fn()
        if rec is not None:
            rec.flip_and_log(win, marker="")
        else:
            win.flip()
        first_marker_free_frame = False
