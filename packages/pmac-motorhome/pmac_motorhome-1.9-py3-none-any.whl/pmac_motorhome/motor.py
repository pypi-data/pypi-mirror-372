from typing import Dict

from pmac_motorhome.constants import PostHomeMove


class Motor:
    """
    Declares a motor for use in homing routines in the enclosing Group, Plc

    Should always be instantiated using `pmac_motorhome.commands.motor`
    """

    instances: Dict[int, "Motor"] = {}

    # offsets into the PLC's PVariables for storing the state of axes
    # these names go into long format strings so keep them short for legibility
    PVARS = {
        "hi_lim": 4,
        "lo_lim": 20,
        "homed": 36,
        "not_homed": 52,
        "lim_flags": 68,
        "pos": 84,
    }

    def __init__(
        self,
        axis: int,
        jdist: int,
        plc_num: int,
        post_home: PostHomeMove = PostHomeMove.none,
        post_distance: int = 0,
        index: int = -1,
        ms: int = -1
    ) -> None:
        """
        Args:
            axis (int): Axis number of the motor
            jdist (int): Distance in counts to jog after finding the home mark
                this should be enough distance to move clear of the home mark
            plc_num (int): the plc number of the enclosing Plc
            post_home (PostHomeMove): the action to perform on this motor when
                homing is complete
            post_distance (int): A distance to use in post_home
            index (int): for internal use in conversion of old scripts sets
                the index of this motor to a different value than the order of
                declaration.
            ms (int): macrostation number
        """
        self.axis = axis
        self.jdist = jdist
        if index == -1:
            self.index = len(self.instances)
        else:
            self.index = index

        self.instances[axis] = self
        self.post_home = post_home
        self.post_distance = post_distance
        self.ms = ms

        # dict is for terse string formatting code in _all_axes() functions
        self.dict = {
            "axis": axis,
            "index": self.index,
            "jdist": jdist,
            "homed_flag": f"7{self.nx}2",
            "pb_homed_flag": f"Gate3[{self.gate}].Chan[{self.chan}].CaptCtrl",
            "inverse_flag": f"7{self.nx}3",
            "pb_inverse_flag": f"Gate3[{self.gate}].Chan[{self.chan}].CaptFlagSel",
            "macro_station": self.macro_station,
            "post_distance": self.post_home_distance,
            "macro_station_brick": self.macro_station_brick_str,
        }
        for name, start in self.PVARS.items():
            self.dict[name] = plc_num * 100 + start + self.index

    @classmethod
    def get_motor(
        cls,
        axis: int,
        jdist: int,
        plc_num: int,
        post_home: PostHomeMove = PostHomeMove.none,
        post_distance: int = 0,
        index: int = -1,
        ms: int = -1,
    ) -> "Motor":
        """
        A factory function to return a Motor object but ensure that there
        is only ever one instance of each axis number. This is required since
        PLC code allocates p variables on a per axis basis.
        """
        motor = cls.instances.get(axis)
        if motor is None:
            motor = Motor(axis, jdist, plc_num, post_home, post_distance, index, ms)

        return motor

    # TODO IMPORTANT - this is used in finding the Home capture flags etc. and is
    # specific to Geobrick - For a full implementation see Motor class in
    #  ... pmacutil/pmacUtilApp/src/motorhome.py
    # HINT: watch out for python 2 vs python 3 handling of integer arithmetic
    @property
    def nx(self) -> str:
        nx = int(int((self.axis - 1) / 4) * 10 + int((self.axis - 1) % 4 + 1))
        return "{:02}".format(nx)

    # Determine the gate number if power pmac
    @property
    def gate(self) -> str:
        return str(int((self.axis - 1) / 4))

    # Determine the channel number of the above gate
    @property
    def chan(self) -> str:
        return str(int((self.axis - 1) % 4))

    @property
    def homed(self):
        return self.dict["homed"]

    @property
    def not_homed(self):
        return self.dict["not_homed"]

    @property
    def macro_station(self) -> str:
        """
        Calculate macro and generate a command string for this motor 
        Pmac specific command string

        Returns:
            str: pmac specific ms command string 
        """
        # this calculations are only correct for a pmac
        if self.ms != -1:
            return "{}".format(self.ms)
        msr = int(4 * int(int(self.axis - 1) / 2) + int(self.axis - 1) % 2)
        return "{}".format(msr)

    @property
    def macro_station_brick_str(self) -> str:
        """
        Generate a command string for this motor 
        Brick specific command string

        Returns:
            str: brick specific ms command string
        """
        if self.macro_station_brick() == -1:
            return ""
        return "{}".format(self.macro_station_brick() )

    def macro_station_brick(self) -> int:
        """
        Return or calculate macro station number.
        Brick specific calculation

        Returns:
            int: brick specific macro station number
        """

        if self.ms != -1:
            return self.ms
        if self.axis > 8:
            return int(4 * int(int(self.axis - 9) / 2) + int(self.axis - 9) % 2)
        return -1

    @property
    def post_home_distance(self) -> str:
        """
        Generate a post distance string

        Returns:
            str: post distance string, "*" if post distance is 0
        """
        if self.post_distance == 0:
            return "*"
        return str(int(self.post_distance))

    @property
    def post_home_with_distance(self) -> str:
        """
        Generate one string which contains the post home move with distance (if applicable) for this motor.

        Returns:
            str:  one string describing the post home move for this motor.
        """
        if self.post_distance == 0:
            return self.post_home.value
        elif self.post_home in (PostHomeMove.none, PostHomeMove.move_absolute):
            return str(self.post_distance)
        return  self.post_home.value + str(self.post_distance)

    def has_macro_station_brick(self) -> bool:
        """"
        Check if the motor has macro station defined (brick only)

        Returns:
            bool: true if macro station defined for the motor
        """
        if self.macro_station_brick() != -1:
            return True
        return False

