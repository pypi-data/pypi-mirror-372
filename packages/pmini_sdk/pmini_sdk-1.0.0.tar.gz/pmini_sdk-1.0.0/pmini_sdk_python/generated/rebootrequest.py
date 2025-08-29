"""
RebootRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import RebootRequest as ProtoRebootRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class RebootRequest:
    """RebootRequest message type.
    

    Parameters
    ----------

    timeout : float
        timeout in seconds


    """

    timeout: "float"


    def __init__(self, timeout: "float"):
        """Initialize RebootRequest.
        

        Parameters
        ----------

        timeout : float
            timeout in seconds


        """

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoRebootRequest) -> "RebootRequest":
        """Create RebootRequest from protobuf message."""
        
        
        
        return cls(

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoRebootRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoRebootRequest()

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg