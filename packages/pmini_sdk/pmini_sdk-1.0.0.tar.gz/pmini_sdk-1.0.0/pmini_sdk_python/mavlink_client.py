import logging
import os
import signal
import time
from dataclasses import dataclass
from threading import Event, Lock, Thread
from typing import Callable, List, Optional, Union

import pymavlink
import pymavlink.dialects.v20.ardupilotmega as mavcmd
import pymavlink.mavutil
from pymavlink.dialects.v20.ardupilotmega import (
    MAV_DATA_STREAM_EXTENDED_STATUS,
    MAV_DATA_STREAM_EXTRA1,
    MAV_DATA_STREAM_EXTRA2,
    MAV_DATA_STREAM_EXTRA3,
    MAV_DATA_STREAM_POSITION,
    MAV_DATA_STREAM_RAW_SENSORS,
    MAV_DATA_STREAM_RC_CHANNELS,
)
from pymavlink.dialects.v20.ardupilotmega import MAVLink_local_position_ned_message as LocalPosition
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message as MavMessage

from pmini_sdk_python.common import FlightMode, MAVResult, PminiState, Quaternion, StatusText, Yaw, parse_mav_result
from pmini_sdk_python.generated import Attitude, Position, Velocity

# Set mavlink version https://mavlink.io/en/mavgen_python/#dialect_file
os.environ["MAVLINK20"] = "1"

logger = logging.getLogger(__name__)

AckCallback = Callable[[Optional[MAVResult]], None]
FlowCallback = Callable[[dict[str, Union[int, float]]], None]
StatusTextCallback = Callable[[StatusText], None]


class TimeoutException(Exception):
    def __init__(self, timeout_duration: int, context: str):
        super().__init__(f"Timeout after {timeout_duration} seconds: {context}")


class NotConnectedError(Exception):
    """Raised when MAVLink connection is not available."""

    pass


class Config:
    def __init__(
        self,
        device: str = "udpout:192.168.4.1:8080",
        source_system: int = 255,
        source_component: int = 0,
        connection_time_sec: int = 10,
    ) -> None:
        self.device = device
        self.source_system = source_system
        self.source_component = source_component
        self.connection_time_sec = connection_time_sec


class MavlinkCommandPackager:
    def __init__(self, connection):
        self.__connection = connection

    def package_arm(self):
        return self.__connection.mav.command_long_encode(
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            pymavlink.mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            0,  # confirmation
            1,  # param 1: arm
            0,
            0,
            0,
            0,
            0,
            0,  # param 2-7
        )

    def package_disarm(self):
        return self.__connection.mav.command_long_encode(
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            pymavlink.mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,  # command
            0,  # confirmation
            0,  # param 1: disarm
            0,
            0,
            0,
            0,
            0,
            0,  # param 2-7
        )

    def package_takeoff(self, height_m: float):
        return self.__connection.mav.command_long_encode(
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            pymavlink.mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,  # command
            0,  # confirmation
            0,  # param 1: pitch angle
            0,
            0,
            0,
            0,
            0,  # param 2-6: unused
            height_m,  # param 7: altitude
        )

    def package_land(self):
        return self.__connection.mav.command_long_encode(
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            pymavlink.mavutil.mavlink.MAV_CMD_NAV_LAND,  # command
            0,  # confirmation
            0,  # param 1: abort altitude
            0,  # param 2: precision land mode
            0,
            0,
            0,
            0,
            0,  # param 3-7: unused/coordinates
        )

    def package_go_to(
        self, x, y, z, type_mask, yaw: Yaw = Yaw(value=0), frame=pymavlink.mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED
    ):
        logger.debug(f"GOTO: {[x, y, -z]}")
        return self.__connection.mav.set_position_target_local_ned_encode(
            0,  # time_boot_ms
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            frame,  # coordinate frame
            type_mask,  # type mask
            x,
            y,
            -z,  # position
            0,
            0,
            0,  # velocity
            0,
            0,
            0,  # acceleration
            yaw.value,  # yaw setpoint [rad]
            0,  # yaw rate setpoint [rad/s]
        )

    def package_velocity(
        self, vx, vy, vz, type_mask, yaw: Yaw = Yaw(value=0), frame=pymavlink.mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED
    ):
        logger.debug(f"VEL: {[vx, vy, -vz]}")
        return self.__connection.mav.set_position_target_local_ned_encode(
            0,  # time_boot_ms
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            frame,  # coordinate frame
            type_mask,  # type mask
            0,
            0,
            0,  # position (ignored)
            vx,
            vy,
            -vz,  # velocity
            0,
            0,
            0,  # acceleration (ignored)
            yaw.value,  # yaw setpoint [rad]
            0,  # yaw rate setpoint [rad/s]
        )

    def package_flight_mode(self, flight_mode: FlightMode):
        return self.__connection.mav.command_long_encode(
            self.__connection.target_system,  # target system
            self.__connection.target_component,  # target component
            pymavlink.mavutil.mavlink.MAV_CMD_DO_SET_MODE,  # command
            0,  # confirmation
            1,  # param 1: mode flag (custom mode enabled)
            flight_mode.to_id(),  # param 2: custom mode
            0,
            0,
            0,
            0,
            0,  # param 3-7
        )


class CallbackList:
    def __init__(self):
        self.callbacks = []
        self._lock = Lock()

    def register(self, cb):
        with self._lock:
            if cb not in self.callbacks:
                self.callbacks.append(cb)

    def unregister(self, cb):
        with self._lock:
            if cb in self.callbacks:
                self.callbacks.remove(cb)

    def call(self, *args):
        with self._lock:
            # Copy to avoid modification during iteration
            copy_callbacks = list(self.callbacks)

        # Call outside lock to avoid deadlock
        for cb in copy_callbacks:
            try:
                cb(*args)
            except Exception as e:
                logger.exception(f"Callback error: {e}\nCallback: {cb}, args: {args}")


class MavlinkDispatcher:
    @dataclass(frozen=True)
    class RegisteredHandler:
        msg_id: int
        callback: Callable

    def __init__(self) -> None:
        self._handlers: List[MavlinkDispatcher.RegisteredHandler] = []
        self._lock = Lock()

    def register_msg(self, msg_id: int, callback: Callable) -> None:
        with self._lock:
            self._handlers.append(self.RegisteredHandler(msg_id, callback))

    def unregister_msg(self, msg_id: int) -> None:
        with self._lock:
            self._handlers = [h for h in self._handlers if h.msg_id != msg_id]

    def handle_message(self, message: MavMessage) -> None:
        with self._lock:
            snapshot = list(self._handlers)

        for h in snapshot:
            if h.msg_id == message.get_msgId():
                try:
                    h.callback(message)
                except Exception as e:
                    logger.exception(f"Message handler error: {e}")


class MavlinkClient(Thread):
    def __init__(self, config: Config, logger: logging.Logger = logging.getLogger(name="mavlink_client")) -> None:
        Thread.__init__(self, name="MavlinkClientThread")
        self.daemon = True
        self.__connection = None
        self.__mav = None
        self._is_connected: bool = False
        self.__config = config
        self.__logger = logger
        self.__hb_send_time_s = 0
        self.__last_msg_time = time.time()
        self.__shutdown_event = Event()
        self.mavlink_dispatcher: MavlinkDispatcher = MavlinkDispatcher()
        self.command_packager = None

        # Setup handlers
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, self.process_global_position)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_LOCAL_POSITION_NED, self.process_local_position)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_HEARTBEAT, self.process_heartbeat)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_ATTITUDE, self.process_attitude)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_ATTITUDE_QUATERNION, self.process_attitude_quat)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_OPTICAL_FLOW, self.process_optical_flow)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_STATUSTEXT, self.process_status_text)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_COMMAND_ACK, self.process_command_ack)
        self.mavlink_dispatcher.register_msg(mavcmd.MAVLINK_MSG_ID_EXTENDED_SYS_STATE, self.process_extended_sys_state)

        # Init fields with proper locking
        self._ack_callbacks: dict[tuple[int, ...], AckCallback] = {}
        self._ack_callbacks_lock = Lock()
        self._current_location: Position = Position(x=0.0, y=0.0, z=0.0)
        self._current_location_lock = Lock()
        self._current_velocity: Velocity = Velocity(v_x=0.0, v_y=0.0, v_z=0.0)
        self._current_velocity_lock = Lock()
        self._attitude: Attitude = Attitude(roll_rad=0.0, pitch_rad=0.0, yaw_rad=0.0)
        self._attitude_lock = Lock()
        self._optical_flow: dict[str, Union[int, float]] = {}
        self._optical_flow_lock = Lock()
        self._attitude_quat = Quaternion()
        self._attitude_quat_lock = Lock()
        self._current_global_location: list[float] = [0.0, 0.0, 0.0]
        self._current_global_location_lock = Lock()
        self._state: PminiState = PminiState.UNDEFINED
        self._state_lock = Lock()
        self._flight_mode: FlightMode = FlightMode.UNKNOWN
        self._flight_mode_lock = Lock()
        self._armed: bool = False
        self._armed_lock = Lock()

        # Init callbacks
        self.pos_callback: CallbackList = CallbackList()
        self.vel_callback: CallbackList = CallbackList()
        self.attitude_callback: CallbackList = CallbackList()
        self.of_callback: CallbackList = CallbackList()
        self.status_text_callback: CallbackList = CallbackList()
        self.attitude_quat_callback: CallbackList = CallbackList()
        self.pmini_state_callback: CallbackList = CallbackList()
        self.flight_mode_callback: CallbackList = CallbackList()

    def run(self) -> None:
        while not self.__shutdown_event.is_set():
            try:
                self.__send_heartbeat()
                self.__rcv_msg()
                time.sleep(0.001)
            except Exception as e:
                self.__logger.exception(f"Error in main loop: {e}")
                time.sleep(0.1)  # Prevent tight error loop

    def shutdown(self):
        """Gracefully shutdown the client"""
        self.__shutdown_event.set()
        if self.__connection:
            try:
                self.__connection.close()
            except Exception as e:
                self.__logger.warning(f"Error closing connection: {e}")

    def health(self) -> bool:
        current_time = time.time()
        # Check if we've received a message in the last 5 seconds
        return self._is_connected and (current_time - self.__last_msg_time) < 5.0

    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> None:
        self.__trying_connection()
        self.__init_stream_rate()
        if self.__connection:
            self.command_packager = MavlinkCommandPackager(self.__connection)

        def ack_callback(msg: str, mid: int, freq: int) -> AckCallback:
            def _cb(result: Optional[MAVResult]):
                if result is None:
                    logger.warning(f"[{msg}] ID={mid}, freq={freq}Hz -> ❌ No response")
                elif result.is_success():
                    logger.info(f"[{msg}] ID={mid}, freq={freq}Hz -> ✅ {result.name}")
                elif result.is_temporary():
                    logger.warning(f"[{msg}] ID={mid}, freq={freq}Hz -> ⚠️ Temporary error: {result.name}")
                else:
                    logger.warning(f"[{msg}] ID={mid}, freq={freq}Hz -> ❌ Failed: {result.name}")

            return _cb

        # Set message intervals with proper error handling
        self.set_message_interval(
            mavcmd.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
            int(1_000_000 / 2),
            callback=ack_callback("SET_MESSAGE_INTERVAL", mavcmd.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 2),
        )
        self.set_message_interval(
            mavcmd.MAVLINK_MSG_ID_LOCAL_POSITION_NED,
            int(100_000),  # 10 Hz
            callback=ack_callback("SET_MESSAGE_INTERVAL", mavcmd.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 10),
        )
        self.set_message_interval(
            mavcmd.MAVLINK_MSG_ID_OPTICAL_FLOW,
            int(100_000),  # 10 Hz
            callback=ack_callback("SET_MESSAGE_INTERVAL", mavcmd.MAVLINK_MSG_ID_OPTICAL_FLOW, 10),
        )

    def __trying_connection(self) -> None:
        self.__logger.info("Trying to connect...")
        start_time = time.time()

        while not self.__wait_heartbeat():
            try:
                if (time.time() - start_time) > self.__config.connection_time_sec:
                    raise TimeoutException(
                        timeout_duration=self.__config.connection_time_sec,
                        context=f"Attempting to connect to device {self.__config.device}",
                    )

                conn = pymavlink.mavutil.mavlink_connection(
                    device=self.__config.device,
                    source_system=self.__config.source_system,
                    source_component=self.__config.source_component,
                )

                self.__connection = conn
                self.__mav = conn.mav
                self.__send_heartbeat()
            except Exception as e:
                self.__logger.exception("Connection failed: %s", e)
                raise e

        self.__logger.info(f"Connection successful to device: {self.__config.device}")

    def __init_stream_rate(self):
        if not self.__connection:
            return

        stream_ids = [
            MAV_DATA_STREAM_RAW_SENSORS,
            MAV_DATA_STREAM_EXTENDED_STATUS,
            MAV_DATA_STREAM_RC_CHANNELS,
            MAV_DATA_STREAM_POSITION,
            MAV_DATA_STREAM_EXTRA1,
            MAV_DATA_STREAM_EXTRA2,
            MAV_DATA_STREAM_EXTRA3,
        ]

        for stream_id in stream_ids:
            self.set_data_stream(stream_id, 0)
        # Temporary solution to make the frequency change work correctly
        time.sleep(1)

    @property
    def connection(self):
        return self.__connection

    def __wait_heartbeat(self) -> bool:
        if self.__connection is None:
            return False
        ret = self.__connection.wait_heartbeat(timeout=1)
        if ret is None:
            return False
        self.__logger.info(
            f"Received heartbeat from target_system: {self.__connection.target_system}, "
            f"target_component: {self.__connection.target_component}"
        )
        self.__hb_send_time_s = 0
        return True

    def __send_heartbeat(self):
        if not self.__mav:
            return

        now = time.time()
        if now - self.__hb_send_time_s > 1:
            try:
                self.__mav.heartbeat_send(mavcmd.MAV_TYPE_GCS, mavcmd.MAV_AUTOPILOT_INVALID, 0, 0, mavcmd.MAV_STATE_ACTIVE)
                self.__hb_send_time_s = now
                self.__logger.debug("Send the heartbeat")
            except Exception as e:
                self.__logger.warning(f"Failed to send heartbeat: {e}")

    def send_msg(self, msg):
        if self.__connection and self.__connection.mav:
            try:
                self.__connection.mav.send(msg)
            except Exception as e:
                self.__logger.error(f"Failed to send message: {e}")
                raise NotConnectedError("Failed to send message")

    def send_msg_with_ack(self, msg, callback: Optional[AckCallback] = None, timeout=5):
        """Send a pre-packed MAVLink message and track the COMMAND_ACK via callback."""
        if msg.get_msgId() == pymavlink.mavutil.mavlink.MAVLINK_MSG_ID_COMMAND_LONG:
            command = msg.command
            key = (
                (command, int(msg.param1)) if command == pymavlink.mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL else (command,)
            )
        elif msg.get_msgId() == pymavlink.mavutil.mavlink.MAVLINK_MSG_ID_COMMAND_INT:
            command = msg.command
            key = (command,)
        else:
            self.__logger.warning(f"Unsupported msg type {msg.get_msgId()}, no ACK tracking")
            self.send_msg(msg)
            return

        if callback is not None:
            with self._ack_callbacks_lock:
                self._ack_callbacks[key] = callback

        self.send_msg(msg)
        self.__logger.debug(f"Sent prepacked command {command} with callback tracking key {key}")

    def send_command_with_ack(self, command, params, callback: Optional[AckCallback] = None, timeout=5):
        if self.__connection is None:
            raise NotConnectedError("MAVLink connection not established.")

        key = (command, int(params[0])) if command == pymavlink.mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL else (command,)

        if callback is not None:
            with self._ack_callbacks_lock:
                self._ack_callbacks[key] = callback

        try:
            self.__connection.mav.command_long_send(
                self.__connection.target_system,
                self.__connection.target_component,
                command,
                0,
                *params,  # unpack the 7 command params
            )
            self.__logger.debug(f"Sent command {command} with params {params}")
        except Exception as e:
            self.__logger.error(f"Failed to send command {command}: {e}")
            # Clean up callback on failure
            if callback is not None:
                with self._ack_callbacks_lock:
                    self._ack_callbacks.pop(key, None)
            raise NotConnectedError(f"Failed to send command: {e}")

    def wait_arm(self, timeout=None):
        """Block until motors are armed, with an optional timeout."""
        if not self.__connection:
            raise NotConnectedError("Not connected to vehicle")

        start_time = time.monotonic()

        while True:
            if timeout is not None:
                elapsed_time = time.monotonic() - start_time
                self.__logger.debug(f"elapsed_time = {elapsed_time}, timeout = {timeout}")
                if elapsed_time >= timeout:
                    raise TimeoutError("Timeout expired while waiting for motors to arm.")

            # Check current armed status instead of waiting for heartbeat
            if self.armed:
                return

            time.sleep(0.1)  # Small delay to prevent busy waiting

    # Getter and private Setter for current_location
    @property
    def current_location(self) -> Position:
        with self._current_location_lock:
            return Position(x=self._current_location.x, y=self._current_location.y, z=self._current_location.z)

    def _set_current_location(self, value: Position) -> None:
        with self._current_location_lock:
            self._current_location = value

    # Getter and private Setter for current_velocity
    @property
    def current_velocity(self) -> Velocity:
        with self._current_velocity_lock:
            return Velocity(v_x=self._current_velocity.v_x, v_y=self._current_velocity.v_y, v_z=self._current_velocity.v_z)

    def _set_current_velocity(self, value: Velocity) -> None:
        with self._current_velocity_lock:
            self._current_velocity = value

    # Getter and private Setter for attitude
    @property
    def attitude(self) -> Attitude:
        with self._attitude_lock:
            return Attitude(
                roll_rad=self._attitude.roll_rad, pitch_rad=self._attitude.pitch_rad, yaw_rad=self._attitude.yaw_rad
            )

    def _set_attitude(self, value: Attitude) -> None:
        with self._attitude_lock:
            self._attitude = value

    # Getter and private Setter for optical_flow
    @property
    def optical_flow(self) -> dict[str, Union[int, float]]:
        with self._optical_flow_lock:
            return dict(self._optical_flow)

    def _set_optical_flow(self, value: dict[str, Union[int, float]]) -> None:
        with self._optical_flow_lock:
            self._optical_flow = dict(value)

    # Getter and private Setter for attitude_quat
    @property
    def attitude_quat(self) -> Quaternion:
        with self._attitude_quat_lock:
            return self._attitude_quat

    def _set_attitude_quat(self, value: Quaternion) -> None:
        with self._attitude_quat_lock:
            self._attitude_quat = value

    # Getter and private Setter for current_global_location
    @property
    def current_global_location(self) -> list[float]:
        with self._current_global_location_lock:
            return list(self._current_global_location)

    def _set_current_global_location(self, value: list[float]) -> None:
        with self._current_global_location_lock:
            self._current_global_location = list(value)

    # Getter and private Setter for state
    @property
    def state(self) -> PminiState:
        with self._state_lock:
            return self._state

    def _set_state(self, value: PminiState) -> None:
        with self._state_lock:
            self._state = value

    # Getter and private Setter for flight_mode
    @property
    def flight_mode(self) -> FlightMode:
        with self._flight_mode_lock:
            return self._flight_mode

    def _set_flight_mode(self, value: FlightMode) -> None:
        with self._flight_mode_lock:
            self._flight_mode = value

    # Getter and private Setter for armed
    @property
    def armed(self) -> bool:
        with self._armed_lock:
            return self._armed

    def _set_armed(self, value: bool) -> None:
        with self._armed_lock:
            self._armed = value

    def disarm(self):
        if self.__connection:
            try:
                self.__connection.arducopter_disarm()
            except Exception as e:
                self.__logger.error(f"Failed to disarm: {e}")
                raise NotConnectedError(f"Failed to disarm: {e}")
        else:
            raise NotConnectedError("Not connected to vehicle")

    def wait_disarm(self):
        """Block until motors are disarmed."""
        if not self.__connection:
            raise NotConnectedError("Not connected to vehicle")
        try:
            self.__connection.motors_disarmed_wait()
        except Exception as e:
            self.__logger.error(f"Error waiting for disarm: {e}")

    def get_mode_id(self, flight_mode):
        mode_map = {
            "STABILIZE": FlightMode.STABILIZE,
            "GUIDED": FlightMode.GUIDED,
            "LOITER": FlightMode.LOITER,
            "LAND": FlightMode.LAND,
        }
        if flight_mode in mode_map:
            return mode_map[flight_mode]
        else:
            raise ValueError(f"Invalid flight mode: {flight_mode}")

    def __rcv_msg(self) -> None:
        try:
            if self.__connection is None:
                return

            msg = self.__connection.recv_match(blocking=False)
            if msg is None:
                return
            else:
                self.__last_msg_time = time.time()
                self.__handle_msg(msg)

        except Exception as err:
            self.__logger.exception(f"Error receiving message: {err}")
            self._is_connected = False

    def __handle_msg(self, msg):
        self.mavlink_dispatcher.handle_message(msg)

    def process_heartbeat(self, msg):
        self._is_connected = True
        armed = msg.base_mode & pymavlink.mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        self._set_armed(bool(armed))

        # Check for flight mode
        if msg.base_mode & pymavlink.mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED:
            flight_mode = FlightMode.from_id(msg.custom_mode)
            self._set_flight_mode(flight_mode)
            self.__trigger_flight_mode_callbacks()
        self.__logger.debug(f"HEARTBEAT: armed={self.armed}, mode={self.flight_mode}")

    def process_global_position(self, msg):
        current_lat = msg.lat / 1e7  # Latitude in degrees
        current_lon = msg.lon / 1e7  # Longitude in degrees
        current_alt = msg.alt / 1e3  # Altitude in meters above mean sea level
        self._set_current_global_location([current_lat, current_lon, current_alt])

    def process_local_position(self, msg: LocalPosition):
        current_north = msg.x  # Position in meters to the north of the home position
        current_east = msg.y  # Position in meters to the east of the home position
        current_down = msg.z  # Position in meters down from the home position
        position = Position(x=current_north, y=current_east, z=current_down)
        velocity = Velocity(v_x=msg.vx, v_y=msg.vy, v_z=msg.vz)
        self._set_current_location(position)
        self._set_current_velocity(velocity)
        self.__trigger_position_callbacks()
        self.__trigger_velocity_callbacks()

    def process_attitude(self, msg):
        attitude = Attitude(roll_rad=msg.roll, pitch_rad=msg.pitch, yaw_rad=msg.yaw)
        self._set_attitude(attitude)
        self.__trigger_attitude_callbacks()

    def process_attitude_quat(self, msg):
        self._set_attitude_quat(Quaternion(x=msg.q2, y=msg.q3, z=msg.q4, w=msg.q1))
        self.__trigger_attitude_quat_callbacks()

    def process_optical_flow(self, msg):
        self._set_optical_flow(
            {
                "time_usec": msg.time_usec,
                "flow_x": msg.flow_x,
                "flow_y": msg.flow_y,
                "sensor_id": msg.sensor_id,
                "flow_comp_m_x": msg.flow_comp_m_x,
                "flow_comp_m_y": msg.flow_comp_m_y,
                "quality": msg.quality,
                "ground_distance": msg.ground_distance,
            }
        )
        self.__trigger_of_callbacks()

    def process_status_text(self, msg):
        severity = msg.severity
        text = msg.text.strip("\x00")  # Remove null characters

        self.__trigger_status_text_callbacks(StatusText(severity, text))

        severity_map = {
            0: "EMERGENCY",  # System is unusable
            1: "ALERT",  # Immediate action required
            2: "CRITICAL",  # Critical conditions
            3: "ERROR",  # Error conditions
            4: "WARNING",  # Warning conditions
            5: "NOTICE",  # Normal but significant condition
            6: "INFO",  # Informational messages
            7: "DEBUG",  # Debug-level messages
        }

        severity_label = severity_map.get(severity, f"UNKNOWN({severity})")
        self.__logger.debug(f"MAVLink [{severity_label}]: {text}")

    def process_command_ack(self, msg):
        command = msg.command
        result = msg.result

        result_enum = parse_mav_result(result)
        matched_key = None

        with self._ack_callbacks_lock:
            for key in list(self._ack_callbacks.keys()):
                if isinstance(key, tuple) and key[0] == command:
                    matched_key = key
                    break

            if matched_key:
                callback = self._ack_callbacks.pop(matched_key)
            else:
                callback = None

        if callback:
            if result_enum is not None:
                callback(result_enum)
            else:
                callback(MAVResult.FAILED)
        else:
            self.__logger.debug(f"No callback registered for COMMAND_ACK {command}")

    def process_extended_sys_state(self, msg):
        state = PminiState.from_msg(msg)
        self._set_state(state)
        self.__trigger_pmini_state_callbacks(state)
        self.__logger.debug(f"MAV_LANDED_STATE: {msg}")

    def reboot_drone(self):
        if not self.__connection:
            raise NotConnectedError("Not connected to vehicle")

        try:
            self.__connection.mav.command_long_send(
                self.__connection.target_system,
                self.__connection.target_component,
                pymavlink.mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                0,  # confirmation
                1,  # param1: reboot autopilot
                0,
                0,
                0,
                0,
                0,
                0,
            )
            self.__logger.info("Reboot command sent to the drone.")

            ack = self.__connection.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
            if ack:
                self.__logger.info(f"Reboot ACK received: command={ack.command}, result={ack.result}")
            else:
                self.__logger.warning("No ACK received after reboot command.")

        except Exception as err:
            self.__logger.exception(f"Failed to send reboot command. {err}")
            raise NotConnectedError(f"Failed to reboot: {err}")

    def wait_ack(self, ack_id):
        if not self.__connection:
            raise NotConnectedError("Not connected to vehicle")

        self.__logger.info("Waiting for ACK...")

        ack = self.__connection.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
        if ack:
            self.__logger.info(f"ACK received: command={ack.command}, result={ack.result}")
            return ack
        else:
            self.__logger.warning("No ACK received.")
            return None

    def __trigger_position_callbacks(self):
        self.pos_callback.call(self.current_location)

    def __trigger_velocity_callbacks(self):
        self.vel_callback.call(self.current_velocity)

    def __trigger_attitude_callbacks(self):
        self.attitude_callback.call(self.attitude)

    def __trigger_of_callbacks(self):
        self.of_callback.call(self.optical_flow)

    def __trigger_status_text_callbacks(self, status_text: StatusText):
        self.status_text_callback.call(status_text)

    def __trigger_attitude_quat_callbacks(self):
        self.attitude_quat_callback.call(self.attitude_quat)

    def __trigger_pmini_state_callbacks(self, state: PminiState):
        self.pmini_state_callback.call(state)

    def __trigger_flight_mode_callbacks(self):
        self.flight_mode_callback.call(self.flight_mode)

    def set_message_interval(self, message_id, interval, callback: Optional[AckCallback] = None):
        self.send_command_with_ack(
            pymavlink.mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, [message_id, interval, 0, 0, 0, 0, 0], callback=callback
        )

    def set_data_stream(self, stream_id, rate_hz):
        if not self.__mav:
            return

        try:
            msg = self.__mav.request_data_stream_encode(
                self.__connection.target_system,  # target_system
                self.__connection.target_component,  # target_component
                stream_id,  # req_stream_id
                rate_hz,  # req_message_rate in Hz
                1,  # start_stop: 1 to start, 0 to stop
            )
            self.send_msg(msg)
        except Exception as e:
            self.__logger.error(f"Failed to set data stream {stream_id}: {e}")

    # Callback registration methods
    def add_position_callback(self, callback):
        self.pos_callback.register(callback)

    def add_velocity_callback(self, callback):
        self.vel_callback.register(callback)

    def add_attitude_callback(self, callback):
        self.attitude_callback.register(callback)

    def add_of_callback(self, callback):
        self.of_callback.register(callback)

    def add_status_text_callback(self, callback):
        self.status_text_callback.register(callback)

    def add_attitude_quat_callback(self, callback):
        self.attitude_quat_callback.register(callback)

    def add_pmini_state_callback(self, callback):
        self.pmini_state_callback.register(callback)

    def add_flight_mode_callback(self, callback):
        self.flight_mode_callback.register(callback)

    # Callback removal methods
    def remove_position_callback(self, callback):
        self.pos_callback.unregister(callback)

    def remove_velocity_callback(self, callback):
        self.vel_callback.unregister(callback)

    def remove_attitude_callback(self, callback):
        self.attitude_callback.unregister(callback)

    def remove_of_callback(self, callback):
        self.of_callback.unregister(callback)

    def remove_status_text_callback(self, callback):
        self.status_text_callback.unregister(callback)

    def remove_attitude_quat_callback(self, callback):
        self.attitude_quat_callback.unregister(callback)

    def remove_pmini_state_callback(self, callback):
        self.pmini_state_callback.unregister(callback)

    def remove_flight_mode_callback(self, callback):
        self.flight_mode_callback.unregister(callback)


def setup_logging():
    FORMAT = "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s"
    logging.basicConfig(filename="out.log", format=FORMAT, level=logging.DEBUG)
    return logging.getLogger(name="mavlink_client")


def initialize_mavlink_client(config, logger):
    try:
        client = MavlinkClient(config, logger)
        client.connect()
        return client
    except TimeoutException:
        logger.exception("Timeout during initialization")
        raise
    except Exception as e:
        logger.exception(f"Connection failed: {e}")
        raise


# Global flag for graceful shutdown
keep_running = True


def signal_handler(sig, frame, logger, mavlink_client=None):
    logger.info("Signal received, stopping...")
    global keep_running
    keep_running = False
    if mavlink_client:
        mavlink_client.shutdown()


def main():
    logger = setup_logging()
    config = Config()
    # config.device = "udp:localhost:8080"

    mavlink_client = None
    try:
        mavlink_client = initialize_mavlink_client(config, logger)
    except TimeoutException:
        logger.error("Initialization timeout")
        return 1
    except Exception as e:
        logger.error(f"Failed to initialize MavlinkClient: {e}")
        return 1

    # Start the client thread
    mavlink_client.start()

    # Wait for connection
    connection_timeout = 10
    start_time = time.time()
    while not mavlink_client.is_connected():
        if time.time() - start_time > connection_timeout:
            logger.error("Connection timeout")
            mavlink_client.shutdown()
            return 1
        time.sleep(0.1)

    logger.info("MavlinkClient initialized and connected")

    # Setup signal handlers with client reference
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, logger, mavlink_client))
    signal.signal(signal.SIGTERM, lambda sig, frame: signal_handler(sig, frame, logger, mavlink_client))

    try:
        while keep_running and mavlink_client.health():
            time.sleep(0.1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        logger.info("Shutting down...")
        if mavlink_client:
            mavlink_client.shutdown()
            mavlink_client.join(timeout=5)  # Wait for thread to finish

    return 0


if __name__ == "__main__":
    exit(main())
