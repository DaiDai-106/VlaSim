import argparse
import os
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from vlasim.app.command_manager import CommandManager
from vlasim.app.sim_stage_builder import SimStageBuilder
from vlasim.grpc.grpc_server import GrpcServer

parser = argparse.ArgumentParser(description="standalone_sim sever launcher script.")
parser.add_argument("--physics_step", type=int, default=120)
parser.add_argument("--rendering_step", type=int, default=30)
parser.add_argument(
    "--enable_gpu_dynamics",
    action="store_true",
    default=False,
    help="enable_gpu_dynamics",
)

args_cli = parser.parse_args()
# import issac sim xiang guan zu jian

def main():
    """Main function."""

    physics_dt = 1.0 / args_cli.physics_step
    # world = World(
    #     stage_units_in_meters=1,
    #     physics_dt=physics_dt,
    #     rendering_dt=1.0 / args_cli.rendering_step,
    # )
    # # Override CPU setting to use GPU
    # if args_cli.enable_gpu_dynamics:
    #     physx_interface = omni.physx.get_physx_interface()
    #     physx_interface.overwrite_gpu_setting(1)
    #     world._physics_context.enable_gpu_dynamics(flag=True)
    #     world._physics_context.enable_ccd(flag=True) # use continous collision 

    # hou xu xu yao tian jia sim 
    sim_stage_builder = SimStageBuilder() 
    server_function = CommandManager(
        sim_stage = sim_stage_builder,
    )
    rpc_server = GrpcServer(server_function=server_function)
    rpc_server.start()

    step = 0
    while True:
        print( step )
        step += 1

        # ui_builder.my_world.step(render=True)
        if rpc_server:
            rpc_server.server_function.on_physics_step()
            if rpc_server.server_function.exit:
                break

    # simulation_app.close()


if __name__ == "__main__":
    # run the main execution
    main()
