"""
Attitude message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import Attitude as ProtoAttitude

if TYPE_CHECKING:
    from typing import Any


@dataclass
class Attitude:
    """Attitude message type.
    

    Parameters
    ----------

    roll_rad : float
        Roll angle in radians

    pitch_rad : float
        Pitch angle in radians

    yaw_rad : float
        Yaw angle in radians


    """

    roll_rad: "float"

    pitch_rad: "float"

    yaw_rad: "float"


    def __init__(self, roll_rad: "float", pitch_rad: "float", yaw_rad: "float"):
        """Initialize Attitude.
        

        Parameters
        ----------

        roll_rad : float
            Roll angle in radians

        pitch_rad : float
            Pitch angle in radians

        yaw_rad : float
            Yaw angle in radians


        """

        self.roll_rad = roll_rad

        self.pitch_rad = pitch_rad

        self.yaw_rad = yaw_rad


    @classmethod
    def from_proto(cls, proto_msg: ProtoAttitude) -> "Attitude":
        """Create Attitude from protobuf message."""
        
        
        
        
        
        
        
        return cls(

            
            roll_rad=proto_msg.roll_rad,
            

            
            pitch_rad=proto_msg.pitch_rad,
            

            
            yaw_rad=proto_msg.yaw_rad,
            

        )

    def to_proto(self) -> ProtoAttitude:
        """Convert to protobuf message."""
        proto_msg = ProtoAttitude()

        
        
        proto_msg.roll_rad = self.roll_rad
        
        

        
        
        proto_msg.pitch_rad = self.pitch_rad
        
        

        
        
        proto_msg.yaw_rad = self.yaw_rad
        
        

        return proto_msg