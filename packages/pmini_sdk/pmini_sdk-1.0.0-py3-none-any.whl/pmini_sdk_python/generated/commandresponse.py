"""
CommandResponse message class.

This file is auto-generated from drone.proto. Do not modify manually.
"""

from typing import Optional, Union, TYPE_CHECKING
from dataclasses import dataclass
from .drone_pb2 import CommandResponse as ProtoCommandResponse

if TYPE_CHECKING:
    from typing import Any


@dataclass
class CommandResponse:
    """CommandResponse message type.
    

    Parameters
    ----------

    error_code : DroneErrorCode
        Error code

    message : str
        Human-readable message

    success : bool
        true if error_code == SUCCESS


    """

    error_code: "DroneErrorCode"

    message: "str"

    success: "bool"


    def __init__(self, error_code: "DroneErrorCode", message: "str", success: "bool"):
        """Initialize CommandResponse.
        

        Parameters
        ----------

        error_code : DroneErrorCode
            Error code

        message : str
            Human-readable message

        success : bool
            true if error_code == SUCCESS


        """

        self.error_code = error_code

        self.message = message

        self.success = success


    @classmethod
    def from_proto(cls, proto_msg: ProtoCommandResponse) -> "CommandResponse":
        """Create CommandResponse from protobuf message."""
        
        
        
        
        
        
        
        return cls(

            
            error_code=proto_msg.error_code,
            

            
            message=proto_msg.message,
            

            
            success=proto_msg.success,
            

        )

    def to_proto(self) -> ProtoCommandResponse:
        """Convert to protobuf message."""
        proto_msg = ProtoCommandResponse()

        
        
        proto_msg.error_code = self.error_code
        
        

        
        
        proto_msg.message = self.message
        
        

        
        
        proto_msg.success = self.success
        
        

        return proto_msg