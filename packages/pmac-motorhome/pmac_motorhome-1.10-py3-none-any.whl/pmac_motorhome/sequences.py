"""
Predefined homing sequences. These functions can all be called directly from
`PlcDefinition`

Call these functions in a group context to
perform the sequence on all axes in the group.
"""
import sys

if sys.version_info[0] > 2:
    from .commands import only_axes, post_home
    from .group import Group
    from .snippets import (
        check_homed,
        disable_limits,
        drive_off_home,
        drive_to_home,
        drive_to_hstop,
        drive_to_limit,
        home,
        jog_if_on_limit,
        pre_home_action,
        restore_limits,
        store_position_diff,
        zero_encoders,
    )


def home_rlim():
    """
    Home on release of a limit

    This can also be used for homing on a rotary encoder (back of motor)
    with an index mark on the rotation: Drive to limit and then home away
    from limit to the first index mark.

    - (Prehome Move) Jog in -hdir until the limit switch is hit
    - (Fast Search) Jog in hdir until the limit switch is released
    - (Fast Retrace) Jog in -hdir until the limit switch is hit
    - (Home) Home

    Finally do post home move if any.

    This example shows homing off the -ve limit with +ve hdir.
    E.g. ixx23 = 1, msyy,i912 = 10, msyy,i913 = 2.

    .. image:: images/RLIM.png
    """

    # drive in opposite to homing direction until limit hit
    drive_to_limit(homing_direction=False)
    drive_to_home(
        with_limits=False, homing_direction=True, state="FastSearch"
    )  # drive away from limit until it releases
    store_position_diff()
    drive_off_home(with_limits=False)  # drive back onto limit switch
    home(with_limits=False)
    zero_encoders()
    check_homed()
    post_home()


def home_hsw():
    """
    Home on a home switch or index mark.

    - (Prehome Move) Jog in -hdir until either index/home switch (Figure 1) or
      limit switch (Figure 2)
    - (Fast Search) Jog in hdir until index/home switch
    - (Fast Retrace) Jog in -hdir until off the index/home switch
    - (Home) Home

    Finally do post home move if any.

    .. image:: images/HSW.png
    """

    # drive in opposite to homing direction until home flag or limit hit
    drive_to_home(homing_direction=False)
    drive_to_home(
        with_limits=True, homing_direction=True, state="FastSearch",
    )
    store_position_diff()
    drive_off_home()
    home()
    zero_encoders()
    check_homed()
    post_home()


def home_hsw_hstop():
    """
    Home on a home switch or index mark on a stage that has no limit switches.

    Detection of following error due to hitting the hard stop is taken as the
    limit indication.

    - (Prehome Move) Jog in -hdir until following error - Ixx97 (in-position
      trigger mode) set to 3 for this phase.
    - (Fast Search) Jog in hdir until index/home switch
    - (Fast Retrace) Jog in -hdir until off the index/home switch
    - (Home) Home

    Finally do post home move if any.

    The axis must be configured to trigger on home index or home flag
    this is used when there are hard stops instead of limit switches
    e.g. piezo walker
    """

    # drive in opposite to homing direction until home flag or following error
    drive_to_hstop()
    drive_to_home(with_limits=True, homing_direction=True, state="FastSearch")
    store_position_diff()
    drive_off_home(homing_direction=False)
    home(with_limits=True)
    check_homed()
    post_home()


def home_hsw_dir():
    """
     Home on a directional home switch (newport style)

    - (Prehome Move) Jog in -hdir until off the home switch
    - (Fast Search) Jog in hdir until the home switch is hit
    - (Fast Retrace) Jog in -hdir until off the home switch
    - (Home) Home

    Finally do post home move if any.

    This example shows homing on a directional home switch with -ve hdir.
    E.g. ixx23 = -1, msyy,i912 = 2, msyy,i913 = 0.

    The first figure shows what happens when the axis starts on the home switch.
    E.g. Pos = -20000 cts, Index = 0 cts

    .. image:: images/HSW_DIR.png

    The second figure shows what happens when the axis starts off the home switch.
    E.g. Pos = 20000 cts, Index = 0 cts

    .. image:: images/HSW_DIR2.png
    """
    drive_off_home(state="PreHomeMove")
    drive_to_home(
        homing_direction=True,
        with_limits=True,
        state="FastSearch",
        restore_homed_flags=True,
    )
    store_position_diff()
    drive_off_home(homing_direction=False, state="FastRetrace")
    home()
    check_homed()
    post_home()


def home_limit():
    """
    Home on a limit switch.
    - (Pre Home action) - only added if group pre-home is defined 
    - (Fast Search) Jog in hdir (direction of ixx23) until limit switch activ
    - (Fast Retrace) Jog in -hdir until limit switch deactivates
    - (Home) Disable limits and home

    Finally re-enable limits and do post home move if any.

    This example shows homing on -ve limit with -ve hdir.
    E.g. ixx23 = -1, msyy,i912 = 2, msyy,i913 = 2.

    .. image:: images/LIMIT.png
    """
    pre_home_action()
    drive_to_home(homing_direction=True, state="FastSearch")
    store_position_diff()
    drive_off_home(with_limits=False)
    disable_limits()
    home()
    restore_limits()
    zero_encoders()
    check_homed()
    post_home()


def home_hsw_hlim():
    """
     Home on a home switch or index mark near the limit switch in hdir.

    - (Prehome Move) Jog in hdir until either index/home switch (Figure 1) or
      limit switch (Figure 2)
    - If limit switch hit, jog in -hdir until index/home switch
    - (Fast Search) Jog in hdir until index/home switch
    - (Fast Retrace) Jog in -hdir until off the index/home switch
    - (Home) Home

    Finally do post home move if any.

    **NOTE:** if using a reference mark, set jdist as described under
    :py:meth:`~pmac_motorhome.commands.group`

    This example shows homing on an index with -ve hdir and +ve jdist.
    E.g. ixx23 = -1, msyy,i912 = 1, jdist = 1000.

    The first figure shows what happens when the index is in hdir of the
    starting position. E.g. Pos = 20000 cts, Index = 0 cts

    .. image:: images/HSW_HLIM.png

    The second figure shows what happens when the index is in -hdir of the

    .. image:: images/HSW_HLIM2.png

    """
    drive_to_home(homing_direction=True)
    jog_if_on_limit()
    drive_to_home(homing_direction=True, state="FastSearch", with_limits=True)
    store_position_diff()
    drive_off_home(homing_direction=False, state="FastRetrace")
    home()
    check_homed()
    post_home()


def home_home():
    """
    Dumb home, shouldn't be needed - just executes HM command on all axes
    in the group
    """
    pre_home_action()
    home()
    check_homed()
    post_home()


def home_nothing():
    """
    NOTHING

    Simply goes through to post home move without homing or changing home status.
    """
    # TODO review why this reference to Group is required
    Group.the_group.htype = "NOTHING"
    post_home()


###############################################################################
# functions for some common motor combinations
###############################################################################


def home_slits_hsw(posx, negx, posy, negy):
    """
    A special seqence for two pairs of slits in which the vertical and horizontal
    pairs may collide with each other at the extreme of their homing direction.

    - move all axes to the limit away from their homing direction
    - home both positive axes using home switch or mark
    - move the positive axes out of the way
    - home both negative axes using home switch or mark
    - move the negative axes out of the way

    Args:
        posx (int): axis number of the positive horizontal motor
        negx (int): axis number of the negative horizontal motor
        posy (int): axis number of the positive vertical motor
        negy (int): axis number of the negative vertical motor
    """
    drive_to_limit(homing_direction=False)

    with only_axes(posx, posy):
        home_hsw()
        drive_to_limit(homing_direction=False)
    with only_axes(negx, negy):
        home_hsw()
        drive_to_limit(homing_direction=False)
