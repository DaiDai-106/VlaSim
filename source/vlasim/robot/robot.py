import numpy as np
import os, time

from vlasim.robot import Robot
from vlasim.grpc.client import RpcClient
from vlasim.utils.logger import Logger

logger = Logger()  # Create singleton instance

# import ik_solver
from copy import deepcopy


class IsaacSimRobot(Robot):
    def __init__(
        self,
        scene_usd="Pick_Place_Franka_Yellow_Table.usd",
        client_host="localhost:50051",
        position=[0, 0, 0],
        rotation=[0, 0, 0, 1],
        gripper_control_type=0,
    ):

        self.client = RpcClient(client_host)
        self.client.InitScene(
            robot_usd="",
            scene_usd=scene_usd,
            init_position=position,
            init_rotation=rotation,
        )

        self.cam_info = None
        self.init_position = position
        self.init_rotation = rotation
        self.gripper_control_type = gripper_control_type