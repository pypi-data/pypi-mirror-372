try:
    from typing import OrderedDict
except Exception:
    from collections import OrderedDict  # type: ignore

import os
import pickle

from converter.pipemessage import IPC_FIFO_NAME, create_msg
from converter.shim.group import Group

from .globals import (  # BrickType,; HomingSequence,
    NO_HOMING_YET,
    PMAC,
    BrickTypes,
    HomingSequences,
)
from .motor import Motor


class PLC:
    # PLC class keeps a list of PLCs - object fatcory
    # TODO: add a factory class - discuss with Giles
    instances = []  # type: list

    def __init__(
        self,
        plc,
        timeout=600000,
        htype=NO_HOMING_YET,
        jdist=0,
        post=None,
        ctype=PMAC,
        allow_debug=True,
    ):
        self.plc = plc
        self.timeout = timeout
        self.htype = htype
        self.jdist = jdist
        self.post = post
        self.ctype = ctype
        self.allow_debug = allow_debug

        self.error = 0
        self.error_msg = ""

        # instantiate some members for translating parameters into the
        # new motorhome nomenclature
        self.sequence = HomingSequences[htype]
        self.bricktype = BrickTypes[ctype]

        # members for recording what is addded to this PLC
        self.groups = OrderedDict()
        self.filename = ""
        self.motor_nums = []

        self.instances.append(self)

    @classmethod
    # TODO: Move this to factory class
    def clear_instances(cls):
        cls.instances = []

    @classmethod
    # TODO: Move this to factory class
    def get_instances(cls):
        """
        Returns a list of instances of PLCs created since the last clear_instance().
        Ignores PLCs with no groups. This avoids an issue with redundant instances that
        came up in the first example.

        Yields:
            PLC: an iterator over all populated PLC instances
        """
        for instance in cls.instances:
            if len(instance.groups) > 0:
                yield instance

    def configure_group(self, group, checks=None, pre=None, post=None):
        self.groups[group].checks = checks
        print("prehome is ", pre)
        if pre is not None:
            self.groups[group].pre = pre
        if self.post is not None and post is None:
            self.groups[group].post = self.post
        elif post is not None:
            self.groups[group].post = post

    def add_motor(
        self,
        axis,
        group=1,
        htype=None,
        jdist=None,
        jdist_overrides=None,
        post=None,
        enc_axes=[],
        ms=None,
    ):
        if axis not in self.motor_nums:
            self.motor_nums.append(axis)
        motor_index = self.motor_nums.index(axis)

        motor = Motor(axis, enc_axes, self.ctype, ms, index=motor_index, post=post)
        if group not in self.groups:
            new_group = Group(group, checks=[], pre="", post=post)
            self.groups[group] = new_group

        if jdist is not None:
            motor.jdist = jdist
        else:
            motor.jdist = self.jdist

        self.groups[group].motors.append(motor)

        # homing type is specified at the group level but may be requested at
        # the motor, group or PLC level

        # specifying no homing type in add_motor impliess
        # using the one already assigned in  group but if group has none set
        # then also look in PLC
        if htype is not None:
            self.groups[group].set_htype(htype)
        elif self.groups[group].htype == NO_HOMING_YET and self.htype != NO_HOMING_YET:
            self.groups[group].set_htype(self.htype)
        # similar for post home action
        # print("post=", post, self.post)
        if post is not None:
            # TODO should check for illegal mixed of post home actions
            self.groups[group].post = post
        elif self.post is not None:
            self.groups[group].post = self.post

    def write(self, filename):
        # USE THIS
        self.filename = filename
        # make code
        plcs = list(PLC.get_instances())  # can't pickle generator objects!
        fifo = os.open(IPC_FIFO_NAME, os.O_WRONLY)
        try:
            msg = create_msg(pickle.dumps(plcs))
            os.write(fifo, msg)
        finally:
            os.close(fifo)
