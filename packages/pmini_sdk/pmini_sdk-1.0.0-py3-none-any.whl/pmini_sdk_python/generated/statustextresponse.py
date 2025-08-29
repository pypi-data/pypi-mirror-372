"""
StatusTextResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import StatusTextResponse as ProtoStatusTextResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class StatusTextResponse:
    """StatusTextResponse message type.
    

    Parameters
    ----------

    status_text : str
        Status Text value


    """

    status_text: "str"


    def __init__(self, status_text: "str"):
        """Initialize StatusTextResponse.
        

        Parameters
        ----------

        status_text : str
            Status Text value


        """

        self.status_text = status_text


    @classmethod
    def from_proto(cls, proto_msg: ProtoStatusTextResponse) -> "StatusTextResponse":
        """Create StatusTextResponse from protobuf message."""
        
        
        
        return cls(

            
            status_text=proto_msg.status_text,
            

        )

    def to_proto(self) -> ProtoStatusTextResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoStatusTextResponse()

        
        
        proto_msg.status_text = self.status_text
        
        

        return proto_msg