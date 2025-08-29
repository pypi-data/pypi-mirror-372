#!/usr/bin/env python3
"""
Synchronous Drone Client Wrapper

This client provides a synchronous interface to the PMini drone server,
similar to mavsdk-python. It blocks until commands complete and handles
subscriptions in a separate thread for real-time updates.
"""

import asyncio
import logging
import threading
import time
from typing import Callable, Dict, List, Optional, Any
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


class SubscriptionCallback:
    """Callback wrapper for subscription data."""
    
    def __init__(self, callback: Callable, data_type: str):
        self.callback = callback
        self.data_type = data_type
        self.active = True
    
    def __call__(self, data: Any):
        if self.active and self.callback:
            try:
                self.callback(data)
            except Exception as e:
                logger.error(f"Error in {self.data_type} callback: {e}")


class SyncDroneClient:
    """
    Synchronous client for controlling PMini drone via gRPC server.
    
    This client provides a synchronous interface that blocks until commands complete.
    Subscriptions are handled in a separate thread for real-time updates.
    """
    
    def __init__(self, server_address: str = "localhost:50051"):
        """
        Initialize the synchronous drone client.
        
        Args:
            server_address: Address of the drone server (host:port)
        """
        self.server_address = server_address
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[DroneServiceStub] = None
        self._connected = False
        self._connection_timeout = 10.0
        
        # Subscription management
        self._subscription_thread: Optional[threading.Thread] = None
        self._subscription_loop: Optional[asyncio.AbstractEventLoop] = None
        self._subscription_callbacks: Dict[str, List[SubscriptionCallback]] = {
            'position': [],
            'velocity': [],
            'attitude': [],
            'status_text': []
        }
        self._subscription_running = False
        self._subscription_lock = threading.Lock()
        
    def connect(self, timeout: float = 10.0) -> None:
        """
        Connect to the drone server (synchronous).
        
        Args:
            timeout: Connection timeout in seconds
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            logger.info(f"Connecting to drone server at {self.server_address}")
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = DroneServiceStub(self.channel)
            
            # Test connection by calling status
            self._test_connection(timeout)
            self._connected = True
            logger.info("Successfully connected to drone server")
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the drone server."""
        # Stop subscription thread
        self._stop_subscription_thread()
        
        if self.channel:
            self.channel.close()
            self._connected = False
            logger.info("Disconnected from drone server")
    
    def _test_connection(self, timeout: float) -> None:
        """Test the connection by calling status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            # Use a future to handle timeout
            future = self.stub.Status.future(StatusRequest())
            status = future.result(timeout=timeout)
            
            if not status.connected:
                raise ConnectionError("Drone not connected")
        except Exception as e:
            raise ConnectionError(f"Connection test failed: {e}")
    
    @property
    def connected(self) -> bool:
        """Check if connected to the server."""
        return self._connected
    
    def _execute_command(self, command_name: str, request, timeout: float = 10.0) -> CommandResponse:
        """
        Execute a command and handle the response (synchronous).
        
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
            
            # Execute synchronously with timeout
            future = method.future(request)
            response = future.result(timeout=timeout)
            
            if not response.success:
                raise CommandError(f"{command_name} failed: {response.message}")
            
            logger.debug(f"{command_name} completed successfully")
            return response
            
        except Exception as e:
            raise CommandError(f"{command_name} failed: {e}")
    
    # Basic flight commands (synchronous)
    def arm(self, timeout: float = 10.0) -> CommandResponse:
        """Arm the drone (blocks until complete)."""
        request = ArmRequest(timeout=timeout)
        return self._execute_command("Arm", request, timeout)
    
    def disarm(self, timeout: float = 10.0) -> CommandResponse:
        """Disarm the drone (blocks until complete)."""
        request = DisarmRequest(timeout=timeout)
        return self._execute_command("Disarm", request, timeout)
    
    def takeoff(self, altitude: float = 1.0, timeout: float = 30.0) -> CommandResponse:
        """
        Takeoff to specified altitude (blocks until complete).
        
        Args:
            altitude: Takeoff altitude in meters
            timeout: Command timeout in seconds
        """
        request = TakeoffRequest(altitude=altitude, timeout=timeout)
        return self._execute_command("Takeoff", request, timeout)
    
    def land(self, timeout: float = 30.0) -> CommandResponse:
        """Land the drone (blocks until complete)."""
        request = LandRequest(timeout=timeout)
        return self._execute_command("Land", request, timeout)
    
    def set_mode(self, mode: FlightMode, timeout: float = 10.0) -> CommandResponse:
        """
        Set flight mode (blocks until complete).
        
        Args:
            mode: Flight mode to set
            timeout: Command timeout in seconds
        """
        request = SetModeRequest(mode=mode, timeout=timeout)
        return self._execute_command("SetMode", request, timeout)
    
    # Movement commands (synchronous)
    def go_to(self, x: float, y: float, z: float, yaw: Optional[float] = None,
              frame: int = 0, timeout: float = 30.0) -> CommandResponse:
        """
        Go to a specific position (blocks until complete).
        
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
        return self._execute_command("GoTo", request, timeout)
    
    def move_velocity(self, v_x: float, v_y: float, v_z: float,
                     yaw_rate: Optional[float] = None, frame: int = 0,
                     timeout: float = 10.0) -> CommandResponse:
        """
        Move with specified velocity (blocks until complete).
        
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
        return self._execute_command("MoveVelocity", request, timeout)
    
    # Emergency commands (synchronous)
    def emergency_stop(self, timeout: float = 5.0) -> CommandResponse:
        """Execute emergency stop (blocks until complete)."""
        request = EmergencyStopRequest(timeout=timeout)
        return self._execute_command("EmergencyStop", request, timeout)
    
    def reboot(self, timeout: float = 10.0) -> CommandResponse:
        """Reboot the drone (blocks until complete)."""
        request = RebootRequest(timeout=timeout)
        return self._execute_command("Reboot", request, timeout)
    
    # Status and health (synchronous)
    def get_status(self) -> StatusResponse:
        """Get current drone status."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            future = self.stub.Status.future(StatusRequest())
            return future.result(timeout=10.0)
        except Exception as e:
            raise CommandError(f"Failed to get status: {e}")
    
    def get_health(self) -> HealthResponse:
        """Get drone health information."""
        if not self.stub:
            raise ConnectionError("Not connected to server")
        
        try:
            future = self.stub.GetHealth.future(GetHealthRequest())
            return future.result(timeout=10.0)
        except Exception as e:
            raise CommandError(f"Failed to get health: {e}")
    
    # Subscription management
    def add_position_callback(self, callback: Callable[[PositionResponse], None]) -> None:
        """
        Add a callback for position updates.
        
        Args:
            callback: Function to call with position data
        """
        with self._subscription_lock:
            self._subscription_callbacks['position'].append(
                SubscriptionCallback(callback, 'position')
            )
        self._ensure_subscription_thread()
    
    def add_velocity_callback(self, callback: Callable[[VelocityResponse], None]) -> None:
        """
        Add a callback for velocity updates.
        
        Args:
            callback: Function to call with velocity data
        """
        with self._subscription_lock:
            self._subscription_callbacks['velocity'].append(
                SubscriptionCallback(callback, 'velocity')
            )
        self._ensure_subscription_thread()
    
    def add_attitude_callback(self, callback: Callable[[AttitudeResponse], None]) -> None:
        """
        Add a callback for attitude updates.
        
        Args:
            callback: Function to call with attitude data
        """
        with self._subscription_lock:
            self._subscription_callbacks['attitude'].append(
                SubscriptionCallback(callback, 'attitude')
            )
        self._ensure_subscription_thread()
    
    def add_status_text_callback(self, callback: Callable[[StatusTextResponse], None]) -> None:
        """
        Add a callback for status text updates.
        
        Args:
            callback: Function to call with status text data
        """
        with self._subscription_lock:
            self._subscription_callbacks['status_text'].append(
                SubscriptionCallback(callback, 'status_text')
            )
        self._ensure_subscription_thread()
    
    def remove_position_callback(self, callback: Callable[[PositionResponse], None]) -> None:
        """Remove a position callback."""
        with self._subscription_lock:
            self._subscription_callbacks['position'] = [
                cb for cb in self._subscription_callbacks['position'] 
                if cb.callback != callback
            ]
    
    def remove_velocity_callback(self, callback: Callable[[VelocityResponse], None]) -> None:
        """Remove a velocity callback."""
        with self._subscription_lock:
            self._subscription_callbacks['velocity'] = [
                cb for cb in self._subscription_callbacks['velocity'] 
                if cb.callback != callback
            ]
    
    def remove_attitude_callback(self, callback: Callable[[AttitudeResponse], None]) -> None:
        """Remove an attitude callback."""
        with self._subscription_lock:
            self._subscription_callbacks['attitude'] = [
                cb for cb in self._subscription_callbacks['attitude'] 
                if cb.callback != callback
            ]
    
    def remove_status_text_callback(self, callback: Callable[[StatusTextResponse], None]) -> None:
        """Remove a status text callback."""
        with self._subscription_lock:
            self._subscription_callbacks['status_text'] = [
                cb for cb in self._subscription_callbacks['status_text'] 
                if cb.callback != callback
            ]
    
    def _ensure_subscription_thread(self) -> None:
        """Ensure the subscription thread is running."""
        if not self._subscription_running:
            self._start_subscription_thread()
    
    def _start_subscription_thread(self) -> None:
        """Start the subscription thread."""
        if self._subscription_running:
            return
        
        self._subscription_running = True
        self._subscription_thread = threading.Thread(
            target=self._subscription_thread_worker,
            daemon=True
        )
        self._subscription_thread.start()
        logger.info("Subscription thread started")
    
    def _stop_subscription_thread(self) -> None:
        """Stop the subscription thread."""
        self._subscription_running = False
        if self._subscription_thread and self._subscription_thread.is_alive():
            self._subscription_thread.join(timeout=2.0)
            logger.info("Subscription thread stopped")
    
    def _subscription_thread_worker(self) -> None:
        """Worker thread for handling subscriptions."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async subscription worker
            loop.run_until_complete(self._async_subscription_worker())
            
        except Exception as e:
            logger.error(f"Subscription thread error: {e}")
        finally:
            try:
                loop.close()
            except Exception:
                pass
    
    async def _async_subscription_worker(self) -> None:
        """Async worker for handling subscriptions."""
        try:
            # Create async client for subscriptions
            async_client = AsyncDroneClient(self.server_address)
            await async_client.connect()
            
            # Start subscription tasks
            tasks = []
            
            if self._subscription_callbacks['position']:
                tasks.append(self._monitor_position(async_client))
            
            if self._subscription_callbacks['velocity']:
                tasks.append(self._monitor_velocity(async_client))
            
            if self._subscription_callbacks['attitude']:
                tasks.append(self._monitor_attitude(async_client))
            
            if self._subscription_callbacks['status_text']:
                tasks.append(self._monitor_status_text(async_client))
            
            # Run all subscription tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Async subscription worker error: {e}")
        finally:
            try:
                await async_client.disconnect()
            except Exception:
                pass
    
    async def _monitor_position(self, async_client) -> None:
        """Monitor position updates."""
        try:
            async for response in async_client.subscribe_position():
                if not self._subscription_running:
                    break
                
                with self._subscription_lock:
                    callbacks = self._subscription_callbacks['position'].copy()
                
                for callback in callbacks:
                    callback(response)
        except Exception as e:
            logger.error(f"Position monitoring error: {e}")
    
    async def _monitor_velocity(self, async_client) -> None:
        """Monitor velocity updates."""
        try:
            async for response in async_client.subscribe_velocity():
                if not self._subscription_running:
                    break
                
                with self._subscription_lock:
                    callbacks = self._subscription_callbacks['velocity'].copy()
                
                for callback in callbacks:
                    callback(response)
        except Exception as e:
            logger.error(f"Velocity monitoring error: {e}")
    
    async def _monitor_attitude(self, async_client) -> None:
        """Monitor attitude updates."""
        try:
            async for response in async_client.subscribe_attitude():
                if not self._subscription_running:
                    break
                
                with self._subscription_lock:
                    callbacks = self._subscription_callbacks['attitude'].copy()
                
                for callback in callbacks:
                    callback(response)
        except Exception as e:
            logger.error(f"Attitude monitoring error: {e}")
    
    async def _monitor_status_text(self, async_client) -> None:
        """Monitor status text updates."""
        try:
            async for response in async_client.subscribe_status_text():
                if not self._subscription_running:
                    break
                
                with self._subscription_lock:
                    callbacks = self._subscription_callbacks['status_text'].copy()
                
                for callback in callbacks:
                    callback(response)
        except Exception as e:
            logger.error(f"Status text monitoring error: {e}")
    
    # Convenience methods
    def wait_for_connection(self, timeout: float = 30.0) -> None:
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
                status = self.get_status()
                if status.connected:
                    logger.info("Drone connected")
                    return
            except Exception:
                pass
            time.sleep(1.0)
        
        raise ConnectionError(f"Drone not connected within {timeout}s")
    
    def wait_for_arm(self, timeout: float = 30.0) -> None:
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
                status = self.get_status()
                if status.armed:
                    logger.info("Drone armed")
                    return
            except Exception:
                pass
            time.sleep(1.0)
        
        raise CommandError(f"Drone not armed within {timeout}s")
    
    def wait_for_disarm(self, timeout: float = 30.0) -> None:
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
                status = self.get_status()
                if not status.armed:
                    logger.info("Drone disarmed")
                    return
            except Exception:
                pass
            time.sleep(1.0)
        
        raise CommandError(f"Drone not disarmed within {timeout}s")
    
    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Import the async client for internal use
from .drone_client import DroneClient as AsyncDroneClient


# Convenience functions for common operations
def create_sync_drone_client(server_address: str = "localhost:50051") -> SyncDroneClient:
    """
    Create and connect a synchronous drone client.
    
    Args:
        server_address: Address of the drone server
        
    Returns:
        SyncDroneClient: Connected synchronous drone client
    """
    client = SyncDroneClient(server_address)
    client.connect()
    return client


def basic_flight_sequence(client: SyncDroneClient, altitude: float = 1.0) -> None:
    """
    Execute a basic flight sequence: arm, takeoff, land, disarm.
    
    Args:
        client: Connected synchronous drone client
        altitude: Takeoff altitude in meters
    """
    try:
        logger.info("Starting basic flight sequence")
        
        # Wait for connection
        client.wait_for_connection()
        
        # Arm
        client.arm()
        client.wait_for_arm()
        
        # Takeoff
        client.takeoff(altitude)
        logger.info(f"Takeoff to {altitude}m completed")
        
        # Hover for a bit
        time.sleep(5.0)
        
        # Land
        client.land()
        logger.info("Landing completed")
        
        # Disarm
        client.disarm()
        client.wait_for_disarm()
        
        logger.info("Basic flight sequence completed successfully")
        
    except Exception as e:
        logger.error(f"Flight sequence failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    def main():
        logging.basicConfig(level=logging.INFO)
        
        # Example callback functions
        def position_callback(response):
            pos = response.position
            print(f"Position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f})")
        
        def status_callback(response):
            print(f"Status: {response.status_text}")
        
        try:
            with SyncDroneClient() as client:
                # Add callbacks for real-time updates
                client.add_position_callback(position_callback)
                client.add_status_text_callback(status_callback)
                
                # Get status
                status = client.get_status()
                logger.info(f"Drone status: {status.message}")
                
                # Get health
                health = client.get_health()
                logger.info(f"Drone health: {health.message}")
                
                # Wait a bit to see some subscription data
                time.sleep(10.0)
                
        except Exception as e:
            logger.error(f"Example failed: {e}")
    
    main()
