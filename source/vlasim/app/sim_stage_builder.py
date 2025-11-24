import asyncio, os
import numpy as np

from vlasim.utils.logger import Logger

logger = Logger() 

# sim manager  需要适配IsaacSim的World
class SimStageBuilder:
    def __init_(self):
        self.articulation = None
        self.articulation_rmpflow = None
        self._target = None
        self._currentCamera = ""
        self._followingPos = np.array([0, 0, 0])
        self._followingOrientation = np.array([1, 0, 0, 0])
        self.currentImg = None
        self.currentCamInfo = None
        self.curoboMotion = None
        self.rmp_move = False
        self.cmd_list = None
        self.reached = False
        self.cameras = []
        self.art_controllers = []