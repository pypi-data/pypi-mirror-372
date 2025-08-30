from typing import Any, Callable, Dict, List, Tuple
from xmlrpc.client import Boolean  # , Optional

from pmac_motorhome.constants import ControllerType, PostHomeMove

from .motor import Motor
from .template import Template


class Group:
    """
    Defines a group of axes to be homed as a unit

    Should always be instantiated using `pmac_motorhome.commands.group`
    """

    # this class variable holds the instance in the current context
    the_group = None

    def __init__(
        self,
        group_num,
        plc_num,
        controller,
        post_home: PostHomeMove = PostHomeMove.none,
        post_distance: int = 0,
        comment=None,
        pre="",
        post="",
    ):
        """
        Args:
            group_num (int): A unique number to represent this group within its
                Plc. group 1 is reservered for 'all groups'
            axes (List[Motor]): A list of axis numbers that this group will control
            plc_num (int): The plc number of the enclosing Plc
            controller (ControllerType): Enum representing the type of motor controller
            post_home (PostHomeMove): action to perform on all axes after the home sequence completes
            post_distance (int): A distance to use in post_home if required
            comment (str): [description]. A comment to place in the output Plc code
                at the beginning of this group's definition
            pre (str): some raw PLC code to insert at the start of a group
            post(str): some raw PLC code to insert at the end of a group
        """
        self.motors = []
        self.encoders = []
        self.all_motors = []
        self.has_encoders = False
        self.post_home = post_home
        self.post_distance = post_distance
        self.comment = comment
        self.plc_num = plc_num
        self.group_num = group_num
        self.templates = []
        self.htype = "unknown"
        self.controller = controller
        self.pre = pre
        self.post = post

    def __enter__(self):
        """
        Entering a context. Store the Group object for use in the scope of
        this context.
        """
        assert not Group.the_group, "cannot create a new Group within a Group context"
        Group.the_group = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Exiting the context. Clear the Group object.
        """
        Group.the_group = None

    @classmethod
    def add_motor(cls, axis: int, jdist: int, index: int, post_home:PostHomeMove, post_distance:int, enc_axes: List, ms:int) -> Motor:
        """
        Add a new motor to the current group

        Args:
            axis (int): Axis number
            jdist (int): distance to jog to move off of home mark
            index (int): internal use
            post_home (PostHomeMove): action to perform on all axes after the home sequence completes
            post_distance (int): A distance to use in post_home if required
            enc_axes (list): List of additional encoders that need zeroing on homing
                completion
            ms (int): macrostation number
        Returns:
            Motor: The newly created Motor
        """
        group = Group.instance()
        assert (
            axis not in group.motors
        ), f"motor {axis} already defined in group {group.plc_num}"
        
        if post_home is PostHomeMove.none: # use the group post home if it exists 
            post_home=group.post_home
        if post_distance == 0:
            post_distance=group.post_distance
        motor = Motor.get_motor(axis, jdist, group.plc_num, index=index, post_home=post_home, post_distance=post_distance, ms=ms)
        group.motors.append(motor)

        group.encoders = group.encoders + enc_axes
        if len(group.encoders) > 0:
            group.has_encoders = True

        group.all_motors.append(motor)
        return motor

    @classmethod
    def instance(cls) -> "Group":
        """
        Get the current in-scope Group
        """
        assert cls.the_group, "There is no group context currently defined"
        return cls.the_group

    @classmethod
    def add_comment(cls, htype: str) -> None:
        """
        Add a group comment to the top of the Plc code in the style of the original
        motorhome.py module but note that you can use any descriptive text
        for htype

        Args:
            htype (str): Homing sequence type e.g. RLIM HSW etc.
        """
        group = Group.instance()
        enc_axes = ""
        if group.controller is ControllerType.pbrick:
            line_start = "//"
        else:
            line_start = ";"
        if len(group.encoders)> 0:
            enc_axes = ", enc_axes = {enc}".format(enc=group.encoders)

            
        group.comment = "\n".join(
            [
                f"{line_start}  Axis {ax.axis}: htype = {htype}, "
                f"jdist = {ax.jdist}, post = {ax.post_home_with_distance}" 
                f"{enc_axes}"
                for ax in group.motors
            ]
        )

    @classmethod
    def add_snippet(cls, template_name: str, **args):
        """
        Add a jinja snippet to the list of snippets to be rendered

        Args:
            template_name (str): prefix of the jinja template's filename
                '.pmc.jinja' is added to this name and the template file
                should be in pmac_motorhome/snippets
        """
        group = Group.instance()
        group.templates.append(
            Template(jinja_file=template_name, args=args, function=None)
        )

    @classmethod
    def add_action(cls, func: Callable, **args):
        """
        Add a callback to the list of 'snippets' to be rendered The callback
        function should return an string to be inserted into the rendered
        template

        Args:
            func (Callable): the function to call
            args (dict): arguments to pass to func
        """
        group = Group.instance()
        group.templates.append(Template(jinja_file=None, function=func, args=args))

    # TODO maybe use *axes here for clarity in calls from Jinja
    def set_axis_filter(self, axes: List[int]) -> str:
        """
        A callback function to set group actions to only act on a subset of the
        group's axes.

        Will be called back during the rendering of plc.pmc.jinja, and is inserted
        using Group.add_action()

        Args:
            axes (List[int]): List of axis numbers to be controlled in this context

        Returns:
            str: Blank string. Required because this function is used as a callback
                from a jinja template and thus must return some string to insert into
                the template
        """
        if axes == []:
            # reset the axis filter
            self.motors = self.all_motors
        else:
            self.motors = [motor for motor in self.all_motors if motor.axis in axes]
            assert len(self.motors) == len(axes), "set_axis_filter: invalid axis number"
            # callback functions must return a string since we call them with
            # {{- group.callback(template.function, template.args) -}} from jinja
        return ""
    
    def all_motors_have_same_post_move_type(self) -> Tuple[bool, PostHomeMove]:
        """Check that all motors in the group have the same post move type
        """
        if len(self.all_motors) > 0:
            first_motor_post_home = self.all_motors[0].post_home
            return (all(motor.post_home == first_motor_post_home for motor in self.all_motors), first_motor_post_home)
        return False, PostHomeMove.none
            

    def command(self, cmd: str) -> str:
        """
        A callback function to insert arbitrarty text into the ouput Plc code.

        Will be called back during the rendering of plc.pmc.jinja, and is inserted
        using Group.add_action()

        Args:
            cmd (str): Any string

        Returns:
            str: the passed string (for jinja rendering)
        """
        return cmd

    def _all_axes(self, format: str, separator: str, *arg, filter_function = None) -> str:
        """
        A helper function that generates a command line by applying each of Motor
        in the group as a parameter to the format string and the concatenating all of
        the results with a separator.

        Args:
            format (str): The format string to apply, passing each Motor in the group
                as its arguments
            separator (str): Separator that goes between the formatted string for each
                axis
            arg ([Any]): additional arguments to pass to the format string

        Returns:
            str: The resulting command string
        """

        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name
        motors = self.motors
        if filter_function is not None:
            motors = filter(filter_function, self.motors)
        
        all = [format.format(*arg, **ax.dict) for ax in motors]
        return separator.join(all)

    def _all_encoders(self, format: str, separator: str, *arg) -> str:
        """
        A helper function that generates a command line by applying each of every
        element in enc_axes of each Motor in the group as a parameter to the format
        string and the concatenating all of the results with a separator.

        Args:
            format (str): The format string to apply, passing each Motor in the group
                as its arguments
            separator (str): Separator that goes between the formatted string for each
                axis
            arg ([Any]): additional arguments to pass to the format string

        Returns:
            str: The resulting command string
        """

        # to the string format: pass any extra arguments first, then the dictionary
        # of the axis object so its elements can be addressed by name

        all = [format.format(*arg, enc_axis=enc) for enc in self.encoders]
        return separator.join(all)

    def callback(self, function: Callable, args: Dict[str, Any]) -> str:
        """
        Callback from plc.pmc.jinja to a function that was added into the group
        using :func:`~Group.add_action`

        Args:
            function (Callable): the function to call
            args (Dict[str, Any]): arguments to pass to function

        Returns:
            str: The string to insert into the PLC output file
        """
        return function(self, **args)

    ########################################################################
    # The following functions are callbacks from the jinja templates they
    # are called with {{- group.function_name(template.args) -}} from jinja
    #
    # The are presently Turbo PMAC specific
    ########################################################################

    def jog_stopped(self) -> str:
        """
        Generate a command string that will jog any stopped axes in the group
        """

        if self.controller is ControllerType.pbrick:
            code = "if (Motor[{axis}].InPos == 1){\n    jog{axis}^*\n}"
        else:
            code = 'if (m{axis}40=1)\n    cmd "#{axis}J^*"\nendif'
        return self._all_axes(code, "\n")

    def jog_axes(self) -> str:
        """
        Generate a command string for all group axes: jog a set distance
        """
        if self.controller is ControllerType.pbrick:
            return f'jog{self._all_axes("{axis}", ",")}^*'
        else:
            return self._all_axes("#{axis}J^*", " ")

    def set_large_jog_distance(self, homing_direction: bool = True) -> str:
        """
        Generate a command string for all group axes: set large jog distance
        """

        if self.controller is ControllerType.pbrick:
            sign = "" if homing_direction else "-"
            return self._all_axes(
                "Motor[{axis}].ProgJogPos=100000000*({0}Motor[{axis}].HomeVel/"
                + "ABS(Motor[{axis}].HomeVel))",
                " ",
                sign,
            )
        else:
            sign = "" if homing_direction else "-"
            return self._all_axes(
                "m{axis}72=100000000*({0}i{axis}23/ABS(i{axis}23))", " ", sign
            )

    def jog(self, homing_direction: bool = True) -> str:
        """
        Generate a command string for all group axes: jog indefinitely
        """
        sign = "+" if homing_direction else "-"

        if self.controller is ControllerType.pbrick:
            return f'jog{sign}{self._all_axes("{axis}", ",")}'
        else:
            return self._all_axes("#{axis}J{0}", " ", sign)

    def in_pos(self, operator="&", relOperator="==", value=0) -> str:
        """
        Generate a command string for all group axes: check in postiion
        relOperator (relationalOperator) is required for power pmac based
        controllers as each variable needs to be evaluated separately
        """

        if self.controller is ControllerType.pbrick:
            pbrickVar = "Motor[{axis}].InPos"
            return self._all_axes(f"{pbrickVar} {relOperator} {value} ", "|| ")
        else:
            return self._all_axes("m{axis}40", operator)

    def limits(self, relOperator="!=", value=0) -> str:
        """
        Generate a command string for all group axes: check limits
        relOperator (relationalOperator) is required for power pmac based
        controllers as each variable needs to be evaluated separately
        """
        if self.controller is ControllerType.pbrick:
            pbrickVar = "Motor[{axis}].LimitStop"
            return self._all_axes(f"{pbrickVar} {relOperator} {value} ", "|| ")
        else:
            return self._all_axes("m{axis}30", "|")

    def following_err(self, relOperator="==", value=0) -> str:
        """
        Generate a command string for all group axes: check following error
        """
        if self.controller is ControllerType.pbrick:
            pbrickVar = "Motor[{axis}].FeFatal"
            return self._all_axes(f"{pbrickVar} {relOperator} {value} ", "|| ")
        else:
            return self._all_axes("m{axis}42", "|")

    def homed(self, value=0) -> str:
        """
        Generate a command string for all group axes: check homed
        """
        if self.controller is ControllerType.pbrick:
            pbrickVar = "Motor[{axis}].HomeComplete == "
            return self._all_axes(f"{pbrickVar}{value} ", "&& ")
        else:
            return self._all_axes("m{axis}45", "&")

    def clear_home(self) -> str:
        """
        Generate a command string for all group axes: clear home flag
        """

        if self.controller is ControllerType.pbrick:
            return self._all_axes("// Can't clear home on PBRICK", " ")
        else:
            return self._all_axes("m{axis}45=0", " ")

    def store_position_diff(self):
        """
        Generate a command string for all group axes: save position
        """

        if self.controller is ControllerType.pbrick:
            return self._all_axes(
                "P{pos}=(P{pos} - (Motor[{axis}].Pos - Motor[{axis}].HomePos))"
                + " + {jdist} - Motor[{axis}].HomeOffset",
                separator="\n        ",
            )
        else:
            return self._all_axes(
                "P{pos}=(P{pos}-M{axis}62)/(I{axis}08*32)+{jdist}-(i{axis}26/16)",
                separator="\n        ",
            )

    def stored_pos_to_jogdistance(self):
        """
        Generate a command string for all group axes: calculate jog distance
        to return to pre homed position
        """

        if self.controller is ControllerType.pbrick:
            return self._all_axes("Motor[{axis}].ProgJogPos=P{pos}", " ")
        else:
            return self._all_axes("m{axis}72=P{pos}", " ")

    def stored_limit_to_jogdistance(self, homing_direction=True):
        """
        Generate a command string for all group axes: save distance to limit
        """
        if self.controller is ControllerType.pbrick:
            if homing_direction:
                return self._all_axes("Motor[{axis}].ProgJogPos=P{hi_lim}", " ")
            else:
                return self._all_axes("Motor[{axis}].ProgJogPos=P{lo_lim}", " ")
        else:
            if homing_direction:
                return self._all_axes("m{axis}72=P{hi_lim}", " ")
            else:
                return self._all_axes("m{axis}72=P{lo_lim}", " ")

    def jog_distance(self):
        """
        Generate a command string for all group axes: jog to prejog position.
        Useful if a program has been aborted in the middle of a move, because it
        will move the motor to the programmed move end position
        """
        if self.controller is ControllerType.pbrick:
            return self._all_axes("jog{axis}={post_distance}", "") 
        else:
            return self._all_axes("#{axis}J=%s" % ("{post_distance}"), " ")

    def negate_home_flags(self):
        """
        Generate a command string for all group axes: invert homing flags
        """
        if self.controller == ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{not_homed}", " ")

        if self.controller == ControllerType.pbrick:
            return self._all_axes("{pb_homed_flag}=P{not_homed}", " ")
        
        if self.controller is ControllerType.brick and self.has_motors_with_macro_brick():
            return self._all_axes("MSW{macro_station_brick},i912,P{not_homed}", " ",filter_function = Group.filter_motors_with_macro) + " " + self._all_axes("i{homed_flag}=P{not_homed}", " ",filter_function = Group.filter_motors_without_macro)

        return self._all_axes("i{homed_flag}=P{not_homed}", " ")

    def restore_home_flags(self):
        """
        Generate a command string for all group axes: restore original homing flags
        """
        if self.controller == ControllerType.pmac:
            return self._all_axes("MSW{macro_station},i912,P{homed}", " ")

        if self.controller == ControllerType.pbrick:
            return self._all_axes("{pb_homed_flag}=P{homed}", " ")
        
        if self.controller is ControllerType.brick and self.has_motors_with_macro_brick():
            return self._all_axes("MSW{macro_station_brick},i912,P{homed}", " ", filter_function = Group.filter_motors_with_macro) + " " + self._all_axes("i{homed_flag}=P{homed}", " ", filter_function = Group.filter_motors_without_macro)

        return self._all_axes("i{homed_flag}=P{homed}", " ")

    def jog_to_home_jdist(self):
        """
        Generate a command string for all group axes: jog to home and then move jdist
        """

        if self.controller == ControllerType.pbrick:
            return self._all_axes("jog{axis}^*^{jdist}", " ")
        else:
            return self._all_axes("#{axis}J^*^{jdist}", " ")

    def home(self) -> str:
        """
        Generate a command string for all group axes: home command
        """
        if self.controller == ControllerType.pbrick:
            return f'home{self._all_axes("{axis}", ",")}'
        else:
            return self._all_axes("#{axis}hm", " ")

    def set_home(self, encoder=False) -> str:
        """
        Generate a command string for all group axes: set current position as home
        """
        if encoder:
            if self.controller == ControllerType.pbrick:
                return f'homez{self._all_encoders("{enc_axis}", ",")}'
            else:
                return self._all_encoders("#{enc_axis}hmz", " ")
        else:
            if self.controller == ControllerType.pbrick:
                return f'homez{self._all_axes("{axis}", ",")}'
            else:
                return self._all_axes("#{axis}hmz", " ")

    def restore_limit_flags(self):
        """
        Generate a command string for all group axes: restore original limit flags
        """

        if self.controller == ControllerType.pbrick:
            return self._all_axes("Motor[{axis}].pLimits=P{lim_flags}", " ")
        else:
            return self._all_axes("i{axis}24=P{lim_flags}", " ")

    def overwrite_inverse_flags(self):
        """
        Generate a command string for all group axes: reuse the not homed store to
        store ?? (TODO what is this doing ?)
        """
        # meow
        if self.controller == ControllerType.pmac:
            return self._all_axes("MSR{macro_station},i913,P{not_homed}", " ")
        if self.controller == ControllerType.pbrick:
            return self._all_axes("P{not_homed}={pb_inverse_flag}", " ")
        
        if self.controller is ControllerType.brick and self.has_motors_with_macro_brick():
            return self._all_axes("MSR{macro_station_brick},i912,P{not_homed}", " ",filter_function = Group.filter_motors_with_macro) + " " + self._all_axes("P{not_homed}=i{inverse_flag}", " ",filter_function = Group.filter_motors_without_macro)

        return self._all_axes("P{not_homed}=i{inverse_flag}", " ")

    def set_inpos_trigger(self, value: int):
        """
        Generate a command string for all group axes: set the inpos trigger ixx97
        """
        return self._all_axes("I{axis}97 = {0}", " ", value)
    
    @staticmethod
    def filter_motors_with_macro(motor) -> bool:
        """ 
        Check if motor (on a brick) has macro.

        Args:
            motor (Motor): motor being checked

        Returns:
            bool: true if the motor has macro (brick only)
        """
        return motor.has_macro_station_brick()
    
    @staticmethod
    def filter_motors_without_macro(motor) -> bool:
        """ 
        Check if motor (on a brick) doesn't have a  macro.

        Args:
            motor (Motor): motor being checked

        Returns:
            bool: true if the motor doesn't have macro (brick only)
        """
        return not (motor.has_macro_station_brick())

    def has_motors_with_macro_brick(self) -> bool:
        """
        Check if any of the motors in the group has macros (brick specific)

        Returns:
            bool: returns true is any of the motors in the group have defined macro (brick specific)
        """
        motors = list(filter(Group.filter_motors_with_macro, self.motors))
        return len(motors) > 0

