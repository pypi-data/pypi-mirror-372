"""
TakeoffRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import TakeoffRequest as ProtoTakeoffRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class TakeoffRequest:
    """TakeoffRequest message type.
    

    Parameters
    ----------

    altitude : float
        meters

    timeout : float
        timeout in seconds


    """

    altitude: "float"

    timeout: "float"


    def __init__(self, altitude: "float", timeout: "float"):
        """Initialize TakeoffRequest.
        

        Parameters
        ----------

        altitude : float
            meters

        timeout : float
            timeout in seconds


        """

        self.altitude = altitude

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoTakeoffRequest) -> "TakeoffRequest":
        """Create TakeoffRequest from protobuf message."""
        
        
        
        
        
        return cls(

            
            altitude=proto_msg.altitude,
            

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoTakeoffRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoTakeoffRequest()

        
        
        proto_msg.altitude = self.altitude
        
        

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg