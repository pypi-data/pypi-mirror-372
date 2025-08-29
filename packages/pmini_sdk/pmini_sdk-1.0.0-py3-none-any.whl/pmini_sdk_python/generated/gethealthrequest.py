"""
GetHealthRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import GetHealthRequest as ProtoGetHealthRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class GetHealthRequest:
    """GetHealthRequest message type.
    

    """


    def __init__(self):
        """Initialize GetHealthRequest.
        

        """


    @classmethod
    def from_proto(cls, proto_msg: ProtoGetHealthRequest) -> "GetHealthRequest":
        """Create GetHealthRequest from protobuf message."""
        
        return cls(

        )

    def to_proto(self) -> ProtoGetHealthRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoGetHealthRequest()

        return proto_msg