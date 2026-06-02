"""
settings.py
-----------
Centralized experiment configuration.
All magic numbers, paths, and display parameters live here.
"""

from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR        = Path(__file__).resolve().parents[2]
STIMULI_DIR     = ROOT_DIR / "stimuli" / "image"
DATA_DIR        = ROOT_DIR / "data"
TRIAL_TABLE_CSV = ROOT_DIR / "stimuli" / "trial_table.csv"

# ─── Window ───────────────────────────────────────────────────────────────────
WINDOW_SIZE      = (1920, 1080)   # TODO: adjust to your display
WINDOW_UNITS     = "pix"
WINDOW_FULLSCR   = False          # Set True for actual experiment
BACKGROUND_COLOR = "#2b2b2b"      # Dark gray matching PDF screenshots
MONITOR_NAME     = "testMonitor"  # TODO: calibrate your monitor
SCREEN_NUMBER = 1


# ─── Timing ──────────────────────────────────────────────────────────────────
MAX_RESPONSE_TIME = 10.0          # seconds; None = unlimited
ITI_DURATION      = 1.5          # inter-trial interval (seconds)
FRAME_RATE        = 60           # Hz – used for frame log sanity checks

# ─── Text ────────────────────────────────────────────────────────────────────
FONT             = "Arial"        # TODO: swap to a CJK-capable font if needed
TEXT_COLOR       = "white"


# Phase 0

P0_INSTRUCTION = (
    "Phase 0\n\nFor each character, rate how familiar you are with it\n"
    "on a scale of 1 to 6 by clicking the number.\n\nPress SPACEBAR to start."
)
P0_QUESTION = "Q. How familiar are you with this character?"

# Phase 1
P1_QUESTION = "Q. Can the two characters below be combined to form a new character?"
P1_YES_LABEL = "Yes"
P1_NO_LABEL  = "No"

# Phase 2
P2_QUESTION = (
    "Q. If these two characters were combined to form a new character,\n"
    "what would its meaning be?"
)
# TODO: per-trial meaning options are loaded from trial_table.csv

# Phase 3
P3_QUESTION_TMPL = (
    "Q. These two characters combine to convey the meaning below.\n"
    "Where should the second character be placed relative to the first one\n"
    "to produce that meaning?"
)
CIRCLE_NUMS = ["1", "2", "3", "4"]   # shared across Phase 2 and Phase 3


# ─── Layout (pixel offsets from screen centre) ───────────────────────────────
STIM_CHAR1_POS  = (-200,  50)   # TODO: fine-tune
STIM_PLUS_POS   = ( -100,  50)
STIM_CHAR2_POS  = (   0,  50)
STIM_EQ_POS     = ( 100,  50)
STIM_QMARK_POS  = ( 200,  50)
STIM_CHAR_SIZE  = 120           # font size for Chinese characters

# Phase 1 button positions
P1_YES_BOX_POS  = (-300, -330)
P1_NO_BOX_POS   = ( 300, -330)
P1_BTN_WIDTH    = 220
P1_BTN_HEIGHT   = 80

# Phase 2 equation layout (pixel offsets from screen centre)
P2_EQ_CHAR1_POS    = (-260, 160)
P2_EQ_PLUS_POS     = (-140, 160)
P2_EQ_CHAR2_POS    = (   0, 160)
P2_EQ_EQ_POS       = ( 140, 160)
P2_EQ_QMARK_POS    = ( 260, 160)
P2_QUESTION_POS    = (0, 360)
P2_QUESTION_HEIGHT = 36
P2_CHOICE_HEIGHT   = 34
P2_CHOICE_CIRCLE_RADIUS = 55
P2_CHOICE_CIRCLE_POS    = [(-640, 40), (70, 40), (-640, -160), (70, -160)]
P2_CHOICE_TEXT_POS      = [(-380, 40), (380, 40), (-380, -160), (380, -160)]

# Phase 3: Click-and-paste layout
# Left area: 5-circle cross pattern for character placement
P3_CROSS_CENTER     = (-300, 0)
P3_CIRCLE_SPACING   = 150        # pixel distance between circles
P3_CIRCLE_RADIUS    = 60         # detection radius

# Right area: clickable characters
P3_CHAR1_POS        = (350, 100)
P3_CHAR2_POS        = (350, -100)

# Question and meaning
P3_QUESTION_POS     = (0, 360)
P3_MEANING_BOX_POS  = (0, 155)

# Circle position names and offsets (relative to cross center)
P3_POSITIONS = {
    'TOP':    (0,  P3_CIRCLE_SPACING),
    'LEFT':   (-P3_CIRCLE_SPACING, 0),
    'CENTER': (0, 0),
    'RIGHT':  (P3_CIRCLE_SPACING, 0),
    'BOTTOM': (0, -P3_CIRCLE_SPACING),
}


# ─── Hover ITI ───────────────────────────────────────────────────────────────
HOVER_ITI_MIN_DISPLAY  = 0.3     # seconds before button becomes active
HOVER_ITI_DWELL_TIME   = 0.5     # seconds of continuous hover to proceed
HOVER_BUTTON_RADIUS    = 45      # pixels
HOVER_BUTTON_LABEL     = "+"
HOVER_PROMPT_TEXT      = "Hover to continue"

# ─── Colours ─────────────────────────────────────────────────────────────────
WHITE_COLOR    = "white"
GREEN_COLOR = "green"
BLACK_COLOR    = "black"
HIGHLIGHT_COLOR   = "#ffdd00"    # selected option highlight

# ─────────────────────────────────────────────────────────────────────────────
# Phase configuration  (phase_num, instruction)
# run_fn is resolved in main.py to avoid circular imports
# ─────────────────────────────────────────────────────────────────────────────
PHASE_CONFIG = [
    (1,
     "Phase 1\n\n"
     "For each pair of Chinese characters,\n"
     "decide whether they can combine to form a new character.\n\n"
     "Press SPACEBAR to start."),
    
    (2,
     "Phase 2\n\n"
     "You will see the character pairs again,\n"
     "along with a new question.\n\n"
     "Please read the question carefully\n"
     "and choose the best answer.\n\n"
     "Press SPACEBAR to continue."),
    
    (3,
     "Phase 3\n\n"
     "You will see each pair once more,\n"
     "along with a follow-up question.\n\n"
     "Please select the answer that best fits the question.\n\n"
     "Press SPACEBAR to continue."),
]