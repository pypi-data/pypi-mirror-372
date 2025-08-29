"""
DroneService service wrapper.

This file is auto-generated from drone.proto. Do not modify manually.
"""

import grpc
from typing import Iterator, Optional
from .drone_pb2_grpc import DroneServiceStub

from .takeoffrequest import TakeoffRequest

from .landrequest import LandRequest

from .armrequest import ArmRequest

from .disarmrequest import DisarmRequest

from .setmoderequest import SetModeRequest

from .gotorequest import GoToRequest

from .movevelocityrequest import MoveVelocityRequest

from .emergencystoprequest import EmergencyStopRequest

from .rebootrequest import RebootRequest

from .gethealthrequest import GetHealthRequest

from .healthresponse import HealthResponse

from .subscribepositionrequest import SubscribePositionRequest

from .positionresponse import PositionResponse

from .position import Position

from .subscribevelocityrequest import SubscribeVelocityRequest

from .velocityresponse import VelocityResponse

from .velocity import Velocity

from .attitude import Attitude

from .subscribestatustextrequest import SubscribeStatusTextRequest

from .statustextresponse import StatusTextResponse

from .commandresponse import CommandResponse

from .statusrequest import StatusRequest

from .statusresponse import StatusResponse

from .subscribeattituderequest import SubscribeAttitudeRequest

from .attituderesponse import AttitudeResponse



class DroneService:
    """DroneService wrapper for gRPC service."""
    
    def __init__(self, channel: grpc.Channel):
        """Initialize DroneService with gRPC channel."""
        self._stub = DroneServiceStub(channel)
    

    
    def takeoff(self, request: TakeoffRequest) -> CommandResponse:
        """Takeoff method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Takeoff(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def land(self, request: LandRequest) -> CommandResponse:
        """Land method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Land(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def arm(self, request: ArmRequest) -> CommandResponse:
        """Arm method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Arm(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def disarm(self, request: DisarmRequest) -> CommandResponse:
        """Disarm method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Disarm(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def setmode(self, request: SetModeRequest) -> CommandResponse:
        """SetMode method."""
        proto_request = request.to_proto()
        proto_response = self._stub.SetMode(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def goto(self, request: GoToRequest) -> CommandResponse:
        """GoTo method."""
        proto_request = request.to_proto()
        proto_response = self._stub.GoTo(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def movevelocity(self, request: MoveVelocityRequest) -> CommandResponse:
        """MoveVelocity method."""
        proto_request = request.to_proto()
        proto_response = self._stub.MoveVelocity(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def emergencystop(self, request: EmergencyStopRequest) -> CommandResponse:
        """EmergencyStop method."""
        proto_request = request.to_proto()
        proto_response = self._stub.EmergencyStop(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def reboot(self, request: RebootRequest) -> CommandResponse:
        """Reboot method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Reboot(proto_request)
        return CommandResponse.from_proto(proto_response)
    


    
    def gethealth(self, request: GetHealthRequest) -> HealthResponse:
        """GetHealth method."""
        proto_request = request.to_proto()
        proto_response = self._stub.GetHealth(proto_request)
        return HealthResponse.from_proto(proto_response)
    


    
    def subscribeposition(self, request: SubscribePositionRequest) -> Iterator[PositionResponse]:
        """SubscribePosition streaming method."""
        proto_request = request.to_proto()
        for proto_response in self._stub.SubscribePosition(proto_request):
            yield PositionResponse.from_proto(proto_response)
    


    
    def subscribestatustext(self, request: SubscribeStatusTextRequest) -> Iterator[StatusTextResponse]:
        """SubscribeStatusText streaming method."""
        proto_request = request.to_proto()
        for proto_response in self._stub.SubscribeStatusText(proto_request):
            yield StatusTextResponse.from_proto(proto_response)
    


    
    def subscribevelocity(self, request: SubscribeVelocityRequest) -> Iterator[VelocityResponse]:
        """SubscribeVelocity streaming method."""
        proto_request = request.to_proto()
        for proto_response in self._stub.SubscribeVelocity(proto_request):
            yield VelocityResponse.from_proto(proto_response)
    


    
    def subscribeattitude(self, request: SubscribeAttitudeRequest) -> Iterator[AttitudeResponse]:
        """SubscribeAttitude streaming method."""
        proto_request = request.to_proto()
        for proto_response in self._stub.SubscribeAttitude(proto_request):
            yield AttitudeResponse.from_proto(proto_response)
    


    
    def status(self, request: StatusRequest) -> StatusResponse:
        """Status method."""
        proto_request = request.to_proto()
        proto_response = self._stub.Status(proto_request)
        return StatusResponse.from_proto(proto_response)
    

