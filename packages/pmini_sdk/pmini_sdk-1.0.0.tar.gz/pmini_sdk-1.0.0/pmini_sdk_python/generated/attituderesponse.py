"""
AttitudeResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import AttitudeResponse as ProtoAttitudeResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class AttitudeResponse:
    """AttitudeResponse message type.
    

    Parameters
    ----------

    attitude : Attitude
        Attitude value


    """

    attitude: "Attitude"


    def __init__(self, attitude: "Attitude"):
        """Initialize AttitudeResponse.
        

        Parameters
        ----------

        attitude : Attitude
            Attitude value


        """

        self.attitude = attitude


    @classmethod
    def from_proto(cls, proto_msg: ProtoAttitudeResponse) -> "AttitudeResponse":
        """Create AttitudeResponse from protobuf message."""
        
        
        from .attitude import Attitude
        
        
        return cls(

            
            attitude=Attitude.from_proto(proto_msg.attitude),
            

        )

    def to_proto(self) -> ProtoAttitudeResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoAttitudeResponse()

        
        
        proto_msg.attitude.CopyFrom(self.attitude.to_proto())
        
        

        return proto_msg