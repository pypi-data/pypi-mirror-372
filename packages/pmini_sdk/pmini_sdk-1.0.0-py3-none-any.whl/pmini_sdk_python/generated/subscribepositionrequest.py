"""
SubscribePositionRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import SubscribePositionRequest as ProtoSubscribePositionRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class SubscribePositionRequest:
    """SubscribePositionRequest message type.
    

    Parameters
    ----------

    rate_hz : float
        requested update rate in Hz


    """

    rate_hz: "float"


    def __init__(self, rate_hz: "float"):
        """Initialize SubscribePositionRequest.
        

        Parameters
        ----------

        rate_hz : float
            requested update rate in Hz


        """

        self.rate_hz = rate_hz


    @classmethod
    def from_proto(cls, proto_msg: ProtoSubscribePositionRequest) -> "SubscribePositionRequest":
        """Create SubscribePositionRequest from protobuf message."""
        
        
        
        return cls(

            
            rate_hz=proto_msg.rate_hz,
            

        )

    def to_proto(self) -> ProtoSubscribePositionRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoSubscribePositionRequest()

        
        
        proto_msg.rate_hz = self.rate_hz
        
        

        return proto_msg