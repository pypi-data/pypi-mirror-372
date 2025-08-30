"""
The commands module contains functions that can be called directly
from the `PlcDefinition`.

These functions are used to define PLCs, axes and axis groupings.
"""

from pathlib import Path

from pmac_motorhome.onlyaxes import OnlyAxes

from .constants import ControllerType, PostHomeMove
from .group import Group
from .plc import Plc
from .snippets import (
    drive_relative,
    drive_to_hard_limit,
    drive_to_initial_pos,
    drive_to_soft_limit,
    post_home_action,
)


def plc(plc_num, controller, filepath, timeout=600000, post=None, post_home=PostHomeMove.none, post_home_distance=0):
    """
    Define a new PLC. Use this to create a new Plc context using the 'with'
    keyword.

    Must be called in the global context.

    Args:
        plc_num (int): Number of the generated homing PLC
        controller (ControllerType): Determines the class of controller Pmac or
            Geobrick
        filepath (pathlib.Path): The output file where the PLC will be written
        pre (str): some raw PLC code to insert at the start of a group
        post(str): some raw PLC code to insert at the end of a group
        post_home (PostHomeMove): action to perform on all axes after the
            home sequence completes
        post_distance (int): A distance to use in post_home

    Returns:
        Plc: the Plc object for use in the context
    """

    return Plc(plc_num, ControllerType(controller), Path(filepath), timeout, post, post_home, post_home_distance)


def group(
    group_num,
    post_home=PostHomeMove.none,
    post_distance=0,
    comment=None,
    pre="",
    post="",
):
    """
    Define a new group of axes within a PLC that should be homed simultaneously.
    Use this to create a new context using the 'with' keyword from within a Plc
    context.

    Must be called in a Plc context.

    Args:
        group_num (int): an identifying number note that group 1 is reserved for
            homing all groups
        axes (List[int]): a list of axis numbers to include in the group
        post_home (PostHomeMove): action to perform on all axes after the
            home sequence completes
        post_distance (int): A distance to use in post_home

    Returns:
        Group: The Group object for use in the context
    """
    return Plc.add_group(
        group_num, PostHomeMove(post_home), post_distance, comment, pre, post
    )


def comment(htype):
    Group.add_comment(htype)


def motor(axis, jdist=0, index=-1, post_home=PostHomeMove.none, post_distance=0, enc_axes=list(), ms=-1):
    """
    Declare a motor for use in the current group.

    Must be called in a group context.

    Args:
        axis (int): axis number
        jdist (int): number of counts to jog after reaching a home mark. Required
            to far enough to move off of the home mark.
        index (int): for internal use in conversion of old scripts sets
            the index of this motor to a different value than the order of
            declaration. -1 means use the order that motors were added.
        post_home(PostHomeMove):
        post_distance:
        enc_axes (list): List of additional encoders that need zeroing on homing
            completion
    """
    motor = Group.add_motor(axis, jdist, index, post_home, post_distance, enc_axes, ms)
    Plc.add_motor(axis, motor)


def only_axes(*axes):
    """
    Creates a context in which actions are performed on a subset of the groups axes

    Must be called in a group context.

    For an example of the use of this, see :doc:`../tutorials/custom`

    Args:
        axes (int): List of axis numbers

    Returns:
        OnlyAxes: an OnlyAxes object for use in the context
    """
    return OnlyAxes(*axes)


###############################################################################
# post_home actions to recreate post= from the original motorhome.py
###############################################################################
def post_home(**args):
    """
    Perform one of the predefined post homing actions on all axes in the
    current group.

    Must be called in a Group context.

    This function is called as the last step in all of the :doc:`sequences`
    functions
    """
    group = Group.instance()
    are_same, post_homes_motors = group.all_motors_have_same_post_move_type()
    if not (are_same):
        pass # different types of post home move not supported in the current version 
    elif post_homes_motors == PostHomeMove.none:
        if group.post is not "":
            post_home_action()
    elif post_homes_motors == PostHomeMove.initial_position:
        drive_to_initial_pos(**args)
    elif post_homes_motors == PostHomeMove.high_limit:
        drive_to_soft_limit(homing_direction=True)
    elif post_homes_motors == PostHomeMove.low_limit:
        drive_to_soft_limit(homing_direction=False)
    elif post_homes_motors == PostHomeMove.hard_hi_limit:
        drive_to_hard_limit(homing_direction=True)
    elif post_homes_motors == PostHomeMove.hard_lo_limit:
        drive_to_hard_limit(homing_direction=False)
    elif post_homes_motors == PostHomeMove.relative_move:
        drive_relative()
    elif post_homes_motors == PostHomeMove.move_and_hmz:
        drive_relative(set_home=True)
    elif post_homes_motors == PostHomeMove.move_absolute:
        # TODO this is wrong - we need a jog absolute snippet
        drive_relative()
    else:
        pass
