from enum import IntEnum

import sys
if sys.version_info >= (3, 9):
    import neuromeka.proto.common_msgs_pb2 as common_msgs
    import neuromeka.proto.control_msgs_pb2 as control_msgs
    import neuromeka.proto.device_msgs_pb2 as device_msgs
else:
    import neuromeka.proto_step.common_msgs_pb2 as common_msgs
    import neuromeka.proto_step.control_msgs_pb2 as control_msgs
    import neuromeka.proto_step.device_msgs_pb2 as device_msgs

from dataclasses import dataclass, field
from typing import List, Tuple



class OpState:
    SYSTEM_OFF = common_msgs.OP_SYSTEM_OFF
    SYSTEM_ON = common_msgs.OP_SYSTEM_ON
    VIOLATE = common_msgs.OP_VIOLATE
    RECOVER_HARD = common_msgs.OP_RECOVER_HARD
    RECOVER_SOFT = common_msgs.OP_RECOVER_SOFT
    IDLE = common_msgs.OP_IDLE
    MOVING = common_msgs.OP_MOVING
    TEACHING = common_msgs.OP_TEACHING
    COLLISION = common_msgs.OP_COLLISION
    STOP_AND_OFF = common_msgs.OP_STOP_AND_OFF
    COMPLIANCE = common_msgs.OP_COMPLIANCE
    BRAKE_CONTROL = common_msgs.OP_BRAKE_CONTROL
    SYSTEM_RESET = common_msgs.OP_SYSTEM_RESET
    SYSTEM_SWITCH = common_msgs.OP_SYSTEM_SWITCH
    VIOLATE_HARD = common_msgs.OP_VIOLATE_HARD
    MANUAL_RECOVER = common_msgs.OP_MANUAL_RECOVER
    TELE_OP = common_msgs.TELE_OP


class ProgramState:
    IDLE = common_msgs.PROG_IDLE
    RUNNING = common_msgs.PROG_RUNNING
    PAUSING = common_msgs.PROG_PAUSING
    STOPPING = common_msgs.PROG_STOPPING

class DigitalState:
    UNUSED = device_msgs.UNUSED_STATE
    OFF = device_msgs.OFF_STATE
    ON = device_msgs.ON_STATE

class EndtoolState:
    UNUSED = device_msgs.UNUSED
    HIGH_PNP = device_msgs.HIGH_PNP
    HIGH_NPN = device_msgs.HIGH_NPN
    LOW_NPN = device_msgs.LOW_NPN
    LOW_PNP = device_msgs.LOW_PNP


class StopCategory:
    CAT0 = common_msgs.IMMEDIATE_BRAKE
    CAT1 = common_msgs.SMOOTH_BRAKE
    CAT2 = common_msgs.SMOOTH_ONLY

class JointBaseType:
    ABSOLUTE = control_msgs.ABSOLUTE_JOINT
    RELATIVE = control_msgs.RELATIVE_JOINT

class TaskBaseType:
    ABSOLUTE = control_msgs.ABSOLUTE_TASK
    RELATIVE = control_msgs.RELATIVE_TASK
    TCP = control_msgs.TCP_TASK

class InterpolatorType(IntEnum):
    VELOCITY = 0
    TIME = 1


class CircularSettingType(IntEnum):
    POINT_SET = control_msgs.POINT_SET
    CENTER_AXIS = control_msgs.CENTER_AXIS


class BlendingType:
    NONE = control_msgs.BlendingType.NONE
    OVERRIDE = control_msgs.BlendingType.OVERRIDE
    DUPLICATE = control_msgs.BlendingType.DUPLICATE
    RADIUS = 4

class JointTeleopType:
    ABSOLUTE = control_msgs.TELE_JOINT_ABSOLUTE
    RELATIVE = control_msgs.TELE_JOINT_RELATIVE

class TaskTeleopType:
    ABSOLUTE = control_msgs.TELE_TASK_ABSOLUTE
    RELATIVE = control_msgs.TELE_TASK_RELATIVE

class TrajCondType:
    STARTED = common_msgs.TRAJ_STARTED
    ACC_DONE = common_msgs.TRAJ_ACC_DONE
    CRZ_DONE = common_msgs.TRAJ_CRZ_DONE
    DEC_DONE = common_msgs.TRAJ_DEC_DONE


class TrajState:
    NONE = common_msgs.TrajState.TRAJ_NONE
    INIT = common_msgs.TRAJ_INIT
    CALC = common_msgs.TRAJ_CALC
    STAND_BY  = common_msgs.TRAJ_STAND_BY
    ACC = common_msgs.TRAJ_ACC
    CRUISE = common_msgs.TRAJ_CRUISE
    DEC = common_msgs.TRAJ_DEC
    CANCELLING = common_msgs.TRAJ_CANCELLING
    FINISHED = common_msgs.TRAJ_FINISHED
    ERROR = common_msgs.TRAJ_ERROR


class BlendingCondType:
    TIME = 0
    DIO = 1
    PROGRESS = 2
    ACCELERATION = 3
    CONSTSPEED = 4
    DECELERATION = 5
    RADIUS = 6
    EXPRESSION = 7


class CircularSettingType:
    POINT_SET = 0
    CENTER_AXIS = 1


class CircularMovingType:
    CONSTANT = 0
    RADIAL = 1
    SMOOTH = 2


class StopType:
    IMMEDIATE_BRAKE = common_msgs.IMMEDIATE_BRAKE
    SLOW_AND_BRAKE = common_msgs.SMOOTH_BRAKE
    SLOW = common_msgs.SMOOTH_ONLY


class PauseType:
    SMOOTH = common_msgs.SMOOTH_PAUSE
    IMMEDIATE = common_msgs.IMMEDIATE_PAUSE



class CollisionPolicyType:
    NONE = common_msgs.COLL_NO_DETECT
    NO_DETECT = common_msgs.COLL_NO_DETECT
    PAUSE = common_msgs.COLL_PAUSE
    RESUME_AFTER_SLEEP = common_msgs.COLL_RESUME_AFTER_SLEEP
    STOP = common_msgs.COLL_STOP


class ConditionType:
    CONST_CONT = control_msgs.MotionCondition.CONST_COND
    IO_CONT = control_msgs.MotionCondition.IO_COND
    VAR_COND = control_msgs.MotionCondition.VAR_COND


class ReactionType:
    NONE = 0  # control_data.MotionCondition.NONE_COND
    STOP = 1  # control_data.MotionCondition.STOP_COND
    PAUSE = 2  # control_data.MotionCondition.PAUSE_COND


@dataclass
class PostCondition:
    condition_type: ConditionType = ConditionType.CONST_CONT
    reaction_type: ReactionType = ReactionType.NONE
    const_cond: bool = True
    digital_inputs: List[Tuple[int, bool]] = field(default_factory=list)
    i_vars: List[Tuple[str, int]] = field(default_factory=list)
    f_vars: List[Tuple[str, float]] = field(default_factory=list)
    b_vars: List[Tuple[str, bool]] = field(default_factory=list)
    m_vars: List[Tuple[str, int]] = field(default_factory=list)
    j_vars: List[Tuple[str, List[float]]] = field(default_factory=list)
    t_vars: List[Tuple[str, List[float]]] = field(default_factory=list)


# Boundaries for Indy High-level Command
class Limits(IntEnum):
    LevelMin = 1
    LevelMax = 9
    JogLevelMin = 1
    JogLevelMax = 3
    JogVelLevelDefault = 2
    JogAccLevelDefault = 2

    JogVelRatioDefault = 15  # %
    JogAccRatioDefault = 100  # %
    VelRatioMax = 100  # %
    VelRatioMin = 1  # %
    AccRatioMax = 900  # %
    AccRatioMin = 1  # %

    JogVelRatioMin = 5  # %
    JogVelRatioMax = 25  # %
    VelAutoLevelValue = (VelRatioMax - JogVelRatioMax) / (LevelMax - JogLevelMax)  # %
    VelManualLevelValue = (JogVelRatioMax - JogVelRatioMin) / (JogLevelMax - JogLevelMin)  # %

    TaskDispVelValueDefault = 250  # 250mm/s
    TaskDispAccValueDefault = 250  # 250mm/s^2
    TaskDispVelValueMax = 1000  # mm/s
    TaskRotVelValueMax = 120  # deg/s

    ExternalMotorSpeedMax = 250  # mm/s : 3000rpm -> 50 rev/sec * 5 mm/rev -> 250 mm/s


class DetectType:
    DETECT = 0
    RETRIEVE = 1


class VisionServerType:
    INDYEYE = 0
    PICKIT = 1
    OMRON = 2


@dataclass
class VisionFrame:
    vision_server: str
    target_object: str


@dataclass
class VisionServer:
    name: str
    vision_server_type: VisionServerType
    ip: str
    port: str


@dataclass
class VisionResult:
    object_name: str
    detected: bool
    passed: bool
    frame: list


# @dataclass
# class CollisionConfig:
#     policy: CollisionPolicyType = CollisionPolicyType.PAUSE
#     sleep_time: int = 5


# @dataclass
# class CollisionTuning:
#     precision: TuningPrecision = TuningPrecision.MIDDLE
#     tuning_space: TuningSpace = TuningSpace.NONE
#     vel_level_max: int = 3



# @dataclass
# class Blend:
#     blending_type: BlendingType = BlendingType.NONE
#     blending_condition_type: BlendingCondType = BlendingCondType.RADIUS
#     conjunction: int = 0
#     async_sleep: bool = True
#
#     traj_radius: float = 0.0
#     time: int = -1
#     digital_outputs: List[Tuple[int, bool]] = field(default_factory=list)
#     digital_inputs: List[Tuple[int, bool]] = field(default_factory=list)
#     traj_progress: int = -1

class EtherCATStatus(IntEnum):
    OP_MODE_NO_MODE = 0x00
    OP_MODE_PROFILE_POSITION = 0x01
    OP_MODE_VELOCITY = 0x02
    OP_MODE_PROFILE_VELOCITY = 0x03
    OP_MODE_TORQUE_PROFILE = 0x04
    OP_MODE_HOMING = 0x06
    OP_MODE_INTERPOLATED_POSITION = 0x07
    OP_MODE_CYCLIC_SYNC_POSITION = 0x08
    OP_MODE_CYCLIC_SYNC_VELOCITY = 0x09
    OP_MODE_CYCLIC_SYNC_TORQUE = 0x0a

    @staticmethod
    def status2string(statusword):
        if (((statusword) & 0x004f) == 0x0000):  # x0xx 0000
            return "NOT_READY"
        elif (((statusword) & 0x004f) == 0x0040):  # x1xx 0000
            return "SWITCH_DISABLED"
        elif (((statusword) & 0x006f) == 0x0021):  # x01x 0001
            return "READY_SWITCH"
        elif (((statusword) & 0x006f) == 0x0023):  # x01x 0011
            return "SWITCHED_ON"
        elif (((statusword) & 0x006f) == 0x0027):  # x01x 0111
            return "OPERATION_ENABLED"
        elif (((statusword) & 0x006f) == 0x0007):  # x00x 0111
            return "QUICK_STOP"
        elif (((statusword) & 0x004f) == 0x000f):  # x0xx 1111
            return "FAULT_REACTION"
        elif (((statusword) & 0x004f) == 0x0008):  # x0xx 1000
            return "FAULT"
        else:
            return "UNKNOWN"

    @staticmethod
    def modeop2string(modeop):
        if modeop == 0x00:
            return "None"
        elif modeop == 0x01:
            return "PP"
        elif modeop == 0x03:
            return "PV"
        elif modeop == 0x04:
            return "TP"
        elif modeop == 0x06:
            return "Homing"
        elif modeop == 0x08:
            return "CSP"
        elif modeop == 0x09:
            return "CSV"
        elif modeop == 0x0a:
            return "CST"
        else:
            return "UNKNOWN"

    @staticmethod
    def error_code(mode_op, status_word):
        string_out = []
        if mode_op == EtherCATStatus.OP_MODE_PROFILE_POSITION:
            if (status_word & 0x2000):
                string_out.append("Following error")
            if (status_word & 0x1000):
                string_out.append("Set-point acknowledge")
            if (status_word & 0x0400):
                string_out.append("Target reached")

        elif mode_op == EtherCATStatus.OP_MODE_PROFILE_VELOCITY:
            if (status_word & 0x2000):
                string_out.append("Max slippage error")
            if (status_word & 0x1000):
                string_out.append("Speed")
            if (status_word & 0x0400):
                string_out.append("Target reached")

        elif mode_op == EtherCATStatus.OP_MODE_CYCLIC_SYNC_POSITION:
            if (status_word & 0x2000):
                string_out.append("Following error")
            if (status_word & 0x1000):
                string_out.append("Drive follows command value")

        elif mode_op == EtherCATStatus.OP_MODE_CYCLIC_SYNC_VELOCITY:
            if (status_word & 0x1000):
                string_out.append("Drive follows command value")

        elif mode_op == EtherCATStatus.OP_MODE_CYCLIC_SYNC_TORQUE:
            if (status_word & 0x1000):
                string_out.append("Drive follows command value")

        return string_out