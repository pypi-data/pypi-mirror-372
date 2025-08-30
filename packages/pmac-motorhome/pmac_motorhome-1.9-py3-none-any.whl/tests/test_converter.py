import os
from pathlib import Path

import pytest

from converter.motionarea import MotionArea

ROOT_DIR = Path(__file__).parent.parent

# TODO add a test for the 'file' entrypoint when it is working


@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="conversion tests are not relevant outside DLS",
)
def test_bl02i_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL02I_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()


@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="conversion tests are not relevant outside DLS",
)
def test_bl08j_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL08J_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()


@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="conversion tests are not relevant outside DLS",
)
def test_bl38p_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL38P_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()
    
def test_bl13i_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL13I_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()
    
def test_bl18b_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL18B_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()
    
def test_bl16b_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL16B_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()
    
def test_bl22i_convert():
    """
    Test conversion of an entire motion area
    """
    motion_dir = ROOT_DIR / "tests" / "converter" / "BL22I_Motion"

    motionarea = MotionArea(motion_dir)

    motionarea.make_old_motion()
    motionarea.make_new_motion()
    motionarea.check_matches()