# Compositionality_Chinese_Character (sound branch)

A PsychoPy-based behavioral experiment on Chinese character compositionality.
Participants are shown two Chinese characters and judge whether they can be
combined into a new character, and if so, what that combination would mean.

## Experiment flow (`main.py`)

1. **Initialization** (`initiate.py`) — collect subject info, load/create the
   trial table, create the window, measure the screen refresh rate,
   (optionally) set up EyeLink
2. **Practice** — Practice Phase 0 (familiarity rating, not saved) → Practice
   Phases 1–3 (a QUIT button lets the participant skip straight to the main
   experiment at any time)
3. **Phase 0** — Familiarity rating for individual characters (six circular
   buttons, rated 1–6)
4. **Phase 1** — "Can these two characters be combined into a new character?"
   (Yes/No)
5. **Phase 2** — "If combined, what would the new character mean?"
   (4-alternative forced choice, circular option layout)
6. **Phase 3** — Given a target meaning, click-and-place the second character
   at the correct relative position (top/bottom/left/right/center) around the
   first character
7. **Data export** — per-trial CSV/JSON summary is exported, then a farewell
   message plays and the window closes

## Directory structure

| Path | Contents |
|---|---|
| `function/config/` | Experiment settings (`settings.py`), key/mouse mapping, window factory |
| `function/phases/` | Phase 0–3 screen logic and the phase-loop controller |
| `function/practice/` | Practice-phase logic |
| `function/stimuli/` | Trial loader and image path management |
| `function/io/` | Output handling (frame log, metadata, per-subject path management) |
| `function/utils/` | Shared utilities (drawing, response handling, sound playback, progress bar, etc.) |
| `function/utils/sounds/` | Sound effect WAVs and the PsychoPy Sound preload/playback module |
| `stimuli/` | Stimulus generation scripts, character images, trial/practice tables (CSV) |
| `eye_func/` | EyeLink eye-tracker integration for PsychoPy |
| `data/` | Per-subject result data (frame logs, per-phase summaries) |
| `analysis/` | Scripts for checking collected data (e.g. frame-drop detection) |

## Key settings (`config.py`, `function/config/settings.py`)

- `USE_EYELINK` — whether to use the EyeLink eye tracker (0/1)
- `TEST_MODE` — if 1, uses `test/test_trial.csv`; if 0, uses the real
  `stimuli/trial_table.csv`
- Centralized management of stimulus layout coordinates, response time limit
  (`MAX_RESPONSE_TIME`), ITI, and photodiode marker frame counts
  (`MARKER_FRAMES_ONSET/RESPONSE`)

## What's new in the `sound` branch

- `function/utils/sounds/sounds.py` — preloads PsychoPy `sound.Sound` objects
  using the PTB (PsychToolbox) audio backend so effect sounds
  (`sound_effect.wav`, `sound_effect_quit.wav`, `sound_effect_done.wav`) can be
  played asynchronously during the experiment without first-play latency
- Sound-effect triggers added at experiment completion (done) and early exit
  (quit)

## How to run

```bash
pip install -r requirements.txt   # psychopy, psychtoolbox
python main.py
```

## Notes

- `main_auto.py` — appears to be an automation/debugging entry point (e.g.
  auto-advancing trials)
- `test.py`, `test/test_trial.csv` — reduced trial set used when
  `TEST_MODE=1`