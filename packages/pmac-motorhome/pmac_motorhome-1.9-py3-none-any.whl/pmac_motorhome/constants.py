"""
Defines some Enumerations for constant values

"""
from enum import Enum


class ControllerType(Enum):
    """
    Defines the types of controller supported
    """

    #: Geobrick controller
    brick = "GeoBrick"
    #: VME PMAC Controller
    pmac = "PMAC"
    #: Power pmac controller
    pbrick = "PowerBrick"


class PostHomeMove(Enum):
    """
    Defines the set up actions available upon completion of the homing sequence
    """

    #: no action
    none = "None"
    zero = "0" # setting post to 0 will result in no post and not inheriting the group post
    #: move jdist counts away from the home mark and set that as home
    move_and_hmz = "z"
    #: move jdist counts away from the home mark
    relative_move = "r"
    #: return to the original position before the homing sequence
    initial_position = "i"
    #: jog to the high limit
    high_limit = "h"
    #: jog to the low limit
    low_limit = "l"
    #: jog to the high limit, ignorning soft limits
    hard_hi_limit = "H"
    #: jog to the low limit, ignorning soft limits
    hard_lo_limit = "L"
    #: jog to the absolute position in counts
    move_absolute = "a"


class HomingState(Enum):
    """
    Defines the stages of homing as reported back to the monitoring IOC
    TODO docs for this are incorrect and I'm confusing HomingState with HomingStatus
    """

    #: Homing is not running
    StateIdle = 0
    #: Homing is starting up
    StateConfiguring = 1
    #: Homing is moving in opposite direction to homing direction
    StateMoveNeg = 2
    #: Homing is moving in the homing direction
    StateMovePos = 3
    #: HM command has been issued to the pmac
    StateHoming = 4
    #: executing any post home moves
    StatePostHomeMove = 5
    #: executing alignment (unused)
    StateAligning = 6
    #: Homing is complete
    StateDone = 7
    #: Pre Home fast search for home position
    StateFastSearch = 8
    #: Moving back to just before home position
    StateFastRetrace = 9
    #:
    StatePreHomeMove = 10
