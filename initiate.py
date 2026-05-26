import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from psychopy import core

from config import USE_EYELINK, EYELINK_IP
from function.config.window_factory import create_window
from function.config import settings as cfg
from function.stimuli.trial_loader import get_or_create_subject_trials, load_char_list
from function.io.path_builder import get_subject_dir
from function.utils.screen_utils import get_subject_info

if USE_EYELINK:
    import pylink
    from eye_func.EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy


@dataclass
class ExperimentContext:
    subject_id:   str
    trials:       List[Dict[str, Any]]
    char_list:    List[Any]
    win:          Any
    global_clock: Any
    el_tracker:   Optional[Any]


def initiate_experiment() -> ExperimentContext:
    """Run all pre-experiment setup and return initialized state."""
    subject_id = get_subject_info()["subject_id"]

    trials: List[Dict[str, Any]] = get_or_create_subject_trials(subject_id)
    char_list = load_char_list()

    win = create_window()
    global_clock = core.Clock()

    el_tracker = initiate_eyelink(win, get_subject_dir(subject_id))

    return ExperimentContext(
        subject_id   = subject_id,
        trials       = trials,
        char_list    = char_list,
        win          = win,
        global_clock = global_clock,
        el_tracker   = el_tracker,
    )


def initiate_eyelink(win, save_directory):
# calibration of eyelink
# Returns: el_tracker(pylink.Eyelink)
    try:
        if USE_EYELINK == 0:
            return None
        el_tracker = pylink.EyeLink(EYELINK_IP)
    except (RuntimeError, ModuleNotFoundError):
        print("⚠ EyeLink tracker not detected. EyeLink functionality will be disabled.")
        return None

    print("EyeLink tracker detected. Initializing...")
    os.makedirs(save_directory, exist_ok=True)

    edf_name = "test.edf"
    try:
        el_tracker.openDataFile(edf_name)
    except RuntimeError as err:
        print("ERROR: ", err)
        if el_tracker.isConnected():
            el_tracker.close()

    preamble_text = "RECORDED BY %s" % os.path.basename(__file__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)
    el_tracker.setOfflineMode()

    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    print("Running experiment on %s, version %d" % (vstr, eyelink_ver))

    el_tracker.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
    el_tracker.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS")

    scn_width, scn_height = win.size
    el_tracker.sendCommand(f"screen_pixel_coords = 0 0 {scn_width-1} {scn_height-1}")
    el_tracker.sendMessage(f"DISPLAY_COORDS 0 0 {scn_width-1} {scn_height-1}")

    try:
        print("Starting EyeLink calibration on monitor...")
        genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
        pylink.openGraphicsEx(genv)
        print("Calibration in progress...")
        el_tracker.doTrackerSetup()
        print("Calibration complete.")
    except Exception as e:
        print(f"⚠ EyeLink calibration skipped: {e}")

    return el_tracker