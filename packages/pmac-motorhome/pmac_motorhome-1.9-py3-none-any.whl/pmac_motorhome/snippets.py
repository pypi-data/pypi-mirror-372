"""
All of these functions will insert a small snippet of PLC code into the
generated PLC. Each snippet performs a specific action on all of the axes
in a group simultaneously.

These functions can all be called directly from
`PlcDefinition`. They should be called in the context of a Group object.
"""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, TypeVar, cast

from .group import Group


# the command action simply inserts the text in 'cmd' into the PLC output
def command(cmd):
    Group.add_action(Group.command, cmd=cmd)


snippet_docstring = """
    This will cause the jinja template {template} to be expanded and inserted
    into the PLC code. The template is as follows:

    .. include:: ../../pmac_motorhome/snippets/turbo/{template}
        :literal:
"""

wait_for_done_docstring = """

    The included template wait_for_done.pmc.jinja allows this function to take these
    additional parameters which all default to False:

    Args:
        no_following_err (bool): don't check for following error during moves
        with_limits (bool): check for limits during the move. When False we continue
            waiting even if a subset of the axes have stopped on a limit
        wait_for_one_motor (bool): stop wating as soon as one of the motors
            has stopped instead of waiting for all motors
"""

# jinja snippets that include wait_for_done.pmc.jinja also may pass
# these arguments - the dictionary values are the defaults
wait_for_done_args = {
    "no_following_err": False,
    "with_limits": False,
    "wait_for_one_motor": False,
}
"""
A set of arguments to pass to the wait_for_done function
"""

F = TypeVar("F", bound=Callable)
"""
A type to represent a callable function
"""


def _snippet_function(*arglists: Dict[str, Any]) -> Callable[[F], F]:
    """
    A decorator function to allow simple declaration of snippet functions.
    Snippet functions are used to append snippets of Jinja PLC code to
    the current PLC.

    The decorated function should have:

    - the same name as a jinja template file (less .pmc.jinja)
      in the folder pmac_motorhome/snippets. The function should take
    - Type hinted parameters that the template will use
    - A docstring that describes the function of the snippet

    The snippet may itself include further snippets and if this is the case
    any argument lists required by further snippets should be passed to the
    decorator. The only example of this at present is `wait_for_done_args`.

    The decorator adds the following to the decorated function:

    - code to check parameters passed at runtime
    - code to implement appending the template with parameters
    - appends the original Jinja to the docstring
    - appends a description of parameters to the wait_for_done template
      if  wait_for_done_args was passed to the decorator
    """

    def wrap(wrapped: F) -> F:
        sig = inspect.signature(wrapped)
        assert (
            "kwargs" in sig.parameters.keys() or len(arglists) == 0
        ), f"Bad snippet function definition - {wrapped.__name__} must take **kwargs"

        merged_args = {}
        # merge in any included jinja tempates arguments with defaults
        for included_args in arglists:
            merged_args.update(included_args)
        # add in the snippet function's arguments, possibly overriding above defaults
        merged_args.update({k: v.default for k, v in sig.parameters.items()})

        @wraps(wrapped)
        def wrapper(**kwargs) -> None:
            bad_keys = kwargs.keys() - merged_args.keys()
            assert (
                len(bad_keys) == 0
            ), f"illegal arguments: {wrapped.__name__} does not take {bad_keys}"

            all_merged = merged_args.copy()
            all_merged.update(kwargs)

            # add a jinja snippet and its processed arguments to the current group
            Group.add_snippet(wrapped.__name__, **all_merged)

        # insert the original function's signature at the top of the docstring
        doc = wrapped.__name__ + str(sig)
        # then insert the original function's docstring
        doc += wrapped.__doc__ or ""
        # insert information about jinja the template this function is inserting
        doc += str.format(snippet_docstring, template=wrapped.__name__ + ".pmc.jinja")
        # insert documentation on any jinja templates included by the above template
        if wait_for_done_args in arglists:
            doc += wait_for_done_docstring
        wrapper.__doc__ = doc

        return cast(F, wrapper)

    return wrap


# TODO state should be an enum
@_snippet_function(wait_for_done_args)
def drive_to_limit(state="PreHomeMove", homing_direction=False, **kwargs):
    """
    Jog all of the group's axes until they have each hit a limit

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            the axis' homing direction, defaults False: opposite to homing direction
    """


@_snippet_function(wait_for_done_args)
def drive_off_home(
    state="FastRetrace", homing_direction=False, with_limits=True, **kwargs
):
    """
    Jog all the group's axes until the home flag is released

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            the axis' homing direction, defaults False: opposite to homing direction
        with_limits (bool): check for limits during the move
    """


@_snippet_function()
def store_position_diff():
    """
    Save the current offset from the original position.

    This is only required in order to support driving back to initial position
    after the home operation is complete
    """


@_snippet_function(wait_for_done_args)
def drive_to_home(
    state="PreHomeMove", homing_direction=False, restore_homed_flags=False, **kwargs
):
    """
    Drive all axes in the group until they hit the home flag or a limit

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
        restore_homed_flags (bool): restore the home flags original state before
            starting. Required if a previous step changed the home flags
    """


@_snippet_function(wait_for_done_args)
def drive_to_hstop(
    state="PreHomeMove", homing_direction=False, no_following_err=True, **kwargs
):
    """
    Drive all axes in the group until they hit the hard stop (following error)

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
    """


@_snippet_function(wait_for_done_args)
def home(with_limits=True, **kwargs):
    """
    Initiate the home command on all axes in the group

    Args:
        with_limits (bool): check for limits during the move
    """


@_snippet_function()
def debug_pause():
    """
    When running in debug mode, pause until the user indicates to continue
    """


@_snippet_function(wait_for_done_args)
def drive_to_initial_pos(with_limits=True, **kwargs):
    """
    Return all axes in the group to their original positions before the homing
    sequence began. Requires that store_position_diff was called before home.

    Args:
        with_limits (bool): check for limits during the move
    """


@_snippet_function(wait_for_done_args)
def drive_to_soft_limit(homing_direction=False, with_limits=True, **kwargs):
    """
    Drive all axes in the group until they hit their soft limits

    Args:
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
        with_limits (bool): check for limits during the move
    """


@_snippet_function(wait_for_done_args)
def drive_relative(set_home=False, with_limits=True, **kwargs):
    """
    Drive all axes in the group a relative distance from current position

    Args:
        set_home (bool): set the home flag afterward if True
        with_limits (bool): check for limits during the move
    """


@_snippet_function()
def zero_encoders():
    """
    Zero an associated encoders
    """


@_snippet_function()
def check_homed():
    """
    Verfiy that all axes in the group are homed. Set error condition if not.
    """


@_snippet_function(wait_for_done_args)
def drive_to_home_if_on_limit(homing_direction=False, **kwargs):
    """
    Drive axes to the home mark or switch. Only perform this action on
    axes that are currently on a limit.

    Args:
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
    """


@_snippet_function()
def disable_limits():
    """
    Disable the soft limits on all axes in the group
    """


@_snippet_function()
def restore_limits():
    """
    Restore the saved soft limits on all axes on the group. By default the
    Plc will always record the soft limits of all axes at the start.
    """


@_snippet_function(wait_for_done_args)
def drive_to_hard_limit(state="PostHomeMove", homing_direction=False, **kwargs):
    """
    Drive all axes until they hit a hard limit.

    Args:
        state (str): Which homing state to report to EPICS for monitoring
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
    """


@_snippet_function(wait_for_done_args)
def jog_if_on_limit(homing_direction=False, with_limits=True, **kwargs):
    """
    Jog all axes in the group that are currently on a limit

    Args:
        homing_direction (bool): When True Jog in the same direction as
            each axis' homing direction, defaults False: opposite to homing direction
    """


@_snippet_function(wait_for_done_args)
def continue_home_maintain_axes_offset(**kwargs):
    """
    Monitor axes that are homing and when one achieves home jog it in the
    same direction as home. This is to avoid tilt on pairs of axes that have
    misaligned home marks.
    """


@_snippet_function()
def post_home_action():
    """
    Insert an extra block with the group's post home action in it
    """

@_snippet_function()
def pre_home_action():
    """
    Insert an extra block with the group's pre home action in it
    """
