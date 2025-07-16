#!/bin/bash

USER=cat

sleep 5

sudo -u ${USER} nohup python3 /home/${USER}/xwsoft/audio_controller/src/main.py > /home/${USER}/xwsoft/audio_controller/log/audio_controller.log 2>&1 &