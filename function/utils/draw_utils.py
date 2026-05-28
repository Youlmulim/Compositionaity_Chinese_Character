"""
draw_utils.py
-------------
Reusable PsychoPy drawing primitives shared across phases.
Phase modules call these helpers rather than constructing
visual objects themselves.
"""

import math
from typing import Optional, Tuple
from psychopy import visual, event
from function.config.settings import (
    FONT, TEXT_COLOR, STIM_CHAR_SIZE,
    GREEN_COLOR, WHITE_COLOR, BLACK_COLOR,
    HIGHLIGHT_COLOR,
    P1_BTN_WIDTH, P1_BTN_HEIGHT,
)
from function.stimuli.image_paths import get_char_image_path


# ─── Text helpers ─────────────────────────────────────────────────────────────

def make_text(
    win: visual.Window,
    text: str,
    pos: Tuple[float, float] = (0, 0),
    height: int = 40,
    color: str = TEXT_COLOR,
    bold: bool = False,
    align_horiz: str = "center",
) -> visual.TextStim:
    """Return a TextStim (not yet drawn)."""
    return visual.TextStim(
        win,
        text=text,
        font=FONT,
        pos=pos,
        height=height,
        color=color,
        bold=bold,
        alignText=align_horiz,
        wrapWidth=1600,    # TODO: adjust wrap width if text clips
    )


def make_chinese_char(
    win: visual.Window,
    char: str,
    pos: Tuple[float, float],
    size: int = STIM_CHAR_SIZE,
) -> visual.ImageStim:
    """Chinese character as ImageStim loaded from stimuli/image/{char}.png."""
    return visual.ImageStim(
        win,
        image=str(get_char_image_path(char)),
        pos=pos,
        size=(size, size),
    )


# ─── Button helpers ───────────────────────────────────────────────────────────

def make_button(
    win: visual.Window,
    label: str,
    pos: Tuple[float, float],
    width: int = P1_BTN_WIDTH,
    height: int = P1_BTN_HEIGHT,
) -> Tuple[visual.Rect, visual.TextStim]:
    """
    Return (Rect background, TextStim label) for a clickable button.
    The caller is responsible for calling .draw() on both.
    """
    rect = visual.Rect(
        win,
        width=width,
        height=height,
        pos=pos,
        fillColor=WHITE_COLOR,
        lineColor=WHITE_COLOR,
        lineWidth=10,
    )
    txt = visual.TextStim(
        win,
        text=label,
        font=FONT,
        pos=pos,
        height=36,
        color=BLACK_COLOR,
        bold=False,
    )
    return rect, txt


def is_clicked(
    stim: visual.BaseVisualStim,
    mouse: event.Mouse,
    button: int = 0,
) -> bool:
    """True if *stim* contains the mouse cursor and *button* is pressed."""
    return mouse.isPressedIn(stim, buttons=[button])


def is_hovered(
    stim: visual.BaseVisualStim,
    mouse: event.Mouse,
) -> bool:
    """True if mouse cursor is currently over the stim."""
    return stim.contains(mouse)


def set_button_border_color(
    stim: visual.BaseVisualStim,
    hovered: bool = False,
    selected: bool = False,
    normal_color: str = WHITE_COLOR,
    hover_color: str = GREEN_COLOR,
    selected_color: str = GREEN_COLOR,
) -> None:
    """
    Update border color based on button state.
    Priority: selected > hovered > normal
    """
    if selected:
        stim.fillColor = selected_color
    elif hovered:
        stim.lineColor = hover_color
    else:
        stim.lineColor = normal_color

def make_circle_button(
    win: visual.Window,
    label: str,
    pos: Tuple[float, float],
    radius: int = 36,
) -> Tuple[visual.Circle, visual.TextStim]:
    """
    Return (Circle background, TextStim label) for a clickable circular button.
    """
    circle = visual.Circle(
        win,
        radius=radius,
        pos=pos,
        fillColor=WHITE_COLOR,
        lineColor=WHITE_COLOR,
        lineWidth=10,
        edges=64,
    )
    txt = visual.TextStim(
        win,
        text=label,
        font=FONT,
        pos=pos,
        height=32,
        color=BLACK_COLOR,
        bold=False,
    )
    return circle, txt


# ─── Equation display (水 + 火 = ?) ──────────────────────────────────────────

def build_char_equation(
    win: visual.Window,
    char1: str,
    char2: str,
    char1_pos: Tuple[float, float],
    plus_pos: Tuple[float, float],
    char2_pos: Tuple[float, float],
    eq_pos: Tuple[float, float],
    qmark_pos: Tuple[float, float],
) -> dict:
    """
    Pre-build all stimuli for the  char1 + char2 = ?  equation.
    Call once before the flip loop; pass the result to draw_char_equation().
    """
    return {
        "char1":  make_chinese_char(win, char1, char1_pos),
        "plus":   make_text(win, "+",  pos=plus_pos,   height=STIM_CHAR_SIZE),
        "char2":  make_chinese_char(win, char2, char2_pos),
        "eq":     make_text(win, "=",  pos=eq_pos,     height=STIM_CHAR_SIZE),
        "qmark":  make_text(win, "?",  pos=qmark_pos,  height=STIM_CHAR_SIZE, bold=True),
    }


def draw_char_equation(eq_stims: dict, show_char2: bool = True) -> None:
    """
    Draw the pre-built equation stims returned by build_char_equation().
    If *show_char2* is False the second character is omitted.
    """
    eq_stims["char1"].draw()
    eq_stims["plus"].draw()
    if show_char2:
        eq_stims["char2"].draw()
    eq_stims["eq"].draw()
    eq_stims["qmark"].draw()


# ─── Rating button layout (circular, 6-point) ────────────────────────────────

def build_rating_buttons(
    win: visual.Window,
    radius: float = 200,
    rotation_offset: float = 0.0,
) -> list:
    """
    Build 6 circular rating buttons arranged evenly around a circle.
    Returns a list of dicts with keys: rating, circle, label, pos.
    """
    rating_buttons = []
    for idx, rating in enumerate(range(1, 7)):
        angle = rotation_offset + idx * (math.pi / 3)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        circle, label = make_circle_button(win=win, label=str(rating), pos=(x, y))
        rating_buttons.append({"rating": rating, "circle": circle, "label": label, "pos": (x, y)})
    return rating_buttons


def update_rating_button_states(rating_buttons, mouse, selected_rating=None) -> None:
    """
    Update border color and label visibility of circular rating buttons.
    Priority: selected > hover > normal.
    Label is shown only for the hovered button when any button is hovered.
    """
    hovered_rating = next(
        (b["rating"] for b in rating_buttons if is_hovered(b["circle"], mouse)),
        None,
    )
    for button in rating_buttons:

        rating = button["rating"]
        hovered = hovered_rating == rating
        selected = selected_rating == rating

        set_button_border_color(
            stim=button["circle"],
            hovered=hovered,
            selected=selected,
            normal_color=WHITE_COLOR,
            hover_color=GREEN_COLOR,
            selected_color=GREEN_COLOR,
        )
        
        if selected_rating is not None:
            button["label"].opacity = 1.0 if selected else 0.0

            # for all labels
            # button["label"].opacity = 0.0 
        
        else:
            button["label"].opacity = 1.0


# ─── Rect button state (Yes/No style) ────────────────────────────────────────

def update_button_states(buttons, mouse, selected_button=None) -> None:
    """
    Update border color of rect buttons based on hover/selected state.
    Priority: selected > hover > normal.
    Each button dict must have keys: rect, label (str).
    """
    for button in buttons:
        hovered = is_hovered(button["rect"], mouse)
        selected = selected_button == button["label"]
        set_button_border_color(button["rect"], hovered, selected, selected_color=GREEN_COLOR)

# ---- circle hovering ----
def is_hovering(pos: Tuple[float, float], target: Tuple[float, float], radius: float) -> bool:
    """Check if position is within radius of target."""
    dx = pos[0] - target[0]
    dy = pos[1] - target[1]
    distance = (dx**2 + dy**2) ** 0.5
    return distance <= radius