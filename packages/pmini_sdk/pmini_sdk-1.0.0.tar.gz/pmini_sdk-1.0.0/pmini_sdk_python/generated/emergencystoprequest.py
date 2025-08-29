"""
EmergencyStopRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import EmergencyStopRequest as ProtoEmergencyStopRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class EmergencyStopRequest:
    """EmergencyStopRequest message type.
    

    Parameters
    ----------

    timeout : float
        timeout in seconds


    """

    timeout: "float"


    def __init__(self, timeout: "float"):
        """Initialize EmergencyStopRequest.
        

        Parameters
        ----------

        timeout : float
            timeout in seconds


        """

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoEmergencyStopRequest) -> "EmergencyStopRequest":
        """Create EmergencyStopRequest from protobuf message."""
        
        
        
        return cls(

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoEmergencyStopRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoEmergencyStopRequest()

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg