"""
settings.py
-----------
Centralized experiment configuration.
All magic numbers, paths, and display parameters live here.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import TEST_MODE

# ─── Paths ───────────────────────────────────────────────────────────────────
ROOT_DIR        = Path(__file__).resolve().parents[2]
STIMULI_DIR     = ROOT_DIR / "stimuli" / "image"
DATA_DIR        = ROOT_DIR / "data"
TRIAL_TABLE_CSV = (
    ROOT_DIR / "test" / "test_trial.csv"
    if TEST_MODE
    else ROOT_DIR / "stimuli" / "trial_table.csv"
)

# ─── Window ───────────────────────────────────────────────────────────────────
WINDOW_SIZE      = (1470, 956)   # TODO: adjust to your display
WINDOW_UNITS     = "pix"
WINDOW_FULLSCR   = True          # Set True for actual experiment
BACKGROUND_COLOR = "#2b2b2b"      # Dark gray matching PDF screenshots
MONITOR_NAME     = "testMonitor"  # TODO: calibrate your monitor
SCREEN_NUMBER = 1


# ─── Timing ──────────────────────────────────────────────────────────────────
MAX_RESPONSE_TIME = 10.0          # seconds; None = unlimited
ITI_DURATION      = 1.5          # inter-trial interval (seconds)
FRAME_RATE        = 60           # Hz – used for frame log sanity checks

# ─── Text ────────────────────────────────────────────────────────────────────
FONT             = "Kaiti SC"        # TODO: swap to a CJK-capable font if needed
TEXT_COLOR       = "white"


# Phase 0

P0_INSTRUCTION = (
        "第 0 阶段\n\n请根据你对每个汉字的熟悉程度，\n"
        "点击 1 到 6 之间的数字进行评分。\n\n按空格键开始。"
)
P0_QUESTION = "Q. 你对这个汉字有多熟悉？"

# Phase 1
P1_QUESTION = "Q. 下面两个汉字可以组合成一个新的汉字吗？"
P1_YES_LABEL = "是"
P1_NO_LABEL  = "否"

# Phase 2
P2_QUESTION = (
    "Q. 如果这两个汉字组合成一个新的汉字，\n" "它的意思会是什么？"
)
# TODO: per-trial meaning options are loaded from trial_table.csv
P23_MEANING_FONT = "Kaiti SC"
# macOS fallback candidates:
# "Kaiti SC", "STKaiti", "PingFang SC", "Songti SC"

# Phase 3
P3_QUESTION_TMPL = (
    "Q. 这两个汉字组合后可以表示下面的意思。\n" "第二个汉字应该放在第一个汉字的哪个相对位置，\n" "才能表达这个意思？"
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
P2_CHOICE_HEIGHT   = 50
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
HOVER_PROMPT_TEXT      = "悬停以继续"

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
    "第1阶段\n\n"
    "对于每一对汉字，\n"
    "请判断它们是否可以组合成一个新的汉字。\n\n"
    "按空格键开始。"),
    
    (2,
"第2阶段\n\n" "你将再次看到这些汉字组合，\n" "并回答一个新的问题。\n\n" "请仔细阅读问题，\n" "并选择最合适的答案。\n\n" "按空格键继续。"),
    
    (3,
"第3阶段\n\n" "你将再次看到每一对汉字，\n" "并回答一个后续问题。\n\n" "请选择最符合问题的答案。\n\n" "按空格键继续。"),
]