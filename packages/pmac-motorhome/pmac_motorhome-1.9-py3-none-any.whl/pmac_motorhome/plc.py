import logging
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

from .constants import ControllerType, PostHomeMove
from .group import Group
from .motor import Motor
from .plcgenerator import PlcGenerator

log = logging.getLogger(__name__)


class Plc:
    """
    This class is used in a PLC definition to declare that a PLC is to
    be generated.

    Should always be instantiated using `pmac_motorhome.commands.plc`
    """

    # this class variable holds the instance in the current context
    the_plc: Optional["Plc"] = None

    def __init__(
        self,
        plc_num: int,
        controller: ControllerType,
        filepath: Path,
        timeout: int = 600000,
        post: str = "",
        post_home: PostHomeMove = PostHomeMove.none,
        post_distance: int = 0,
    ) -> None:
        """
        Args:
            plc_num (int): The PLC number to use in generated code
            controller (ControllerType):  Target controller type for the code
            filepath (pathlib.Path): Output file to receive the generated code
            timeout (int): Timeout for the plc - default 600000ms (10min).
            post(str): some raw PLC code to insert at the end of a group
            post_home (PostHomeMove): action to perform on all axes after the home sequence completes
            post_distance (int): A distance to use in post_home if required

        Raises:
            ValueError: Invalid output file name
            ValueError: Invalid PLC number supplied
        """
        self.filepath = filepath
        self.plc_num = plc_num
        self.controller: ControllerType = controller
        self.timeout: int = timeout
        self.post = post
        self.post_home: PostHomeMove = post_home
        self.post_distance: int = post_distance
        self.groups: List[Group] = []
        self.motors: "OrderedDict[int, Motor]" = OrderedDict()
        self.generator = PlcGenerator(self.controller)
        if not self.filepath.parent.exists():
            log.error(f"Cant find parent of {self.filepath} from dir {Path.cwd()}")
            raise ValueError(
                f"bad file path {self.filepath.parent}\
                from dir {Path.cwd()}"
            )
        if not isinstance(self.plc_num, int):
            raise ValueError("plc_number should be an integer")

        if self.controller == ControllerType.pbrick:
            if self.plc_num < 11 or self.plc_num > 15: # PLC 11-15 are reserved for homing PLCs
                raise ValueError("For pbrick, plc_number should be integer between 11 and 15")
        else:
            if self.plc_num < 8 or self.plc_num > 31: # PLCs 1-8 are reserved | 31 is the highest PLC number possible
                raise ValueError("For non-pbrick, plc_number should be integer between 8 and 31")

    def __enter__(self):
        """
        Enter context: store the in-scope Plc object
        """
        assert not Plc.the_plc, "cannot create a new Plc within a Plc context"
        Plc.the_plc = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        Plc.the_plc = None
        """
        Leaving the context. Use the in scope Plc object to generate the
        PLC output code.
        """
        # need to do this for the case where 2 PLCs are defined in one file
        # (including in the unit tests)
        Motor.instances = {}

        # write out PLC
        plc_text = self.generator.render("plc.pmc.jinja", plc=self)
        with self.filepath.open("w") as stream:
            stream.write(plc_text)

    @classmethod
    def instance(cls) -> "Plc":
        """
        Get the current in-scope PLC.
        """
        assert cls.the_plc, "There is no group context currently defined"
        return cls.the_plc

    @classmethod
    def add_group(
        cls,
        group_num: int,
        post_home: PostHomeMove,
        post_distance: int,
        comment: str = "",
        pre: str = "",
        post: str = "",
    ) -> Group:
        """
        Add a new group of axes to the current Plc

        Args:
            group_num (int): A Unique group number (1 is reserved for 'All Groups')
            post_home (PostHomeMove): A post home action to perform on success
            post_distance (int): A distance for those post home actions which require it
            comment (str): Add a group comment to the top of the Plc code
            pre (str): some raw PLC code to insert at the start of a group
            post (str): some raw PLC code to insert at the end of a group

        Returns:
            Group: The newly created Group
        """
        plc = Plc.instance()
        group = Group(
            group_num,
            plc.plc_num,
            plc.controller,
            post_home,
            post_distance,
            comment,
            pre,
            post,
        )
        if group.post_home is PostHomeMove.none: # use the plc post home if it exists
            group.post_home=plc.post_home
        if group.post_distance == 0:
            group.post_distance=plc.post_distance
        plc.groups.append(group)
        return group

    @classmethod
    def add_motor(cls, axis: int, motor: Motor):
        """
        Add a motor to the PLC. The Plc object collects all the motors in all
        of its groups for use in the Plc callback functions.

        Args:
            axis (int): axis number
            motor (Motor): motor details
        """
        plc = Plc.instance()
        if axis not in plc.motors:
            plc.motors[axis] = motor

    def _all_axes(self, format: str, separator: str, *arg, filter_function = None) -> str:
        """
        A helper function to generate code for all axes in a group when one
        of the callback functions below is called from a Jinja template.

        Args:
            format (str): A format string to apply to each motor in the Plc
            separator (str): The separator between each formatted string

        Returns:
            str: [description]
        """
        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name

        # PLC P variables etc must be sorted to match original motorhome.py
        motors = sorted(self.motors.values(), key=lambda x: x.index)
        if filter_function is not None:
            motors = filter(filter_function, motors)
        all = [format.format(*arg, **ax.dict) for ax in motors]
        return separator.join(all)

    ############################################################################
    # the following functions are callled from Jinja templates to generate
    # snippets of PLC code that act on all motors in a plc
    #
    # We call these Plc Axis Snippet functions
    ############################################################################

    def save_hi_limits(self):
        """
        Generate a command string for saving all axes high limits
        """
        if self.controller == ControllerType.pbrick:
            return self._all_axes("P{hi_lim}=Motor[{axis}].MaxPos", " ")
        else:
            return self._all_axes("P{hi_lim}=i{axis}13", " ")

    def restore_hi_limits(self):
        """
        Generate a command string for restoring all axes high limits
        """
        if self.controller == ControllerType.pbrick:
            return self._all_axes("Motor[{axis}].MaxPos=P{hi_lim}", " ")
        else:
            return self._all_axes("i{axis}13=P{hi_lim}", " ")

    def save_lo_limits(self):
        """
        Generate a command string for saving all axes low limits
        """
        if self.controller == ControllerType.pbrick:
            return self._all_axes("P{lo_lim}=Motor[{axis}].MinPos", " ")
        else:
            return self._all_axes("P{lo_lim}=i{axis}14", " ")

    def restore_lo_limits(self):
        """
        Generate a command string for restoring all axes low limits
        """
        if self.controller == ControllerType.pbrick:
            return self._all_axes("Motor[{axis}].MinPos=P{lo_lim}", " ")
        else:
            return self._all_axes("i{axis}14=P{lo_lim}", " ")

    def save_homed(self):
        """
        Generate a command string for saving all axes homed state
        """
        if self.controller is ControllerType.pmac:
            return self._all_axes("MSR{macro_station},i912,P{homed}", " ")
        if self.controller is ControllerType.pbrick:
            return self._all_axes("P{homed}={pb_homed_flag}", " ")
        if self.controller is ControllerType.brick and self.has_motors_with_macro_brick():
            return self._all_axes("MSR{macro_station_brick},i912,P{homed}", " ",filter_function = Group.filter_motors_with_macro) + " " + self._all_axes("P{homed}=i{homed_flag}", " ",filter_function = Group.filter_motors_without_macro)

        return self._all_axes("P{homed}=i{homed_flag}", " ")

    def save_not_homed(self):
        """
        Generate a command string for saving the inverse of all axes homed state
        """
        if self.controller is ControllerType.pbrick:
            return self._all_axes("P{not_homed}=P{homed}^12", " ")

        return self._all_axes("P{not_homed}=P{homed}^$C", " ")

    def restore_homed(self):
        """
        Generate a command string for restoring all axes homed state
        """
        if self.controller is ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{homed}", " ")
        if self.controller is ControllerType.pbrick:
            return self._all_axes("{pb_homed_flag}=P{homed}", " ")
        if self.controller is ControllerType.brick and self.has_motors_with_macro_brick():
            return self._all_axes("MSW{macro_station_brick},i912,P{homed}", " ",filter_function = Group.filter_motors_with_macro) + " " + self._all_axes("i{homed_flag}=P{homed}", " ",filter_function = Group.filter_motors_without_macro)

        return self._all_axes("i{homed_flag}=P{homed}", " ")

    def save_limit_flags(self):
        """
        Generate a command string for saving all axes limit flags
        """
        if self.controller is ControllerType.pbrick:
            return self._all_axes("P{lim_flags}=Motor[{axis}].pLimits", " ")
        else:
            return self._all_axes("P{lim_flags}=i{axis}24", " ")

    def restore_limit_flags(self):
        """
        Generate a command string for restoring all axes limit flags
        """
        if self.controller == ControllerType.pbrick:
            return self._all_axes("Motor[{axis}].pLimits=P{lim_flags}", " ")
        else:
            return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def save_position(self):
        """
        Generate a command string for saving all axes positions
        """
        if self.controller is ControllerType.pbrick:
            return self._all_axes(
                "P{pos}=Motor[{axis}].Pos - Motor[{axis}].HomePos", " "
            )
        else:
            return self._all_axes("P{pos}=M{axis}62", " ")

    def clear_limits(self):
        """
        Generate a command string for clearing all axes limits
        """

        if self.controller is ControllerType.pbrick:
            r = self._all_axes("Motor[{axis}].MaxPos=0", " ")
            r += "\n"
            r += self._all_axes("Motor[{axis}].MinPos=0", " ")
            return r
        else:
            r = self._all_axes("i{axis}13=0", " ")
            r += "\n"
            r += self._all_axes("i{axis}14=0", " ")
            return r

    def stop_motors(self):
        """
        Generate a command string for stopping all axes
        """
        if self.controller is ControllerType.pbrick:
            return self._all_axes(
                "if (Motor[{axis}].FeFatal == 0){{\n    jog/{axis}\n}}", "\n"
            )
        else:
            return self._all_axes('if (m{axis}42=0)\n    cmd "#{axis}J/"\nendif', "\n")

    def are_homed_flags_zero(self):
        """
        Generate a command string for checking if all axes homed=0
        """
        return self._all_axes("P{homed}=0", " or ")

    # use filter to apply this only to the motors of a brick which have macro
    def are_homed_flags_zero_brick(self) -> str:
        """
        Generate a command string for all axes in the plc which have macros: zero the homed flag (brick specific)

        Returns:
            str: the resulting command string
        """
        return self._all_axes("P{homed}=0", " or ", filter_function = Group.filter_motors_with_macro)

    def has_motors_with_macro_brick(self) -> bool:
        """
        Check if any of the motors in the plc has macros (brick specific)

        Returns:
            bool: returns true is any of the motors in the plc have defined macro (brick specific)
        """
        motors = list(filter(Group.filter_motors_with_macro, self.motors.values()))
        return len(motors) > 0

