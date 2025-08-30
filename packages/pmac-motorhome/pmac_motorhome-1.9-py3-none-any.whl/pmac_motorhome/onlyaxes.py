# from typing import Optional

from .group import Group


class OnlyAxes:
    """
    Sets the current axis filter applied to the current group

    Should always be instantiated using `pmac_motorhome.commands.only_axes`
    """

    # a class member to hold the current context instance
    the_only_axes = None

    def __init__(self, *axes):
        """
        Args:
            group (Group): The parent group context
            axes (List[int]): The subset of axes from the parent to enable
        """
        self.axes = axes

    def __enter__(self):
        assert (
            not OnlyAxes.the_only_axes
        ), "cannot use only_axes within another only_axes"

        OnlyAxes.the_only_axes = self
        group = Group.instance()
        group.add_action(Group.set_axis_filter, axes=self.axes)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        OnlyAxes.the_only_axes = None
        group = Group.instance()
        # empty axis filter means reset the axis filter
        group.add_action(Group.set_axis_filter, axes=[])
