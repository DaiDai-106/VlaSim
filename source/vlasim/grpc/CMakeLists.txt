cmake_minimum_required(VERSION 3.16)
project(daidai_protocol)

# 查找所有 proto 文件
file(GLOB_RECURSE PROTO_FILES "daidai/protocol/*.proto")

# 为每个 proto 文件生成 Python 代码
foreach(PROTO_FILE ${PROTO_FILES})
    get_filename_component(PROTO_DIR ${PROTO_FILE} DIRECTORY)
    get_filename_component(PROTO_NAME ${PROTO_FILE} NAME_WE)
    
    # 在 proto 文件所在目录生成代码
    execute_process(
        COMMAND python -m grpc_tools.protoc
        --proto_path=${CMAKE_SOURCE_DIR}
        --python_out=${CMAKE_SOURCE_DIR}
        --grpc_python_out=${CMAKE_SOURCE_DIR}
        ${PROTO_FILE}
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
    
    message(STATUS "Generated: ${PROTO_DIR}/${PROTO_NAME}_pb2.py")
endforeach()