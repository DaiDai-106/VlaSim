import os
import numpy as np
import sys
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import grpc

# observation
from daidai.protocol.sim import sim_observation_service_pb2
from daidai.protocol.sim import sim_observation_service_pb2_grpc



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