import logging
from typing import Optional

import pymavlink.dialects.v20.ardupilotmega as mavcmd

from .common import FlightMode, Frame, Yaw
from .mavlink_client import AckCallback

logger = logging.getLogger(__name__)


class HighLevelCommander:
    def __init__(self, mavlink_client=None):
        self.__mavlink_client = mavlink_client

    def go_to(self, x: float, y: float, z: float, yaw: Yaw = Yaw(value=0), frame: Frame = Frame.BODY):
        logger.debug(f"Send go to: pos = ({x}, {y}, {z}) yaw = {yaw.value}[deg] in {frame}")
        type_mask = (
            mavcmd.POSITION_TARGET_TYPEMASK_VX_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_VY_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_VZ_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AX_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AY_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AZ_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_FORCE_SET
            | mavcmd.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
        )

        self.__mavlink_client.send_msg(self.__mavlink_client.command_packager.package_go_to(x, y, z, type_mask, yaw))

    def forward(self, dist_m: float):
        self.go_to(dist_m, 0, 0, Yaw(), frame=Frame.BODY)

    def backward(self, dist_m: float):
        self.go_to(-dist_m, 0, 0, Yaw(), frame=Frame.BODY)

    def up(self, dist_m: float):
        self.go_to(0, 0, dist_m, Yaw(), frame=Frame.BODY)

    def down(self, dist_m: float):
        self.go_to(0, 0, -dist_m, Yaw(), frame=Frame.BODY)

    def arm(self, callback: Optional[AckCallback] = None):
        self.__mavlink_client.send_msg_with_ack(self.__mavlink_client.command_packager.package_arm(), callback)

    def change_mode(self, mode: FlightMode, callback: Optional[AckCallback] = None):
        self.__mavlink_client.send_msg_with_ack(self.__mavlink_client.command_packager.package_flight_mode(mode), callback)

    def takeoff(self, height_m: float = 0.5, callback: Optional[AckCallback] = None):
        self.__mavlink_client.send_msg_with_ack(self.__mavlink_client.command_packager.package_takeoff(height_m), callback)

    def land(self, callback: Optional[AckCallback] = None):
        self.__mavlink_client.send_msg_with_ack(self.__mavlink_client.command_packager.package_land(), callback)
        logger.debug("Land")

    def set_height(self, height_m: float, callback: Optional[AckCallback] = None):
        if height_m == 0.0:
            self.land(callback)
        elif height_m <= 0.3:
            logger.warning("You cannot set a height less than 0.3[m]")
        logger.debug(f"Set the height of {height_m} meters")

    def __arm_with_retry(self):
        while True:
            try:
                # Attempt to arm the drone
                self.__mavlink_client.arm()
                logger.info("Attempting to arm the drone.")

                # Wait for the arming process to complete
                self.__mavlink_client.wait_arm(0.2)

                logger.info("Drone armed successfully.")
                break  # Exit the loop if arming succeeds
            except TimeoutError as e:
                # Log the timeout and retry
                logger.warning(f"Timeout expired while arming the drone: {e}")
                logger.warning("Retrying to arm the drone...")
            except Exception as e:
                # Handle other unexpected exceptions
                logger.exception(f"Unexpected error occurred: {e}")
                logger.warning("Retrying to arm the drone...")

    def __disarm(self):
        logger.debug("Disarm")
