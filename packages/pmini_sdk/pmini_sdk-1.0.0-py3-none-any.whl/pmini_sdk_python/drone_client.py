#!/usr/bin/env python3
"""
Comprehensive Drone Client Wrapper

This client provides a high-level interface to the PMini drone server,
similar to mavsdk-python. It handles connection management, error handling,
and provides convenient methods for drone control.
"""

import asyncio
import logging
import time
from typing import AsyncIterator, Optional
import grpc

from pmini_sdk_python.generated.drone_pb2 import (
    ArmRequest,
    AttitudeResponse,
    CommandResponse,
    DisarmRequest,
    EmergencyStopRequest,
    FlightMode,
    GetHealthRequest,
    GoToRequest,
    HealthResponse,
    LandRequest,
    MoveVelocityRequest,
    PositionResponse,
    RebootRequest,
    SetModeRequest,
    StatusRequest,
    StatusResponse,
    StatusTextResponse,
    SubscribeAttitudeRequest,
    SubscribePositionRequest,
    SubscribeStatusTextRequest,
    SubscribeVelocityRequest,
    TakeoffRequest,
    VelocityResponse,
)
from pmini_sdk_python.generated.drone_pb2_grpc import DroneServiceStub

logger = logging.getLogger(__name__)


class DroneError(Exception):
    """Base exception for drone operations."""
    pass


class ConnectionError(DroneError):
    """Raised when connection to the drone server fails."""
    pass


class CommandError(DroneError):
    """Raised when a drone command fails."""
    pass


class DroneClient:
    """
    High-level client for controlling PMini drone via gRPC server.
    
    This client provides a convenient interface similar to mavsdk-python
    for controlling the drone, with proper error handling and connection management.
    """
    
    def __init__(self, server_address: str = "localhost:50051"):
        """
        Initialize the drone client.
        
        Args:
            server_address: Address of the drone server (host:port)
        """
        self.server_address = server_address
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[DroneServiceStub] = None
        self._connected = False
        self._connection_timeout = 10.0
        
    async def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to the drone server.
        
        Args:
            timeout: Connection timeout in seconds
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to drone server at {self.server_address}")
            self.channel = grpc.aio.insecure_channel(self.server_address)
            self.stub = DroneServiceStub(self.channel)
            
            # Test connection by calling status
            await asyncio.wait_for(self._test_connection(), timeout=timeout)
            self._connected = True
            logger.info("Successfully connected to drone server")
            
        except asyncio.TimeoutError:
            raise ConnectionError(f"Connection timeout after {timeout}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    async def disconnect(self) -> None:
        """Disconnect from the drone server."""
        if self.channel:
            await self.channel.close()
            self._connected = False
            logger.info("Disconnected from drone server")
    
    async def _test_connection(self) -> None:
        """Test the connection by calling status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            status = await self.stub.Status(StatusRequest())
            if not status.connected:
                raise ConnectionError("Drone not connected")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")
    
    @property
    def connected(self) -> bool:
        """Check if connected to the server."""
        return self._connected
    
    async def _execute_command(self, command_name: str, request, timeout: float = 10.0) -> CommandResponse:
        """
        Execute a command and handle the response.
        
        Args:
            command_name: Name of the command for logging
            request: The gRPC request object
            timeout: Command timeout in seconds
            
        Returns:
            CommandResponse: The command response
            
        Raises:
            CommandError: If command fails
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            logger.debug(f"Executing {command_name}")
            
            # Map request types to stub methods
            method_map = {
                TakeoffRequest: self.stub.Takeoff,
                LandRequest: self.stub.Land,
                ArmRequest: self.stub.Arm,
                DisarmRequest: self.stub.Disarm,
                SetModeRequest: self.stub.SetMode,
                GoToRequest: self.stub.GoTo,
                MoveVelocityRequest: self.stub.MoveVelocity,
                EmergencyStopRequest: self.stub.EmergencyStop,
                RebootRequest: self.stub.Reboot,
            }
            
            method = method_map.get(type(request))
            if not method:
                raise CommandError(f"Unknown request type: {type(request)}")
            
            response = await asyncio.wait_for(method(request), timeout=timeout)
            
            if not response.success:
                raise CommandError(f"{command_name} failed: {response.message}")
            
            logger.debug(f"{command_name} completed successfully")
            return response
            
        except asyncio.TimeoutError:
            raise CommandError(f"{command_name} timed out after {timeout}s")
        except grpc.RpcError as e:
            raise CommandError(f"{command_name} gRPC error: {e}")
        except Exception as e:
            raise CommandError(f"{command_name} failed: {e}")
    
    # Basic flight commands
    async def arm(self, timeout: float = 10.0) -> CommandResponse:
        """Arm the drone."""
        request = ArmRequest(timeout=timeout)
        return await self._execute_command("Arm", request, timeout)
    
    async def disarm(self, timeout: float = 10.0) -> CommandResponse:
        """Disarm the drone."""
        request = DisarmRequest(timeout=timeout)
        return await self._execute_command("Disarm", request, timeout)
    
    async def takeoff(self, altitude: float = 1.0, timeout: float = 30.0) -> CommandResponse:
        """
        Takeoff to specified altitude.
        
        Args:
            altitude: Takeoff altitude in meters
            timeout: Command timeout in seconds
        """
        request = TakeoffRequest(altitude=altitude, timeout=timeout)
        return await self._execute_command("Takeoff", request, timeout)
    
    async def land(self, timeout: float = 30.0) -> CommandResponse:
        """Land the drone."""
        request = LandRequest(timeout=timeout)
        return await self._execute_command("Land", request, timeout)
    
    async def set_mode(self, mode: FlightMode, timeout: float = 10.0) -> CommandResponse:
        """
        Set flight mode.
        
        Args:
            mode: Flight mode to set
            timeout: Command timeout in seconds
        """
        request = SetModeRequest(mode=mode, timeout=timeout)
        return await self._execute_command("SetMode", request, timeout)
    
    # Movement commands
    async def go_to(self, x: float, y: float, z: float, yaw: Optional[float] = None,
                    frame: int = 0, timeout: float = 30.0) -> CommandResponse:
        """
        Go to a specific position.
        
        Args:
            x: North position in meters (or latitude if global frame)
            y: East position in meters (or longitude if global frame)
            z: Down position in meters (or altitude if global frame)
            yaw: Yaw angle in radians (optional)
            frame: Coordinate frame (0=body, 1=local, 2=global)
            timeout: Command timeout in seconds
        """
        request = GoToRequest(
            x=x, y=y, z=z, yaw_rad=yaw, frame=frame, timeout=timeout
        )
        return await self._execute_command("GoTo", request, timeout)
    
    async def move_velocity(self, v_x: float, v_y: float, v_z: float,
                           yaw_rate: Optional[float] = None, frame: int = 0,
                           timeout: float = 10.0) -> CommandResponse:
        """
        Move with specified velocity.
        
        Args:
            v_x: North velocity in m/s
            v_y: East velocity in m/s
            v_z: Down velocity in m/s
            yaw_rate: Yaw rate in rad/s (optional)
            frame: Coordinate frame (0=body, 1=local)
            timeout: Command timeout in seconds
        """
        request = MoveVelocityRequest(
            v_x=v_x, v_y=v_y, v_z=v_z, yaw_rate_rad_s=yaw_rate, 
            frame=frame, timeout=timeout
        )
        return await self._execute_command("MoveVelocity", request, timeout)
    
    # Emergency commands
    async def emergency_stop(self, timeout: float = 5.0) -> CommandResponse:
        """Execute emergency stop."""
        request = EmergencyStopRequest(timeout=timeout)
        return await self._execute_command("EmergencyStop", request, timeout)
    
    async def reboot(self, timeout: float = 10.0) -> CommandResponse:
        """Reboot the drone."""
        request = RebootRequest(timeout=timeout)
        return await self._execute_command("Reboot", request, timeout)
    
    # Status and health
    async def get_status(self) -> StatusResponse:
        """Get current drone status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            return await self.stub.Status(StatusRequest())
        except Exception as e:
            raise CommandError(f"Failed to get status: {e}")
    
    async def get_health(self) -> HealthResponse:
        """Get drone health information."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            return await self.stub.GetHealth(GetHealthRequest())
        except Exception as e:
            raise CommandError(f"Failed to get health: {e}")
    
    # Streaming methods
    async def subscribe_position(self, rate_hz: float = 10.0) -> AsyncIterator[PositionResponse]:
        """
        Subscribe to position updates.
        
        Args:
            rate_hz: Requested update rate in Hz
            
        Yields:
            PositionResponse: Position updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            request = SubscribePositionRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribePosition(request):
                yield response
        except Exception as e:
            raise CommandError(f"Position subscription failed: {e}")
    
    async def subscribe_velocity(self, rate_hz: float = 10.0) -> AsyncIterator[VelocityResponse]:
        """
        Subscribe to velocity updates.
        
        Args:
            rate_hz: Requested update rate in Hz
            
        Yields:
            VelocityResponse: Velocity updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            request = SubscribeVelocityRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeVelocity(request):
                yield response
        except Exception as e:
            raise CommandError(f"Velocity subscription failed: {e}")
    
    async def subscribe_attitude(self, rate_hz: float = 10.0) -> AsyncIterator[AttitudeResponse]:
        """
        Subscribe to attitude updates.
        
        Args:
            rate_hz: Requested update rate in Hz
            
        Yields:
            AttitudeResponse: Attitude updates
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            request = SubscribeAttitudeRequest(rate_hz=rate_hz)
            async for response in self.stub.SubscribeAttitude(request):
                yield response
        except Exception as e:
            raise CommandError(f"Attitude subscription failed: {e}")
    
    async def subscribe_status_text(self) -> AsyncIterator[StatusTextResponse]:
        """
        Subscribe to status text messages.
        
        Yields:
            StatusTextResponse: Status text messages
        """
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            request = SubscribeStatusTextRequest()
            async for response in self.stub.SubscribeStatusText(request):
                yield response
        except Exception as e:
            raise CommandError(f"Status text subscription failed: {e}")
    
    # Convenience methods
    async def wait_for_connection(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be connected.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            ConnectionError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = await self.get_status()
                if status.connected:
                    logger.info("Drone connected")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)
        
        raise ConnectionError(f"Drone not connected within {timeout}s")
    
    async def wait_for_arm(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be armed.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            CommandError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = await self.get_status()
                if status.armed:
                    logger.info("Drone armed")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)
        
        raise CommandError(f"Drone not armed within {timeout}s")
    
    async def wait_for_disarm(self, timeout: float = 30.0) -> None:
        """
        Wait for drone to be disarmed.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Raises:
            CommandError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                status = await self.get_status()
                if not status.armed:
                    logger.info("Drone disarmed")
                    return
            except Exception:
                pass
            await asyncio.sleep(1.0)
        
        raise CommandError(f"Drone not disarmed within {timeout}s")
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience functions for common operations
async def create_drone_client(server_address: str = "localhost:50051") -> DroneClient:
    """
    Create and connect a drone client.
    
    Args:
        server_address: Address of the drone server
        
    Returns:
        DroneClient: Connected drone client
    """
    client = DroneClient(server_address)
    await client.connect()
    return client


async def basic_flight_sequence(client: DroneClient, altitude: float = 1.0) -> None:
    """
    Execute a basic flight sequence: arm, takeoff, land, disarm.
    
    Args:
        client: Connected drone client
        altitude: Takeoff altitude in meters
    """
    try:
        logger.info("Starting basic flight sequence")
        
        # Wait for connection
        await client.wait_for_connection()
        
        # Arm
        await client.arm()
        await client.wait_for_arm()
        
        # Takeoff
        await client.takeoff(altitude)
        logger.info(f"Takeoff to {altitude}m completed")
        
        # Hover for a bit
        await asyncio.sleep(5.0)
        
        # Land
        await client.land()
        logger.info("Landing completed")
        
        # Disarm
        await client.disarm()
        await client.wait_for_disarm()
        
        logger.info("Basic flight sequence completed successfully")
        
    except Exception as e:
        logger.error(f"Flight sequence failed: {e}")
        raise


async def monitor_drone_state(client: DroneClient, duration: float = 30.0) -> None:
    """
    Monitor drone state for a specified duration.
    
    Args:
        client: Connected drone client
        duration: Monitoring duration in seconds
    """
    try:
        logger.info(f"Monitoring drone state for {duration}s")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(_monitor_position(client)),
            asyncio.create_task(_monitor_velocity(client)),
            asyncio.create_task(_monitor_attitude(client)),
            asyncio.create_task(_monitor_status_text(client)),
        ]
        
        # Wait for duration
        await asyncio.sleep(duration)
        
        # Cancel monitoring tasks
        for task in tasks:
            task.cancel()
        
        logger.info("Drone state monitoring completed")
        
    except Exception as e:
        logger.error(f"State monitoring failed: {e}")
        raise


async def _monitor_position(client: DroneClient) -> None:
    """Monitor position updates."""
    try:
        async for response in client.subscribe_position():
            pos = response.position
            logger.info(f"Position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
    except asyncio.CancelledError:
        pass


async def _monitor_velocity(client: DroneClient) -> None:
    """Monitor velocity updates."""
    try:
        async for response in client.subscribe_velocity():
            vel = response.velocity
            logger.info(f"Velocity: ({vel.v_x:.2f}, {vel.v_y:.2f}, {vel.v_z:.2f}) m/s")
    except asyncio.CancelledError:
        pass


async def _monitor_attitude(client: DroneClient) -> None:
    """Monitor attitude updates."""
    try:
        async for response in client.subscribe_attitude():
            att = response.attitude
            logger.info(f"Attitude: roll={att.roll_rad:.2f}, pitch={att.pitch_rad:.2f}, yaw={att.yaw_rad:.2f}")
    except asyncio.CancelledError:
        pass


async def _monitor_status_text(client: DroneClient) -> None:
    """Monitor status text messages."""
    try:
        async for response in client.subscribe_status_text():
            logger.info(f"Status: {response.status_text}")
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    # Example usage
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        try:
            async with DroneClient() as client:
                # Get status
                status = await client.get_status()
                logger.info(f"Drone status: {status.message}")
                
                # Get health
                health = await client.get_health()
                logger.info(f"Drone health: {health.message}")
                
                # Monitor state for 10 seconds
                await monitor_drone_state(client, 10.0)
                
        except Exception as e:
            logger.error(f"Example failed: {e}")
    
    asyncio.run(main())
