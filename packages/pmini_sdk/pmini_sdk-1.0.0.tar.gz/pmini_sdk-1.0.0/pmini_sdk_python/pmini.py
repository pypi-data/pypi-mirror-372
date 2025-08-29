import argparse
import logging
import time
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FuturesTimeoutError
from importlib import metadata
from typing import Optional

import pymavlink.dialects.v20.ardupilotmega as mavcmd

from .common import FlightMode, Frame, MAVResult, Yaw
from .generated import Attitude, Position, Velocity
from .high_level_commander import HighLevelCommander
from .low_level_commander import LowLevelCommander
from .mavlink_client import Config, MavlinkClient, TimeoutException


class Health:
    def __init__(self) -> None:
        self.is_data_pos = False
        self.is_data_lidar = False
        self.is_data_optical_flow = False
        self.is_calibration_accel = False
        self.is_calibration_gyro = False

    def is_health(self) -> bool:
        return (
            self.is_data_pos
            and self.is_data_lidar
            and self.is_data_optical_flow
            and self.is_calibration_accel
            and self.is_calibration_gyro
        )


class Pmini:
    MAX_TAKEOFF_HEIGHT = 1.5
    POSITION_NORM_THRESHOLD = 0.5

    def __init__(self, config=Config()) -> None:
        self.__mavlink_client = MavlinkClient(config)
        self.__health = Health()
        try:
            self.__mavlink_client.connect()
        except TimeoutException as e:
            logging.exception(f"Could not connect: {e}")
            logging.critical("MAVLink connection failed, system will exit")
            raise SystemExit(1)

        self.__mavlink_client.daemon = True
        self.__mavlink_client.start()
        self.__is_stream = False

        # Wait when mavlink_client is connected
        while not self.__mavlink_client.is_connected():
            time.sleep(0.1)

        self.high_level_commander = HighLevelCommander(self.__mavlink_client)
        self.low_level_commander = LowLevelCommander(self.__mavlink_client)

    def health(self) -> bool:
        return True
        # return self.__health.is_health()

    def enable_stream(self):
        logging.debug("Enable camera stream")
        self.__is_stream = True

    def disable_stream(self):
        logging.debug("Disable camera stream")
        self.__is_stream = True

    def get_image(self):
        if self.__is_stream:
            logging.debug("Get one frame")
        else:
            logging.warning("Stream is unavailable")

    def get_position(self) -> Position:
        """Get current position in NED coordinates.

        Returns
        -------
        Position
            Current position with x (north), y (east), z (down) in meters
        """
        return self.__mavlink_client.current_location

    def get_attitude(self) -> Attitude:
        """Get current attitude.

        Returns
        -------
        Attitude
            Current attitude with roll, pitch, yaw in radians
        """
        return self.__mavlink_client.attitude

    def get_velocity(self) -> Velocity:
        """Get current velocity in NED coordinates.

        Returns
        -------
        Velocity
            Current velocity with v_x (north), v_y (east), v_z (down) in m/s
        """
        return self.__mavlink_client.current_velocity

    def get_of(self):
        return self.__mavlink_client.optical_flow

    def send_msg(self, msg):
        self.__mavlink_client.send_msg(msg)

    def arm(self, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1) -> MAVResult:
        """
        Arms the drone. If the current flight mode is not armable, switches to GUIDED mode first.
        Returns:
            MAVResult: The result of the arm command.
        """
        future: Future[MAVResult] = Future()

        def call_arm():
            self.high_level_commander.arm(None)
            self.high_level_commander.arm(lambda result: future.set_result(result if result is not None else MAVResult.FAILED))

        if self.__mavlink_client.flight_mode != FlightMode.GUIDED:
            logging.warning(f"Current mode is not armable[{self.__mavlink_client.flight_mode}]")
            if self.change_mode(FlightMode.GUIDED).is_failed():
                logging.error("Failed to change mode to GUIDED")
                return MAVResult.FAILED
            call_arm()
        else:
            logging.debug(f"Arming drone in mode {self.__mavlink_client.flight_mode}")
            call_arm()

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending arm attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.arm(None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.error("Arm command timed out")
            return MAVResult.FAILED

    def takeoff(self, height_m: float = 0.5, check_height: bool = True) -> MAVResult:
        """
        Takeoff the drone.
        Args:
            height_m: The height to takeoff to.
            check_height: If True, check if the height is too high.
        Returns:
            MAVResult: The result of the takeoff command.
        """
        if check_height:
            if height_m >= self.MAX_TAKEOFF_HEIGHT:
                logging.error("Takeoff height is too high")
                return MAVResult.FAILED

        future: Future[MAVResult] = Future()

        if self.arm().is_failed():
            logging.error("Arm failed")
            return MAVResult.FAILED

        self.high_level_commander.takeoff(height_m, None)
        self.high_level_commander.takeoff(
            height_m, lambda result: future.set_result(result if result is not None else MAVResult.FAILED)
        )

        try:
            result = future.result(timeout=4.0)
            logging.debug(f"Takeoff at {height_m} meters: {result}")
            logging.debug(f"Initial position: {self.__mavlink_client.current_location}")
            return result
        except FuturesTimeoutError:
            logging.error("Takeoff command timed out")
            return MAVResult.FAILED

    def go_to(self, x: float, y: float, z: float, yaw: Yaw = Yaw(value=0), frame: Frame = Frame.BODY):
        """
        Go to a position.
        Args:
            x: The x coordinate of the position.
            y: The y coordinate of the position.
            z: The z coordinate of the position.
            yaw: The yaw angle of the position.
            frame: The frame of the position.
        """

        self.high_level_commander.go_to(x, y, z, yaw, frame)

    def land(self, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1) -> MAVResult:
        """
        Land the drone.
        """
        future: Future[MAVResult] = Future()

        self.high_level_commander.land(None)
        self.high_level_commander.land(lambda result: future.set_result(result if result is not None else MAVResult.FAILED))

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending land attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.land(None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.error("Takeoff command timed out")
            return MAVResult.FAILED

    def add_sys_status_callback(self, callback):

        def on_result(result: Optional[MAVResult]):
            if result is None or result.is_failed():
                logging.warning("Set EXTENDED_SYS_STATE interval failed or rejected")
            else:
                self.__mavlink_client.add_pmini_state_callback(callback)

        self.__mavlink_client.set_message_interval(
            mavcmd.MAVLINK_MSG_ID_EXTENDED_SYS_STATE,
            int(1_000_000 / 2),
            callback=on_result,
        )

    def change_mode(self, mode: FlightMode, timeout: float = 2.0, retries: int = 5, retry_delay: float = 0.1):
        future: Future[MAVResult] = Future()

        self.high_level_commander.change_mode(mode)

        def on_result(result: Optional[MAVResult]):
            if result is None or result.is_failed():
                logging.error(f"Change mode failed or rejected: {result}")
                return MAVResult.FAILED
            else:
                future.set_result(result)

        self.high_level_commander.change_mode(mode, on_result)

        # subsequent retries send the same message but do not re-register a callback
        for attempt in range(1, retries):
            if future.done():
                break
            logging.debug(f"Resending change mode attempt #{attempt+1} (no callback registration)")
            self.high_level_commander.change_mode(mode, None)
            time.sleep(retry_delay)

        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            logging.exception("Change mode command timed out")
            return MAVResult.FAILED

    def wait_arm(self, timeout=None):
        """
        Block until motors are armed.
        """
        self.__mavlink_client.wait_arm(timeout)

    def disarm(self):
        self.__mavlink_client.disarm()

    def reboot(self):
        self.__mavlink_client.reboot_drone()

    def wait_disarm(self):
        self.__mavlink_client.wait_disarm()

    def add_position_callback(self, callback):
        self.__mavlink_client.add_position_callback(callback)

    def add_velocity_callback(self, callback):
        self.__mavlink_client.add_velocity_callback(callback)

    def add_attitude_callback(self, callback):
        self.__mavlink_client.add_attitude_callback(callback)

    def add_of_callback(self, callback):
        self.__mavlink_client.add_of_callback(callback)

    def add_status_text_callback(self, callback):
        self.__mavlink_client.add_status_text_callback(callback)

    def add_attitude_quat_callback(self, callback):
        self.__mavlink_client.add_attitude_quat_callback(callback)

    def add_flight_mode_callback(self, callback):
        self.__mavlink_client.add_flight_mode_callback(callback)

    def add_pmini_state_callback(self, callback):
        self.__mavlink_client.add_pmini_state_callback(callback)


def get_package_version(package_name):
    try:
        version = metadata.version(package_name)
        return version
    except metadata.PackageNotFoundError:
        return None


def arg_parse():
    parser = argparse.ArgumentParser(description="SDK logging level.")
    parser.add_argument(
        "--log", type=str, default="INFO", help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    args = parser.parse_args()

    # Convert the logging level from string to the corresponding logging constant
    return getattr(logging, args.log.upper(), logging.INFO)


def get_pmini(config=Config()) -> Optional[Pmini]:
    FORMAT = "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s"
    logging.basicConfig(filename="out.log", format=FORMAT, level=arg_parse())

    package_name = "pmini"
    version = get_package_version(package_name)
    if version:
        framed_message = (
            f"\n"
            f"***************************\n"
            f"* Version of {package_name}: {version} *\n"
            f"***************************\n"
        )
        logging.info(framed_message)
    else:
        logging.warning(f"Failed to get the version for the {package_name} package")

    try:
        pmini = Pmini(config)
    except Exception as e:
        logging.error(f"Failed to initialize Pmini: {e}")
        return None

    return pmini


def main():
    FORMAT = "[%(asctime)s] %(levelname)s: %(name)s: %(funcName)s: %(message)s"
    logging.basicConfig(filename="out.log", format=FORMAT, level=arg_parse())

    try:
        pmini = Pmini()
    except Exception as e:
        logging.error(f"Failed to initialize Pmini: {e}")
        return

    if pmini.health():
        logging.info("Pmini ok")
    else:
        logging.error("Pmini not ok")

    pmini.high_level_commander.takeoff()

    # Image
    pmini.get_image()

    pmini.enable_stream()
    pmini.get_image()
    # End image

    pmini.high_level_commander.go_to(0, 1, 0, Yaw(value=45))
    pmini.high_level_commander.forward(1)
    pmini.high_level_commander.backward(1)
    pmini.high_level_commander.up(1)
    pmini.high_level_commander.down(1)

    pmini.high_level_commander.land()
    pmini.low_level_commander.emergency_stop()


if __name__ == "__main__":
    main()
