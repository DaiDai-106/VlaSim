import os
import omni
import omni.graph.core as og
import omni.ui as ui
import numpy as np
from vlasim.utils.logger import Logger
from isaacsim.sensors.camera import Camera

from omni.isaac.core.utils.viewports import (
    set_active_viewport_camera,
    create_viewport_for_camera
)

logger = Logger() 

class USDBase:
    def __init__(self):
        black_image = np.zeros((720, 1280, 4), dtype=np.uint8)
        black_image[:, :, 3] = 255  # 设置alpha通道为不透明
        self.current_image = black_image
        self.camera = None
        pass
    
    def step(self):
        pass

    def _init_camera(self, rendering_dt, param):
        # 初始化相机传感器
        camera = Camera(
            prim_path=param["path"],
            frequency=param["frequency"],
            resolution=(
                param["resolution"]["width"],
                param["resolution"]["height"],
            ),
        )

        self.camera = camera
        camera.set_world_pose(position=param["pose"]["position"], orientation=param["pose"]["quaternion"], camera_axes="usd")    
        camera.initialize()
        rgb_data = self.camera.get_rgb()
        self.current_image = rgb_data
        create_viewport_for_camera("camera viewport", param["path"])
        # set_active_viewport_camera( param["path"] )      

        # vp = viewport_util.create_viewport_window("Camera Preview", width=640, height=480)
        # viewport_util.set_camera_for_viewport(vp, param["path"])
        # vp.viewport_api.camera_path = param["path"]
    
        
    def update_rgb( self ):
        rgb_data = self.camera.get_rgb()
        self.current_image = rgb_data


