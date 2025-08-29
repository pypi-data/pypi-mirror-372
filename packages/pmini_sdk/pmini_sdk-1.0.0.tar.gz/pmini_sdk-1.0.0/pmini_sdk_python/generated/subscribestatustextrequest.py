"""
SubscribeStatusTextRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import SubscribeStatusTextRequest as ProtoSubscribeStatusTextRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class SubscribeStatusTextRequest:
    """SubscribeStatusTextRequest message type.
    

    """


    def __init__(self):
        """Initialize SubscribeStatusTextRequest.
        

        """


    @classmethod
    def from_proto(cls, proto_msg: ProtoSubscribeStatusTextRequest) -> "SubscribeStatusTextRequest":
        """Create SubscribeStatusTextRequest from protobuf message."""
        
        return cls(

        )

    def to_proto(self) -> ProtoSubscribeStatusTextRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoSubscribeStatusTextRequest()

        return proto_msg