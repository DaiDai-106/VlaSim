import os
import omni
import omni.graph.core as og
import omni.ui as ui
import numpy as np
from vlasim.utils.logger import Logger
from isaacsim.sensors.camera import Camera

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
        camera.set_world_pose(position=param["pose"]["position"], orientation=param["pose"]["quaternion"])
        camera.initialize()
        rgb_data = self.camera.get_rgb()
        self.current_image = rgb_data

        self.window = ui.Window(
                    title=param["path"],
                    width=1300,
                    height=740,  # 为标题栏留出额外空间
                    visible=True,
                    dockPreference=ui.DockPreference.DISABLED
                )
    
        
    def update_rgb( self ):
        rgb_data = self.camera.get_rgb()
        self.current_image = rgb_data


