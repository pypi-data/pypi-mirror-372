"""
MoveVelocityRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import MoveVelocityRequest as ProtoMoveVelocityRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class MoveVelocityRequest:
    """MoveVelocityRequest message type.
    

    Parameters
    ----------

    v_x : float
        North velocity in m/s

    v_y : float
        East velocity in m/s

    v_z : float
        Down velocity in m/s

    yaw_rate_rad_s : float
        Yaw rate in rad/s

    frame : CoordinateFrame
        Coordinate frame

    timeout : float
        timeout in seconds


    """

    v_x: "float"

    v_y: "float"

    v_z: "float"

    yaw_rate_rad_s: "float"

    frame: "CoordinateFrame"

    timeout: "float"


    def __init__(self, v_x: "float", v_y: "float", v_z: "float", yaw_rate_rad_s: "float", frame: "CoordinateFrame", timeout: "float"):
        """Initialize MoveVelocityRequest.
        

        Parameters
        ----------

        v_x : float
            North velocity in m/s

        v_y : float
            East velocity in m/s

        v_z : float
            Down velocity in m/s

        yaw_rate_rad_s : float
            Yaw rate in rad/s

        frame : CoordinateFrame
            Coordinate frame

        timeout : float
            timeout in seconds


        """

        self.v_x = v_x

        self.v_y = v_y

        self.v_z = v_z

        self.yaw_rate_rad_s = yaw_rate_rad_s

        self.frame = frame

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoMoveVelocityRequest) -> "MoveVelocityRequest":
        """Create MoveVelocityRequest from protobuf message."""
        
        
        
        
        
        
        
        
        
        
        
        
        
        return cls(

            
            v_x=proto_msg.v_x,
            

            
            v_y=proto_msg.v_y,
            

            
            v_z=proto_msg.v_z,
            

            
            yaw_rate_rad_s=proto_msg.yaw_rate_rad_s,
            

            
            frame=proto_msg.frame,
            

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoMoveVelocityRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoMoveVelocityRequest()

        
        
        proto_msg.v_x = self.v_x
        
        

        
        
        proto_msg.v_y = self.v_y
        
        

        
        
        proto_msg.v_z = self.v_z
        
        

        
        
        proto_msg.yaw_rate_rad_s = self.yaw_rate_rad_s
        
        

        
        
        proto_msg.frame = self.frame
        
        

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg