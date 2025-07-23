#!/bin/bash

USER=cat

# 先停止播控程序
/home/${USER}/xwsoft/audio_controller/script/shutdown_audio_controller.sh

sleep 15

# 启动播控程序
nohup python3 /home/${USER}/xwsoft/audio_controller/src/main.py > /home/${USER}/xwsoft/audio_controller/log/audio_controller.log 2>&1 &