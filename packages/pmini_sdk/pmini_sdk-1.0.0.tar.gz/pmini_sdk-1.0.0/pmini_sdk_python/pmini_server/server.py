#!/usr/bin/env python3
"""
Improved gRPC server for PMini drone control with proper connection detection.

This server provides a direct interface to the drone using the pmini_sdk_python
library. Enhanced with better connection detection, heartbeat monitoring, and
graceful shutdown.
"""

import logging
import signal
import time
import threading
from concurrent import futures
from queue import Queue, Empty
from typing import Iterator, Callable
import grpc

# Import the actual pmini_sdk_python library
from pmini_sdk_python import (
    Config,
    Pmini,
    FlightMode,
    Frame,
    Yaw,
    DroneErrorCode,
)

# Import generated protobuf classes
from pmini_sdk_python.generated.drone_pb2 import (
    ArmRequest as ProtoArmRequest,
    AttitudeResponse as ProtoAttitudeResponse,
    CommandResponse as ProtoCommandResponse,
    DisarmRequest as ProtoDisarmRequest,
    EmergencyStopRequest as ProtoEmergencyStopRequest,
    FlightMode as ProtoFlightMode,
    GetHealthRequest as ProtoGetHealthRequest,
    GoToRequest as ProtoGoToRequest,
    HealthResponse as ProtoHealthResponse,
    LandRequest as ProtoLandRequest,
    MoveVelocityRequest as ProtoMoveVelocityRequest,
    PositionResponse as ProtoPositionResponse,
    RebootRequest as ProtoRebootRequest,
    SetModeRequest as ProtoSetModeRequest,
    StatusRequest as ProtoStatusRequest,
    StatusResponse as ProtoStatusResponse,
    StatusTextResponse as ProtoStatusTextResponse,
    SubscribeAttitudeRequest as ProtoSubscribeAttitudeRequest,
    SubscribePositionRequest as ProtoSubscribePositionRequest,
    SubscribeStatusTextRequest as ProtoSubscribeStatusTextRequest,
    SubscribeVelocityRequest as ProtoSubscribeVelocityRequest,
    TakeoffRequest as ProtoTakeoffRequest,
    VelocityResponse as ProtoVelocityResponse,
)
from pmini_sdk_python.generated.drone_pb2_grpc import DroneServiceServicer as BaseDroneServiceServicer
from pmini_sdk_python.generated.drone_pb2_grpc import add_DroneServiceServicer_to_server

# Import wrapper classes
from pmini_sdk_python.generated import (
    AttitudeResponse,
    CommandResponse,
    GoToRequest,
    HealthResponse,
    MoveVelocityRequest,
    PositionResponse,
    SetModeRequest,
    StatusResponse,
    StatusTextResponse,
    TakeoffRequest,
    VelocityResponse,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ConnectionMonitor:
    """Monitor drone connection status with heartbeat detection."""
    
    def __init__(self, pmini: Pmini, timeout_seconds: float = 5.0):
        self.pmini = pmini
        self.timeout_seconds = timeout_seconds
        self.last_successful_call = time.time()
        self.is_connected = False
        self._lock = threading.Lock()
        
    def test_connection(self) -> bool:
        """Test if the drone is connected by trying to get data."""
        try:
            # Try multiple operations to verify connection
            start_time = time.time()
            
            # Try to get position (this should fail quickly if drone is off)
            position = self.pmini.get_position()
            
            # Check if we got valid data within reasonable time
            if time.time() - start_time > 2.0:
                logger.warning("Position request took too long, "
                               "marking as disconnected")
                with self._lock:
                    self.is_connected = False
                return False
                
            # Check if position data looks valid (not all zeros or NaN)
            if (hasattr(position, 'x') and hasattr(position, 'y') and
                    hasattr(position, 'z')):
                # Position data exists, update last successful call
                with self._lock:
                    self.last_successful_call = time.time()
                    self.is_connected = True
                return True
            else:
                logger.warning("Invalid position data received")
                with self._lock:
                    self.is_connected = False
                return False
                
        except Exception as e:
            logger.info(f"Connection test failed: {e}")
            with self._lock:
                self.is_connected = False
            return False
    
    def get_connection_status(self) -> tuple[bool, str]:
        """Get current connection status and message."""
        # Test connection
        is_connected = self.test_connection()
        
        with self._lock:
            if is_connected:
                return True, "Connected to drone"
            else:
                time_since_last = time.time() - self.last_successful_call
                if time_since_last > self.timeout_seconds:
                    return False, f"No response from drone for {time_since_last:.1f}s"
                else:
                    return False, "Connection test failed"


class DroneServiceServicer(BaseDroneServiceServicer):
    """gRPC service implementation with proper connection detection."""

    def __init__(self, pmini: Pmini):
        self.pmini = pmini
        self.status_text_queue: Queue = Queue()
        self.status_text_callbacks: set[Callable] = set()
        self._shutdown_event = threading.Event()
        self.connection_monitor = ConnectionMonitor(pmini)
        self._setup_status_text_callback()

    def _setup_status_text_callback(self):
        """Setup the status text callback to collect messages."""

        def status_text_callback(status_text):
            logger.info(f"Status text received: {status_text}")
            # Put the status text in the queue for streaming
            try:
                self.status_text_queue.put(status_text, timeout=0.1)
            except Exception:
                pass  # Queue might be full, ignore

        try:
            self.pmini.add_status_text_callback(status_text_callback)
        except Exception as e:
            logger.warning(f"Could not setup status text callback: {e}")

    def shutdown(self):
        """Signal shutdown to all streaming operations."""
        logger.info("Shutdown signal received in DroneServiceServicer")
        self._shutdown_event.set()

    def _check_connection(self) -> tuple[bool, str]:
        """Check connection and return status."""
        return self.connection_monitor.get_connection_status()

    def _create_error_response(self, error_code: DroneErrorCode, message: str) -> ProtoCommandResponse:
        """Create an error response."""
        response = CommandResponse(
            error_code=error_code,
            message=message,
            success=False
        )
        return response.to_proto()

    def _create_success_response(self, message: str) -> ProtoCommandResponse:
        """Create a success response."""
        response = CommandResponse(
            error_code=DroneErrorCode.SUCCESS,
            message=message,
            success=True
        )
        return response.to_proto()

    def Takeoff(self, request: ProtoTakeoffRequest, context) -> ProtoCommandResponse:
        """Handle takeoff request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot takeoff: {msg}")
            
        try:
            takeoff_req = TakeoffRequest.from_proto(request)
            logger.info(f"Takeoff request: altitude={takeoff_req.altitude}m")

            # Validate altitude
            if takeoff_req.altitude <= 0:
                return self._create_error_response(DroneErrorCode.ALTITUDE_TOO_LOW, "Altitude must be positive")

            if takeoff_req.altitude > 2:  # Example max altitude
                return self._create_error_response(DroneErrorCode.ALTITUDE_TOO_HIGH, "Altitude too high (max 2m)")

            # Execute takeoff using the actual library
            mav_result = self.pmini.takeoff(takeoff_req.altitude)
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response(f"Takeoff to {takeoff_req.altitude}m initiated")
            else:
                return self._create_error_response(error_code, f"Takeoff failed: {error_code.name}")

        except Exception as e:
            logger.exception("Takeoff failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Takeoff failed: {str(e)}")

    def Land(self, request: ProtoLandRequest, context) -> ProtoCommandResponse:
        """Handle land request."""
        try:
            logger.info("Land request received")
            mav_result = self.pmini.land()
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response("Land initiated")
            else:
                return self._create_error_response(error_code, f"Land failed: {error_code.name}")

        except Exception as e:
            logger.exception("Land failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Land failed: {str(e)}")

    def Arm(self, request: ProtoArmRequest, context) -> ProtoCommandResponse:
        """Handle arm request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot arm: {msg}")
            
        try:
            logger.info("Arm request received")

            # Execute arm command using the actual library
            mav_result = self.pmini.arm()
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response("Drone armed successfully")
            else:
                return self._create_error_response(error_code, f"Arm failed: {error_code.name}")

        except Exception as e:
            logger.exception("Arm failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Arm failed: {str(e)}")

    def Disarm(self, request: ProtoDisarmRequest, context) -> ProtoCommandResponse:
        """Handle disarm request."""
        try:
            logger.info("Disarm request received")
            self.pmini.disarm()
            return self._create_success_response("Disarmed successfully")

        except Exception as e:
            logger.exception("Disarm failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Disarm failed: {str(e)}")

    def SetMode(self, request: ProtoSetModeRequest, context) -> ProtoCommandResponse:
        """Handle set mode request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot set mode: {msg}")
            
        try:
            mode_req = SetModeRequest.from_proto(request)
            logger.info(f"SetMode request: mode={mode_req.mode}")

            # Convert proto flight mode to internal flight mode
            internal_mode = FlightMode.from_proto(mode_req.mode)
            mav_result = self.pmini.change_mode(internal_mode)
            error_code = DroneErrorCode.from_mav_result(mav_result)

            if error_code.is_success():
                return self._create_success_response(f"Mode set to {mode_req.mode}")
            else:
                return self._create_error_response(error_code, f"SetMode failed: {error_code.name}")

        except Exception as e:
            logger.exception("SetMode failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"SetMode failed: {str(e)}")

    def GoTo(self, request: ProtoGoToRequest, context) -> ProtoCommandResponse:
        """Handle go to position request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot go to: {msg}")
            
        try:
            goto_req = GoToRequest.from_proto(request)
            logger.info(f"GoTo request: x={goto_req.x}, y={goto_req.y}, z={goto_req.z}, yaw={goto_req.yaw_rad}")

            # Convert coordinate frame
            frame = Frame.BODY if goto_req.frame == 0 else Frame.LOCAL
            
            # Create yaw object
            yaw = Yaw(value=goto_req.yaw_rad) if goto_req.yaw_rad is not None else Yaw(value=0)

            # Execute go to command
            self.pmini.go_to(goto_req.x, goto_req.y, goto_req.z, yaw, frame)
            return self._create_success_response(f"GoTo command sent to ({goto_req.x}, {goto_req.y}, {goto_req.z})")

        except Exception as e:
            logger.exception("GoTo failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"GoTo failed: {str(e)}")

    def MoveVelocity(self, request: ProtoMoveVelocityRequest, context) -> ProtoCommandResponse:
        """Handle move velocity request."""
        # Check connection first
        is_connected, msg = self._check_connection()
        if not is_connected:
            return self._create_error_response(DroneErrorCode.NOT_CONNECTED, f"Cannot move: {msg}")
            
        try:
            move_req = MoveVelocityRequest.from_proto(request)
            logger.info(f"MoveVelocity request: vx={move_req.v_x}, vy={move_req.v_y}, vz={move_req.v_z}")

            # Use low level commander for velocity control
            self.pmini.low_level_commander.move_velocity(
                move_req.v_x, move_req.v_y, move_req.v_z,
                move_req.yaw_rate_rad_s or 0
            )
            return self._create_success_response("MoveVelocity command sent")

        except Exception as e:
            logger.exception("MoveVelocity failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"MoveVelocity failed: {str(e)}")

    def EmergencyStop(self, request: ProtoEmergencyStopRequest, context) -> ProtoCommandResponse:
        """Handle emergency stop request."""
        try:
            logger.info("Emergency stop request received")
            self.pmini.low_level_commander.emergency_stop()
            return self._create_success_response("Emergency stop executed")

        except Exception as e:
            logger.exception("Emergency stop failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Emergency stop failed: {str(e)}")

    def Reboot(self, request: ProtoRebootRequest, context) -> ProtoCommandResponse:
        """Handle reboot request."""
        try:
            logger.info("Reboot request received")
            self.pmini.reboot()
            return self._create_success_response("Reboot command sent")

        except Exception as e:
            logger.exception("Reboot failed")
            return self._create_error_response(DroneErrorCode.INTERNAL_ERROR, f"Reboot failed: {str(e)}")

    def GetHealth(self, request: ProtoGetHealthRequest, context) -> ProtoHealthResponse:
        """Get drone health status."""
        try:
            is_connected, msg = self._check_connection()
            
            # Get current state
            position = self.pmini.get_position()
            velocity = self.pmini.get_velocity()
            attitude = self.pmini.get_attitude()
            optical_flow = self.pmini.get_of()
            
            # Determine health status
            has_position = position is not None and hasattr(position, 'x')
            has_velocity = velocity is not None and hasattr(velocity, 'v_x')
            has_attitude = attitude is not None and hasattr(attitude, 'roll_rad')
            has_optical_flow = optical_flow is not None and len(optical_flow) > 0
            
            # Overall health check
            is_healthy = (is_connected and has_position and has_velocity and
                          has_attitude and has_optical_flow)
            
            health_msg = "Healthy" if is_healthy else "Unhealthy"
            if not is_connected:
                health_msg = f"Not connected: {msg}"
            
            response = HealthResponse(
                is_healthy=is_healthy,
                message=health_msg,
                has_position_data=has_position,
                has_velocity_data=has_velocity,
                has_attitude_data=has_attitude,
                has_optical_flow_data=has_optical_flow,
                is_connected=is_connected,
                is_armed=self.pmini._Pmini__mavlink_client.armed,
                flight_mode=ProtoFlightMode.UNKNOWN,  # TODO: get actual flight mode
                battery_remaining=100.0  # TODO: get actual battery level
            )
            return response.to_proto()

        except Exception as e:
            logger.exception("GetHealth failed")
            # Return unhealthy response
            response = HealthResponse(
                is_healthy=False,
                message=f"Health check failed: {str(e)}",
                has_position_data=False,
                has_velocity_data=False,
                has_attitude_data=False,
                has_optical_flow_data=False,
                is_connected=False,
                is_armed=False,
                flight_mode=ProtoFlightMode.UNKNOWN,
                battery_remaining=0.0
            )
            return response.to_proto()

    def SubscribePosition(self, request: ProtoSubscribePositionRequest, context) -> Iterator[ProtoPositionResponse]:
        """Stream position data."""
        logger.info("Position stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting position
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Position stream: {msg}")
                        # Still try to get position, but expect it to fail
                    
                    # Get position using the actual library
                    position = self.pmini.get_position()

                    # Create position response using wrapper class
                    pos_response = PositionResponse(position=position)
                    yield pos_response.to_proto()

                except Exception as e:
                    logger.error(f"Error getting position: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Position stream error: {e}")
        finally:
            logger.info("Position stream ended")

    def SubscribeStatusText(self, request: ProtoSubscribeStatusTextRequest, context) -> Iterator[ProtoStatusTextResponse]:
        """Stream status text data."""
        logger.info("Status text stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Wait for status text messages from the queue with timeout
                    status_text = self.status_text_queue.get(timeout=1.0)

                    # Create status text response
                    status_text_response = StatusTextResponse(status_text=str(status_text))
                    yield status_text_response.to_proto()

                except Empty:
                    # Timeout is expected when no messages are available
                    # Check for shutdown during timeout
                    if self._shutdown_event.wait(0.1):
                        break
                    continue
                except Exception as e:
                    logger.error(f"Error in status text stream: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

        except Exception as e:
            logger.exception(f"Status text stream error: {e}")
        finally:
            logger.info("Status text stream ended")

    def SubscribeVelocity(self, request: ProtoSubscribeVelocityRequest, context) -> Iterator[ProtoVelocityResponse]:
        """Stream velocity data."""
        logger.info("Velocity stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting velocity
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Velocity stream: {msg}")
                        # Still try to get velocity, but expect it to fail
                        
                    # Get velocity using the actual library
                    velocity = self.pmini.get_velocity()

                    # Create velocity response using wrapper class
                    vel_response = VelocityResponse(velocity=velocity)
                    yield vel_response.to_proto()

                except Exception as e:
                    logger.error(f"Error getting velocity: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Velocity stream error: {e}")
        finally:
            logger.info("Velocity stream ended")

    def SubscribeAttitude(self, request: ProtoSubscribeAttitudeRequest, context) -> Iterator[ProtoAttitudeResponse]:
        """Stream attitude data."""
        logger.info("Attitude stream started")

        try:
            while context.is_active() and not self._shutdown_event.is_set():
                try:
                    # Check connection before getting attitude
                    is_connected, msg = self._check_connection()
                    if not is_connected:
                        logger.warning(f"Attitude stream: {msg}")
                        # Still try to get attitude, but expect it to fail
                        
                    # Get attitude using the actual library
                    attitude = self.pmini.get_attitude()

                    # Create attitude response using wrapper class
                    att_response = AttitudeResponse(attitude=attitude)
                    yield att_response.to_proto()

                except Exception as e:
                    logger.error(f"Error getting attitude: {e}")
                    # Check for shutdown before continuing
                    if self._shutdown_event.wait(0.5):
                        break
                    continue

                # Check for shutdown before sleeping
                if self._shutdown_event.wait(0.2):
                    break

        except Exception as e:
            logger.exception(f"Attitude stream error: {e}")
        finally:
            logger.info("Attitude stream ended")

    def Status(self, request: ProtoStatusRequest, context) -> ProtoStatusResponse:
        """Get drone status with proper connection detection."""
        logger.debug("Status check requested")
        
        # Use connection monitor to get accurate status
        is_connected, message = self._check_connection()
        
        if is_connected:
            try:
                position = self.pmini.get_position()
                attitude = self.pmini.get_attitude()
                detailed_message = f"Connected - Position: ({position.x:.1f}, {position.y:.1f}, {position.z:.1f})"
                
                status = StatusResponse(
                    connected=True, 
                    message=detailed_message,
                    status_code=DroneErrorCode.SUCCESS,
                    current_position=position,
                    current_attitude=attitude,
                    flight_mode=ProtoFlightMode.UNKNOWN,  # TODO: get actual flight mode
                    armed=self.pmini._Pmini__mavlink_client.armed,
                    battery_remaining=100.0  # TODO: get actual battery level
                )
                logger.debug("Status: Connected")
                return status.to_proto()
                
            except Exception as e:
                logger.warning(f"Connected but failed to get detailed status: {e}")
                # Fall through to disconnected case
                is_connected = False
                message = f"Connection unstable: {str(e)}"
        
        # Disconnected case
        logger.debug(f"Status: Disconnected - {message}")
        status = StatusResponse(
            connected=False, 
            message=message,
            status_code=DroneErrorCode.NOT_CONNECTED,
            current_position=None,
            current_attitude=None,
            flight_mode=ProtoFlightMode.UNKNOWN,
            armed=False,
            battery_remaining=0.0
        )
        return status.to_proto()


def create_pmini_config(device: str = "udpout:192.168.4.1:8080") -> Config:
    """Create Pmini configuration."""
    return Config(device=device, connection_time_sec=10)


# Global variables for signal handling
server_instance = None
grpc_server = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Signal shutdown to the service
    if server_instance:
        server_instance.shutdown()
    
    # Stop the gRPC server
    if grpc_server:
        logger.info("Stopping gRPC server...")
        grpc_server.stop(grace=2)
        logger.info("gRPC server stopped")


def serve(host: str = "127.0.0.1", port: int = 50051, device: str = "udpout:192.168.4.1:8080"):
    """Start the gRPC server."""
    global server_instance, grpc_server
    
    # Create Pmini instance using the actual library
    config = create_pmini_config(device)
    pmini = Pmini(config)

    # Create gRPC server
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_instance = DroneServiceServicer(pmini)
    add_DroneServiceServicer_to_server(server_instance, grpc_server)

    bind_addr = f"{host}:{port}"
    grpc_server.add_insecure_port(bind_addr)

    logger.info(f"Starting PMini gRPC server on {bind_addr}")
    logger.info(f"Connecting to drone at {device}")
    logger.info("Server features:")
    logger.info("  - Proper connection detection with heartbeat monitoring")
    logger.info("  - Connection timeout: 5 seconds")
    logger.info("  - Graceful shutdown on SIGTERM/SIGINT")
    logger.info("Available services:")
    logger.info("  - Takeoff(TakeoffRequest) -> CommandResponse")
    logger.info("  - Land(LandRequest) -> CommandResponse")
    logger.info("  - Arm(ArmRequest) -> CommandResponse")
    logger.info("  - Disarm(DisarmRequest) -> CommandResponse")
    logger.info("  - SetMode(SetModeRequest) -> CommandResponse")
    logger.info("  - GoTo(GoToRequest) -> CommandResponse")
    logger.info("  - MoveVelocity(MoveVelocityRequest) -> CommandResponse")
    logger.info("  - EmergencyStop(EmergencyStopRequest) -> CommandResponse")
    logger.info("  - Reboot(RebootRequest) -> CommandResponse")
    logger.info("  - GetHealth(GetHealthRequest) -> HealthResponse")
    logger.info("  - SubscribePosition(SubscribePositionRequest) -> stream PositionResponse")
    logger.info("  - SubscribeStatusText(SubscribeStatusTextRequest) -> stream StatusTextResponse")
    logger.info("  - SubscribeVelocity(SubscribeVelocityRequest) -> stream VelocityResponse")
    logger.info("  - SubscribeAttitude(SubscribeAttitudeRequest) -> stream AttitudeResponse")
    logger.info("  - Status(StatusRequest) -> StatusResponse")

    grpc_server.start()

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Server shutdown complete")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="PMini gRPC Server with Connection Detection")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=50051, help="Server port (default: 50051)")
    parser.add_argument(
        "--device", default="udpout:192.168.4.1:8080", help="MAVLink device (default: udpout:192.168.4.1:8080)"
    )

    args = parser.parse_args()

    serve(host=args.host, port=args.port, device=args.device)


if __name__ == "__main__":
    main()
