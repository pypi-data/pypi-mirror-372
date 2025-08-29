"""
HealthResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import HealthResponse as ProtoHealthResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class HealthResponse:
    """HealthResponse message type.
    

    Parameters
    ----------

    is_healthy : bool
        Is Healthy value

    message : str
        Message value

    has_position_data : bool
        Has Position Data value

    has_velocity_data : bool
        Has Velocity Data value

    has_attitude_data : bool
        Has Attitude Data value

    has_optical_flow_data : bool
        Has Optical Flow Data value

    is_connected : bool
        Is Connected value

    is_armed : bool
        Is Armed value

    flight_mode : FlightMode
        Flight Mode value

    battery_remaining : float
        Battery Remaining value


    """

    is_healthy: "bool"

    message: "str"

    has_position_data: "bool"

    has_velocity_data: "bool"

    has_attitude_data: "bool"

    has_optical_flow_data: "bool"

    is_connected: "bool"

    is_armed: "bool"

    flight_mode: "FlightMode"

    battery_remaining: "float"


    def __init__(self, is_healthy: "bool", message: "str", has_position_data: "bool", has_velocity_data: "bool", has_attitude_data: "bool", has_optical_flow_data: "bool", is_connected: "bool", is_armed: "bool", flight_mode: "FlightMode", battery_remaining: "float"):
        """Initialize HealthResponse.
        

        Parameters
        ----------

        is_healthy : bool
            Is Healthy value

        message : str
            Message value

        has_position_data : bool
            Has Position Data value

        has_velocity_data : bool
            Has Velocity Data value

        has_attitude_data : bool
            Has Attitude Data value

        has_optical_flow_data : bool
            Has Optical Flow Data value

        is_connected : bool
            Is Connected value

        is_armed : bool
            Is Armed value

        flight_mode : FlightMode
            Flight Mode value

        battery_remaining : float
            Battery Remaining value


        """

        self.is_healthy = is_healthy

        self.message = message

        self.has_position_data = has_position_data

        self.has_velocity_data = has_velocity_data

        self.has_attitude_data = has_attitude_data

        self.has_optical_flow_data = has_optical_flow_data

        self.is_connected = is_connected

        self.is_armed = is_armed

        self.flight_mode = flight_mode

        self.battery_remaining = battery_remaining


    @classmethod
    def from_proto(cls, proto_msg: ProtoHealthResponse) -> "HealthResponse":
        """Create HealthResponse from protobuf message."""
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        return cls(

            
            is_healthy=proto_msg.is_healthy,
            

            
            message=proto_msg.message,
            

            
            has_position_data=proto_msg.has_position_data,
            

            
            has_velocity_data=proto_msg.has_velocity_data,
            

            
            has_attitude_data=proto_msg.has_attitude_data,
            

            
            has_optical_flow_data=proto_msg.has_optical_flow_data,
            

            
            is_connected=proto_msg.is_connected,
            

            
            is_armed=proto_msg.is_armed,
            

            
            flight_mode=proto_msg.flight_mode,
            

            
            battery_remaining=proto_msg.battery_remaining,
            

        )

    def to_proto(self) -> ProtoHealthResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoHealthResponse()

        
        
        proto_msg.is_healthy = self.is_healthy
        
        

        
        
        proto_msg.message = self.message
        
        

        
        
        proto_msg.has_position_data = self.has_position_data
        
        

        
        
        proto_msg.has_velocity_data = self.has_velocity_data
        
        

        
        
        proto_msg.has_attitude_data = self.has_attitude_data
        
        

        
        
        proto_msg.has_optical_flow_data = self.has_optical_flow_data
        
        

        
        
        proto_msg.is_connected = self.is_connected
        
        

        
        
        proto_msg.is_armed = self.is_armed
        
        

        
        
        proto_msg.flight_mode = self.flight_mode
        
        

        
        
        proto_msg.battery_remaining = self.battery_remaining
        
        

        return proto_msg