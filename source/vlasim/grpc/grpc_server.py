import os
import numpy as np
import sys
from pathlib import Path

current_directory = os.path.dirname(os.path.abspath(__file__))
if current_directory not in sys.path:
    sys.path.append(current_directory)


import threading
from concurrent.futures import ThreadPoolExecutor
import grpc

# observation
from daidai.protocol.sim import sim_observation_service_pb2
from daidai.protocol.sim import sim_observation_service_pb2_grpc

class ObservationService(sim_observation_service_pb2_grpc.SimObservationService):
    def __init__(self, server_function):
        self.server_function = server_function


    def InitScene(self, req, rsp):
        rsp = sim_observation_service_pb2.InitSceneRsp()
        target_position = np.array(
            [
                req.robot_pose.position.x,
                req.robot_pose.position.y,
                req.robot_pose.position.z,
            ]
        )
        target_rotation = np.array(
            [
                req.robot_pose.orientation.x,
                req.robot_pose.orientation.y,
                req.robot_pose.orientation.z,
                req.robot_pose.orientation.w,
            ]
        )
        rsp.msg = self.server_function.blocking_start_server(
            data={
                "camera_config":req.camera_config,
                "scene_usd_path": req.scene_usd_path,
                "robot_position": target_position,
                "robot_rotation": target_rotation,
            },
            command=1,
        )

        return rsp
    

class GrpcServer:
    def __init__(self, server_function):
        self.server_function = server_function

    def start(self):
        server_thread = threading.Thread(target=self.server)
        server_thread.start()

    def server(self):
        self._server = grpc.server(
            ThreadPoolExecutor(max_workers=10),
            options=[
                ("grpc.max_send_message_length", 50 * 1024 * 1024),
                ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ],
        )

        sim_observation_service_pb2_grpc.add_SimObservationServiceServicer_to_server(
            ObservationService(self.server_function), self._server
        )
        self.stop()
        self._server.add_insecure_port("0.0.0.0:50051")
        self._server.start()

    def stop(self):
        if self._server:
            self._server.stop(0)