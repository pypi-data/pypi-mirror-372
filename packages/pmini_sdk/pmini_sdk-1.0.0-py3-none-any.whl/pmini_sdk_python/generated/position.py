"""
Position message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import Position as ProtoPosition

if TYPE_CHECKING:
    from typing import Any


@dataclass
class Position:
    """Position message type.
    

    Parameters
    ----------

    x : float
        North position in meters

    y : float
        East position in meters

    z : float
        Down position in meters (negative = altitude)


    """

    x: "float"

    y: "float"

    z: "float"


    def __init__(self, x: "float", y: "float", z: "float"):
        """Initialize Position.
        

        Parameters
        ----------

        x : float
            North position in meters

        y : float
            East position in meters

        z : float
            Down position in meters (negative = altitude)


        """

        self.x = x

        self.y = y

        self.z = z


    @classmethod
    def from_proto(cls, proto_msg: ProtoPosition) -> "Position":
        """Create Position from protobuf message."""
        
        
        
        
        
        
        
        return cls(

            
            x=proto_msg.x,
            

            
            y=proto_msg.y,
            

            
            z=proto_msg.z,
            

        )

    def to_proto(self) -> ProtoPosition:
        """Convert to protobuf message."""
        proto_msg = ProtoPosition()

        
        
        proto_msg.x = self.x
        
        

        
        
        proto_msg.y = self.y
        
        

        
        
        proto_msg.z = self.z
        
        

        return proto_msg