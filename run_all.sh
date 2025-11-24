#!/bin/bash

# 设置 Python 解释器路径
PYTHON_BIN="/home/wangyf/miniconda3/envs/env_isaacsim/bin/python"

# 定义清理函数
cleanup() {
    echo "Stopping processes..."
    # 关闭 Server
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null
    fi
    # 关闭 tail
    if [ -n "$TAIL_PID" ]; then
        kill $TAIL_PID 2>/dev/null
    fi
    exit
}

# 捕获信号
trap cleanup SIGINT SIGTERM

# 1. 启动 Server (后台运行)，输出重定向到文件
echo "Starting Server..."
$PYTHON_BIN run_server.py > server.log 2>&1 &
SERVER_PID=$!

# 2. 启动 tail 实时显示日志 (后台运行)
# 这样既能看到日志，又能通过脚本管理进程
tail -f server.log &
TAIL_PID=$!

# 等待几秒钟确保 Server 启动完成
echo "Waiting for server to initialize..."
sleep 5

# 3. 启动 Client
echo "Starting Client..."
$PYTHON_BIN run_client.py

# 4. Client 运行结束后，清理进程
echo "Client finished."
cleanup
