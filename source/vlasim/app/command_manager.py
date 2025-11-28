import os, sys
import numpy as np
import threading
import queue
import json
import asyncio
import subprocess
import signal

from pathlib import Path
from typing import Tuple
from PIL import Image
from vlasim.utils.logger import Logger
from pprint import pprint
from opentelemetry import trace
from vlasim.utils.utils import *

logger = Logger() 

from isaacsim.core.prims import SingleArticulation
from isaacsim.core.api.materials import PhysicsMaterial, OmniPBR, OmniGlass
from isaacsim.core.api.objects import cuboid, cylinder
from isaacsim.core.prims import SingleXFormPrim, SingleGeometryPrim, SingleRigidPrim
from isaacsim.core.utils.prims import get_prim_at_path, get_prim_object_type
from isaacsim.core.utils.bounds import compute_aabb, create_bbox_cache
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.robot.manipulators.grippers.surface_gripper import SurfaceGripper
from isaacsim.core.utils.stage import get_current_stage
from isaacsim.sensors.camera import Camera
from isaacsim.sensors.physics import ContactSensor
from isaacsim.robot.manipulators import SingleManipulator
from isaacsim.robot.manipulators.examples.franka.controllers.pick_place_controller import PickPlaceController
from isaacsim.robot.manipulators.grippers import ParallelGripper
from isaacsim.storage.native import get_assets_root_path

from omni.kit.viewport.utility import (
    create_viewport_window,
    get_active_viewport,
    get_active_viewport_window,
    get_num_viewports,
    get_active_viewport_and_window,
)
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, UsdPhysics, PhysxSchema

import omni.ui as ui
import omni.replicator.core as rep
import omni.timeline
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from omni.physx.scripts import utils, physicsUtils, particleUtils
import omni.usd

tracer = trace.get_tracer(__name__)

# 用于接受客户端的请求并分发任务
class CommandManager:
    def __init__(
        self,
        sim_stage,
    ):
        self.sim_stage = sim_stage
        self.data = None
        self.command = 0  # index flag
        self.data_to_send = None
        self._lock = threading.Lock()
        self.condition = threading.Condition()
        self.result_queue = queue.Queue()
        self.exit = False
        self.status = 0

        self.robot = None
        self.controller = None
        self.articulation_controller = None

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
            self.status = 0
            self.result_queue.put(result)

    def on_command_step(self):
        if not self.data or not self.command:
            return
        if self.status:
            return
        else:
            with tracer.start_as_current_span(
                f"server.step_command_{self.command}"
            ) as span:
                self.status = 1
                if self.command == 1:
                    self._init_scene_cfg(
                        scene_usd=self.data["scene_usd_path"],
                        init_position=self.data["robot_position"],
                        init_rotation=self.data["robot_rotation"],
                    )
                    logger.info("init scene success")
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
        init_rotation=[0, 0, 0, 1],
    ):
        logger.info(f"start isaac sim starge configuration_{ threading.get_ident() }")
        # 尝试加载场景
        scene_usd_path = str(assets_path()) + "/" + scene_usd + "/" + scene_usd + ".usda"
        prim = get_prim_at_path("/World")
        # 添加引用
        add_reference_to_stage(scene_usd_path, "/World")
        camera_state = ViewportCameraState("/OmniverseKit_Persp")
        camera_state.set_position_world(
            Gf.Vec3d(1.9634841037804776, 0.9488467163528935, 2.1182000480154555), True
        )
        camera_state.set_target_world(
            Gf.Vec3d(init_position[0], init_position[1], init_position[2]), True
        )

        # 这里尝试添加机器人的引用, 目前写死的franka, 无非是你想将franka放置在哪里
        all_assets_root_path = get_assets_root_path()
        asset_path = all_assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
        robot = add_reference_to_stage(usd_path=asset_path, prim_path="/World/Franka")
        robot.GetVariantSet("Gripper").SetVariantSelection("AlternateFinger")
        robot.GetVariantSet("Mesh").SetVariantSelection("Quality")
        gripper = ParallelGripper(
            end_effector_prim_path="/World/Franka/panda_rightfinger",
            joint_prim_names=["panda_finger_joint1", "panda_finger_joint2"],
            joint_opened_positions=np.array([0.05, 0.05]),
            joint_closed_positions=np.array([0.02, 0.02]),
            action_deltas=np.array([0.01, 0.01]),
        )

        my_franka = self.sim_stage.my_world.scene.add(
            SingleManipulator(
                prim_path="/World/Franka",
                name="my_franka",
                end_effector_prim_path="/World/Franka/panda_rightfinger",
                gripper=gripper,
                position=init_position,  # 设置初始位置
                orientation=init_rotation  # 设置初始旋转（四元数）
            )
        )

        my_franka.gripper.set_default_state(my_franka.gripper.joint_opened_positions)
        self.sim_stage.my_world.reset()
        my_controller = PickPlaceController(
            name="pick_place_controller", gripper=my_franka.gripper, robot_articulation=my_franka
        )
        articulation_controller = my_franka.get_articulation_controller()
        self.controller = my_controller
        self.articulation_controller = articulation_controller

        # 设置物理场景
        stage = omni.usd.get_context().get_stage()
        self.scene = UsdPhysics.Scene.Define(stage, Sdf.Path("/physicsScene"))
        self.scene.CreateGravityDirectionAttr().Set(Gf.Vec3f(0.0, 0.0, -1.0))
        self.scene.CreateGravityMagnitudeAttr().Set(9.81)

        self._play()

        
    def _play(self):
        self.sim_stage.my_world.play()
     
    def on_physics_step(self):
        self.on_command_step()