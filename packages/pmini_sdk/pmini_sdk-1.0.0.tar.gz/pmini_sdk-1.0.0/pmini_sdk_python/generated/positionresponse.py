"""
PositionResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import PositionResponse as ProtoPositionResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class PositionResponse:
    """PositionResponse message type.
    

    Parameters
    ----------

    position : Position
        Position value


    """

    position: "Position"


    def __init__(self, position: "Position"):
        """Initialize PositionResponse.
        

        Parameters
        ----------

        position : Position
            Position value


        """

        self.position = position


    @classmethod
    def from_proto(cls, proto_msg: ProtoPositionResponse) -> "PositionResponse":
        """Create PositionResponse from protobuf message."""
        
        
        from .position import Position
        
        
        return cls(

            
            position=Position.from_proto(proto_msg.position),
            

        )

    def to_proto(self) -> ProtoPositionResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoPositionResponse()

        
        
        proto_msg.position.CopyFrom(self.position.to_proto())
        
        

        return proto_msg