"""
ArmRequest message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import ArmRequest as ProtoArmRequest

if TYPE_CHECKING:
    from typing import Any


@dataclass
class ArmRequest:
    """ArmRequest message type.
    

    Parameters
    ----------

    timeout : float
        timeout in seconds


    """

    timeout: "float"


    def __init__(self, timeout: "float"):
        """Initialize ArmRequest.
        

        Parameters
        ----------

        timeout : float
            timeout in seconds


        """

        self.timeout = timeout


    @classmethod
    def from_proto(cls, proto_msg: ProtoArmRequest) -> "ArmRequest":
        """Create ArmRequest from protobuf message."""
        
        
        
        return cls(

            
            timeout=proto_msg.timeout,
            

        )

    def to_proto(self) -> ProtoArmRequest:
        """Convert to protobuf message."""
        proto_msg = ProtoArmRequest()

        
        
        proto_msg.timeout = self.timeout
        
        

        return proto_msg