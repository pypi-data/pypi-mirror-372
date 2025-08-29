"""
GoToRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import GoToRequest as ProtoGoToRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class GoToRequest:
    """GoToRequest message type.
    

    Parameters
    ----------

    x : float
        North position in meters (or latitude if global frame)

    y : float
        East position in meters (or longitude if global frame)

    z : float
        Down position in meters (or altitude if global frame)

    yaw_rad : float
        Yaw angle in radians

    frame : CoordinateFrame
        Coordinate frame

    timeout : float
        timeout in seconds


    """

    x: "float"

    y: "float"

    z: "float"

    yaw_rad: "float"

    frame: "CoordinateFrame"

    timeout: "float"


    def __init__(self, x: "float", y: "float", z: "float", yaw_rad: "float", frame: "CoordinateFrame", timeout: "float"):
        """Initialize GoToRequest.
        

        Parameters
        ----------

        x : float
            North position in meters (or latitude if global frame)

        y : float
            East position in meters (or longitude if global frame)

        z : float
            Down position in meters (or altitude if global frame)

        yaw_rad : float
            Yaw angle in radians

        frame : CoordinateFrame
            Coordinate frame

        timeout : float
            timeout in seconds


        """

        self.x = x

        self.y = y

        self.z = z

        self.yaw_rad = yaw_rad

        self.frame = frame

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoGoToRequest) -> "GoToRequest":
        """Create GoToRequest from protobuf message."""
        
        
        
        
        
        
        
        
        
        
        
        
        
        return cls(

            
            x=proto_msg.x,
            

            
            y=proto_msg.y,
            

            
            z=proto_msg.z,
            

            
            yaw_rad=proto_msg.yaw_rad,
            

            
            frame=proto_msg.frame,
            

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoGoToRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoGoToRequest()

        
        
        proto_msg.x = self.x
        
        

        
        
        proto_msg.y = self.y
        
        

        
        
        proto_msg.z = self.z
        
        

        
        
        proto_msg.yaw_rad = self.yaw_rad
        
        

        
        
        proto_msg.frame = self.frame
        
        

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg