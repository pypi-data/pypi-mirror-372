"""
LandRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import LandRequest as ProtoLandRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class LandRequest:
    """LandRequest message type.
    

    Parameters
    ----------

    timeout : float
        timeout in seconds


    """

    timeout: "float"


    def __init__(self, timeout: "float"):
        """Initialize LandRequest.
        

        Parameters
        ----------

        timeout : float
            timeout in seconds


        """

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoLandRequest) -> "LandRequest":
        """Create LandRequest from protobuf message."""
        
        
        
        return cls(

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoLandRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoLandRequest()

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg