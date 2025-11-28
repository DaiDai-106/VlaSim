import numpy as np
import sys 
import os, time

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)


from vlasim.robot import Robot
from vlasim.grpc.client import RpcClient
from vlasim.utils.logger import Logger

logger = Logger()  # Create singleton instance

# import ik_solver
from copy import deepcopy


class IsaacSimRobot(Robot):
    def __init__(
        self,
        scene_usd="pour water",
        client_host="localhost:50051",
        position=[0, 0, 0],
        rotation=[0, 0, 0, 1],
    ):
        self.client = RpcClient(client_host)
        self.client.InitScene(
            scene_usd=scene_usd,
            init_position=position,
            init_rotation=rotation,
        )

        self.cam_info = None
        self.init_position = position
        self.init_rotation = rotation