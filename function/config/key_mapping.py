"""
key_mapping.py
--------------
All keyboard / mouse response mappings in one place.
Change keys here without touching phase logic.
"""

# ─── Phase 1 ─────────────────────────────────────────────────────────────────
# Keyboard shortcuts (fallback / EEG button-box friendly)
P1_YES_KEY  = "f"   # TODO: swap to button-box key if needed
P1_NO_KEY   = "j"

# Mouse button index (0 = left click) used for on-screen Yes/No boxes
P1_MOUSE_BUTTON = 0

# ─── Phase 3 ──────────────────────────────────────────────────────
P3_KEYS = {
    "1": "above",   # position ① (top)
    "2": "left",   # position ② (left)
    "3": "right",   # position ③ (right)
    "4": "bottom",   # position ④ (bottom)
    "num_1": 0,
    "num_2": 1,
    "num_3": 2,
    "num_4": 3,
}
P3_MOUSE_BUTTON = 0

# ─── Phase 2 ───────────────────────────────────────────────────────
P2_KEYS = {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "num_1": 0,
    "num_2": 1,
    "num_3": 2,
    "num_4": 3,
}
P2_MOUSE_BUTTON = 0

# ─── Global ──────────────────────────────────────────────────────────────────
QUIT_KEY   = "escape"
PAUSE_KEY  = "p"       # TODO: implement pause screen if needed
