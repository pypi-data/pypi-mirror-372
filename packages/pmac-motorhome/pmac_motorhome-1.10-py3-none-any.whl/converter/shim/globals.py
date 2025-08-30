# from typing import Callable, Optional

from converter.shim.controllertype import ControllerType
from pmac_motorhome.sequences import (
    home_home,
    home_hsw,
    home_hsw_dir,
    home_hsw_hlim,
    home_hsw_hstop,
    home_limit,
    home_nothing,
    home_rlim,
)

HOME = 0
LIMIT = 1
HSW = 2
HSW_HLIM = 3
HSW_DIR = 4
RLIM = 5
NOTHING = 6
HSW_HSTOP = 7

NO_HOMING_YET = -1

PMAC = 0
GEOBRICK = 1
BRICK = 1


class HomingSequence:
    # def __init__(self, function: Optional[Callable] = None, old_name: str = "NONE"):
    def __init__(self, function=None, old_name="NONE"):
        self.function = function
        if function is None:
            self.name = "No Homing Type Specified"
        else:
            self.name = function.__name__
        self.old_name = old_name

    def __repr__(self):
        return self.name


HomingSequences = {
    NO_HOMING_YET: HomingSequence(None, "NONE"),
    HOME: HomingSequence(home_home, "HOME"),
    LIMIT: HomingSequence(home_limit, "LIMIT"),
    HSW: HomingSequence(home_hsw, "HSW"),
    HSW_HLIM: HomingSequence(home_hsw_hlim, "HSW_HLIM"),
    HSW_DIR: HomingSequence(home_hsw_dir, "HSW_DIR"),
    RLIM: HomingSequence(home_rlim, "RLIM"),
    NOTHING: HomingSequence(home_nothing, "NOTHING"),
    HSW_HSTOP: HomingSequence(home_hsw_hstop, "HSW_HSTOP"),
}


class BrickType:
    # def __init__(self, type: ControllerType) -> None:
    def __init__(self, type):
        self.type = type
        self.name = str(type)

    def __repr__(self):
        return self.name


BrickTypes = {
    PMAC: BrickType(ControllerType.pmac),
    GEOBRICK: BrickType(ControllerType.brick),
    BRICK: BrickType(ControllerType.brick),
}
