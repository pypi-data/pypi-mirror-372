from pathlib import Path

import pytest

from pmac_motorhome.commands import group, plc
from pmac_motorhome.constants import ControllerType


def test_one_plc():
    with plc(11, ControllerType.brick, Path("/tmp/t")):
        with pytest.raises(AssertionError):
            with plc(12, ControllerType.brick, Path("/tmp/u")):
                pass


def test_one_group():
    with plc(11, ControllerType.brick, Path("/tmp/t")):
        with pytest.raises(AssertionError):
            with group(2):
                with group(3):
                    pass
