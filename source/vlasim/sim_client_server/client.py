import grpc
import numpy as np
import sys, os
import time
import json

# observation
from daidai.protocol.sim import sim_observation_service_pb2
from daidai.protocol.sim import sim_observation_service_pb2_grpc
from vlasim.utils.logger import Logger
logger = Logger()

class Rpc_Client:
    def __init__(self, client_host ):
        for i in range(600):
            try:
                self.channel = grpc.insecure_channel(
                    client_host,
                    options=[("grpc.max_receive_message_length", 50 * 1024 * 1024)],
                )
                grpc.channel_ready_future(self.channel).result(timeout=5)
                break
            except grpc.FutureTimeoutError as e:
                logger.error(f"Failed to connect to gRPC server[{i}]: {e}")
                time.sleep(3)
                if i >= 599:
                    raise e
            except grpc.RpcError as e:
                logger.error(f"Failed to connect to gRPC server[{i}]: {e}")
                time.sleep(3)
                if i >= 599:
                    raise e
                

    def InitScene(
        self,
        scene_usd,
        init_position=[0, 0, 0],
        init_rotation=[0, 0, 0, 1],
    ):
        stub = sim_observation_service_pb2_grpc.SimObservationServiceStub(self.channel)
        req = sim_observation_service_pb2.InitRobotReq()
        req.scene_usd_path = (
            scene_usd,
        )
        (
            req.robot_pose.position.x,
            req.robot_pose.position.y,
            req.robot_pose.position.z,
        ) = init_position
        (
            req.robot_pose.orientation.x,
            req.robot_pose.orientation.y,
            req.robot_pose.orientation.z,
            req.robot_pose.orientation.w,
        ) = init_rotation
        response = stub.InitRobot(req)
        return response