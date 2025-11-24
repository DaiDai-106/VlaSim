import os, sys
from pathlib import Path
from typing import Tuple
import numpy as np
from PIL import Image
from vlasim.utils.logger import Logger

import threading
import queue
import json
import asyncio
from opentelemetry import trace

import subprocess
import signal
from pprint import pprint


logger = Logger() 
tracer = trace.get_tracer(__name__)

# 用于接受客户端的请求并分发任务
class CommandManager:
    def __init__(
        self,
        sim_stage,
    ):
        self.sim_stage = sim_stage

        # 
        self.data = None
        self.command = 0  # index flag
        self.data_to_send = None
        self._lock = threading.Lock()
        self.condition = threading.Condition()
        self.result_queue = queue.Queue()
        self.exit = False

    # 异步执行服务
    def blocking_start_server(self, data, command):
        with self._lock:
            self._on_blocking_thread(data, command)
            if not self.result_queue.empty():
                result = self.result_queue.get()
                return result
            
    def _on_blocking_thread(self, data, command):
        self.data = data
        self.command = command
        with self.condition:
            while self.data_to_send is None:
                self.condition.wait()
            result = self.data_to_send
            self.data_to_send = None
            self.command = 0
            self.result_queue.put(result)

    def on_command_step(self):
        if not self.data or not self.command:
            return
        else:
            with tracer.start_as_current_span(
                f"server.step_command_{self.command}"
            ) as span:
                if self.command == 1:
                    self._init_scene_cfg(
                        scene_usd=self.data["scene_usd_path"],
                        init_position=self.data["robot_position"],
                        init_rotation=self.data["robot_rotation"],
                    )
                    self.data_to_send = "success"
                elif self.command == 2:
                    pass 

        if self.command:
            with self.condition:
                self.condition.notify_all()
                        
    def _init_scene_cfg(
        self,
        scene_usd,
        init_position=[0, 0, 0],
        init_rotation=[1, 0, 0, 0],
    ):
        logger.info("start isaac sim starge configuration")
     
    def on_physics_step(self):
        self.on_command_step()