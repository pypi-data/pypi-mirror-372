from enum import Enum, IntEnum, unique
from typing import Optional
from .generated.drone_pb2 import FlightMode as ProtoFlightMode  # type: ignore[attr-defined]

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_LANDED_STATE_IN_AIR,
    MAV_LANDED_STATE_LANDING,
    MAV_LANDED_STATE_ON_GROUND,
    MAV_LANDED_STATE_TAKEOFF,
    MAV_LANDED_STATE_UNDEFINED,
    MAV_RESULT_ACCEPTED,
    MAV_RESULT_COMMAND_INT_ONLY,
    MAV_RESULT_COMMAND_LONG_ONLY,
    MAV_RESULT_DENIED,
    MAV_RESULT_FAILED,
    MAV_RESULT_IN_PROGRESS,
    MAV_RESULT_TEMPORARILY_REJECTED,
    MAV_RESULT_UNSUPPORTED,
)


class Frame(Enum):
    LOCAL = 1
    BODY = 2
    GLOBAL = 3
    GENERIC = 4
    UNKNOWN = 0


class StatusText:
    def __init__(self, severity, msg):
        self.severity = severity
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.severity}: {self.msg}"


@unique
class PminiState(Enum):
    UNDEFINED = MAV_LANDED_STATE_UNDEFINED  # pmini landed state is unknown
    ON_GROUND = MAV_LANDED_STATE_ON_GROUND  # pmini is landed (on ground)
    IN_AIR = MAV_LANDED_STATE_IN_AIR  # pmini is in air
    TAKEOFF = MAV_LANDED_STATE_TAKEOFF  # pmini currently taking off
    LANDING = MAV_LANDED_STATE_LANDING  # pmini currently landing

    def is_flight(self) -> bool:
        return self == PminiState.IN_AIR or self == PminiState.TAKEOFF or self == PminiState.LANDING

    def is_on_ground(self) -> bool:
        return self == PminiState.ON_GROUND

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_msg(msg) -> "PminiState":
        if msg.get_type() != "EXTENDED_SYS_STATE":
            raise ValueError(f"Cannot convert {msg.get_type()} to PminiState")
        try:
            return PminiState(msg.landed_state)
        except ValueError:
            return PminiState.UNDEFINED


class Yaw:
    class Frame(Enum):
        ANGLE = 1
        ANG_VEL = 2

    def __init__(self, value: float = 0.0, frame: Frame = Frame.ANGLE):
        self.value = value
        self.frame = frame

    def __add__(self, other):
        if not isinstance(other, Yaw):
            return NotImplemented

        if self.frame != other.frame:
            raise ValueError("Cannot add Yaw instances with different frames")

        return Yaw(self.value + other.value, self.frame)


class Quaternion:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w


@unique
class FlightMode(Enum):
    STABILIZE = 0
    ACRO = 1
    ALT_HOLD = 2
    AUTO = 3
    GUIDED = 4
    LOITER = 5
    RTL = 6
    CIRCLE = 7
    LAND = 9
    DRIFT = 11
    SPORT = 13
    FLIP = 14
    AUTO_TUNE = 15
    POS_HOLD = 16
    BREAK = 17
    THROW = 18
    AVOID_ADBS = 19
    GUIDED_NO_GPS = 20
    SMART_RTL = 21
    FLOW_HOLD = 22
    FOLLOW = 23
    ZIGZAG = 24
    SYSTEM_ID = 25
    AUTO_ROTATE = 26
    AUTO_RTL = 27
    TURTLE = 28
    UNKNOWN = 100

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def from_msg(msg) -> "FlightMode":
        if msg.get_type() != "HEARTBEAT":
            raise ValueError(f"Cannot convert {msg.get_type()} to FlightMode")
        return FlightMode(msg.custom_mode)

    @staticmethod
    def from_proto(proto_msg: ProtoFlightMode) -> "FlightMode":
        # Map proto FlightMode enum values to SDK FlightMode enum values
        proto_to_sdk = {
            0: FlightMode.STABILIZE,
            1: FlightMode.ACRO,
            2: FlightMode.ALT_HOLD,
            3: FlightMode.AUTO,
            4: FlightMode.GUIDED,
            5: FlightMode.LOITER,
            6: FlightMode.RTL,
            7: FlightMode.CIRCLE,
            8: FlightMode.LAND,
            9: FlightMode.DRIFT,
            10: FlightMode.SPORT,
            11: FlightMode.FLIP,
            12: FlightMode.AUTO_TUNE,
            13: FlightMode.POS_HOLD,
            14: FlightMode.BREAK,
            15: FlightMode.THROW,
            16: FlightMode.AVOID_ADBS,
            17: FlightMode.GUIDED_NO_GPS,
            18: FlightMode.SMART_RTL,
            19: FlightMode.FLOW_HOLD,
            20: FlightMode.FOLLOW,
            21: FlightMode.ZIGZAG,
            22: FlightMode.SYSTEM_ID,
            23: FlightMode.AUTO_ROTATE,
            24: FlightMode.AUTO_RTL,
            25: FlightMode.TURTLE,
            26: FlightMode.UNKNOWN,
        }
        # Accept either enum or int
        value = proto_msg.value if hasattr(proto_msg, "value") else int(proto_msg)
        return proto_to_sdk.get(value, FlightMode.UNKNOWN)

    @staticmethod
    def from_id(id: int) -> "FlightMode":
        for mode in FlightMode:
            if mode.value == id:
                return mode
        return FlightMode.UNKNOWN

    def to_id(self) -> int:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FlightMode):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, FlightMode):
            return NotImplemented
        return self.value != other.value

    def is_armable(self) -> bool:
        return self not in {FlightMode.LAND, FlightMode.RTL, FlightMode.AUTO_RTL, FlightMode.AUTO, FlightMode.UNKNOWN}


@unique
class MAVResult(Enum):
    ACCEPTED = MAV_RESULT_ACCEPTED  # Valid, supported, executed
    TEMPORARILY_REJECTED = MAV_RESULT_TEMPORARILY_REJECTED  # Valid, but not now
    DENIED = MAV_RESULT_DENIED  # Invalid params
    UNSUPPORTED = MAV_RESULT_UNSUPPORTED  # Unknown command
    FAILED = MAV_RESULT_FAILED  # Executed, but failed
    IN_PROGRESS = MAV_RESULT_IN_PROGRESS  # Still running
    COMMAND_LONG_ONLY = MAV_RESULT_COMMAND_LONG_ONLY  # Command is only accepted when sent as a COMMAND_LONG
    COMMAND_INT_ONLY = MAV_RESULT_COMMAND_INT_ONLY  # Command is only accepted when sent as a COMMAND_INT

    def __str__(self) -> str:
        return self.name

    def is_success(self) -> bool:
        return self == MAVResult.ACCEPTED

    def is_temporary(self) -> bool:
        return self == MAVResult.TEMPORARILY_REJECTED or self == MAVResult.IN_PROGRESS

    def is_failed(self) -> bool:
        return self in {
            MAVResult.DENIED,
            MAVResult.UNSUPPORTED,
            MAVResult.FAILED,
            MAVResult.COMMAND_LONG_ONLY,
            MAVResult.COMMAND_INT_ONLY,
        }


def parse_mav_result(code: int) -> Optional[MAVResult]:
    """Maps raw int to MAVResult enum, or None if unknown."""
    try:
        return MAVResult(code)
    except ValueError:
        return None


@unique
class DroneErrorCode(IntEnum):
    """Enhanced error codes for drone operations with MAVLink integration."""

    SUCCESS = 0
    FAILED = 1
    TIMEOUT = 2
    INVALID_PARAMETER = 3
    NOT_CONNECTED = 4
    NOT_ARMED = 5
    ALREADY_ARMED = 6
    INVALID_MODE = 7
    MODE_CHANGE_FAILED = 8
    ALTITUDE_TOO_HIGH = 9
    ALTITUDE_TOO_LOW = 10
    BATTERY_LOW = 11
    GPS_NOT_READY = 12
    SENSORS_NOT_READY = 13
    TAKEOFF_FAILED = 14
    LANDING_FAILED = 15
    COMMAND_DENIED = 16
    TEMPORARILY_REJECTED = 17
    UNSUPPORTED = 18
    IN_PROGRESS = 19
    COMMUNICATION_ERROR = 20
    INTERNAL_ERROR = 21

    def __str__(self) -> str:
        return self.name

    def is_success(self) -> bool:
        return self == DroneErrorCode.SUCCESS

    def is_temporary(self) -> bool:
        return self in {DroneErrorCode.TEMPORARILY_REJECTED, DroneErrorCode.IN_PROGRESS, DroneErrorCode.TIMEOUT}

    def is_failed(self) -> bool:
        return not self.is_success() and not self.is_temporary()

    @staticmethod
    def from_mav_result(mav_result: MAVResult) -> "DroneErrorCode":
        """Convert MAVResult to DroneErrorCode."""
        mapping = {
            MAVResult.ACCEPTED: DroneErrorCode.SUCCESS,
            MAVResult.TEMPORARILY_REJECTED: DroneErrorCode.TEMPORARILY_REJECTED,
            MAVResult.DENIED: DroneErrorCode.COMMAND_DENIED,
            MAVResult.UNSUPPORTED: DroneErrorCode.UNSUPPORTED,
            MAVResult.FAILED: DroneErrorCode.FAILED,
            MAVResult.IN_PROGRESS: DroneErrorCode.IN_PROGRESS,
            MAVResult.COMMAND_LONG_ONLY: DroneErrorCode.UNSUPPORTED,
            MAVResult.COMMAND_INT_ONLY: DroneErrorCode.UNSUPPORTED,
        }
        return mapping.get(mav_result, DroneErrorCode.FAILED)

    def to_mav_result(self) -> MAVResult:
        """Convert DroneErrorCode to MAVResult (best effort)."""
        mapping = {
            DroneErrorCode.SUCCESS: MAVResult.ACCEPTED,
            DroneErrorCode.TEMPORARILY_REJECTED: MAVResult.TEMPORARILY_REJECTED,
            DroneErrorCode.COMMAND_DENIED: MAVResult.DENIED,
            DroneErrorCode.UNSUPPORTED: MAVResult.UNSUPPORTED,
            DroneErrorCode.IN_PROGRESS: MAVResult.IN_PROGRESS,
            DroneErrorCode.TIMEOUT: MAVResult.TEMPORARILY_REJECTED,
        }
        return mapping.get(self, MAVResult.FAILED)
