# this is a shim for the original motorhome library which
# replaces the original PLC generating code.
# Instead it generates a new dls_motohome style python file

from converter.shim.functions import parse_args
from converter.shim.globals import (
    BRICK,
    GEOBRICK,
    HOME,
    HSW,
    HSW_DIR,
    HSW_HLIM,
    HSW_HSTOP,
    LIMIT,
    NOTHING,
    PMAC,
    RLIM,
)
from converter.shim.group import Group
from converter.shim.motor import Motor
from converter.shim.plc import PLC

# I split the code into modules but the original users of motorhome.py
# expect to import a single file. Hence this file that only does imports.
# I use __all__ here to suppress linter issues only.

__all__ = (
    "Motor",
    "PLC",
    "Group",
    "BRICK",
    "GEOBRICK",
    "HOME",
    "HSW",
    "HSW_DIR",
    "HSW_HLIM",
    "HSW_HSTOP",
    "LIMIT",
    "NOTHING",
    "PMAC",
    "RLIM",
    "parse_args",
)
