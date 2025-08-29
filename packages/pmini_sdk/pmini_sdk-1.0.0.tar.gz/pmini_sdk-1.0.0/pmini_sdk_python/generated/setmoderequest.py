"""
SetModeRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import SetModeRequest as ProtoSetModeRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class SetModeRequest:
    """SetModeRequest message type.
    

    Parameters
    ----------

    mode : FlightMode
        Mode value

    timeout : float
        timeout in seconds


    """

    mode: "FlightMode"

    timeout: "float"


    def __init__(self, mode: "FlightMode", timeout: "float"):
        """Initialize SetModeRequest.
        

        Parameters
        ----------

        mode : FlightMode
            Mode value

        timeout : float
            timeout in seconds


        """

        self.mode = mode

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoSetModeRequest) -> "SetModeRequest":
        """Create SetModeRequest from protobuf message."""
        
        
        
        
        
        return cls(

            
            mode=proto_msg.mode,
            

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoSetModeRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoSetModeRequest()

        
        
        proto_msg.mode = self.mode
        
        

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg