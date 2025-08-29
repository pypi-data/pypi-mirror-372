"""
Velocity message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import Velocity as ProtoVelocity

if TYPE_CHECKING:
    from typing import Any


@dataclass
class Velocity:
    """Velocity message type.
    

    Parameters
    ----------

    v_x : float
        North velocity in m/s

    v_y : float
        East velocity in m/s

    v_z : float
        Down velocity in m/s


    """

    v_x: "float"

    v_y: "float"

    v_z: "float"


    def __init__(self, v_x: "float", v_y: "float", v_z: "float"):
        """Initialize Velocity.
        

        Parameters
        ----------

        v_x : float
            North velocity in m/s

        v_y : float
            East velocity in m/s

        v_z : float
            Down velocity in m/s


        """

        self.v_x = v_x

        self.v_y = v_y

        self.v_z = v_z


    @classmethod
    def from_proto(cls, proto_msg: ProtoVelocity) -> "Velocity":
        """Create Velocity from protobuf message."""
        
        
        
        
        
        
        
        return cls(

            
            v_x=proto_msg.v_x,
            

            
            v_y=proto_msg.v_y,
            

            
            v_z=proto_msg.v_z,
            

        )

    def to_proto(self) -> ProtoVelocity:
        """Convert to protobuf message."""
        proto_msg = ProtoVelocity()

        
        
        proto_msg.v_x = self.v_x
        
        

        
        
        proto_msg.v_y = self.v_y
        
        

        
        
        proto_msg.v_z = self.v_z
        
        

        return proto_msg