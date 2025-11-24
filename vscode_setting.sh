#!/bin/bash

echo "Generating VSCode Settings file..."

cd "$(dirname "$0")"
python -m isaacsim --generate-vscode-settings
python -m isaaclab --generate-vscode-settings

if [ $? -eq 0 ]; then
    echo "Setting Successfully！"
    echo "Location: $(pwd)/.vscode/settings.json"
else
    echo "Generation failed. Please check if Isaac Sim is installed correctly..."
fi