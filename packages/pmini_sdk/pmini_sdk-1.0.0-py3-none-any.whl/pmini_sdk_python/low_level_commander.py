import logging

import pymavlink.dialects.v20.ardupilotmega as mavcmd

from .common import Frame

logger = logging.getLogger(__name__)


class LowLevelCommander:
    def __init__(self, mavlink_client=None):
        self.__mavlink_client = mavlink_client

    def send_velocity(self):
        logger.debug("send velocity")

    def emergency_stop(self):
        logger.debug("Emergency stop")

    def set_velocity(self, x: float, y: float, z: float, yaw: float, frame: Frame = Frame.BODY):
        logger.info(f"package and send: vel = ({x}, {y}, {z}) yaw = {yaw}[deg] in {frame}")
        type_mask = (
            mavcmd.POSITION_TARGET_TYPEMASK_X_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_Y_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_Z_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AX_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AY_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_AZ_IGNORE
            | mavcmd.POSITION_TARGET_TYPEMASK_FORCE_SET
            | mavcmd.POSITION_TARGET_TYPEMASK_YAW_RATE_IGNORE
        )

        self.__mavlink_client.send_msg(self.__mavlink_client.command_packager.package_velocity(x, y, z, type_mask, yaw))

    def set_angle(self, r: float, p: float, y: float, yaw: float, frame: Frame = Frame.BODY):
        logger.debug(f"Send angle: vel = ({r}, {p}, {y}) yaw = {yaw}[deg] in {frame}")
