"""
StatusRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import StatusRequest as ProtoStatusRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class StatusRequest:
    """StatusRequest message type.
    

    """


    def __init__(self):
        """Initialize StatusRequest.
        

        """


    @classmethod
    def from_proto(cls, proto_msg: ProtoStatusRequest) -> "StatusRequest":
        """Create StatusRequest from protobuf message."""
        
        return cls(

        )

    def to_proto(self) -> ProtoStatusRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoStatusRequest()

        return proto_msg