"""
StatusResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import StatusResponse as ProtoStatusResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class StatusResponse:
    """StatusResponse message type.
    

    Parameters
    ----------

    connected : bool
        Connected value

    message : str
        Message value

    status_code : DroneErrorCode
        Status Code value

    current_position : Position
        Current Position value

    current_attitude : Attitude
        Current Attitude value

    flight_mode : FlightMode
        Flight Mode value

    armed : bool
        Armed value

    battery_remaining : float
        Battery Remaining value


    """

    connected: "bool"

    message: "str"

    status_code: "DroneErrorCode"

    current_position: "Position"

    current_attitude: "Attitude"

    flight_mode: "FlightMode"

    armed: "bool"

    battery_remaining: "float"


    def __init__(self, connected: "bool", message: "str", status_code: "DroneErrorCode", current_position: "Position", current_attitude: "Attitude", flight_mode: "FlightMode", armed: "bool", battery_remaining: "float"):
        """Initialize StatusResponse.
        

        Parameters
        ----------

        connected : bool
            Connected value

        message : str
            Message value

        status_code : DroneErrorCode
            Status Code value

        current_position : Position
            Current Position value

        current_attitude : Attitude
            Current Attitude value

        flight_mode : FlightMode
            Flight Mode value

        armed : bool
            Armed value

        battery_remaining : float
            Battery Remaining value


        """

        self.connected = connected

        self.message = message

        self.status_code = status_code

        self.current_position = current_position

        self.current_attitude = current_attitude

        self.flight_mode = flight_mode

        self.armed = armed

        self.battery_remaining = battery_remaining


    @classmethod
    def from_proto(cls, proto_msg: ProtoStatusResponse) -> "StatusResponse":
        """Create StatusResponse from protobuf message."""
        
        
        
        
        
        
        
        
        from .position import Position
        
        
        
        from .attitude import Attitude
        
        
        
        
        
        
        
        
        return cls(

            
            connected=proto_msg.connected,
            

            
            message=proto_msg.message,
            

            
            status_code=proto_msg.status_code,
            

            
            current_position=Position.from_proto(proto_msg.current_position),
            

            
            current_attitude=Attitude.from_proto(proto_msg.current_attitude),
            

            
            flight_mode=proto_msg.flight_mode,
            

            
            armed=proto_msg.armed,
            

            
            battery_remaining=proto_msg.battery_remaining,
            

        )

    def to_proto(self) -> ProtoStatusResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoStatusResponse()

        
        
        proto_msg.connected = self.connected
        
        

        
        
        proto_msg.message = self.message
        
        

        
        
        proto_msg.status_code = self.status_code
        
        

        
        
        proto_msg.current_position.CopyFrom(self.current_position.to_proto())
        
        

        
        
        proto_msg.current_attitude.CopyFrom(self.current_attitude.to_proto())
        
        

        
        
        proto_msg.flight_mode = self.flight_mode
        
        

        
        
        proto_msg.armed = self.armed
        
        

        
        
        proto_msg.battery_remaining = self.battery_remaining
        
        

        return proto_msg