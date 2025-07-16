#!/bin/bash

USER=cat

#! audio_controller
echo "setup audio_controller systemd ..."
SYSTEMD_SERVICE_NAME="audio_controller.service"
sudo cp -f  /home/${USER}/xwsoft/audio_controller/script/setup/${SYSTEMD_SERVICE_NAME} /etc/systemd/system/${SYSTEMD_SERVICE_NAME}
sudo systemctl enable ${SYSTEMD_SERVICE_NAME}
