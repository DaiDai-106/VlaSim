import argparse
import os, sys
import numpy as np
import glob
import json, uuid
from pathlib import Path
from collections import defaultdict
from vlasim.robot.robot import IsaacSimRobot
from vlasim.utils.logger import Logger

logger = Logger()

class TaskManager:
    def __init__(self,args):
        self.single_evaluate_ret = None
        self.output_dir = args.output_dir
        self.tasks = self.check_task(args)    # TODO 后续可以支持更多并行的tasks 
        self.args = args
        self.task_config = None

    def check_task(self, args):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if args.task_name != "":
            self.task_name = args.task_name
        else:
            raise ValueError("Invalid task_name")
        return self.task_name

    # 进行模型推理的核心的接口
    def model_policy(self):
        # init robot and scene
        robot = IsaacSimRobot(
            self.tasks,
            client_host=self.args.client_host
        )




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--client_host",
        type=str,
        default="localhost:50051",
        help="The client host",
    )
    parser.add_argument(
        "--task_name",
        type=str,
        default="iros_stamp_the_seal",
        help="Specify the task to evaluate",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=("output"),   # TODO 
        help="Set output directory",
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Set the fps of the recording"
    )
    parser.add_argument("--record", action="store_true", help="Enable data recording")
    args = parser.parse_args()

    logger.info(
        "Evaluating vla model of on task: {}".format(args.task_name)
    )

    task_manager = TaskManager( args )
    task_manager.model_policy()
    logger.info("Task finished")
    # benchmark.evaluate_policy()  # Evaluate agent on the benchmark
    # policy.shutdown()


if __name__ == "__main__":
    main()
