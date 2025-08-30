from filecmp import cmp
from pathlib import Path

from pmac_motorhome.commands import (
    ControllerType,
    PostHomeMove,
    comment,
    group,
    motor,
    plc,
    post_home,
)
from pmac_motorhome.sequences import (
    home_home,
    home_hsw,
    home_hsw_dir,
    home_hsw_hlim,
    home_hsw_hstop,
    home_limit,
    home_nothing,
    home_rlim,
    home_slits_hsw,
)
from pmac_motorhome.snippets import (
    check_homed,
    command,
    continue_home_maintain_axes_offset,
    drive_to_limit,
    home,
)


def verify(file: str):
    this_path = Path(__file__).parent

    tmp_file = Path("/tmp") / file
    example = this_path / "examples" / file
    assert cmp(
        tmp_file, example
    ), f"File mismatch, see:\ncode --diff {tmp_file} {example} "


def test_BL07I_STEP_04_plc11():
    file_name = "BL07I-MO-STEP-04.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1)
            motor(axis=2)
            comment("RLIM")
            home_rlim()

        with group(group_num=3):
            motor(axis=4)
            motor(axis=5)
            comment("RLIM")
            home_rlim()

    verify(file_name)


def test_BL02I_STEP_13_plc11():
    file = "BL02I-MO-STEP-13.plc11"
    tmp_file = Path("/tmp") / file
    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1, jdist=-10000)
            comment("HSW_HSTOP")
            home_hsw_hstop()

        with group(group_num=3):
            motor(axis=2, jdist=-10000)
            comment("HSW_HSTOP")
            home_hsw_hstop()

        with group(group_num=4):
            motor(axis=3, jdist=10000)

            comment("HSW_HSTOP")
            home_hsw_hstop()

    verify(file)
    
def test_BL13J_STEP_25_plc11():
    file = "BL13J-MO-STEP-25.plc11"
    tmp_file = Path("/tmp") / file
    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file, timeout=900000):
        pre2 = """i122=5 """

        with group(group_num=2, pre=pre2):
            motor(axis=1, jdist=-2000, index=0)
            comment("HSW_HSTOP")
            home_hsw_hstop()

        pre3 = """i322=5 """

        with group(group_num=3, pre=pre3):
            motor(axis=3, jdist=-2000, index=1)
            comment("HSW_HSTOP")
            home_hsw_hstop()

        pre4 = """i222=5 """

        with group(group_num=4, pre=pre4):
            motor(axis=2, jdist=-2000, index=2)
            comment("HSW_HSTOP")
            home_hsw_hstop()

        with group(group_num=5):
            motor(axis=8, jdist=-4000, index=3)
            comment("HSW")
            home_hsw()
        
    verify(file)

def test_BL18B_STEP01_plc13():
    file_name = "BL18B-MO-STEP-01.plc13"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
        initial = PostHomeMove.initial_position

        with group(group_num=2, post_home=initial):
            motor(axis=1, jdist=-400)
            motor(axis=2, jdist=-400)

            comment(htype="HSW")
            home_hsw()

        with group(group_num=3, post_home=initial):
            motor(axis=3, jdist=-400)
            motor(axis=4, jdist=-400)

            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_BL20I_STEP02_plc11():
    file_name = "BL20I-MO-STEP-02.plc11"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):

        initial = PostHomeMove.initial_position

        with group(group_num=2, post_home=initial):
            motor(axis=3)
            motor(axis=4)
            comment(htype="LIMIT")
            home_limit()

        with group(group_num=3, post_home=initial):
            motor(axis=5)
            motor(axis=6)
            comment(htype="LIMIT")
            home_limit()

        with group(group_num=4, post_home=initial):
            motor(axis=1)
            motor(axis=2)
            comment(htype="LIMIT")
            home_limit()

        with group(group_num=5, post_home=initial):
            motor(axis=7)
            comment(htype="LIMIT")
            home_limit()

    verify(file_name)


def test_BL06I_STEP21_plc12():
    file_name = "BL06I-MO-STEP-21.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        initial = PostHomeMove.initial_position

        with group(group_num=1, post_home=initial):
            motor(axis=2)
            comment(htype="HSW_DIR")
            home_hsw_dir()

    verify(file_name)


def test_BL02I_PMAC01_plc17():
    file_name = "BL02I-MO-PMAC-01.plc17"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=17, controller=ControllerType.pmac, filepath=tmp_file):

        with group(group_num=2):
            motor(axis=1, jdist=-500)
            comment(htype="HSW_HLIM")
            home_hsw_hlim()

        with group(group_num=3):
            motor(axis=2, jdist=-500)
            comment(htype="HSW_HLIM")
            home_hsw_hlim()

        with group(group_num=4):
            motor(axis=3, jdist=-500)
            comment(htype="HSW_HLIM")
            home_hsw_hlim()

        with group(group_num=5):
            motor(axis=4, jdist=-500)
            comment(htype="HSW_HLIM")
            home_hsw_hlim()

    verify(file_name)


def test_NOTHING_plc12() -> None:
    """
    Note this also tests reusing the same axis in two groups. Not a recommended
    thing but is supported by the framework
    """
    file_name = "NOTHING.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        hard_hi_limit = PostHomeMove.hard_hi_limit

        with group(group_num=2, post_home=hard_hi_limit):
            motor(axis=2, jdist=1000)
            comment(htype="NOTHING")
            home_nothing()

        with group(group_num=3, post_home=hard_hi_limit):
            motor(axis=2, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_post_high_limit():
    file_name = "post_high_limit.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        hi_limit = PostHomeMove.high_limit

        with group(group_num=2, post_home=hi_limit):
            motor(axis=1, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_post_low_limit():
    file_name = "post_low_limit.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        low_limit = PostHomeMove.low_limit

        with group(group_num=3, post_home=low_limit):
            motor(axis=2, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_post_jog_relative():
    file_name = "post_jog_relative.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        with group(
            group_num=4,
            post_home=PostHomeMove.relative_move,
            post_distance=1000,
        ):
            motor(axis=3, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_post_move_to_position():
    file_name = "post_move_to_position.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        with group(
            group_num=5,
            post_home=PostHomeMove.move_and_hmz,
            post_distance=1000,
        ):
            motor(axis=4, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_post_distance():
    file_name = "post_distance.plc12"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        with group(
            group_num=6,
            post_home=PostHomeMove.move_absolute,
            post_distance=32767,
        ):
            motor(axis=5, jdist=1000)
            comment(htype="HSW")
            home_hsw()

    verify(file_name)


def test_HOME_two_axes_post_L():
    file_name = "HOME_two_axes_post_L.pmc"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):

        low_limit = PostHomeMove.hard_lo_limit

        with group(group_num=2, post_home=low_limit):
            motor(axis=3, jdist=-500)
            motor(axis=4, jdist=-500)
            comment(htype="HOME")
            home_home()

    verify(file_name)

def test_two_axes_different_post_homes():
    # not supported - will not add any additional post home text to the plc
    file_name = "two_axes_different_post_homes.pmc"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):

        low_limit = PostHomeMove.hard_lo_limit

        with group(group_num=2):
            motor(axis=1, post_home=low_limit)
            motor(axis=2, post_home=PostHomeMove.move_absolute, post_distance=32767)
            comment("RLIM")
            home_rlim()

        with group(group_num=3):
            motor(axis=4)
            motor(axis=5)
            comment("RLIM")
            home_rlim()

    verify(file_name)

def test_BL18B_STEP01_plc13_slits():
    # generate a similar plc as test_BL18B_STEP01_plc13 but use the shortcut
    # home_slits() command
    # this separates the two pairs of slits so that they will not clash
    # the resulting PLC looks exactly like BL18B-MO-STEP-01.plc13 except that
    # it has an additional drive_to_limit for all axes at the start
    # and it has only one group instead of two
    file_name = "BL18B-MO-STEP-01_slits.plc13"
    tmp_file = Path("/tmp") / file_name

    with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
        initial = PostHomeMove.initial_position

        with group(group_num=2, post_home=initial):
            motor(axis=1, jdist=-400)
            motor(axis=2, jdist=-400)
            motor(axis=3, jdist=-400)
            motor(axis=4, jdist=-400)

            comment(htype="HSW")
            home_slits_hsw(posx=1, negx=2, posy=3, negy=4)

    verify(file_name)


def test_BL09I_STEP03_plc12_custom():
    # test the 'command' command which inserts arbitrary code
    file_name = "BL09I-MO-STEP-03.plc12"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file):
        with group(
            group_num=2,
            comment="; Special homing for a group of axes with tilt limits\n"
            "; and misaligned home marks",
        ):
            motor(axis=1)
            motor(axis=2)

            drive_to_limit(homing_direction=False, with_limits=False)
            # drive_to_home(with_limits=False)
            home(with_limits=False, wait_for_one_motor=True)
            continue_home_maintain_axes_offset(wait_for_one_motor=True)
            check_homed()
            post_home()

    verify(file_name)


def test_any_code():
    # test the 'command' command which inserts arbitrary code
    file_name = "any_code.plc"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1)
            motor(axis=2)

            command("Any old string will do for this test")
            command(" - multiple commands can be on the same line\n")

    verify(file_name)

def test_ms_string_correct_for_brick():
    # test the 'command' command which inserts arbitrary code
    file_name = "ms_string_for_brick.pmc"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=13, controller=ControllerType.brick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1)
            motor(axis=2, ms = 8)

    verify(file_name)


def test_two_plcs():
    # verfiy that you can create two plcs in a single definition file
    file_name1 = "two_plcs1.pmc"
    tmp_file1 = Path("/tmp") / file_name1
    file_name2 = "two_plcs2.pmc"
    tmp_file2 = Path("/tmp") / file_name2

    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file1):

        with group(group_num=2):
            motor(axis=1)
            home_hsw()

    with plc(plc_num=12, controller=ControllerType.brick, filepath=tmp_file2):

        with group(group_num=3):
            motor(axis=2)
            home_hsw()

    verify(file_name1)
    verify(file_name2)


def test_pre_post():
    file_name = "pre_post.plc"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.brick, filepath=tmp_file):
        with group(
            group_num=2, pre="\n\n        >> before  <<\n", post="\nafter\n"
        ):
            motor(axis=1)
            home_hsw()
    verify(file_name)


def test_pb_rlim_post_hard_high_limit():
    file_name = "pb_rlim_post_hard_high_limit.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.pbrick, filepath=tmp_file):
        with group(
            group_num=2, post_home=PostHomeMove.hard_hi_limit, post="P1199=1"
        ):
            motor(axis=1, enc_axes=[9])
            home_rlim()
    verify(file_name)


def test_pb_rlim_post_jog_relative():
    file_name = "pb_rlim_post_jog_relative.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.pbrick, filepath=tmp_file):
        with group(
            group_num=2,
            post_distance=200,
            post_home=PostHomeMove.relative_move,
        ):
            motor(axis=1, enc_axes=[9])
            home_rlim()
    verify(file_name)


def test_pb_rlim_post_high_limit():
    file_name = "pb_rlim_post_high_limit.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.pbrick, filepath=tmp_file):
        with group(group_num=2, post_home=PostHomeMove.high_limit):
            motor(axis=1, enc_axes=[9])
            home_rlim()
    verify(file_name)


def test_pb_home_limit():
    file_name = "pb_home_limit.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.pbrick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1, enc_axes=[9])
            home_limit()
    verify(file_name)


def test_pb_home_hsw_hlim():
    file_name = "pb_home_hsw_hlim.plc11"
    tmp_file = Path("/tmp") / file_name
    with plc(plc_num=11, controller=ControllerType.pbrick, filepath=tmp_file):
        with group(group_num=2):
            motor(axis=1, jdist=50000, enc_axes=[9])
            home_hsw_hlim()
    verify(file_name)
