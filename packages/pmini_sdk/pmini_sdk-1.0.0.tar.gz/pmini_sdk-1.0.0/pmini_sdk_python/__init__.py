"""
Pmini SDK Python - Python SDK for Pmini quadcopter.

This package provides both MAVLink and gRPC interfaces for controlling
Pmini quadcopters with full type safety and comprehensive documentation.
"""

from .common import DroneErrorCode, FlightMode, Frame, MAVResult, PminiState, StatusText, Yaw

# Import generated classes for convenience
from .generated import (
    ArmRequest,
    Attitude,
    CommandResponse,
    DisarmRequest,
    DroneService,
    LandRequest,
    Position,
    PositionResponse,
    SetModeRequest,
    StatusResponse,
    TakeoffRequest,
    Velocity,
    VelocityResponse,
)
from .drone_client import DroneClient, DroneError, ConnectionError, CommandError
from .sync_drone_client import SyncDroneClient
from .high_level_commander import HighLevelCommander
from .low_level_commander import LowLevelCommander
from .mavlink_client import Config, MavlinkClient
from .pmini import Pmini

__version__ = "0.0.0"

__all__ = [
    # Main classes
    "Pmini",
    "Config",
    "MavlinkClient",
    # Commanders
    "HighLevelCommander",
    "LowLevelCommander",
    # Client classes
    "DroneClient",
    "SyncDroneClient",
    "DroneError",
    "ConnectionError",
    "CommandError",
    # Common types
    "FlightMode",
    "Frame",
    "MAVResult",
    "PminiState",
    "Yaw",
    "DroneErrorCode",
    "StatusText",
    # Generated classes
    "Attitude",
    "Position",
    "Velocity",
    "TakeoffRequest",
    "LandRequest",
    "ArmRequest",
    "DisarmRequest",
    "SetModeRequest",
    "CommandResponse",
    "StatusResponse",
    "PositionResponse",
    "VelocityResponse",
    "DroneService",
]
