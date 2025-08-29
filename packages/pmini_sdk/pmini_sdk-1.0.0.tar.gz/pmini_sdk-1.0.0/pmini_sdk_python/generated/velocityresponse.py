"""
VelocityResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import VelocityResponse as ProtoVelocityResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class VelocityResponse:
    """VelocityResponse message type.
    

    Parameters
    ----------

    velocity : Velocity
        Velocity value


    """

    velocity: "Velocity"


    def __init__(self, velocity: "Velocity"):
        """Initialize VelocityResponse.
        

        Parameters
        ----------

        velocity : Velocity
            Velocity value


        """

        self.velocity = velocity


    @classmethod
    def from_proto(cls, proto_msg: ProtoVelocityResponse) -> "VelocityResponse":
        """Create VelocityResponse from protobuf message."""
        
        
        from .velocity import Velocity
        
        
        return cls(

            
            velocity=Velocity.from_proto(proto_msg.velocity),
            

        )

    def to_proto(self) -> ProtoVelocityResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoVelocityResponse()

        
        
        proto_msg.velocity.CopyFrom(self.velocity.to_proto())
        
        

        return proto_msg